import os
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

def derive_shared_key(private_key, peer_public_key):
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secure-protocol"
    ).derive(shared_key)
    return derived_key

def encrypt_message(key, plaintext):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # GCM requires a 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce, ciphertext

def decrypt_message(key, nonce, ciphertext):
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()
