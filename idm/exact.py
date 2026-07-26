"""idm.exact — exact, finite arithmetic: number theory, exact-ℚ linear algebra, polynomials.

Everything here is exact and finite: integers and `Fraction`, finite loops, no floating point in the
result (√ excepted, an algebraic finite operation). These are the discrete, decidable readouts — the
`Th_coqc`-eligible layer of the solver.
"""
from fractions import Fraction as Q
from math import gcd, isqrt

# ---------------------------------------------------------------- number theory ----
def lcm(a, b): return abs(a * b) // gcd(a, b) if a and b else 0
def factorial(n):
    p = 1
    for k in range(2, n + 1): p *= k
    return p
def binomial(n, k):
    if k < 0 or k > n: return 0
    k = min(k, n - k); num = 1; den = 1
    for i in range(k): num *= (n - i); den *= (i + 1)
    return num // den
def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d = n - 1; r = 0
    while d % 2 == 0: d //= 2; r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):   # deterministic for n < 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
def factorize(n):
    """prime factorization as {prime: exponent} (trial division + Pollard for larger)."""
    n = abs(n); f = {}
    for p in range(2, 1000):
        while n % p == 0: f[p] = f.get(p, 0) + 1; n //= p
    while n > 1:
        if is_prime(n): f[n] = f.get(n, 0) + 1; break
        d = _pollard(n);
        while n % d == 0: f[d] = f.get(d, 0) + 1; n //= d
    return f
def _pollard(n):
    if n % 2 == 0: return 2
    x = 2; y = 2; d = 1; c = 1
    f = lambda v: (v * v + c) % n
    while d == 1:
        x = f(x); y = f(f(y)); d = gcd(abs(x - y), n)
    return d if d != n else _pollard(n)  # pragma: no cover
def divisors(n):
    n = abs(n); ds = [1]
    for p, e in factorize(n).items():
        ds = [d * p ** i for d in ds for i in range(e + 1)]
    return sorted(set(ds))
def totient(n):
    r = n
    for p in factorize(n): r -= r // p
    return r
def primes_up_to(N):
    sieve = bytearray([1]) * (N + 1); sieve[0:2] = b"\x00\x00"
    for i in range(2, isqrt(N) + 1):
        if sieve[i]: sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(N + 1) if sieve[i]]
def mod_inverse(a, m):
    g, x, _ = _egcd(a % m, m)
    if g != 1: raise ValueError("no modular inverse (gcd≠1)")
    return x % m
def _egcd(a, b):
    if b == 0: return a, 1, 0
    g, x, y = _egcd(b, a % b); return g, y, x - (a // b) * y
def crt(residues, moduli):
    from functools import reduce
    M = reduce(lambda x, y: x * y, moduli); x = 0
    for a, m in zip(residues, moduli):
        Mi = M // m; x += a * Mi * mod_inverse(Mi, m)
    return x % M
def fibonacci(n):
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * (2 * b - a); d = a * a + b * b
        a, b = (d, c + d) if bit == "1" else (c, d)
    return a
def bernoulli(n):
    """B_n exact ℚ via the finite recurrence Σ_{k=0}^{m} C(m+1,k) B_k = 0 (B_1 = −1/2)."""
    B = [Q(1)]
    for m in range(1, n + 1):
        s = sum(binomial(m + 1, k) * B[k] for k in range(m))
        B.append(-Q(s, m + 1))
    return B[n]
def partition(n, _c={0: 1}):
    if n in _c: return _c[n]
    if n < 0: return 0
    total = 0; k = 1
    while True:
        g1 = k * (3 * k - 1) // 2; g2 = k * (3 * k + 1) // 2
        if g1 > n and g2 > n: break
        s = (-1) ** (k + 1)
        if g1 <= n: total += s * partition(n - g1)
        if g2 <= n: total += s * partition(n - g2)
        k += 1
    _c[n] = total; return total
def catalan(n): return binomial(2 * n, n) // (n + 1)
def stirling2(n, k):
    if k == 0: return 1 if n == 0 else 0
    return k * stirling2(n - 1, k) + stirling2(n - 1, k - 1) if n and k else 0
def bell(n): return sum(stirling2(n, k) for k in range(n + 1))
def continued_fraction(num, den=1, terms=20):
    """CF expansion [a0; a1, a2, …] of a rational num/den (or of an integer). Finite, exact."""
    a = []; p, q = int(num), int(den)
    for _ in range(terms):
        if q == 0: break
        a.append(p // q); p, q = q, p - (p // q) * q
    return a

# ---------------------------------------------------------------- exact-ℚ linear algebra ----
def _M(A): return [[Q(x) for x in row] for row in A]
def mat_mul(A, B):
    A, B = _M(A), _M(B); n, p, m = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(p)) for j in range(m)] for i in range(n)]
def determinant(A):
    """exact determinant over ℚ by fraction-free Gaussian elimination."""
    A = _M(A); n = len(A); det = Q(1)
    for i in range(n):
        piv = next((r for r in range(i, n) if A[r][i] != 0), None)
        if piv is None: return Q(0)
        if piv != i: A[i], A[piv] = A[piv], A[i]; det = -det
        det *= A[i][i]
        for r in range(i + 1, n):
            f = A[r][i] / A[i][i]
            A[r] = [A[r][c] - f * A[i][c] for c in range(n)]
    return det
def solve_linear(A, b):
    """solve Ax=b exactly over ℚ by Gauss–Jordan; returns the solution vector or None if singular."""
    A = _M(A); b = [Q(x) for x in b]; n = len(A)
    for i in range(n):
        piv = next((r for r in range(i, n) if A[r][i] != 0), None)
        if piv is None: return None
        if piv != i: A[i], A[piv] = A[piv], A[i]; b[i], b[piv] = b[piv], b[i]
        inv = A[i][i]; A[i] = [c / inv for c in A[i]]; b[i] /= inv
        for r in range(n):
            if r != i and A[r][i] != 0:
                f = A[r][i]; A[r] = [A[r][c] - f * A[i][c] for c in range(n)]; b[r] -= f * b[i]
    return b
def inverse(A):
    n = len(A); cols = []
    for j in range(n):
        e = [Q(1) if i == j else Q(0) for i in range(n)]
        col = solve_linear(A, e)
        if col is None: return None
        cols.append(col)
    return [[cols[j][i] for j in range(n)] for i in range(n)]

# ---------------------------------------------------------------- polynomials (coeffs low→high) ----
def poly_eval(coeffs, x):
    r = Q(0)
    for c in reversed(coeffs): r = r * x + Q(c)
    return r
def rational_roots(coeffs):
    """all RATIONAL roots (exact) by the rational-root theorem + division."""
    c = [Q(x) for x in coeffs]
    while len(c) > 1 and c[-1] == 0: c = c[:-1]
    while len(c) > 1 and c[0] == 0: c = c[1:]  # (drops x=0 roots; reported separately)
    if len(c) <= 1: return []
    from math import gcd as _g
    den = 1
    for x in c: den = den * x.denominator // _g(den, x.denominator)
    ci = [int(x * den) for x in c]
    a0, an = ci[0], ci[-1]
    def facs(m):
        m = abs(m); return [d for d in range(1, m + 1) if m % d == 0] or [1]
    cands = set()
    for p in facs(a0):
        for qd in facs(an):
            cands.add(Q(p, qd)); cands.add(Q(-p, qd))
    return sorted({r for r in cands if poly_eval(c, r) == 0})
