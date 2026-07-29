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
# Deterministic Miller–Rabin: the FIRST 13 PRIMES are witnesses for every n strictly below this exact
# bound. MR_DET_BOUND = 3,317,044,064,679,887,385,961,981 is the smallest strong pseudoprime to all of
# them (Jaeschke / Sorenson–Webster), so the test is a PROOF of primality only for n < MR_DET_BOUND.
# NOTE: base 41 is required — without it the smallest counterexample is 318665857834031151167461
# (≈3.19e23, composite = 399165290221·798330580441) which passes bases {2..37} yet sits below the
# 13-prime bound, producing a FALSE "prime" verdict. Above MR_DET_BOUND the same routine is only a
# strong-probable-prime check, never a proof — callers must tier accordingly (see solve.py).
MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
MR_DET_BOUND = 3317044064679887385961981

def is_prime(n):
    n = int(n)
    if n < 2: return False
    for p in MR_BASES:
        if n % p == 0: return n == p
    d = n - 1; r = 0
    while d % 2 == 0: d //= 2; r += 1
    for a in MR_BASES:
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
    """all RATIONAL roots (exact) by the rational-root theorem + division. Coefficients are given
    low-order first (c[0] + c[1]·x + …). x=0 is included whenever the constant term is 0."""
    c = [Q(x) for x in coeffs]
    while len(c) > 1 and c[-1] == 0: c = c[:-1]           # drop leading (high-order) zeros
    roots = set()
    if len(c) > 1 and c[0] == 0:                          # a zero constant term ⇒ x=0 IS a root
        roots.add(Q(0))
        while len(c) > 1 and c[0] == 0: c = c[1:]         # factor out x^k, keep solving the rest
    if len(c) <= 1: return sorted(roots)
    from math import gcd as _g
    den = 1
    for x in c: den = den * x.denominator // _g(den, x.denominator)
    ci = [int(x * den) for x in c]
    a0, an = ci[0], ci[-1]
    def facs(m):
        # every divisor of |m|, found in O(√m) (was O(m) trial division — it hung rational_roots on the
        # large constant/leading coefficients of a big matrix's characteristic polynomial). Order is
        # irrelevant here (the divisors feed a set of candidate roots), so no downstream output changes.
        m = abs(m)
        if m == 0:
            return [1]
        ds = []
        i = 1
        while i * i <= m:
            if m % i == 0:
                ds.append(i)
                if i != m // i:
                    ds.append(m // i)
            i += 1
        return ds
    cands = set()
    for p in facs(a0):
        for qd in facs(an):
            cands.add(Q(p, qd)); cands.add(Q(-p, qd))
    roots |= {r for r in cands if poly_eval(c, r) == 0}
    return sorted(roots)

# ================================================================ number theory (extended) =========
def num_divisors(n):
    r = 1
    for e in factorize(n).values(): r *= (e + 1)
    return r
def sigma(n, k=1):
    """sum of the k-th powers of the divisors of n (k=1 → σ(n))."""
    r = 1
    for p, e in factorize(n).items():
        r *= sum(p ** (k * i) for i in range(e + 1))
    return r
def next_prime(n):
    m = n + 1
    while not is_prime(m): m += 1
    return m
def prime_pi(N):
    return len(primes_up_to(N))
def integer_sqrt(n): return isqrt(int(n))
def is_perfect_square(n):
    if n < 0: return False
    r = isqrt(int(n)); return r * r == n
def integer_root(n, k):
    """exact integer k-th root of n if one exists, else None. Pure integer arithmetic (binary search) —
    no float, so it is correct for arbitrarily large n (a float k-th root loses precision past 2^53)."""
    n = int(n); k = int(k)
    if k < 1: return None
    if n < 0 and k % 2 == 0: return None
    m = abs(n)
    if m < 2: r = m
    else:
        lo, hi = 1, 1 << ((m.bit_length() + k - 1) // k + 1)   # hi ≥ true root
        while lo <= hi:                                          # exact integer binary search
            mid = (lo + hi) // 2; p = mid ** k
            if p == m: r = mid; break
            if p < m: lo = mid + 1
            else: hi = mid - 1
        else: return None
    if r ** k != m: return None
    return r if n >= 0 else -r
def digital_root(n, base=10):
    n = abs(n)
    while n >= base: n = sum(int(d) for d in _digits(n, base))
    return n
def _digits(n, base):
    if n == 0: return [0]
    d = []
    while n: d.append(n % base); n //= base
    return d[::-1]
def base_convert(n, base):
    """digits of |n| in the given base (2..36), most significant first, as a string."""
    n = int(n); sign = "-" if n < 0 else ""; n = abs(n)
    if n == 0: return "0"
    alpha = "0123456789abcdefghijklmnopqrstuvwxyz"; out = ""
    while n: out = alpha[n % base] + out; n //= base
    return sign + out
def bezout(a, b):
    """extended Euclid: returns (g, x, y) with a·x + b·y = g = gcd(a,b)."""
    return _egcd(int(a), int(b))
def legendre_symbol(a, p):
    a %= p
    if a == 0: return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls
def jacobi_symbol(a, n):
    a %= n; result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5): result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3: result = -result
        a %= n
    return result if n == 1 else 0
def discrete_log(g, h, p):
    """smallest x with g^x ≡ h (mod p) by baby-step giant-step, or None."""
    m = isqrt(p - 1) + 1; table = {}
    e = 1
    for j in range(m): table[e] = j; e = e * g % p
    factor = pow(g, (p - 2) * m % (p - 1) if is_prime(p) else -m, p) if is_prime(p) else pow(mod_inverse(g, p), m, p)
    e = h
    for i in range(m):
        if e in table: return i * m + table[e]
        e = e * factor % p
    return None
def primitive_root(p):
    if p == 2: return 1
    phi = p - 1; facs = list(factorize(phi))
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in facs): return g
    return None
def lucas(n):
    a, b = 2, 1
    for _ in range(n): a, b = b, a + b
    return a
def derangements(n):
    d = [1, 0]
    for k in range(2, n + 1): d.append((k - 1) * (d[k - 1] + d[k - 2]))
    return d[n]
def perm_count(n, k): return factorial(n) // factorial(n - k) if 0 <= k <= n else 0
def comb_with_rep(n, k): return binomial(n + k - 1, k)
def multinomial(ks):
    from functools import reduce
    num = factorial(sum(ks)); den = reduce(lambda a, b: a * b, (factorial(k) for k in ks), 1)
    return num // den
def faulhaber(p, N):
    """Σ_{i=1}^{N} i^p exact — finite sum in exact ℤ."""
    return sum(i ** p for i in range(1, N + 1))

# ================================================================ polynomials (algebra) ============
def _ptrim(c):
    c = [Q(x) for x in c]
    while len(c) > 1 and c[-1] == 0: c = c[:-1]
    return c
def poly_add(a, b):
    a, b = [Q(x) for x in a], [Q(x) for x in b]; n = max(len(a), len(b))
    return _ptrim([(a[i] if i < len(a) else Q(0)) + (b[i] if i < len(b) else Q(0)) for i in range(n)])
def poly_mul(a, b):
    a, b = [Q(x) for x in a], [Q(x) for x in b]; r = [Q(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b): r[i + j] += ai * bj
    return _ptrim(r)
def poly_divmod(a, b):
    a, b = _ptrim(a), _ptrim(b); q = [Q(0)] * (max(len(a) - len(b) + 1, 1)); r = a[:]
    while len(r) >= len(b) and r != [Q(0)]:
        if len(r) < len(b): break
        coef = r[-1] / b[-1]; deg = len(r) - len(b); q[deg] = coef
        for i in range(len(b)): r[deg + i] -= coef * b[i]
        r = _ptrim(r)
        if len(r) < len(b): break
    return _ptrim(q), _ptrim(r)
def poly_gcd(a, b):
    a, b = _ptrim(a), _ptrim(b)
    while b != [Q(0)]:
        _, r = poly_divmod(a, b); a, b = b, r
    lead = a[-1]; return [x / lead for x in a] if lead != 0 else a
def poly_derivative(c):
    c = [Q(x) for x in c]; return _ptrim([c[i] * i for i in range(1, len(c))]) if len(c) > 1 else [Q(0)]
def poly_integral(c):
    c = [Q(x) for x in c]; return [Q(0)] + [c[i] / (i + 1) for i in range(len(c))]
def poly_from_roots(roots):
    p = [Q(1)]
    for r in roots: p = poly_mul(p, [-Q(r), Q(1)])
    return p

# ================================================================ matrix (extended) ================
def transpose(A): return [list(row) for row in zip(*A)]
def trace(A): return sum(Q(A[i][i]) for i in range(len(A)))
def mat_add(A, B): return [[Q(A[i][j]) + Q(B[i][j]) for j in range(len(A[0]))] for i in range(len(A))]
def mat_power(A, k):
    n = len(A); R_ = [[Q(1) if i == j else Q(0) for j in range(n)] for i in range(n)]; B = _M(A)
    while k:
        if k & 1: R_ = mat_mul(R_, B)
        B = mat_mul(B, B); k >>= 1
    return R_
def rref(A):
    """reduced row-echelon form over ℚ, returning (rref, rank)."""
    M = _M(A); rows, cols = len(M), len(M[0]); r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; inv = M[r][c]; M[r] = [v / inv for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [M[i][j] - f * M[r][j] for j in range(cols)]
        r += 1
        if r == rows: break
    return M, r
def matrix_rank(A): return rref(A)[1]

# ================================================================ geometry (exact ℚ) ===============
def dot(u, v): return sum(Q(a) * Q(b) for a, b in zip(u, v))
def cross3(u, v):
    return [Q(u[1]) * Q(v[2]) - Q(u[2]) * Q(v[1]), Q(u[2]) * Q(v[0]) - Q(u[0]) * Q(v[2]),
            Q(u[0]) * Q(v[1]) - Q(u[1]) * Q(v[0])]
def cross2(u, v): return Q(u[0]) * Q(v[1]) - Q(u[1]) * Q(v[0])
def polygon_area(pts):
    """signed area of a simple polygon by the shoelace formula — exact ℚ."""
    n = len(pts); s = Q(0)
    for i in range(n):
        x1, y1 = Q(pts[i][0]), Q(pts[i][1]); x2, y2 = Q(pts[(i + 1) % n][0]), Q(pts[(i + 1) % n][1])
        s += x1 * y2 - x2 * y1
    return abs(s) / 2
def triangle_area(a, b, c): return polygon_area([a, b, c])

# ================================================================ number theory (P1) ===============
def diophantine_linear(a, b, c):
    """all integer solutions of a·x + b·y = c: (x0, y0, dx, dy) with x=x0+t·dx, y=y0+t·dy, or None."""
    g, x, y = _egcd(abs(a), abs(b))
    if c % g != 0: return None
    x *= (1 if a >= 0 else -1); y *= (1 if b >= 0 else -1)
    return (x * (c // g), y * (c // g), b // g, -a // g)
def tonelli_shanks(n, p):
    """a square root of n modulo an odd prime p (or None if n is a non-residue)."""
    n %= p
    if n == 0: return 0
    if pow(n, (p - 1) // 2, p) != 1: return None
    if p % 4 == 3: return pow(n, (p + 1) // 4, p)
    q = p - 1; s = 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m = s; c = pow(z, q, p); t = pow(n, q, p); r = pow(n, (q + 1) // 2, p)
    while t != 1:
        i = 0; tt = t
        while tt != 1: tt = tt * tt % p; i += 1
        b = pow(c, 1 << (m - i - 1), p); m = i; c = b * b % p; t = t * c % p; r = r * b % p
    return r
def pell(D):
    """the fundamental solution (x,y) of Pell's equation x²−D·y²=1 via the continued fraction of √D."""
    a0 = isqrt(D)
    if a0 * a0 == D: return None
    m, d, a = 0, 1, a0; h1, h0, k1, k0 = a0, 1, 1, 0
    while h1 * h1 - D * k1 * k1 != 1:
        m = d * a - m; d = (D - m * m) // d; a = (a0 + m) // d
        h1, h0 = a * h1 + h0, h1; k1, k0 = a * k1 + k0, k1
    return (h1, k1)
def mobius(n):
    n = abs(n)
    if n == 1: return 1
    f = factorize(n)
    return 0 if any(e > 1 for e in f.values()) else (-1) ** len(f)
def mertens(N): return sum(mobius(k) for k in range(1, N + 1))
def liouville(n): return (-1) ** sum(factorize(n).values()) if n > 1 else 1
def von_mangoldt(n):
    import math as _m
    f = factorize(n)
    return _m.log(list(f)[0]) if len(f) == 1 else 0.0

# ================================================================ linear algebra (P1) ==============
def matrix_exp(A, terms=60):
    """e^A = Σ A^k/k! (finite series). A over ℚ/ℝ; returns a float matrix."""
    n = len(A); import mpmath as mp
    S = [[mp.mpf(1) if i == j else mp.mpf(0) for j in range(n)] for i in range(n)]
    T = [[mp.mpf(1) if i == j else mp.mpf(0) for j in range(n)] for i in range(n)]
    Am = [[mp.mpf(str(float(x))) for x in row] for row in A]
    for k in range(1, terms):
        T = [[sum(T[i][l] * Am[l][j] for l in range(n)) / k for j in range(n)] for i in range(n)]
        S = [[S[i][j] + T[i][j] for j in range(n)] for i in range(n)]
    return S
def null_space(A):
    """a basis (list of vectors) for the kernel of A over ℚ, from the reduced row-echelon form."""
    M, r = rref(A); rows, cols = len(M), len(M[0])
    pivots = []
    for i in range(r):
        pivots.append(next(j for j in range(cols) if M[i][j] != 0))
    free = [j for j in range(cols) if j not in pivots]
    basis = []
    for fcol in free:
        v = [Q(0)] * cols; v[fcol] = Q(1)
        for i, pc in enumerate(pivots): v[pc] = -M[i][fcol]
        basis.append(v)
    return basis
def hermite_normal_form(A):
    """column-style Hermite normal form of an integer matrix (upper-triangular, exact)."""
    M = [[int(x) for x in row] for row in A]; rows = len(M); cols = len(M[0]); r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        if M[r][c] < 0: M[r] = [-x for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                q = M[i][c] // M[r][c]; M[i] = [M[i][j] - q * M[r][j] for j in range(cols)]
        r += 1
        if r == rows: break
    return M
def smith_normal_form(A):
    """the invariant factors d_1 | d_2 | … of an integer matrix (Smith normal form diagonal)."""
    M = [[int(x) for x in row] for row in A]; rows = len(M); cols = len(M[0]); res = []; t = 0
    import math as _m
    while t < min(rows, cols):
        nz = [(i, j) for i in range(t, rows) for j in range(t, cols) if M[i][j] != 0]
        if not nz: break
        i0, j0 = min(nz, key=lambda p: abs(M[p[0]][p[1]]))
        M[t], M[i0] = M[i0], M[t]
        for r in range(rows): M[r][t], M[r][j0] = M[r][j0], M[r][t]
        changed = True
        while changed:
            changed = False
            for i in range(t + 1, rows):
                if M[i][t]:
                    q = M[i][t] // M[t][t]; M[i] = [M[i][j] - q * M[t][j] for j in range(cols)]
                    if M[i][t]: M[t], M[i] = M[i], M[t]; changed = True
            for j in range(t + 1, cols):
                if M[t][j]:
                    q = M[t][j] // M[t][t]
                    for r in range(rows): M[r][j] -= q * M[r][t]
                    if M[t][j]:
                        for r in range(rows): M[r][t], M[r][j] = M[r][j], M[r][t]
                        changed = True
        res.append(abs(M[t][t])); t += 1
    # enforce divisibility d_i | d_{i+1}
    for i in range(len(res) - 1):
        for j in range(i + 1, len(res)):
            if res[i] and res[j] % res[i] != 0:
                g = _m.gcd(res[i], res[j]); res[j] = res[i] * res[j] // g; res[i] = g
    return res
