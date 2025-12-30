from core.hkdf import HKDF

class Party:
    def __init__(self, name: str, dh):
        self.name = name
        self.dh = dh
        # Use DHKE's private key generation to ensure consistency
        self.secret = dh.generate_private_key()
        self.public = dh.generate_public_key(self.secret)
        self.session_key = None
        self.hkdf = HKDF()

    def compute_shared_key(self, other_public: int) -> bytes:
        if not self.dh.validate_public_key(other_public):
            raise ValueError(f"{self.name}: Invalid public key")

        # Use DHKE's shared-secret computation
        shared = self.dh.compute_shared_secret(self.secret, other_public)
        shared_bytes = shared.to_bytes((shared.bit_length() + 7) // 8, "big")

        self.session_key = self.hkdf.derive(shared_bytes, length=32)
        return self.session_key
