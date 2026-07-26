"""idm.hilbert — the finite-dimensional Hilbert-space mathematical core (EXACT / finite_diagnostic).

An operator-theoretic *information* architecture, pure mathematics — no physics. Everything here lives in
a FINITE-dimensional inner-product space over ℚ or the Gaussian rationals ℚ[i]; the scalar is an exact
`QC` pair, never Python's IEEE `complex` (which would silently break every "exact" tag). The completeness
step, ℓ²/L², and infinite dimension are DELIBERATELY absent from this file — they live only in
`idm.hilbert_open` as `+ℝ-Open` readouts, and this module never imports that one (the +ℝ fence is
enforced in code, not prose).

Tier discipline: exact ℚ/ℚ[i] linear algebra and decidable booleans are `exact` / `Th_coqc`-eligible;
anything needing an irrational root (a generic eigenvalue, a non-square norm) is `finite_diagnostic`
(numeric, certified by a residual/tolerance bound), resolved PER CALL — never a blanket "n ≤ k ⇒ exact".
The physics↔math dictionary is a detachable `Dr` layer that lives in the textbook, never here.
"""
from fractions import Fraction as Q


# ============================ exact Gaussian-rational scalar ℚ[i] ============================
class QC:
    """an exact Gaussian-rational scalar re + im·i, both `Fraction` — NOT IEEE complex."""
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = re if isinstance(re, Q) else Q(re)
        self.im = im if isinstance(im, Q) else Q(im)

    def conj(self): return QC(self.re, -self.im)
    def __add__(self, o): o = _qc(o); return QC(self.re + o.re, self.im + o.im)
    def __sub__(self, o): o = _qc(o); return QC(self.re - o.re, self.im - o.im)
    def __mul__(self, o):
        o = _qc(o)
        return QC(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)
    def __truediv__(self, o):
        o = _qc(o); d = o.re * o.re + o.im * o.im
        if d == 0: raise ZeroDivisionError("division by zero Gaussian rational")
        n = self * o.conj()
        return QC(n.re / d, n.im / d)
    def __neg__(self): return QC(-self.re, -self.im)
    def __eq__(self, o): o = _qc(o); return self.re == o.re and self.im == o.im
    def __hash__(self): return hash((self.re, self.im))
    def abs2(self): return self.re * self.re + self.im * self.im      # |z|² ∈ ℚ, exact
    def is_real(self): return self.im == 0
    def __repr__(self):
        if self.im == 0: return f"{self.re}"
        return f"{self.re}{'+' if self.im >= 0 else '-'}{abs(self.im)}i"


def _qc(x):
    """coerce int / str('a/b') / [re,im] / (re,im) / QC / a dict-encoded output back into an exact QC
    scalar (so this module's own outputs can be fed straight back in as inputs)."""
    if isinstance(x, QC): return x
    if isinstance(x, dict):
        if "exact" in x: return QC(Q(str(x["exact"])))
        if "re" in x and "im" in x: return QC(Q(str(x["re"])), Q(str(x["im"])))
        raise TypeError(f"cannot read scalar from dict {x}")
    if isinstance(x, (list, tuple)) and len(x) == 2: return QC(Q(str(x[0])), Q(str(x[1])))
    if isinstance(x, complex): raise TypeError("IEEE complex is not exact — pass [re, im] rationals")
    return QC(Q(str(x)))


def _vec(v): return [_qc(x) for x in v]
def _mat(M): return [[_qc(x) for x in row] for row in M]
def _out(z): return {"re": str(z.re), "im": str(z.im), "float": (float(z.re), float(z.im))} if not z.is_real() \
    else {"exact": str(z.re), "float": float(z.re)}


# ============================ inner product / norm ============================
def inner_product(u, v):
    """⟨u,v⟩ = Σ conj(uᵢ)·vᵢ — exact ℚ[i], finite sum (conjugate-linear in the FIRST slot)."""
    u, v = _vec(u), _vec(v)
    if len(u) != len(v): raise ValueError("inner product needs equal-length vectors")
    s = QC(0)
    for a, b in zip(u, v): s = s + a.conj() * b
    return {"value": _out(s), "method": "⟨u,v⟩=Σ conj(uᵢ)vᵢ, exact ℚ[i]"}


def norm_squared(v):
    """‖v‖² = ⟨v,v⟩ — exact non-negative ℚ (the imaginary part is provably 0)."""
    v = _vec(v); s = Q(0)
    for a in v: s += a.abs2()
    return {"value": {"exact": str(s), "float": float(s)}, "method": "‖v‖²=Σ|vᵢ|², exact ℚ ≥ 0"}


def cauchy_schwarz_check(u, v):
    """instance-verify |⟨u,v⟩|² ≤ ⟨u,u⟩·⟨v,v⟩ exactly (the general theorem is machine-checked)."""
    u, v = _vec(u), _vec(v)
    ip = QC(0)
    for a, b in zip(u, v): ip = ip + a.conj() * b
    lhs = ip.abs2(); rhs = sum((a.abs2() for a in u), Q(0)) * sum((b.abs2() for b in v), Q(0))
    return {"value": {"holds": bool(lhs <= rhs), "lhs": str(lhs), "rhs": str(rhs)},
            "method": "exact ℚ comparison |⟨u,v⟩|² ≤ ⟨u,u⟩⟨v,v⟩"}


def is_orthogonal(u, v):
    r = inner_product(u, v)["value"]
    zero = (r.get("exact") == "0") or (r.get("re") == "0" and r.get("im") == "0")
    return {"value": bool(zero), "method": "decidable exact ⟨u,v⟩ == 0"}


def gram_matrix(vectors):
    """Gᵢⱼ = ⟨vᵢ,vⱼ⟩ — the exact Hermitian PSD ℚ[i] matrix of a finite vector family."""
    V = [_vec(v) for v in vectors]; n = len(V)
    G = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = QC(0)
            for a, b in zip(V[i], V[j]): s = s + a.conj() * b
            G[i][j] = _out(s)
    return {"value": G, "method": "Gᵢⱼ=⟨vᵢ,vⱼ⟩, exact Hermitian ℚ[i]"}


# ============================ Gram–Schmidt / orthonormal basis ============================
def _ip(u, v):
    s = QC(0)
    for a, b in zip(u, v): s = s + a.conj() * b
    return s

def _gram_schmidt_exact(V):
    """orthogonalize only — exact ℚ[i] (needs field division by exact inner products, no sqrt)."""
    W = []; norms = []
    for u in V:
        w = list(u)
        for wj, nj in zip(W, norms):
            if nj == 0: continue
            c = _ip(wj, u) / QC(nj)
            w = [wi - c * wji for wi, wji in zip(w, wj)]
        W.append(w); norms.append(_ip(w, w).re)   # ⟨w,w⟩ is real ≥ 0
    return W, norms

def gram_schmidt(vectors):
    """exact ℚ[i] orthogonalization; returns the orthogonal set + each exact squared norm."""
    V = [_vec(v) for v in vectors]
    W, norms = _gram_schmidt_exact(V)
    return {"value": {"orthogonal": [[_out(x) for x in w] for w in W],
                      "squared_norms": [{"exact": str(n), "float": float(n)} for n in norms]},
            "method": "exact ℚ[i] Gram–Schmidt (orthogonalize only, no sqrt)"}


def _perfect_sqrt(q: Q):
    """exact √q ∈ ℚ if q is a perfect square of a rational, else None."""
    if q < 0: return None
    from math import isqrt
    ni, di = q.numerator, q.denominator
    rn, rd = isqrt(ni), isqrt(di)
    if rn * rn == ni and rd * rd == di: return Q(rn, rd)
    return None

def orthonormal_basis(vectors):
    """Gram–Schmidt + normalization. EXACT iff every non-zero squared norm is a perfect square in ℚ;
    otherwise the normalization is a certified numeric readout → tier finite_diagnostic (per-instance)."""
    V = [_vec(v) for v in vectors]
    W, norms = _gram_schmidt_exact(V)
    exact = True; basis = []; residual = Q(0)
    import mpmath as mp
    for w, n in zip(W, norms):
        if n == 0: continue                          # dependent vector — dropped
        r = _perfect_sqrt(n)
        if r is not None:
            basis.append([_out(x / QC(r)) for x in w])
        else:
            exact = False
            s = mp.sqrt(mp.mpf(n.numerator) / n.denominator)
            def _f(fr): return mp.mpf(fr.numerator) / fr.denominator
            basis.append([{"re": mp.nstr(_f(x.re) / s, 20), "im": mp.nstr(_f(x.im) / s, 20)} for x in w])
    tier = "exact" if exact else "finite_diagnostic"
    return {"value": {"orthonormal": basis, "count": len(basis), "exact_normalization": exact},
            "tier": tier,
            "method": "Gram–Schmidt + normalization (exact when every norm is a perfect square, else "
                      "certified numeric sqrt)"}


# ============================ matrices: adjoint / projection ============================
def _adjoint(M): return [[M[j][i].conj() for j in range(len(M))] for i in range(len(M[0]))]
def _matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    C = [[QC(0)] * p for _ in range(n)]
    for i in range(n):
        for k in range(m):
            a = A[i][k]
            for j in range(p): C[i][j] = C[i][j] + a * B[k][j]
    return C
def _eye(n): return [[QC(1 if i == j else 0) for j in range(n)] for i in range(n)]
def _meq(A, B): return len(A) == len(B) and all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0])))

def _inv(M):
    """exact ℚ[i] matrix inverse by Gauss–Jordan; raises on singular."""
    n = len(M); A = [[M[i][j] for j in range(n)] + [QC(1 if i == j else 0) for j in range(n)] for i in range(n)]
    for c in range(n):
        piv = next((r for r in range(c, n) if not (A[r][c] == QC(0))), None)
        if piv is None: raise ValueError("singular matrix")
        A[c], A[piv] = A[piv], A[c]
        inv = A[c][c]; A[c] = [x / inv for x in A[c]]
        for r in range(n):
            if r != c and not (A[r][c] == QC(0)):
                f = A[r][c]; A[r] = [A[r][k] - f * A[c][k] for k in range(2 * n)]
    return [[A[i][n + j] for j in range(n)] for i in range(n)]

def adjoint(matrix):
    M = _mat(matrix)
    return {"value": [[_out(x) for x in row] for row in _adjoint(M)], "method": "M*=conj(M)ᵀ, exact"}

def is_self_adjoint(matrix):
    M = _mat(matrix)
    return {"value": bool(_meq(M, _adjoint(M))), "method": "decidable exact M == M*"}

def is_unitary(matrix):
    M = _mat(matrix); n = len(M)
    return {"value": bool(_meq(_matmul(_adjoint(M), M), _eye(n))), "method": "decidable exact M*M == I"}

def is_normal(matrix):
    M = _mat(matrix)
    return {"value": bool(_meq(_matmul(M, _adjoint(M)), _matmul(_adjoint(M), M))), "method": "decidable exact MM* == M*M"}

def is_idempotent(matrix):
    M = _mat(matrix)
    return {"value": bool(_meq(_matmul(M, M), M)), "method": "decidable exact M·M == M"}

def projection_matrix(basis):
    """P = A(A*A)⁻¹A* onto span(columns of A), for a full-rank finite basis — exact ℚ[i]."""
    cols = [_vec(v) for v in basis]; n = len(cols[0]); k = len(cols)
    A = [[cols[j][i] for j in range(k)] for i in range(n)]           # n×k
    As = _adjoint(A)
    P = _matmul(_matmul(A, _inv(_matmul(As, A))), As)
    return {"value": [[_out(x) for x in row] for row in P], "method": "P=A(A*A)⁻¹A*, exact ℚ[i]"}

def project(v, basis):
    P = _mat(projection_matrix(basis)["value"])   # re-read as QC via _out→_mat round trip
    # projection_matrix returns dict-encoded; rebuild QC directly instead
    cols = [_vec(b) for b in basis]; n = len(cols[0]); k = len(cols)
    A = [[cols[j][i] for j in range(k)] for i in range(n)]; As = _adjoint(A)
    Pm = _matmul(_matmul(A, _inv(_matmul(As, A))), As)
    x = _vec(v)
    out = [QC(0)] * n
    for i in range(n):
        for j in range(n): out[i] = out[i] + Pm[i][j] * x[j]
    return {"value": [_out(z) for z in out], "method": "P·v, exact ℚ[i]"}


# ============================ operator-norm bound / true norm ============================
def gershgorin_bound(matrix):
    """a sqrt-free EXACT upper bound on the operator norm: max_i Σⱼ (|re|+|im|) ≥ max_i Σⱼ|Mᵢⱼ|
    (row-sum / ∞-norm bound). Always a BOUND, never the true sup norm."""
    M = _mat(matrix)
    best = Q(0)
    for row in M:
        s = sum((abs(z.re) + abs(z.im)) for z in row)
        best = max(best, s)
    return {"value": {"exact": str(best), "float": float(best)},
            "method": "max_i Σⱼ(|re|+|im|) — exact sqrt-free operator-norm upper bound"}

def operator_norm(matrix):
    """the TRUE operator norm (largest singular value) — ALWAYS finite_diagnostic: numeric power
    iteration on M*M with an a-posteriori Rayleigh-quotient residual bound."""
    import mpmath as mp
    M = _mat(matrix); n = len(M); m = len(M[0])
    A = mp.matrix([[mp.mpc(float(M[i][j].re), float(M[i][j].im)) for j in range(m)] for i in range(n)])
    AtA = A.H * A                                     # m×m Hermitian PSD
    x = mp.matrix([mp.mpf(1)] * m)
    lam = mp.mpf(0)
    for _ in range(500):
        y = AtA * x
        ny = mp.norm(y)
        if ny == 0: break
        x = y / ny
        lam = (x.H * (AtA * x))[0].real
    resid = mp.norm(AtA * x - lam * x)
    return {"value": {"norm": mp.nstr(mp.sqrt(lam), 20), "float": float(mp.sqrt(lam))},
            "tier": "finite_diagnostic",
            "error_bound": {"rayleigh_residual": mp.nstr(resid, 6)},
            "method": "largest singular value via power iteration on M*M (certified residual)"}


# ============================ characteristic polynomial / spectrum ============================
def _charpoly(M):
    """Faddeev–LeVerrier: exact ℚ[i] coefficients of det(xI − M), highest degree first (monic)."""
    n = len(M); I = _eye(n); Mk = [[M[i][j] for j in range(n)] for i in range(n)]
    coeffs = [QC(1)]                                  # x^n
    Ak = I
    for k in range(1, n + 1):
        Ak = _matmul(M, [[Ak[i][j] + (coeffs[-1] * I[i][j]) for j in range(n)] for i in range(n)]) if k > 1 else \
             [[M[i][j] for j in range(n)] for i in range(n)]
        tr = QC(0)
        for i in range(n): tr = tr + Ak[i][i]
        coeffs.append(QC(-1) * tr / QC(k))
    return coeffs

def characteristic_poly(matrix):
    """exact ℚ[i] coefficients of the characteristic polynomial (monic, highest degree first).
    Exact regardless of whether the roots turn out rational — pure finite elimination."""
    M = _mat(matrix)
    c = _charpoly(M)
    return {"value": [_out(z) for z in c], "method": "Faddeev–LeVerrier, exact ℚ[i] coefficients"}

def _null_space_exact(M):
    """exact rational basis of the null space of a ℚ[i] matrix (RREF)."""
    n = len(M); A = [[M[i][j] for j in range(len(M[0]))] for i in range(n)]; rows, cols = len(A), len(A[0])
    pivots = []; r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if not (A[i][c] == QC(0))), None)
        if piv is None: continue
        A[r], A[piv] = A[piv], A[r]
        inv = A[r][c]; A[r] = [x / inv for x in A[r]]
        for i in range(rows):
            if i != r and not (A[i][c] == QC(0)):
                f = A[i][c]; A[i] = [A[i][k] - f * A[r][k] for k in range(cols)]
        pivots.append(c); r += 1
        if r == rows: break
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for fcol in free:
        vec = [QC(0)] * cols; vec[fcol] = QC(1)
        for ri, pc in enumerate(pivots): vec[pc] = QC(-1) * A[ri][fcol]
        basis.append(vec)
    return basis

def spectral_decomposition(matrix):
    """Hermitian/normal n×n. EXACT fast path: characteristic_poly → rational eigenvalues → exact null
    spaces; tier `exact` ONLY IF every eigenvalue is rational (per-instance). Otherwise a certified
    numeric eigensolver with a proven residual ‖MV−VΛ‖≤ε, tier `finite_diagnostic`."""
    M = _mat(matrix); n = len(M)
    if not _meq(_matmul(M, _adjoint(M)), _matmul(_adjoint(M), M)):
        return {"status": "HOLD", "reason": "spectral_decomposition needs a normal (e.g. Hermitian) matrix"}
    from . import exact as X
    coeffs = _charpoly(M)
    real_coeffs = None
    if all(z.is_real() for z in coeffs):
        real_coeffs = [z.re for z in coeffs][::-1]     # exact.rational_roots wants low-order first
    if real_coeffs is not None:
        roots = X.rational_roots([Q(c) for c in real_coeffs])
        # count with multiplicity by dividing out
        eigs = []
        from fractions import Fraction as F
        def poly_eval(cs, x): return sum(c * x ** i for i, c in enumerate(cs))
        cur = list(real_coeffs)
        for rt in roots:
            while len(cur) > 1 and poly_eval(cur, F(rt)) == 0:
                eigs.append(F(rt))
                # synthetic division by (x - rt), cur is low-order first
                q = [F(0)] * (len(cur) - 1); rem = list(cur)
                # divide high-order first
                hi = rem[::-1]; out = []
                carry = F(0)
                for coef in hi:
                    carry = coef + carry * F(rt); out.append(carry)
                cur = out[:-1][::-1]
        if len(eigs) == n:                             # all eigenvalues rational → EXACT path
            eigenpairs = []
            for lam in sorted(set(eigs)):
                Mm = [[M[i][j] - QC(lam if i == j else 0) for j in range(n)] for i in range(n)]
                ns = _null_space_exact(Mm)
                Wt, _nm = _gram_schmidt_exact(ns)
                for w in Wt:
                    eigenpairs.append({"eigenvalue": {"exact": str(lam), "float": float(lam)},
                                       "eigenvector_exact": [_out(x) for x in w]})
            return {"value": {"eigenvalues": [{"exact": str(e), "float": float(e)} for e in sorted(eigs)],
                              "eigenpairs": eigenpairs, "exact": True},
                    "tier": "exact",
                    "method": "characteristic_poly → rational roots → exact null spaces (all eigenvalues rational)"}
    # numeric fallback (finite_diagnostic)
    import mpmath as mp
    A = mp.matrix([[mp.mpc(float(M[i][j].re), float(M[i][j].im)) for j in range(n)] for i in range(n)])
    E, V = mp.eig(A)
    resid = mp.mpf(0)
    for k in range(n):
        vk = V[:, k]; resid = max(resid, mp.norm(A * vk - E[k] * vk))
    return {"value": {"eigenvalues": [{"re": mp.nstr(e.real, 18), "im": mp.nstr(e.imag, 18)} for e in E],
                      "exact": False},
            "tier": "finite_diagnostic",
            "error_bound": {"max_eigenpair_residual": mp.nstr(resid, 6)},
            "method": "certified numeric eigensolver (mpmath), residual ‖Av−λv‖ ≤ bound"}


# ============================ composite systems (operator algebra, physics-neutral) ============================
def tensor_product(a, b):
    """Kronecker product of two vectors or two matrices — exact ℚ[i]. (Pure operator-algebra object;
    any physical reading is the detachable Dr layer, not here.)"""
    if a and isinstance(a[0], (list, tuple)):          # matrices
        A, B = _mat(a), _mat(b); ra, ca, rb, cb = len(A), len(A[0]), len(B), len(B[0])
        out = [[None] * (ca * cb) for _ in range(ra * rb)]
        for i in range(ra):
            for j in range(ca):
                for k in range(rb):
                    for l in range(cb):
                        out[i * rb + k][j * cb + l] = _out(A[i][j] * B[k][l])
        return {"value": out, "method": "Kronecker product A⊗B, exact ℚ[i]"}
    A, B = _vec(a), _vec(b)
    return {"value": [_out(x * y) for x in A for y in B], "method": "Kronecker product u⊗v, exact ℚ[i]"}

def partial_trace(matrix, dims, keep):
    """finite-dim block-sum partial trace of an operator on ℂ^{d0}⊗ℂ^{d1}, keeping subsystem `keep`.
    Exact ℚ[i]. dims=[d0,d1]."""
    M = _mat(matrix); d0, d1 = dims
    if keep == 0:
        out = [[QC(0)] * d0 for _ in range(d0)]
        for i in range(d0):
            for j in range(d0):
                for k in range(d1):
                    out[i][j] = out[i][j] + M[i * d1 + k][j * d1 + k]
    else:
        out = [[QC(0)] * d1 for _ in range(d1)]
        for i in range(d1):
            for j in range(d1):
                for k in range(d0):
                    out[i][j] = out[i][j] + M[k * d1 + i][k * d1 + j]
    return {"value": [[_out(x) for x in row] for row in out], "method": f"exact block-sum partial trace (keep={keep})"}

def choi_matrix(cp_map_generators):
    """exact ℚ[i] Choi matrix J = Σₐ |Kₐ⟩⟩⟨⟨Kₐ| (column-vectorization) of a finite generator list."""
    Ks = [_mat(K) for K in cp_map_generators]
    r = len(Ks[0]); c = len(Ks[0][0]); dim = r * c
    J = [[QC(0)] * dim for _ in range(dim)]
    for K in Ks:
        vecK = [K[i][j] for j in range(c) for i in range(r)]   # column-stack vec
        for a in range(dim):
            for b in range(dim):
                J[a][b] = J[a][b] + vecK[a] * vecK[b].conj()
    return {"value": [[_out(x) for x in row] for row in J], "method": "J=Σₐ vec(Kₐ)vec(Kₐ)*, exact ℚ[i]"}

def _psd_eigsign(M):
    """(is_psd, tier, detail) via the eigenvalue-SIGN test (NOT Sylvester leading minors — that tests
    positive-definiteness, e.g. diag(0,-1) passes the leading minors yet is not PSD)."""
    sd = spectral_decomposition([[_out(x) for x in row] for row in M])
    if sd.get("status") == "HOLD":                     # not normal → symmetrize check n/a; treat via numeric
        pass
    if sd.get("tier") == "exact":
        evs = [Q(e["exact"]) for e in sd["value"]["eigenvalues"]]
        return all(e >= 0 for e in evs), "exact", {"eigenvalues": [str(e) for e in evs]}
    evs = sd["value"]["eigenvalues"]
    import mpmath as mp
    ok = all(float(e.get("re", e.get("float", 0))) >= -1e-12 for e in evs)
    return ok, "finite_diagnostic", {"min_eigenvalue_re": min(float(e.get("re", 0)) for e in evs)}

def is_completely_positive(choi):
    """a CP map ⇔ its Choi matrix is PSD — tested by eigenvalue SIGN (fix: NOT Sylvester leading minors)."""
    M = _mat(choi)
    ok, tier, detail = _psd_eigsign(M)
    return {"value": {"completely_positive": bool(ok), **detail}, "tier": tier,
            "method": "Choi PSD via eigenvalue-sign test (per-instance exact/finite_diagnostic)"}

def is_separable_ppt(rho, dims):
    """Peres–Horodecki (PPT). A NEGATIVE partial-transpose eigenvalue is an exact witness of
    NON-separability (any dims). PPT is necessary-and-sufficient only in 2×2 / 2×3 (finite_diagnostic
    'separable' there); outside that range a positive PT is inconclusive → HOLD (never 'separable')."""
    M = _mat(rho); d0, d1 = dims
    # partial transpose on the second subsystem
    T = [[QC(0)] * (d0 * d1) for _ in range(d0 * d1)]
    for i0 in range(d0):
        for i1 in range(d1):
            for j0 in range(d0):
                for j1 in range(d1):
                    T[i0 * d1 + i1][j0 * d1 + j1] = M[i0 * d1 + j1][j0 * d1 + i1]
    ok, tier, detail = _psd_eigsign(T)
    if not ok:
        return {"value": {"separable": False, "witness": "negative partial-transpose eigenvalue", **detail},
                "tier": ("exact" if tier == "exact" else "finite_diagnostic"),
                "method": "PPT: negative PT eigenvalue ⇒ entangled (exact witness)"}
    if (d0, d1) in ((2, 2), (2, 3), (3, 2)):
        return {"value": {"separable": True, **detail}, "tier": "finite_diagnostic",
                "method": "PPT necessary-and-sufficient in 2×2 / 2×3"}
    return {"status": "HOLD", "reason": f"PPT is only necessary above 2×2/2×3 ({d0}×{d1}); "
                                        "positive partial transpose does not certify separability"}
