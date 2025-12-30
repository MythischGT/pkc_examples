import hashlib
import hmac

class HKDF:
    def __init__(self, hash_fn=hashlib.sha256):
        self.hash_fn = hash_fn
        self.hash_len = hash_fn().digest_size

    def extract(self, salt: bytes, ikm: bytes) -> bytes:
        if not salt:
            salt = b"\x00" * self.hash_len
        return hmac.new(salt, ikm, self.hash_fn).digest()

    def expand(self, prk: bytes, info: bytes, length: int) -> bytes:
        output = b""
        prev = b""
        counter = 1

        while len(output) < length:
            data = prev + info + bytes([counter])
            prev = hmac.new(prk, data, self.hash_fn).digest()
            output += prev
            counter += 1

        return output[:length]

    def derive(self, ikm: bytes, length: int, salt=b"", info=b"dh-session") -> bytes:
        prk = self.extract(salt, ikm)
        return self.expand(prk, info, length)
