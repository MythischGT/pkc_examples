class Field:
    """A simple prime-field helper for modular arithmetic.

    This class provides a small, self-contained implementation of modular
    exponentiation (binary exponentiation) and a basic element validity check
    for a multiplicative group modulo 'p'.
    """

    def __init__(self, p: int):
        """Create a field helper for modulus 'p'.

        :param p: The modulus (should typically be prime for multiplicative
                  group properties to hold).
        """
        self.p = p

    def exp(self, base: int, exponent: int) -> int:
        """Compute (base ** exponent) % p using binary exponentiation.

        This method uses the standard fast exponentiation algorithm (also
        called exponentiation by squaring). It reduces the base modulo 'p'
        up-front and then iterates over the bits of 'exponent', squaring the
        base each step and multiplying it into the result when the current
        exponent bit is 1. All multiplications are performed modulo 'p' to
        keep intermediate values small.

        :param base: The base integer.
        :param exponent: The non-negative integer exponent.
        :return: (base ** exponent) % p
        """
        result = 1

        # Reduce the base modulo p immediately to keep values small.
        base %= self.p

        # Process each binary digit of exponent from least significant to
        # most significant. If the current bit is 1, multiply it into result.
        while exponent > 0:
            if exponent & 1:
                result = (result * base) % self.p

            # Square the base for the next bit and reduce modulo p.
            base = (base * base) % self.p

            # Shift exponent right by one bit.
            exponent >>= 1

        return result

    def is_valid_element(self, x: int) -> bool:
        """Return True when 'x' is a likely valid non-trivial multiplicative
        group element modulo 'p'.

        This simple check enforces that 'x' is not 0, 1, or p-1 which are
        typically excluded for some protocols that expect a generator-like
        element. It is not a full primality or generator test.
        """
        return 1 < x < self.p - 1
