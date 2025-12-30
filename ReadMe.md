# Introduction
I provide compact, readable implementations and examples of key-exchange building
blocks used for learning and experimentation. The repository focuses on a
finite-field Diffie-Hellman demonstration and supporting utilities; other
algorithms are listed as planned extensions.

Implemented components:
- A small `FiniteField` helper for GF(p) (prime fields) and optional support
    for binary extension fields (GF(2^n)) when `pyfinite` is available.
- A `DHKE` class implementing Diffie-Hellman over a shared prime domain with
    deterministic generator selection and subgroup validation.
- A `Party` helper that derives a session key via HKDF from the DH shared
    secret and exposes simple encrypt/decrypt examples.
- A set of participant scripts (in `participants/`) that demonstrate message
    exchange and simple XOR-based transport encryption for examples.

# Definitions
## Finite Fields

The repository uses a conservative, easy-to-follow `FiniteField` class:

- For prime fields (n == 1) the class uses modular integer arithmetic with
    a binary-exponentiation implementation (`exp(base, exponent)`).
- For binary extension fields (p == 2, n > 1) it will initialize `pyfinite`'s
    `FField` when available and fall back to prime-field behavior otherwise.
- `random_element()` has been chosen to produce private exponents suitable for
    subgroup membership when using safe primes (see DHKE notes below).

The implementation intentionally keeps the arithmetic explicit and readable so
it can be inspected and adapted for experiments.

## Diffie-Hellman Key Exchange

The `DHKE` class implements a textbook Diffie-Hellman key exchange with the
following design points:

- Uses a single shared domain: `p = 467`, `q = (p-1)//2` (a safe-prime-style
    setup). These domain parameters are class-level constants so every `DHKE`
    instance uses the exact same `p` and `q`.
- Generator `g` is computed deterministically and cached once per process. For
    prime fields the code factors `p-1` and searches for the smallest primitive
    root; for binary fields it returns a conventional constant (polynomial `x`).
- Private key generation is derived from the `FiniteField` helper. For the
    prime-field example the field returns an even exponent `r = 2*k`, ensuring the
    public value `g^r` lies in the subgroup of order `q` (so `(g^r)^q == 1 mod p`).
- Public keys are `g^secret mod p`. Validation checks the numeric range and
    enforces the subgroup test `y^q == 1 (mod p)` when `q` is defined.

## HKDF

The shared integer secret computed by DH (an integer) is converted to bytes
and fed into an HKDF instance to derive a symmetric session key. The HKDF
wrapper in `core/hkdf.py` follows the usual HKDF-Extract/Expand pattern and is
used by `Party` to produce a 32-byte session key.

## Party

`Party` is a convenience wrapper combining a `DHKE` instance and HKDF to:

- Generate a private exponent (via `DHKE` / `FiniteField`).
- Publish the corresponding public key.
- Compute and validate a peer's public key, then derive a session key via HKDF.

The project includes simple example encryption using an HKDF-derived key to
produce a stream-like keystream (SHA-256 based) used for XOR masking of
application payloads in the examples directory.

## Man-in-the-Middle

Participant scripts under `participants/` include examples of a basic
client/server exchange and a simple MITM script that demonstrates interception
and forwarding with separate shared keys on each leg. These are educational
examples and not intended for production use.

# DHKE Implementation Details
The `core/dhke.py` and `core/field.py` files contain the key implementation
details. Look-up points:

- `core/field.py`: `FiniteField.get_generator()`, `exp()`, and `random_element()`
    (private-exponent derivation for the prime-field example).
- `core/dhke.py`: `generate_private_key()`, `generate_public_key()`,
    `compute_shared_secret()`, `validate_public_key()` and class-level domain
    parameter caching.
- `core/party.py`: `Party` wrapper that uses `DHKE` + `HKDF` to create session
    keys and supply simple encryption helpers.

Script usage and terminal views: see the `participants/` launcher and
`main.py` (top-level) for example commands that spawn participant processes and
demonstrate the message flows.

Security note: this code is for learning and experimentation. It makes
assumptions (small prime sizes, simplified validation, XOR-based example
encryption) that are unsuitable for real-world cryptographic use. Use well-
reviewed libraries and standard parameter sizes for production security.
