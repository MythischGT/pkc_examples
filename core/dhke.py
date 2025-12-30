from core.field import FiniteField
import random


class DHKE:
    """Diffie-Hellman Key Exchange in the prime field GF(467).
    
    All instances share the same domain parameters (p, q, g) for interoperability.
    """

    # Class-level domain parameters (shared across all instances)
    p = 467
    q = (p - 1) // 2
    _generator_cache = None  # Cache computed generator

    def __init__(self):
        """Initialize DHKE with shared domain parameters p=467, q=(p-1)/2, g (computed once)."""
        # Use class attributes for p and q
        self.p = DHKE.p
        self.q = DHKE.q
        self.field = FiniteField(self.p, 1)
        
        # Compute generator once and cache it at class level
        if DHKE._generator_cache is None:
            DHKE._generator_cache = self.field.get_generator()
        self.g = DHKE._generator_cache

    def generate_private_key(self) -> int:
        """Generate a private exponent such that g^exponent lies in subgroup of order q.

        For a safe-prime p with q = (p-1)/2 and primitive root g, the subgroup
        of order q consists of even exponents of g (i.e. g^{2k}). Return an
        even exponent in the range [2, p-2].
        """
        # choose k in [1, q-1] and return exponent = 2*k
        return 2 * random.randint(1, self.q - 1)

    def generate_public_key(self, secret: int) -> int:
        """Compute public key from private key: public_key = g^secret mod p.

        :param secret: Private key (random exponent).
        :return: Public key to share with peer.
        """
        return self.field.power(self.g, secret)

    def compute_shared_secret(self, private_key: int, peer_public_key: int) -> int:
        """Compute shared secret: shared_secret = peer_public_key^private_key mod p.

        Both parties independently derive the same shared secret.

        :param private_key: Own private key.
        :param peer_public_key: Peer's public key.
        :return: Shared secret integer.
        """
        return self.field.power(peer_public_key, private_key)

    def validate_public_key(self, y: int) -> bool:
        """Validate a received public key is in the correct subgroup.

        Checks: 
        - y is a valid element in (0, p)
        - y^q = 1 mod p (where q = (p-1)/2), ensuring y is in the subgroup of order q

        :param y: Public key to validate.
        :return: True if valid, False otherwise.
        """
        # Check y is in valid range (0, p)
        if not isinstance(y, int) or y <= 0 or y >= self.p:
            return False

        # For safe prime p where q = (p-1)/2 is prime, check y^q ≡ 1 (mod p)
        # This ensures y is in the subgroup of prime order q
        if self.q is not None:
            return self.field.power(y, self.q) == 1

        return True

    # Backward compatibility aliases
    def generate_public(self, secret: int) -> int:
        """Deprecated: use generate_public_key() instead."""
        return self.generate_public_key(secret)

    def validate_public(self, y: int) -> bool:
        """Deprecated: use validate_public_key() instead."""
        return self.validate_public_key(y)