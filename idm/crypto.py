"""idm.crypto — cryptographic number theory as exact, certificate-bearing computation.

This is the "domain pack" where every answer is exact and, where possible, CERTIFIED: a primality
result carries a checkable witness — a Miller–Rabin base that PROVES compositeness (valid for any n),
or, for a positive verdict, the deterministic base set that proves primality *only* below the proven
bound; RSA/ECC arithmetic is exact modular arithmetic, and a discrete log is an exact meet-in-the-middle
search. Nothing here rounds; nothing here trusts a float. All integers, all decidable — and above the
deterministic bound the primality verdict is honestly downgraded to a probable prime, never certified.
"""
from math import gcd, isqrt

# The first 13 primes are a deterministic Miller–Rabin witness set for every n strictly below this exact
# bound (the smallest strong pseudoprime to all of them). Base 41 is essential: dropping it lets the
# composite 318665857834031151167461 (= 399165290221·798330580441) pass bases {2..37} while still lying
# below the 13-prime bound — a false "prime". Above MR_DET_BOUND, passing every base proves nothing.
MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
MR_DET_BOUND = 3317044064679887385961981


def _mr_passes(a, n):
    """True if n passes the Miller–Rabin test for base a (a is NOT a witness of compositeness)."""
    if a % n == 0: return True
    d = n - 1; r = 0
    while d % 2 == 0: d //= 2; r += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1: return True
    for _ in range(r - 1):
        x = x * x % n
        if x == n - 1: return True
    return False

def is_prime(n):
    """Primality with a checkable, tier-honest certificate:
      • a small prime factor or a Miller–Rabin witness PROVES compositeness (certified, any n);
      • passing every base with n < MR_DET_BOUND PROVES primality (certified deterministic);
      • passing every base with n ≥ MR_DET_BOUND is only a strong probable prime — NOT certified."""
    n = int(n)
    if n < 2: return {"prime": False, "n": n, "certified": True,
                      "certificate": {"type": "definition", "reason": "n < 2 is not prime"}}
    for p in MR_BASES:
        if n % p == 0:
            if n == p: return {"prime": True, "n": n, "certified": True,
                               "certificate": {"type": "small prime", "value": p}}
            return {"prime": False, "n": n, "certified": True,
                    "certificate": {"type": "composite: trial factor", "factor": p}}
    for a in MR_BASES:
        if not _mr_passes(a, n):                       # a witness — a PROOF of compositeness for any n
            return {"prime": False, "n": n, "certified": True,
                    "certificate": {"type": "composite: Miller–Rabin witness", "witness_base": a}}
    if n < MR_DET_BOUND:
        return {"prime": True, "n": n, "certified": True,
                "certificate": {"type": "deterministic Miller–Rabin", "bases": list(MR_BASES),
                                "valid_below": str(MR_DET_BOUND)}}
    return {"prime": True, "n": n, "certified": False,     # beyond the proven bound — honestly downgraded
            "certificate": None,
            "note": f"strong probable prime to the first 13 primes, but n ≥ {MR_DET_BOUND} (the deterministic "
                    "Miller–Rabin bound) — primality is NOT proven here, only probable"}

def next_prime(n):
    """smallest prime > n (deterministic test)."""
    n = int(n) + 1
    if n <= 2: return {"next_prime": 2}
    if n % 2 == 0: n += 1
    while not is_prime(n)["prime"]: n += 2
    return {"next_prime": n}


# ---------------- RSA (exact modular arithmetic) ----------------
def _egcd(a, b):
    if b == 0: return (a, 1, 0)
    g, x, y = _egcd(b, a % b); return (g, y, x - (a // b) * y)

def modinv(a, m):
    """modular inverse a⁻¹ mod m by the extended Euclidean algorithm, or HOLD if gcd(a,m)≠1."""
    g, x, _ = _egcd(a % m, m)
    if g != 1: return {"status": "HOLD", "reason": f"no inverse: gcd({a},{m})={g}≠1"}
    return {"inverse": x % m}

def rsa_keygen(p, q, e=65537):
    """build an RSA keypair from two primes: exact n, φ(n), and d=e⁻¹ mod φ."""
    p, q = int(p), int(q)
    if not (is_prime(p)["prime"] and is_prime(q)["prime"]):
        return {"status": "HOLD", "reason": "p and q must both be prime"}
    n = p * q; phi = (p - 1) * (q - 1)
    inv = modinv(e, phi)
    if "status" in inv: return {"status": "HOLD", "reason": f"e={e} not coprime to φ(n)"}
    return {"public": {"n": n, "e": e}, "private": {"n": n, "d": inv["inverse"]}, "phi": phi}

def rsa_encrypt(m, e, n): return {"cipher": pow(int(m), int(e), int(n))}
def rsa_decrypt(c, d, n): return {"message": pow(int(c), int(d), int(n))}


# ---------------- discrete log (exact BSGS) ----------------
def discrete_log(g, h, p):
    """solve g^x ≡ h (mod p) by exact baby-step/giant-step, or HOLD if no solution exists."""
    g, h, p = int(g), int(h), int(p)
    m = isqrt(p - 1) + 1
    table = {}; e = 1
    for j in range(m): table[e] = j; e = e * g % p
    factor = pow(g, (p - 2) * m % (p - 1) if False else -m % (p - 1), p) if False else pow(pow(g, m, p), p - 2, p)
    gm = pow(g, m, p); ginv = pow(gm, p - 2, p)  # (g^m)^{-1} mod p (p prime)
    y = h
    for i in range(m):
        if y in table: return {"x": i * m + table[y], "verify": pow(g, i * m + table[y], p) == h % p}
        y = y * ginv % p
    return {"status": "HOLD", "reason": "no discrete logarithm found in range"}


# ---------------- elliptic curve over F_p (exact point ops) ----------------
def ec_add(P, Q, a, p):
    """exact point addition on y²=x³+ax+b over F_p. Points as [x,y] or 'O' for infinity."""
    a, p = int(a), int(p)
    if P == "O": return Q
    if Q == "O": return P
    x1, y1 = int(P[0]) % p, int(P[1]) % p; x2, y2 = int(Q[0]) % p, int(Q[1]) % p
    if x1 == x2 and (y1 + y2) % p == 0: return "O"
    if x1 == x2 and y1 == y2:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p; y3 = (lam * (x1 - x3) - y1) % p
    return [x3, y3]

def ec_mul(k, P, a, p):
    """exact scalar multiplication k·P on an elliptic curve over F_p by double-and-add."""
    k = int(k); R = "O"; Qp = P
    while k > 0:
        if k & 1: R = ec_add(R, Qp, a, p)
        Qp = ec_add(Qp, Qp, a, p); k >>= 1
    return {"point": R}
