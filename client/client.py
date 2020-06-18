import binascii
import json
import requests
import time
from umbral import pre, keys, signing, config
from umbral.curve import SECP256K1
from umbral.params import UmbralParameters
from base64 import b64encode, b64decode

nodes = open('nodes.txt').read().splitlines()
params = UmbralParameters(SECP256K1)
api_call = '/api/keyfrags'

plaintext = b'Proxy Re-Encryption is cool!'
nodes_num = len(nodes)
threshold = 2

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
global_id = int(time.time())
print('Distributing key fragment with id {} to nodes...'.format(str(global_id)))
payload = {
    'capsule': binascii.hexlify(capsule.to_bytes()).decode(),
    'delegating': binascii.hexlify(pk_a.to_bytes()).decode(),
    'receiving': binascii.hexlify(pk_b.to_bytes()).decode(),
    'verifying': binascii.hexlify(verify_a.to_bytes()).decode()
}

success = 0
for i, node in enumerate(nodes):
    print('-- Reaching node ' + node)
    pay_tmp = {
        'id': global_id,
        'capsule': payload['capsule'],
        'keyfrag': binascii.hexlify(kfrags[i].to_bytes()).decode(),
        'delegating': payload['delegating'],
        'receiving': payload['receiving'],
        'verifying': payload['verifying']
    }
    resp = requests.post(node+api_call, json=pay_tmp)
    if resp.status_code == 201:
        success += 1
        print('-- Key fragment sent')
    else:
        print('-- ' + resp.text)
if success >= threshold:
    print('Distributed {}/{} key fragments'.format(success, nodes_num))
else:
    raise ValueError(
        'ERROR: Distributed {}/{} key fragments and threshold is {}'.format(success, nodes_num, threshold))


# BOB'S OPERATIONS
print('Starting decryption operations')
cfrags = []
capsule.set_correctness_keys(delegating=pk_a,
                             receiving=pk_b,
                             verifying=verify_a)
node_i = 0
while len(cfrags) < threshold and node_i < nodes_num:
    print('-- Reaching node ' + nodes[node_i])
    resp = requests.get(nodes[node_i]+api_call+'/'+str(global_id))
    if resp.status_code == 200:
        cfrags.append(pre.CapsuleFrag.from_bytes(binascii.unhexlify(
            json.loads(resp.text)['rekeyfrag'].encode()), SECP256K1))
        print('-- Re-encrypted key fragment received')
    else:
        print('-- ' + resp.text)
    node_i += 1
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
