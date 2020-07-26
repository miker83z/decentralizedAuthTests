
import sys
import getopt
import time
import binascii
import json
import requests
from umbral import keys
from umbral.curve import SECP256K1
from umbral.params import UmbralParameters

client_service = 'http://localhost:2222/api/'

nodes = open('nodes.txt').read().splitlines()
nodes_num = len(nodes)
messages_sizes = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000,
                  1000000, 5000000, 10000000]
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
        '-m --message\n-x --fixed\n-f --latency\n-d --debug \n-t --threshold <value>\n-s --step <value>\n-f --final <value>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print(
            '-m --message\n-x --fixed\n-f --latency\n-d --debug \n-t --threshold <value>\n-s --step <value>\n-f --final <value>')
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


def post_json(url, json):
    try:
        with requests.post(url, json=json) as response:
            assert response.status_code == 201
            return response.json()
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

    # Generate encryption keys for Bob
    sk_b = keys.UmbralPrivateKey.gen_key(params)
    pk_b = sk_b.get_pubkey()

    return(pk_a, sk_a, sign_a, verify_a, pk_b, sk_b)


def main():
    print('hello')
    # SETUP
    (pk_a, sk_a, sign_a, verify_a, pk_b, sk_b) = setup()

    case = 'threshold' if threshold_flag else 'message_size'
    filename = '../test/datasets/{}/results{}.json'.format(
        case, int(time.time()*1000))
    with open(filename, 'w', newline='') as file:
        writer = []
        sizes_range = messages_sizes if fixed_messages_sizes else range(
            step_it, max_it, step_it)
        max_rang = 10

        for x in sizes_range:
            time.sleep(.5)
            enc = kfr = ree = dis = cfr = dec = tot = 0
            for _ in range(0, 10):
                time.sleep(.3)
                if threshold_flag:
                    threshold = x
                    plaintext = ''.join('x' for _ in range(30))
                else:
                    threshold = threshold_init
                    plaintext = ''.join('x' for _ in range(x))
                # Alice #####################################################
                # ENCRYPTION
                show_debug('Encrypting...')
                pay_tmp = {
                    'pk': binascii.hexlify(pk_a.to_bytes()).decode(),
                    'plain': plaintext
                }
                now = time.time()*1000
                encr_res = post_json(client_service+'encrypt/', pay_tmp)
                end = time.time()*1000
                enc_tot = end-now
                capsule = encr_res['capsule']
                ciphertext = encr_res['ciphert']
                show_latency('Encrypted in (ms)= ', enc_tot)

                # KEY FRAGMENTS GENERATION AND DISTRIBUTION
                k_id = int(time.time()*1000)
                pay_tmp = {
                    't': threshold,
                    'delegating_secret': binascii.hexlify(sk_a.to_bytes()).decode(),
                    'receiving': binascii.hexlify(pk_b.to_bytes()).decode(),
                    'signer_secret': binascii.hexlify(sign_a.to_bytes()).decode(),
                    'pk': binascii.hexlify(pk_a.to_bytes()).decode(),
                    'capsule': capsule,
                    'id': k_id
                }
                now = time.time()*1000
                kfrags_res = post_json(client_service+'keyfrags/', pay_tmp)
                end = time.time()*1000
                kfr_tot = end-now
                gen_tot = kfrags_res['gen_time']  # TODO
                dis_tot = kfr_tot - gen_tot
                ree_tot = kfrags_res['ree_time']
                show_latency(
                    'Keyfrags generated and distributed in (ms)= ', kfr_tot)
                show_latency(
                    'Keyfrags distributed (includes re-encryption (ms)= {}) in (ms)= '.format(ree_tot), dis_tot)

                # Bob #######################################################
                # CAPSULE FRAGMENTS GATHERING AND DECRYPT
                pay_tmp = {
                    't': threshold,
                    'verifying': binascii.hexlify(verify_a.to_bytes()).decode(),
                    'receiving': binascii.hexlify(pk_b.to_bytes()).decode(),
                    'receiving_secret': binascii.hexlify(sk_b.to_bytes()).decode(),
                    'sender': binascii.hexlify(pk_a.to_bytes()).decode(),
                    'capsule': capsule,
                    'id': k_id,
                    'ciphert': ciphertext
                }
                now = time.time()*1000
                decr_res = post_json(client_service+'decrypt/', pay_tmp)
                end = time.time()*1000
                dec_tot = end-now
                cfr_tot = decr_res['cfr_time']
                dec_par = decr_res['dec_time']  # TODO
                show_latency('Decrypted in (ms)= ', dec_tot)
                show_latency('Cfrags gathered in (ms)= ', cfr_tot)

                # FINISH
                assert(decr_res['plain'] == plaintext)
                show_debug(decr_res['plain'])
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
