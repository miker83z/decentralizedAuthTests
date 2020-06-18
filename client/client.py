import time
import binascii
import json
import asyncio
import aiohttp
from umbral import pre, keys, signing, config
from umbral.curve import SECP256K1
from umbral.params import UmbralParameters

nodes = open('nodes.txt').read().splitlines()
api_call = '/api/keyfrags/'
plaintext = b'Proxy Re-Encryption is cool!'

nodes_num = len(nodes)
threshold = 1
params = UmbralParameters(SECP256K1)
cfrags = []


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                assert response.status == 200
                return await response.read()
        except Exception:
            print("Couldn't get json from " + url)


async def get_cfrag_from_node(node, k_id):
    print('-- {} - Reaching node '.format(node))
    # await asyncio.sleep(random.randint(1, 8))  # test async
    resp = await get_json(node+api_call+str(k_id))
    if resp != None:
        j = json.loads(resp.decode('utf-8'))
        cfrags.append(pre.CapsuleFrag.from_bytes(
            binascii.unhexlify(j['rekeyfrag'].encode()), SECP256K1))
        print('-- {} - Re-encrypted key fragment received'.format(node))
        if len(cfrags) >= threshold:
            shutdown()


def shutdown():
    print('Closing unnecessary connections...')
    for task in asyncio.all_tasks():
        task.cancel()


async def post_json(url, json):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=json) as response:
                assert response.status == 201
                return await response.json()
        except Exception:
            print("Couldn't post json to " + url)


def main():
    distr_success = 0
    # SETUP
    print("Setting up the environment...")
    # Generate encryption keys for Alice
    sk_a = keys.UmbralPrivateKey.gen_key(params)
    pk_a = sk_a.get_pubkey()

    # Generate singing keys for Alice
    sign_a = keys.UmbralPrivateKey.gen_key(params)
    verify_a = sign_a.get_pubkey()
    signer_a = signing.Signer(private_key=sign_a)

    # Generate encryption keys for Bob
    sk_b = keys.UmbralPrivateKey.gen_key(params)
    pk_b = sk_b.get_pubkey()

    # ENCRYPTION
    print('Encrypting...')
    # Encrypt data with Alice's public key
    ciphertext, capsule = pre.encrypt(pk_a, plaintext)

    # Alice generates encryption key fragments
    kfrags = pre.generate_kfrags(delegating_privkey=sk_a,
                                 signer=signer_a,
                                 receiving_pubkey=pk_b,
                                 threshold=threshold,
                                 N=nodes_num)

    # DISTRIBUTION
    k_id = int(time.time())
    print('Distributing key fragment with id {} to nodes...'.format(str(k_id)))
    payload = {
        'capsule': binascii.hexlify(capsule.to_bytes()).decode(),
        'delegating': binascii.hexlify(pk_a.to_bytes()).decode(),
        'receiving': binascii.hexlify(pk_b.to_bytes()).decode(),
        'verifying': binascii.hexlify(verify_a.to_bytes()).decode()
    }
    # Async operations
    loop = asyncio.get_event_loop()
    atasks = []
    for i, node in enumerate(nodes):
        print('-- {} - Reaching node '.format(node))
        pay_tmp = {
            'id': k_id,
            'capsule': payload['capsule'],
            'keyfrag': binascii.hexlify(kfrags[i].to_bytes()).decode(),
            'delegating': payload['delegating'],
            'receiving': payload['receiving'],
            'verifying': payload['verifying']
        }
        print('-- {} - Key fragment sent'.format(node))
        task = asyncio.ensure_future(post_json(node+api_call, pay_tmp))
        atasks.append(task)
    try:
        listko = loop.run_until_complete(asyncio.gather(*atasks))
    finally:
        loop.stop()
        loop.close()

    distr_success = nodes_num - listko.count(None)
    if distr_success >= threshold:
        print('Distributed {}/{} key fragments'.format(distr_success, nodes_num))
    else:
        raise ValueError(
            'ERROR: Distributed {}/{} key fragments and threshold is {}'.format(distr_success, nodes_num, threshold))

    # BOB'S OPERATIONS
    print('Starting decryption operations')
    capsule.set_correctness_keys(delegating=pk_a,
                                 receiving=pk_b,
                                 verifying=verify_a)
    # Async operations
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    atasks = []
    for node in nodes:
        task = asyncio.ensure_future(get_cfrag_from_node(node, k_id))
        atasks.append(task)
    try:
        loop.run_until_complete(asyncio.wait(atasks))
    except asyncio.CancelledError:
        pass
    finally:
        loop.stop()
        loop.close()
    # Combine cfrags
    if len(cfrags) >= threshold:
        print('Decrypting...')
        for cfrag in cfrags:
            capsule.attach_cfrag(cfrag)
        cleartext_b = pre.decrypt(ciphertext=ciphertext,
                                  capsule=capsule,
                                  decrypting_key=sk_b)
        print(cleartext_b)
    else:
        raise ValueError(
            'ERROR: Received {}/{} key fragments and threshold is {}'.format(len(cfrags), nodes_num, threshold))


if __name__ == '__main__':
    main()
