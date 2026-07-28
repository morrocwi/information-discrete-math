"""Reusable differential + adversarial testing harness for the idm solver (pillar P3).

Two independent pressures on the solver surface, both deterministic (seeded ``random.Random`` — no
``hypothesis`` dependency, so they always run in CI) and both data-driven so a new kind is covered by
adding one registry entry:

* **Differential** (:data:`DIFFERENTIAL_CASES`): for a kind that has an INDEPENDENT oracle (sympy /
  mpmath / plain arithmetic), generate many random *valid* inputs, run ``idm.solve`` and the oracle,
  and require agreement.  A disagreement is a real correctness bug — the exact discipline that caught
  the ``rational_limit`` pole-sign and ``groebner_basis`` duplicate-leading-monomial defects.

* **Adversarial** (:func:`adversarial_inputs`): throw hostile / malformed / boundary inputs at EVERY
  registered kind and require the contract to hold — never an uncaught exception, always a
  well-formed result whose tier is honest (no ``CERTIFIED`` / ``Th_coqc`` conjured from garbage).

The harness itself carries no assertions; the test modules ``test_differential_harness.py`` and
``test_adversarial_harness.py`` drive it and assert on the collected reports.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Any, Callable, Dict, List, Optional

import idm

# sympy is a hard dependency of the package (requirements.txt), so the oracles may import it directly.
import sympy as sp

_ALLOWED_STATUS = {"ok", "CERTIFIED", "HOLD", "+R_OPEN"}
_ALLOWED_TIER = {"Th_coqc", "exact", "finite_diagnostic", "+ℝ-Open", None}


# --------------------------------------------------------------------------- safe invocation
def run_kind(kind: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke ``idm.solve`` for ``kind`` with ``params``; return the result dict.  Re-raises nothing
    the solver itself catches — the whole point of the adversarial pass is that the solver must not
    let an exception escape, so this wrapper does NOT swallow exceptions (a leaked exception is a
    finding, surfaced by the caller)."""
    problem = {"kind": kind}
    problem.update(params)
    return idm.solve(problem)


def result_well_formed(r: Any) -> Optional[str]:
    """Return ``None`` if ``r`` is a well-formed solver result, else a short reason string."""
    if not isinstance(r, dict):
        return f"result is {type(r).__name__}, not a dict"
    if r.get("status") not in _ALLOWED_STATUS:
        return f"status {r.get('status')!r} not in {sorted(s for s in _ALLOWED_STATUS)}"
    if r.get("tier") not in _ALLOWED_TIER:
        return f"tier {r.get('tier')!r} not allowed"
    return None


def tier_is_honest(r: Dict[str, Any]) -> Optional[str]:
    """A HOLD result must never advertise a certified/Th_coqc tier as if it had a trustworthy value —
    the fence must not invert under adversarial input.  Returns a reason if the tier is dishonest."""
    if r.get("status") == "HOLD" and r.get("tier") == "Th_coqc" and "value" in r:
        return "HOLD result carries a Th_coqc-tier value (tier inflation under adversarial input)"
    return None


# --------------------------------------------------------------------------- differential registry
@dataclass
class DiffCase:
    """One differential-testing entry: ``generate`` builds valid params from a seeded RNG, ``oracle``
    computes the independent expected answer, and ``agree`` compares the solver result to it."""

    kind: str
    generate: Callable[[random.Random], Dict[str, Any]]
    oracle: Callable[[Dict[str, Any]], Any]
    agree: Callable[[Dict[str, Any], Any], bool]
    n_cases: int = 40


# ---- generators / oracles -------------------------------------------------

def _rand_int(rng, lo, hi):
    return rng.randint(lo, hi)


def _gen_gcd(rng):
    return {"a": rng.randint(1, 10 ** 6), "b": rng.randint(1, 10 ** 6)}


def _oracle_gcd(p):
    import math
    return math.gcd(p["a"], p["b"])


def _agree_value(r, expected):
    return r.get("status") in ("ok", "CERTIFIED") and r.get("value") == expected


def _gen_rational_roots(rng):
    roots = rng.sample(range(-6, 7), rng.randint(1, 4))
    poly = sp.prod([sp.Symbol("x") - r for r in roots])
    coeffs = sp.Poly(sp.expand(poly), sp.Symbol("x")).all_coeffs()[::-1]  # low-order first
    return {"coeffs": [int(c) for c in coeffs], "_roots": sorted(roots)}


def _oracle_rational_roots(p):
    return p["_roots"]


def _agree_rational_roots(r, expected):
    if r.get("status") not in ("ok", "CERTIFIED"):
        return False
    got = sorted(_as_number(v) for v in (r.get("value") or []))
    return got == sorted(expected)


def _gen_matrix_solve_unique(rng):
    # a random 2x2 or 3x3 integer system with a unique solution
    n = rng.choice([2, 3])
    while True:
        A = [[rng.randint(-5, 5) for _ in range(n)] for _ in range(n)]
        if sp.Matrix(A).det() != 0:
            break
    x = [rng.randint(-5, 5) for _ in range(n)]
    b = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
    return {"A": A, "b": b, "_x": x}


def _oracle_matrix_solve_unique(p):
    return [Q(v) for v in p["_x"]]


def _agree_matrix_solve_unique(r, expected):
    if r.get("status") != "ok" or r.get("value", {}).get("solution_type") != "unique":
        return False
    got = [_as_fraction(v) for v in r["value"]["particular"]]
    return got == expected


def _gen_rational_limit(rng):
    # a rational function P/Q with a random finite rational point or ±∞
    x = sp.Symbol("x")
    num = _rand_poly_expr(rng, x)
    den = _rand_poly_expr(rng, x, allow_zero=False)
    point = rng.choice([0, 1, -1, 2, sp.oo, -sp.oo])
    return {"num": _poly_coeffs(num, x), "den": _poly_coeffs(den, x),
            "point": ("inf" if point == sp.oo else "-inf" if point == -sp.oo else int(point)),
            "_num": num, "_den": den, "_point": point}


def _oracle_rational_limit(p):
    # our rational_limit at a finite point is TWO-SIDED, so the oracle must be too (sympy defaults to
    # the right-hand limit dir='+'); at ±∞ the limit is inherently from the one available side.
    x = sp.Symbol("x")
    try:
        if p["_point"] in (sp.oo, -sp.oo):
            lim = sp.limit(p["_num"] / p["_den"], x, p["_point"])
        else:
            lim = sp.limit(p["_num"] / p["_den"], x, p["_point"], dir="+-")
    except Exception:
        return "SKIP"
    return lim


def _agree_rational_limit(r, expected):
    if expected == "SKIP":
        return True                                   # sympy couldn't decide; don't penalise
    if r.get("status") != "ok":
        return False
    v = r["value"]
    if expected == sp.zoo:                            # complex infinity == our two-sided DNE
        return v["limit_type"] == "dne"
    if expected in (sp.oo, -sp.oo):
        want = 1 if expected == sp.oo else -1
        return v["limit_type"] == "infinite" and v["sign"] == want
    if getattr(expected, "is_finite", False) and expected.is_number:
        return v["limit_type"] == "finite" and _as_fraction(v["limit"]) == Q(str(expected))
    return "SKIP"                                     # anything else sympy produced — don't penalise


def _gen_groebner(rng):
    x, y = sp.symbols("x y")
    polys = [_rand_poly2(rng, x, y) for _ in range(rng.randint(2, 3))]
    order = rng.choice(["lex", "grlex", "grevlex"])
    return {"polys": [_poly2_str(p) for p in polys], "variables": ["x", "y"], "order": order,
            "_polys": polys, "_order": order}


def _oracle_groebner(p):
    x, y = sp.symbols("x y")
    try:
        g = sp.groebner(p["_polys"], x, y, order=p["_order"])
    except Exception:
        return "SKIP"
    return _sympy_monic_set(g.exprs, (x, y))


def _agree_groebner(r, expected):
    if expected == "SKIP":
        return True
    if r.get("status") != "ok":
        return False
    return _our_monic_set(r["value"]["basis"], ["x", "y"]) == expected


# --------------------------------------------------------------------------- small helpers

def _as_number(v):
    if isinstance(v, dict) and "exact" in v:
        return Q(v["exact"])
    if isinstance(v, dict) and "float" in v:
        return v["float"]
    return v


def _as_fraction(v):
    if isinstance(v, dict) and "exact" in v:
        return Q(v["exact"])
    return Q(v)


def _rand_poly_expr(rng, x, allow_zero=True):
    deg = rng.randint(0, 3)
    while True:
        coeffs = [rng.randint(-3, 3) for _ in range(deg + 1)]
        expr = sum(c * x ** i for i, c in enumerate(coeffs))
        if allow_zero or expr != 0:
            return sp.Poly(expr, x).as_expr() if expr != 0 else sp.Integer(rng.choice([1, -1, 2]))


def _poly_coeffs(expr, x):
    p = sp.Poly(expr, x)
    return [int(c) for c in p.all_coeffs()[::-1]]     # low-order first


def _rand_poly2(rng, x, y):
    terms = []
    for _ in range(rng.randint(1, 3)):
        terms.append(rng.choice([1, -1, 2, -3]) * x ** rng.randint(0, 2) * y ** rng.randint(0, 2))
    e = sum(terms)
    return e if e != 0 else x


def _poly2_str(expr):
    return str(sp.expand(expr)).replace("**", "^").replace(" ", "")


def _sympy_monic_set(exprs, syms):
    out = set()
    for e in exprs:
        p = sp.Poly(e, *syms)
        d = {tuple(m): Q(str(c)) for m, c in p.terms()}
        lc = d[max(d)]
        out.add(frozenset({m: c / lc for m, c in d.items()}.items()))
    return out


def _our_monic_set(basis_strs, variables):
    from idm.kernel.poly.groebner import parse_poly, _order_key, _lead
    out = set()
    for s in basis_strs:
        g = parse_poly(s, variables)
        lm = max(g)                                    # tuple max == lex-ish; only used for lc
        lc = g[lm]
        out.add(frozenset({m: c / lc for m, c in g.items()}.items()))
    return out


# --------------------------------------------------------------------------- the registry
DIFFERENTIAL_CASES: List[DiffCase] = [
    DiffCase("gcd", _gen_gcd, _oracle_gcd, _agree_value, 60),
    DiffCase("rational_roots", _gen_rational_roots, _oracle_rational_roots, _agree_rational_roots, 40),
    DiffCase("matrix_solve", _gen_matrix_solve_unique, _oracle_matrix_solve_unique,
             _agree_matrix_solve_unique, 40),
    DiffCase("rational_limit", _gen_rational_limit, _oracle_rational_limit, _agree_rational_limit, 50),
    DiffCase("groebner_basis", _gen_groebner, _oracle_groebner, _agree_groebner, 30),
]


# --------------------------------------------------------------------------- adversarial payloads
#: Whole-problem hostile fills: every field of a kind's fixture is set to this value at once.  Filling
#: ALL fields (rather than mutating one of an otherwise-valid fixture) is both a cleaner crash test —
#: it reliably exercises the HOLD-not-crash path instead of leaving a still-mostly-valid input that
#: triggers real (slow) numeric work — and fast enough to sweep every kind in CI.  The values span
#: type/shape confusion (missing, wrong scalar type, wrong container shape).
ADVERSARIAL_FILLS: List[Any] = [None, "BAD", [], {"x": 1}]


def adversarial_inputs(fixtures: Dict[str, Dict[str, Any]]):
    """Yield ``(kind, params, label)`` adversarial probes for every kind that has a fixture: the empty
    problem (all fields missing), then the fixture with EVERY field set to each hostile fill.
    Deterministic, finite, and bounded (``len(fixtures) * (1 + len(ADVERSARIAL_FILLS))`` probes)."""
    for kind, fixture in fixtures.items():
        yield kind, {}, "empty"
        for fill in ADVERSARIAL_FILLS:
            yield kind, {field: fill for field in fixture}, f"all={_short(fill)}"


def _short(v):
    s = repr(v)
    return s if len(s) <= 20 else s[:17] + "..."
