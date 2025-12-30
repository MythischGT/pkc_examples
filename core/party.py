import secrets
from core.hkdf import HKDF

class Party:
    def __init__(self, name: str, dh):
        self.name = name
        self.dh = dh
        self.secret = secrets.randbelow(dh.p - 2) + 1
        self.public = dh.generate_public(self.secret)
        self.session_key = None
        self.hkdf = HKDF()

    def compute_shared_key(self, other_public: int) -> bytes:
        if not self.dh.validate_public(other_public):
            raise ValueError(f"{self.name}: Invalid public key")

        shared = self.dh.field.exp(other_public, self.secret)
        shared_bytes = shared.to_bytes((shared.bit_length() + 7) // 8, "big")

        self.session_key = self.hkdf.derive(shared_bytes, length=32)
        return self.session_key
