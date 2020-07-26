import time
import binascii
from app import app
from flask import request, abort, jsonify
from umbral import pre
from umbral.kfrags import KFrag
from umbral.keys import UmbralPublicKey
from umbral.curve import SECP256K1
from umbral.params import UmbralParameters

show_debug_flag = False

keyfrags = {}
params = UmbralParameters(SECP256K1)


@app.route('/api/keyfrags/', methods=['GET'])
def get_keyfrag():
    if not keyfrags:
        abort(400)
    show_debug('Returning all the key fragments objects stored...')
    payloads = {}
    for kfrag in keyfrags.keys():
        payloads[kfrag] = {
            'capsule': binascii.hexlify(keyfrags[kfrag]['capsule'].to_bytes()).decode(),
            'keyfrag': binascii.hexlify(keyfrags[kfrag]['keyfrag'].to_bytes()).decode(),
            'delegating': binascii.hexlify(keyfrags[kfrag]['delegating'].to_bytes()).decode(),
            'receiving': binascii.hexlify(keyfrags[kfrag]['receiving'].to_bytes()).decode(),
            'verifying': binascii.hexlify(keyfrags[kfrag]['verifying'].to_bytes()).decode()
        }
    return jsonify(payloads), 201


@app.route('/api/keyfrags/', methods=['POST'])
def create_keyfrag():
    if not request.json or not 'id' in request.json or request.json['id'] in keyfrags.keys():
        abort(400)
    k_id = request.json['id']
    show_debug("Storing key fragment with id: " + str(k_id))
    keyfrags[k_id] = {
        'capsule': pre.Capsule.from_bytes(binascii.unhexlify(request.json['capsule'].encode()), params),
        'keyfrag': KFrag.from_bytes(binascii.unhexlify(request.json['keyfrag'].encode()), SECP256K1),
        'delegating': UmbralPublicKey.from_bytes(binascii.unhexlify(request.json['delegating'].encode()), params),
        'receiving': UmbralPublicKey.from_bytes(binascii.unhexlify(request.json['receiving'].encode()), params),
        'verifying': UmbralPublicKey.from_bytes(binascii.unhexlify(request.json['verifying'].encode()), params),
        'rekeyfrag': None
    }
    show_debug('-- Delegating:' + request.json['delegating'])
    show_debug('-- Receiving:' + request.json['receiving'])
    now = time.time()*1000
    keyfrags[k_id]['capsule'].set_correctness_keys(delegating=keyfrags[k_id]['delegating'],
                                                   receiving=keyfrags[k_id]['receiving'],
                                                   verifying=keyfrags[k_id]['verifying'])
    keyfrags[k_id]['rekeyfrag'] = pre.reencrypt(kfrag=keyfrags[k_id]['keyfrag'],
                                                capsule=keyfrags[k_id]['capsule'])
    end = time.time()*1000
    enc_tot = end-now
    show_debug("-- Re-encrypted key fragment with id: " + str(k_id))
    return jsonify({'time': enc_tot}), 201


@app.route('/api/keyfrags/<int:kfrag_id>', methods=['GET'])
def get_task(kfrag_id):
    if not kfrag_id in keyfrags.keys():
        abort(400)
    show_debug('Returning re-key fragment with id: ' + str(kfrag_id))
    payload = binascii.hexlify(
        keyfrags[kfrag_id]['rekeyfrag'].to_bytes()).decode()
    return jsonify({'rekeyfrag': payload})


def show_debug(message):
    if show_debug_flag:
        print(message)
