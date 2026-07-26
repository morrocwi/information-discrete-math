"""idm.stats — statistics & probability as finite readouts.

Discrete distributions are already finite objects (a pmf is a finite table of rationals); their exact
moments come out as ℚ. The few genuinely continuum-flavoured pieces — a normal tail, a t/χ² p-value —
are computed as a finite readout (a converged series / a rational-arithmetic incomplete function),
tier `finite_diagnostic`, never by importing a continuum distribution. Regression is exact least
squares over ℚ (normal equations solved rationally). Markov chain absorbing/hitting times are exact ℚ
linear solves. Bayesian update is exact rational renormalization.
"""
from fractions import Fraction as Q
from math import comb, factorial, isqrt
import mpmath as mp
mp.mp.dps = 30


# ---------------- discrete distributions (exact pmf/cdf over ℚ) ----------------
def _binom_pmf(n, k, p):
    p = Q(p);
    if k < 0 or k > n: return Q(0)
    return comb(n, k) * p ** k * (1 - p) ** (n - k)

def binomial(n, k=None, p=Q(1, 2)):
    """exact binomial pmf/cdf: P(X=k) and P(X≤k) for X~Bin(n,p), all rational."""
    p = Q(p)
    if not (0 <= p <= 1): raise ValueError(f"binomial needs a probability p∈[0,1], got {p}")
    if int(n) != n or n < 0: raise ValueError(f"binomial needs a non-negative integer n, got {n}")
    mean = Q(n) * p; var = Q(n) * p * (1 - p)
    out = {"mean": mean, "variance": var}
    if k is not None:
        out["pmf"] = _binom_pmf(n, k, p)
        out["cdf"] = sum((_binom_pmf(n, i, p) for i in range(0, k + 1)), Q(0))
    return out

def poisson(lam, k=None):
    """Poisson pmf/cdf with rational λ — P(X=k)=e^{-λ}λ^k/k! as a finite readout."""
    if float(lam) < 0: raise ValueError(f"Poisson needs rate λ≥0, got {lam}")
    if k is not None and (int(k) != k or k < 0): raise ValueError(f"Poisson needs a non-negative integer k, got {k}")
    lam_m = mp.mpf(str(lam)); mean = mp.mpf(str(lam))
    out = {"mean": mean, "variance": mean}
    if k is not None:
        out["pmf"] = mp.e ** (-lam_m) * lam_m ** k / factorial(k)
        out["cdf"] = mp.fsum(mp.e ** (-lam_m) * lam_m ** i / factorial(i) for i in range(0, k + 1))
    return out

def hypergeometric(N, K, n, k):
    """exact hypergeometric pmf/cdf: drawing n from N with K successes, P(X=k) rational."""
    if not (0 <= K <= N and 0 <= n <= N and N >= 1):
        raise ValueError(f"hypergeometric needs 0≤K≤N, 0≤n≤N, N≥1 (got N={N},K={K},n={n})")
    def pmf(i):
        if i < max(0, n - (N - K)) or i > min(K, n): return Q(0)
        return Q(comb(K, i) * comb(N - K, n - i), comb(N, n))
    return {"pmf": pmf(k), "cdf": sum((pmf(i) for i in range(0, k + 1)), Q(0)),
            "mean": Q(n * K, N)}

def geometric(p, k=None):
    """geometric pmf/cdf on {1,2,…}: P(X=k)=(1-p)^{k-1} p, exact rational."""
    p = Q(p)
    if not (0 < p <= 1): raise ValueError(f"geometric needs a success probability p∈(0,1], got {p}")
    out = {"mean": Q(1) / p, "variance": (1 - p) / p ** 2}
    if k is not None:
        out["pmf"] = (1 - p) ** (k - 1) * p
        out["cdf"] = 1 - (1 - p) ** k
    return out

def normal(x, mu=0, sigma=1):
    """standard/general normal pdf & cdf as a finite readout (cdf via erf series)."""
    if float(sigma) <= 0: raise ValueError(f"normal needs standard deviation σ>0, got {sigma}")
    x = mp.mpf(str(x)); mu = mp.mpf(str(mu)); s = mp.mpf(str(sigma))
    z = (x - mu) / s
    pdf = mp.e ** (-z * z / 2) / (s * mp.sqrt(2 * mp.pi))
    cdf = (1 + mp.erf(z / mp.sqrt(2))) / 2
    return {"z": z, "pdf": pdf, "cdf": cdf, "sf": 1 - cdf}


# ---------------- descriptive & inference ----------------
def describe(data):
    """exact sample moments over ℚ: mean, variance (n-1), std (finite readout of the ℚ variance)."""
    xs = [Q(str(v)) for v in data]; n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1) if n > 1 else Q(0)
    return {"n": n, "mean": m, "variance": var, "std": mp.sqrt(mp.mpf(var.numerator) / var.denominator) if var else mp.mpf(0),
            "min": min(xs), "max": max(xs)}

def z_test(sample_mean, mu0, sigma, n):
    """one-sample z-test: statistic and two-sided p-value (finite readout)."""
    z = (mp.mpf(str(sample_mean)) - mp.mpf(str(mu0))) / (mp.mpf(str(sigma)) / mp.sqrt(n))
    p = mp.erfc(abs(z) / mp.sqrt(2))
    return {"z": z, "p_value": p, "reject_at_0.05": bool(p < mp.mpf("0.05"))}

def t_test(sample_mean, mu0, sample_std, n):
    """one-sample t-test: statistic and two-sided p-value via the regularized incomplete beta."""
    t = (mp.mpf(str(sample_mean)) - mp.mpf(str(mu0))) / (mp.mpf(str(sample_std)) / mp.sqrt(n))
    df = n - 1
    x = df / (df + t * t)
    p = mp.betainc(df / mp.mpf(2), mp.mpf(1) / 2, 0, x, regularized=True)
    return {"t": t, "df": df, "p_value": p, "reject_at_0.05": bool(p < mp.mpf("0.05"))}

def chi_square_test(observed, expected):
    """Pearson χ² goodness-of-fit: statistic (exact ℚ) and p-value (finite readout)."""
    chi2 = sum((Q(str(o)) - Q(str(e))) ** 2 / Q(str(e)) for o, e in zip(observed, expected))
    df = len(observed) - 1
    p = mp.gammainc(df / mp.mpf(2), mp.mpf(chi2.numerator) / chi2.denominator / 2, mp.inf, regularized=True)
    return {"chi2": chi2, "df": df, "p_value": p, "reject_at_0.05": bool(p < mp.mpf("0.05"))}


# ---------------- exact-ℚ regression ----------------
def _solve_Q(A, b):
    n = len(A); M = [[Q(str(A[i][j])) for j in range(n)] + [Q(str(b[i]))] for i in range(n)]
    for c in range(n):
        piv = next((r for r in range(c, n) if M[r][c] != 0), None)
        if piv is None: raise ValueError("singular normal equations")
        M[c], M[piv] = M[piv], M[c]
        inv = M[c][c]
        M[c] = [v / inv for v in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [M[r][j] - f * M[c][j] for j in range(n + 1)]
    return [M[i][n] for i in range(n)]

def regression(x, y, degree=1):
    """exact polynomial least-squares over ℚ: fit y≈Σ c_j x^j by solving the ℚ normal equations.
    degree=1 is ordinary linear regression. Returns exact rational coefficients + R²."""
    xs = [Q(str(v)) for v in x]; ys = [Q(str(v)) for v in y]; n = len(xs); d = degree
    # normal equations (XᵀX) c = Xᵀy with X_ij = x_i^j
    XtX = [[sum(xk ** (i + j) for xk in xs) for j in range(d + 1)] for i in range(d + 1)]
    Xty = [sum(xs[k] ** i * ys[k] for k in range(n)) for i in range(d + 1)]
    c = _solve_Q(XtX, Xty)
    ybar = sum(ys) / n
    def pred(xv): return sum(c[j] * xv ** j for j in range(d + 1))
    ss_res = sum((ys[k] - pred(xs[k])) ** 2 for k in range(n))
    ss_tot = sum((yk - ybar) ** 2 for yk in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else Q(1)
    return {"coeffs": c, "r_squared": r2, "degree": d}

def multiple_regression(X, y):
    """exact multiple linear least-squares over ℚ (with intercept): y≈b0+Σ b_j x_j."""
    rows = [[Q(1)] + [Q(str(v)) for v in row] for row in X]; ys = [Q(str(v)) for v in y]
    m = len(rows[0]); n = len(rows)
    XtX = [[sum(rows[k][i] * rows[k][j] for k in range(n)) for j in range(m)] for i in range(m)]
    Xty = [sum(rows[k][i] * ys[k] for k in range(n)) for i in range(m)]
    b = _solve_Q(XtX, Xty)
    return {"coeffs": b, "intercept": b[0], "slopes": b[1:]}


# ---------------- Markov chains (exact ℚ) ----------------
def markov_absorbing(P, absorbing):
    """absorbing Markov chain: expected steps to absorption from each transient state, exact ℚ.
    P = row-stochastic transition matrix (rationals ok); `absorbing` = list of absorbing state indices."""
    n = len(P); trans = [i for i in range(n) if i not in set(absorbing)]
    t = len(trans)
    if t == 0: return {"expected_steps": {}, "note": "all states absorbing"}
    # (I - Q) t = 1  where Q is transient-to-transient block
    idx = {s: k for k, s in enumerate(trans)}
    A = [[(Q(1) if i == j else Q(0)) - Q(str(P[trans[i]][trans[j]])) for j in range(t)] for i in range(t)]
    steps = _solve_Q(A, [1] * t)
    return {"expected_steps": {trans[k]: steps[k] for k in range(t)},
            "method": "fundamental matrix N=(I-Q)⁻¹, exact ℚ"}

def stationary(P):
    """stationary distribution π of a row-stochastic chain (πP=π, Σπ=1), exact ℚ."""
    n = len(P)
    # (Pᵀ - I) π = 0 with last row replaced by Σπ=1
    A = [[Q(str(P[j][i])) - (Q(1) if i == j else Q(0)) for j in range(n)] for i in range(n)]
    A[-1] = [Q(1)] * n
    b = [Q(0)] * (n - 1) + [Q(1)]
    pi = _solve_Q(A, b)
    return {"stationary": pi}


# ---------------- Bayesian update (exact renormalization) ----------------
def bayes_update(prior, likelihood):
    """discrete Bayes: posterior ∝ prior·likelihood, exact rational renormalization.
    prior = list of P(H_i); likelihood = list of P(E|H_i)."""
    pri = [Q(str(v)) for v in prior]; lik = [Q(str(v)) for v in likelihood]
    joint = [pri[i] * lik[i] for i in range(len(pri))]
    ev = sum(joint)
    if ev == 0: return {"status": "HOLD", "reason": "evidence has zero probability under the prior"}
    return {"posterior": [j / ev for j in joint], "evidence": ev}
