import time
import binascii
import json
import asyncio
import aiohttp
from umbral import pre, keys, signing, config
from umbral.curve import SECP256K1
from umbral.params import UmbralParameters
import json
import sys
import getopt

port = "5022"
nodes = open('nodes.txt').read().splitlines()
nodes = ["http://" + node + ":" + port for node in nodes]
api_call = '/api/keyfrags/'
nodes_num = len(nodes)
params = UmbralParameters(SECP256K1)

# Flags
threshold_flag = True
show_latency_flag = False
show_debug_flag = False
fixed_messages_sizes = False
threshold_init = 3
inputfile = ''
outputfile = ''
step_it = 1
max_it = nodes_num + 1
try:
    opts, args = getopt.getopt(sys.argv[1:], "hmxfdt:s:l:", [
                               "threshold=", "step=", "limit="])
except getopt.GetoptError:
    print(
        '-m --message\n-x --fixed\n-l --latency\n-d --debug \n-t --threshold <value>\n-s --step <value>\n-f --final <value>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print(
            '-m --message\n-x --fixed\n-l --latency\n-d --debug \n-t --threshold <value>\n-s --step <value>\n-f --final <value>')
        sys.exit()
    elif opt in ("-m", "--message"):
        threshold_flag = False
    elif opt in ("-x", "--fixed"):
        if not threshold_flag:
            fixed_messages_sizes = True
    elif opt in ("-f", "--latency"):
        show_latency_flag = True
    elif opt in ("-d", "--debug"):
        show_debug_flag = True
    elif opt in ("-t", "--threshold"):
        threshold_init = int(arg)
    elif opt in ("-s", "--step"):
        step_it = int(arg)
    elif opt in ("-l", "--limit"):
        if not threshold_flag or int(arg) <= nodes_num + 1:
            max_it = int(arg)
print('{} is varying\nThreshold is {}\nStep is {}\nLimit value is {}'.format('Threshold' if threshold_flag else 'Message size',
                                                                             threshold_init if threshold_flag else 'not fixed', step_it, max_it))


def show_latency(message, latency):
    if show_latency_flag:
        print('|||| ' + message + str(latency))


def show_debug(message):
    if show_debug_flag:
        print(message)


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                assert response.status == 200
                return await response.read()
        except Exception:
            print("Couldn't get json from " + url)


async def get_cfrag_from_node(node, k_id, cfrags, threshold):
    show_debug('-- {} - Reaching node '.format(node))
    # await asyncio.sleep(random.randint(1, 8))  # test async
    resp = await get_json(node+api_call+str(k_id))
    if resp != None:
        j = json.loads(resp.decode('utf-8'))
        cfrags.append(pre.CapsuleFrag.from_bytes(
            binascii.unhexlify(j['rekeyfrag'].encode()), SECP256K1))
        show_debug('-- {} - Re-encrypted key fragment received'.format(node))
        if len(cfrags) >= threshold:
            shutdown()


def shutdown():
    show_debug('Closing unnecessary connections...')
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


def setup():
    show_debug("Setting up the environment...")
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

    return(pk_a, sk_a, signer_a, verify_a, pk_b, sk_b)


def distribute_key_fragments(k_id, kfrags, payload, threshold):
    show_debug(
        'Distributing key fragment with id {} to nodes...'.format(str(k_id)))

    # Async operations
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    atasks = []
    for i, node in enumerate(nodes):
        show_debug('-- {} - Reaching node '.format(node))
        pay_tmp = {
            'id': k_id,
            'capsule': payload['capsule'],
            'keyfrag': binascii.hexlify(kfrags[i].to_bytes()).decode(),
            'delegating': payload['delegating'],
            'receiving': payload['receiving'],
            'verifying': payload['verifying']
        }
        show_debug('-- {} - Key fragment sent'.format(node))
        task = asyncio.ensure_future(post_json(node+api_call, pay_tmp))
        atasks.append(task)
    try:
        listko = loop.run_until_complete(asyncio.gather(*atasks))
    finally:
        loop.stop()
        loop.close()

    print(listko)

    distr_success = nodes_num - listko.count(None)
    if distr_success >= threshold:
        show_debug(
            'Distributed {}/{} key fragments'.format(distr_success, nodes_num))
        temp = 0
        cnt = 0
        for reslt in listko:
            if reslt is not None:
                cnt += 1
                temp += reslt['time']
        return temp / cnt
    else:
        raise ValueError(
            'ERROR: Distributed {}/{} key fragments and threshold is {}'.format(distr_success, nodes_num, threshold))


def gather_capsule_fragments(k_id, capsule, threshold):
    show_debug('Gathering capsule fragments from nodes...')
    cfrags = []
    # Async operations
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    atasks = []
    for node in nodes:
        task = asyncio.ensure_future(
            get_cfrag_from_node(node, k_id, cfrags, threshold))
        atasks.append(task)
    try:
        loop.run_until_complete(asyncio.wait(atasks))
    except asyncio.CancelledError:
        pass
    finally:
        loop.stop()
        loop.close()
    return cfrags


def decrypt(cfrags, capsule, ciphertext, sk_b, threshold):
    # Combine cfrags
    if len(cfrags) >= threshold:
        show_debug('Decrypting...')
        for cfrag in cfrags:
            capsule.attach_cfrag(cfrag)
        return pre.decrypt(ciphertext=ciphertext,
                           capsule=capsule,
                           decrypting_key=sk_b)

    else:
        raise ValueError(
            'ERROR: Received {}/{} key fragments and threshold is {}'.format(len(cfrags), nodes_num, threshold))


def simple():
    # SETUP
    (pk_a, sk_a, signer_a, verify_a, pk_b, sk_b) = setup()
    threshold = threshold_init

    plaintext = b'Proxy Re-Encryption'

    # Alice #####################################################
    # ENCRYPTION
    show_debug('Encrypting...')
    ciphertext, capsule = pre.encrypt(pk_a, plaintext)

    # KEY FRAGMENTS GENERATION
    kfrags = pre.generate_kfrags(delegating_privkey=sk_a,
                                 signer=signer_a,
                                 receiving_pubkey=pk_b,
                                 threshold=threshold,
                                 N=nodes_num)

    # DISTRIBUTION
    k_id = int(time.time()*1000)
    payload = {
        'capsule': binascii.hexlify(capsule.to_bytes()).decode(),
        'delegating': binascii.hexlify(pk_a.to_bytes()).decode(),
        'receiving': binascii.hexlify(pk_b.to_bytes()).decode(),
        'verifying': binascii.hexlify(verify_a.to_bytes()).decode()
    }
    distribute_key_fragments(k_id, kfrags, payload, threshold)

    # Bob #######################################################
    # CAPSULE FRAGMENTS GATHERING
    capsule.set_correctness_keys(delegating=pk_a,
                                 receiving=pk_b,
                                 verifying=verify_a)
    cfrags = gather_capsule_fragments(k_id, capsule, threshold)

    # DECRYPT
    plaintext_b = decrypt(cfrags, capsule, ciphertext, sk_b, threshold)

    # FINISH
    assert(plaintext_b == plaintext)
    show_debug(plaintext_b)


def main():
    # SETUP
    (pk_a, sk_a, signer_a, verify_a, pk_b, sk_b) = setup()

    case = 'threshold' if threshold_flag else 'message_size'
    filename = 'datasets/{}/results{}.json'.format(case, int(time.time()*1000))
    with open(filename, 'w', newline='') as file:
        writer = []
        sizes_range = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000,
                       1000000] if fixed_messages_sizes else range(step_it, max_it, step_it)

        max_rang = 10

        for x in sizes_range:
            time.sleep(.5)
            enc = kfr = ree = dis = cfr = dec = tot = 0
            for _ in range(0, 10):
                time.sleep(.3)
                if threshold_flag:
                    threshold = x
                    plaintext = ''.join('x' for _ in range(30)).encode()
                else:
                    threshold = threshold_init
                    plaintext = ''.join('x' for _ in range(x)).encode()
                # Alice #####################################################
                # ENCRYPTION
                show_debug('Encrypting...')
                now = time.time()*1000
                ciphertext, capsule = pre.encrypt(pk_a, plaintext)
                end = time.time()*1000
                enc_tot = end-now
                show_latency('Encrypted in (ms)= ', enc_tot)

                # KEY FRAGMENTS GENERATION
                now = time.time()*1000
                kfrags = pre.generate_kfrags(delegating_privkey=sk_a,
                                             signer=signer_a,
                                             receiving_pubkey=pk_b,
                                             threshold=threshold,
                                             N=nodes_num)
                end = time.time()*1000
                kfr_tot = end-now
                show_latency('Keyfrags generated in (ms)= ', kfr_tot)

                # DISTRIBUTION
                now = time.time()*1000
                k_id = int(time.time()*1000)
                payload = {
                    'capsule': binascii.hexlify(capsule.to_bytes()).decode(),
                    'delegating': binascii.hexlify(pk_a.to_bytes()).decode(),
                    'receiving': binascii.hexlify(pk_b.to_bytes()).decode(),
                    'verifying': binascii.hexlify(verify_a.to_bytes()).decode()
                }
                ree_tot = distribute_key_fragments(
                    k_id, kfrags, payload, threshold)
                end = time.time()*1000
                dis_tot = end-now
                show_latency(
                    'Keyfrags distributed (includes re-encryption (ms)= {}) in (ms)= '.format(ree_tot), dis_tot)

                # Bob #######################################################
                # CAPSULE FRAGMENTS GATHERING
                now = time.time()*1000
                capsule.set_correctness_keys(delegating=pk_a,
                                             receiving=pk_b,
                                             verifying=verify_a)
                cfrags = gather_capsule_fragments(k_id, capsule, threshold)
                end = time.time()*1000
                cfr_tot = end-now
                show_latency('Cfrags gathered in (ms)= ', cfr_tot)

                # DECRYPT
                now = time.time()*1000
                plaintext_b = decrypt(
                    cfrags, capsule, ciphertext, sk_b, threshold)
                end = time.time()*1000
                dec_tot = end-now
                show_latency('Decrypted in (ms)= ', dec_tot)

                # FINISH
                assert(plaintext_b == plaintext)
                show_debug(plaintext_b)
                total = enc_tot + kfr_tot + dis_tot + cfr_tot + dec_tot
                tot += total
                enc += enc_tot
                kfr += kfr_tot
                ree += ree_tot
                dis += dis_tot
                cfr += cfr_tot
                dec += dec_tot
            writer.append(
                {
                    case: int(x),
                    "encryption": int(enc / max_rang),
                    "kfrags_gen": int(kfr / max_rang),
                    "kfrags_reenc": int(ree / max_rang),
                    "kfrags_dist": int(dis / max_rang),
                    "cfrags_gen": int(cfr / max_rang),
                    "decryption": int(dec / max_rang),
                    "total": int(tot / max_rang)
                }
            )
            print('{}) Total time (ms)= {}'.format(x, tot / max_rang))
        json.dump(writer, file)


if __name__ == '__main__':
    main()
