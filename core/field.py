import random


class FiniteField:
    """A finite field GF(p^n) with support for prime fields and binary extensions.
    
    For prime fields (n=1): Uses standard modular arithmetic modulo p.
    For binary extensions (p=2, n>1): Requires pyfinite library.
    """

    def __init__(self, p, n):
        """Initialize a finite field GF(p^n).

        :param p: A prime number representing the base of the field.
        :param n: A positive integer representing the degree of the field extension.
        """
        self.p = p
        self.n = n
        self.size = p ** n

        # For binary extension fields, optionally initialize pyfinite.
        self.field = None
        if p == 2 and n > 1:
            try:
                from pyfinite import ffield
                self.field = ffield.FField(n=n)
            except ImportError:
                pass

    def exp(self, base: int, exponent: int) -> int:
        """Modular exponentiation: compute base^exponent mod p using binary exponentiation.

        This works for prime fields GF(p). For extension fields, use field-specific methods.

        :param base: The base element in the range [0, p).
        :param exponent: The non-negative integer exponent.
        :return: result = base^exponent mod p
        """
        result = 1
        base %= self.p

        # Binary exponentiation: process each bit of exponent
        while exponent > 0:
            if exponent & 1:
                result = (result * base) % self.p
            base = (base * base) % self.p
            exponent >>= 1

        return result

    def power(self, base, exponent):
        """Alias for exp() for backward compatibility.

        :param base: The base element.
        :param exponent: The exponent.
        :return: base^exponent mod p
        """
        return self.exp(base, exponent)

    def random_element(self) -> int:
        """Generate a random element in the finite field.

        For prime fields: returns random integer in [1, p-1].
        For binary extension fields with pyfinite: uses field.GetRandomElement().

        :return: A random element in GF(p^n).
        """
        if self.n == 1:
            # For prime fields GF(p) we need a private exponent `r` such that
            # the public value g^r lies in the subgroup of order q = (p-1)//2.
            # A simple construction is to return an even exponent r = 2*k
            # where 1 <= k < q. Then (g^r)^q == 1 mod p.
            q = (self.p - 1) // 2
            k = random.randint(1, q - 1)
            return 2 * k

        if self.field is not None:
            return self.field.GetRandomElement()

        # General fallback for other fields
        return random.randint(1, self.p - 1)

    def is_valid_element(self, a) -> bool:
        """Check if an element is valid in the finite field.

        For prime fields GF(p): valid elements are integers in (0, p).
        For extension fields: valid elements are in [0, p^n).

        :param a: Element to check.
        :return: True if a is a valid element in GF(p^n), False otherwise.
        """
        if not isinstance(a, int):
            try:
                a = int(a)
            except (TypeError, ValueError):
                return False

        # Valid elements are non-zero and less than field size p^n
        # (or 0 if we include the additive identity)
        return 0 < a < self.size

    def get_generator(self) -> int:
        """Deterministically compute a generator (primitive root) for the multiplicative group.

        For prime fields GF(p) (n=1): Factors p-1 and tests candidates g such that
        g^((p-1)/q) ≠ 1 (mod p) for every prime factor q of p-1.

        For binary fields GF(2^n) (p=2): Returns 2 (the polynomial x).

        For other GF(p^n): Raises NotImplementedError.

        :return: A generator element.
        :raises ValueError: If no generator found for the given field.
        :raises NotImplementedError: For unsupported field types.
        """
        # Prime fields: compute primitive root modulo p
        if self.n == 1:
            if self.p < 3:
                raise ValueError("No generator for p < 3")

            phi = self.p - 1

            # Factor phi = p - 1 to get distinct prime factors
            factors = set()
            m = phi
            d = 2
            while d * d <= m:
                if m % d == 0:
                    factors.add(d)
                    while m % d == 0:
                        m //= d
                d += 1 if d == 2 else 2
            if m > 1:
                factors.add(m)

            # Test candidates 2, 3, 4, ... for primitivity
            for g in range(2, self.p):
                if all(pow(g, phi // q, self.p) != 1 for q in factors):
                    return g
            raise ValueError("No generator found for prime field")

        # Binary extension fields: conventional generator is x (represented as 2)
        if self.p == 2:
            return 2

        # Other extension fields not yet supported
        raise NotImplementedError(
            f"get_generator not implemented for GF({self.p}^{self.n}); "
            "only GF(p) (n=1) and GF(2^n) are supported."
        )