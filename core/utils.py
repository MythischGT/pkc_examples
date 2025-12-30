import hashlib

def xor_encrypt(key: bytes, plaintext: bytes) -> bytes:
    keystream = hashlib.sha256(key).digest()
    return bytes(p ^ keystream[i % len(keystream)] for i, p in enumerate(plaintext))

def xor_decrypt(key: bytes, ciphertext: bytes) -> bytes:
    return xor_encrypt(key, ciphertext)
