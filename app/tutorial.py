from umbral import pre, keys, signing

# Generate Umbral keys for Alice.
sk_a = keys.UmbralPrivateKey.gen_key()
pk_a = sk_a.get_pubkey()

sign_a = keys.UmbralPrivateKey.gen_key()
verify_a = sign_a.get_pubkey()
signer_a = signing.Signer(private_key=sign_a)

# Generate Umbral keys for Bob.
sk_b = keys.UmbralPrivateKey.gen_key()
pk_b = sk_b.get_pubkey()

# Encrypt data with Alice's public key.
plaintext = b'Proxy Re-Encryption is cool!'
ciphertext, capsule = pre.encrypt(pk_a, plaintext)

# Decrypt data with Alice's private key.
cleartext = pre.decrypt(ciphertext=ciphertext,
                        capsule=capsule,
                        decrypting_key=sk_a)

# Alice generates "M of N" re-encryption key fragments (or "KFrags") for Bob.
# In this example, 10 out of 20.
kfrags = pre.generate_kfrags(delegating_privkey=sk_a,
                             signer=signer_a,
                             receiving_pubkey=pk_b,
                             threshold=10,
                             N=20)

# Send frags to the network

# Bob
# Several Ursulas perform re-encryption, and Bob collects the resulting `cfrags`.
# He must gather at least `threshold` `cfrags` in order to activate the capsule.
capsule.set_correctness_keys(delegating=pk_a,
                             receiving=pk_b,
                             verifying=verify_a)

cfrags = list()           # Bob's cfrag collection
for kfrag in kfrags[:10]:
    cfrag = pre.reencrypt(kfrag=kfrag, capsule=capsule)
    cfrags.append(cfrag)    # Bob collects a cfrag

# Bob activates and opens the capsule
for cfrag in cfrags:
    capsule.attach_cfrag(cfrag)

cleartext_b = pre.decrypt(ciphertext=ciphertext,
                          capsule=capsule,
                          decrypting_key=sk_b)
assert cleartext_b == plaintext
