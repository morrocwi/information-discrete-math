"""idm.positivity — global nonnegativity of a multivariate polynomial, with an EXACT certificate.

Decides the universal statement

    ∀ x ∈ ℝⁿ,  P(x₁,…,xₙ) ≥ 0

for a polynomial with rational coefficients, and returns a *checkable* certificate rather than a
sampled minimum. The method is the **circuit / weighted-AM–GM (SONC)** certificate of Iliman–de Wolff:
for a *circuit* polynomial — positive coefficients on the vertices of a simplex of even lattice points,
plus one interior term — nonnegativity is decided EXACTLY by comparing the interior term's magnitude to
the **circuit number**

    Θ = ∏ (cᵢ / λᵢ)^{λᵢ},      where  β = Σ λᵢ αᵢ,  Σ λᵢ = 1,  λᵢ > 0.

The bound |d| ≤ Θ is both *necessary and sufficient* for a circuit, so the three verdicts are honest:

* ``CERTIFIED`` — |d| ≤ Θ, proven by an exact rational identity (AM–GM);
* ``REFUTED``  — |d| > Θ, so a real point makes P negative (a rational witness is attached when found);
* ``HOLD``     — the polynomial is not a single supported circuit (needs a full SONC decomposition,
  which this readout does not yet perform).

Everything is exact ℚ arithmetic. Θ is generally irrational, so the comparison |d| ≤ Θ is decided
without ever forming Θ as a float: raise both sides to the power N = lcm(denominators of λ), which makes
every exponent Nλᵢ an integer and both sides exact rationals — `|d|^N ≤ Θ^N` is an exact ℚ comparison.
"""

from __future__ import annotations

import ast
from fractions import Fraction as Q
from itertools import product
from math import gcd


# --------------------------------------------------------------- exact monomial extraction
def monomials(expr: str, variables: list[str]) -> dict[tuple[int, ...], Q]:
    """Parse ``expr`` into an exact ``{exponent_tuple: Fraction}`` monomial map.

    Supports +, -, *, / by a constant, and ** by a nonnegative integer. Every constant becomes an
    exact ``Fraction`` — no float ever enters the polynomial (readout-first).
    """

    idx = {v: i for i, v in enumerate(variables)}
    n = len(variables)
    zero_key = tuple([0] * n)
    tree = ast.parse(expr.replace("^", "**"), mode="eval").body

    def const(c) -> dict:
        # Parse a decimal literal by its written value (0.1 → 1/10), never the binary
        # float artifact — keeps the polynomial an exact rational readout, no float.
        return {zero_key: Q(str(c)) if isinstance(c, float) else Q(c)}

    def add(a: dict, b: dict) -> dict:
        r = dict(a)
        for k, v in b.items():
            r[k] = r.get(k, Q(0)) + v
        return r

    def neg(a: dict) -> dict:
        return {k: -v for k, v in a.items()}

    def mul(a: dict, b: dict) -> dict:
        r: dict = {}
        for ka, va in a.items():
            for kb, vb in b.items():
                k = tuple(x + y for x, y in zip(ka, kb))
                r[k] = r.get(k, Q(0)) + va * vb
        return r

    def powp(a: dict, e: int) -> dict:
        r = {zero_key: Q(1)}
        for _ in range(e):
            r = mul(r, a)
        return r

    def is_const(a: dict) -> bool:
        return set(a) <= {zero_key}

    def go(node):
        if isinstance(node, ast.BinOp):
            left = go(node.left)
            if isinstance(node.op, ast.Add):
                return add(left, go(node.right))
            if isinstance(node.op, ast.Sub):
                return add(left, neg(go(node.right)))
            if isinstance(node.op, ast.Mult):
                return mul(left, go(node.right))
            if isinstance(node.op, ast.Div):
                right = go(node.right)
                if not is_const(right):
                    raise ValueError("division by a non-constant is not a polynomial")
                return {k: v / right[zero_key] for k, v in left.items()}
            if isinstance(node.op, ast.Pow):
                e = go(node.right)
                if not is_const(e) or e[zero_key].denominator != 1 or e[zero_key] < 0:
                    raise ValueError("exponent must be a nonnegative integer")
                return powp(left, int(e[zero_key]))
            raise ValueError(f"unsupported operator {type(node.op).__name__}")
        if isinstance(node, ast.UnaryOp):
            v = go(node.operand)
            return neg(v) if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.Name):
            if node.id not in idx:
                raise ValueError(f"unknown variable {node.id!r}")
            k = [0] * n
            k[idx[node.id]] = 1
            return {tuple(k): Q(1)}
        if isinstance(node, ast.Constant):
            return const(node.value)
        if isinstance(node, ast.Num):  # pragma: no cover - Python < 3.8
            return const(node.n)
        raise ValueError(f"unsupported syntax node {type(node).__name__}")

    poly = go(tree)
    return {k: v for k, v in poly.items() if v != 0}


def evaluate(mons: dict[tuple[int, ...], Q], point: tuple[Q, ...]) -> Q:
    """Exact value of the polynomial at a rational point."""

    total = Q(0)
    for exps, coeff in mons.items():
        term = coeff
        for xj, e in zip(point, exps):
            term *= xj**e
        total += term
    return total


# --------------------------------------------------------------- exact linear algebra
def _solve_square(matrix: list[list[Q]], rhs: list[Q]):
    """Solve an exact square ℚ system; return the solution vector or ``None`` if singular."""

    n = len(matrix)
    aug = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv = aug[col][col]
        aug[col] = [x / piv for x in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [aug[r][j] - factor * aug[col][j] for j in range(n + 1)]
    return [aug[i][n] for i in range(n)]


def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def _exact_root(value: Q, n: int):
    """Return the exact ℚ n-th root of a nonnegative ``value`` if it is rational, else ``None``."""

    def introot(a: int) -> int | None:
        if a < 0:
            return None
        if a == 0:
            return 0
        r = round(a ** (1.0 / n))
        for cand in (r - 1, r, r + 1, r + 2):
            if cand >= 0 and cand**n == a:
                return cand
        return None

    num = introot(value.numerator)
    den = introot(value.denominator)
    if num is None or den is None:
        return None
    return Q(num, den)


# --------------------------------------------------------------- the certificate
_WITNESS_GRID = (Q(1), Q(-1), Q(2), Q(-2), Q(1, 2), Q(-1, 2), Q(3, 2), Q(-3, 2))


def _find_witness(mons, n):
    """Search a small rational grid for an exact point where the polynomial is negative."""

    for point in product(_WITNESS_GRID, repeat=n):
        if evaluate(mons, point) < 0:
            return point
    return None


def _rational_zeros(mons, n):
    """Report rational grid points (from {-1,1}) where the polynomial is exactly zero."""

    zeros = []
    for point in product((Q(1), Q(-1)), repeat=n):
        if evaluate(mons, point) == 0:
            zeros.append(point)
    return zeros


def positivity_certificate(expr: str, variables: list[str], domain: str = "R") -> dict:
    """Decide ∀x∈ℝⁿ P(x)≥0 and return a certificate dict (status/tier/value/method/…)."""

    if domain not in ("R", "ℝ", "real", "reals"):
        return {"status": "HOLD", "tier": "exact",
                "reason": f"only the real domain is supported (got {domain!r})"}
    try:
        mons = monomials(expr, variables)
    except ValueError as exc:
        return {"status": "HOLD", "tier": "exact", "reason": f"parse: {exc}"}

    n = len(variables)
    if not mons:
        return {"status": "CERTIFIED", "tier": "exact", "value": True,
                "method": "zero polynomial", "certificate": {"note": "P ≡ 0"}}

    def all_even(exps):
        return all(e % 2 == 0 for e in exps)

    # A term is trivially safe (always ≥ 0) iff it has a positive coefficient on an all-even exponent.
    problem_terms = [(k, c) for k, c in mons.items() if not (c > 0 and all_even(k))]

    if not problem_terms:
        return {"status": "CERTIFIED", "tier": "exact", "value": True,
                "method": "sum of positive even monomials (each term ≥ 0)",
                "certificate": {"note": "every term has a positive coefficient on an even exponent"}}

    outer = [(k, c) for k, c in mons.items() if c > 0 and all_even(k)]

    if len(problem_terms) != 1 or len(outer) != n + 1:
        return {"status": "HOLD", "tier": "exact",
                "reason": ("outside the supported single-circuit form: need exactly one interior/"
                           "negative term and exactly n+1 positive even-exponent outer terms forming a "
                           f"simplex (got {len(problem_terms)} interior term(s), {len(outer)} outer "
                           "term(s) for n=%d); a full SONC decomposition is not yet implemented" % n)}

    inner_exp, inner_coeff = problem_terms[0]
    outer_exps = [k for k, _ in outer]
    outer_coeffs = [c for _, c in outer]

    # Barycentric coordinates λ: Σ λᵢ αᵢ = β, Σ λᵢ = 1  (square system, n+1 unknowns).
    mat = [[Q(outer_exps[i][j]) for i in range(n + 1)] for j in range(n)]
    mat.append([Q(1) for _ in range(n + 1)])
    rhs = [Q(inner_exp[j]) for j in range(n)] + [Q(1)]
    lam = _solve_square(mat, rhs)
    if lam is None or any(w <= 0 for w in lam):
        return {"status": "HOLD", "tier": "exact",
                "reason": "interior exponent is not in the strict interior of the outer simplex "
                          "(no positive barycentric weights) — not a circuit"}

    # Circuit number, compared exactly by raising to N = lcm of the weight denominators.
    big_n = 1
    for w in lam:
        big_n = _lcm(big_n, w.denominator)
    theta_pow_n = Q(1)
    for ci, wi in zip(outer_coeffs, lam):
        theta_pow_n *= (ci / wi) ** int(wi * big_n)  # integer exponent → exact ℚ
    d = abs(inner_coeff)
    d_pow_n = d**big_n

    theta = _exact_root(theta_pow_n, big_n)
    inner_is_even = all_even(inner_exp)
    circuit_number = (str(theta) if theta is not None
                      else {"nth_power": str(theta_pow_n), "n": big_n})

    certificate = {
        "certificate": "circuit polynomial / weighted AM-GM (SONC)",
        "outer_exponents": [list(e) for e in outer_exps],
        "outer_coefficients": [str(c) for c in outer_coeffs],
        "inner_exponent": list(inner_exp),
        "inner_coefficient": str(inner_coeff),
        "weights": [f"{w.numerator}/{w.denominator}" for w in lam],
        "circuit_number": circuit_number,
        "comparison": {"abs_inner_coeff_pow_n": str(d_pow_n),
                       "circuit_number_pow_n": str(theta_pow_n), "n": big_n},
        "inner_term_even": inner_is_even,
        "necessary_and_sufficient": True,
    }

    if d_pow_n <= theta_pow_n:
        result = {"status": "CERTIFIED", "tier": "exact", "value": True,
                  "method": "circuit polynomial / weighted AM-GM", "certificate": certificate}
        if d_pow_n == theta_pow_n:  # boundary: equality attained → real zeros exist
            zeros = _rational_zeros(mons, n)
            if zeros:
                result["zeros"] = [{"point": [str(v) for v in pt]} for pt in zeros]
            result["certificate"]["boundary_equality"] = True
        return result

    # d > Θ  ⇒  not globally nonnegative (circuit bound is tight).
    witness = _find_witness(mons, n)
    refuted = {"status": "REFUTED", "tier": "exact", "value": False,
               "claimed": "globally nonnegative",
               "method": "circuit bound exceeded (|d| > Θ); the circuit condition is necessary",
               "certificate": certificate}
    if witness is not None:
        refuted["witness"] = [str(v) for v in witness]
        refuted["witness_value"] = str(evaluate(mons, witness))
    else:
        refuted["note"] = ("|d| > Θ proves a negative point exists (circuit tightness); no rational "
                           "witness found on the search grid")
    return refuted


__all__ = ["monomials", "evaluate", "positivity_certificate"]
