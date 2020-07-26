
from app import app
from flask import request, abort, jsonify
import time
import binascii
import json
import asyncio
import aiohttp
from umbral import pre, signing
from umbral.curve import SECP256K1
from umbral.params import UmbralParameters
from umbral.keys import UmbralPublicKey, UmbralPrivateKey

show_debug_flag = False

api_call = '/api/keyfrags/'
port = "5022"
nodes = open('nodes.txt').read().splitlines()
nodes = ["http://" + node + ":" + port for node in nodes]
nodes_num = len(nodes)
params = UmbralParameters(SECP256K1)


@app.route('/api/encrypt/', methods=['POST'])
def encrypt_r():
    if not request.json or not 'pk' in request.json or not 'plain' in request.json:
        abort(400)
    pk_a = UmbralPublicKey.from_bytes(
        binascii.unhexlify(request.json['pk'].encode()), params)
    show_debug("Encrypting message")
    ciphertext, capsule = pre.encrypt(
        pk_a, request.json['plain'].encode())
    show_debug("Encrypted message")
    payload = {
        'ciphert': binascii.hexlify(ciphertext).decode(),
        'capsule': binascii.hexlify(capsule.to_bytes()).decode()
    }
    return jsonify(payload), 201


@app.route('/api/keyfrags/', methods=['POST'])
def create_keyfrag():
    if (not request.json or
        not 't' in request.json or not 'delegating_secret' in request.json or
            not 'receiving' in request.json or not 'signer_secret' in request.json):
        abort(400)
    threshold = request.json['t']

    show_debug(request.json['delegating_secret'])

    sk_a = UmbralPrivateKey.from_bytes(binascii.unhexlify(
        request.json['delegating_secret'].encode()), params=params)
    pk_b = UmbralPublicKey.from_bytes(binascii.unhexlify(
        request.json['receiving'].encode()), params)
    sign_a = UmbralPrivateKey.from_bytes(binascii.unhexlify(
        request.json['signer_secret'].encode()), params=params)
    signer_a = signing.Signer(private_key=sign_a)

    show_debug("Generating kfrags")
    now = time.time()*1000
    kfrags = pre.generate_kfrags(delegating_privkey=sk_a,
                                 signer=signer_a,
                                 receiving_pubkey=pk_b,
                                 threshold=threshold,
                                 N=nodes_num)
    end = time.time()*1000
    gen_tot = end-now
    show_debug("Generated key fragment in: " + str(gen_tot))

    show_debug("Distributing kfrags")
    k_id = request.json['id']
    payload = {
        'capsule': request.json['capsule'],
        'delegating': request.json['pk'],
        'receiving': request.json['receiving'],
        'verifying': binascii.hexlify(sign_a.get_pubkey().to_bytes()).decode()
    }
    ree_tot = distribute_key_fragments(k_id, kfrags, payload, threshold)
    show_debug("Distributed key fragments")

    return jsonify({'gen_time': gen_tot, 'ree_time': ree_tot}), 201


@app.route('/api/decrypt/', methods=['POST'])
def decrypt_r():
    if (not request.json or
        not 't' in request.json or not 'verifying' in request.json or
            not 'receiving' in request.json or not 'receiving_secret' in request.json):
        abort(400)
    threshold = request.json['t']
    verify_a = UmbralPublicKey.from_bytes(binascii.unhexlify(
        request.json['verifying'].encode()), params)
    pk_b = UmbralPublicKey.from_bytes(binascii.unhexlify(
        request.json['receiving'].encode()), params)
    sk_b = UmbralPrivateKey.from_bytes(binascii.unhexlify(
        request.json['receiving_secret'].encode()), params=params)
    pk_a = UmbralPublicKey.from_bytes(binascii.unhexlify(
        request.json['sender'].encode()), params)
    capsule = pre.Capsule.from_bytes(binascii.unhexlify(
        request.json['capsule'].encode()), params)
    k_id = request.json['id']
    ciphertext = binascii.unhexlify(request.json['ciphert'].encode())

    show_debug("Gathering cfrags")
    now = time.time()*1000
    capsule.set_correctness_keys(delegating=pk_a,
                                 receiving=pk_b,
                                 verifying=verify_a)
    cfrags = gather_capsule_fragments(k_id, threshold)
    end = time.time()*1000
    cfr_tot = end-now
    show_debug("Gathered capsule fragments in: " + str(cfr_tot))

    show_debug("Decrypting")
    now = time.time()*1000
    plaintext_b = decrypt(
        cfrags, capsule, ciphertext, sk_b, threshold)
    end = time.time()*1000
    dec_tot = end-now
    show_debug('Decrypted in (ms)= ' + str(dec_tot))

    return jsonify({'plain': plaintext_b.decode(), 'cfr_time': cfr_tot, 'dec_time': dec_tot}), 201


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


def gather_capsule_fragments(k_id, threshold):
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
