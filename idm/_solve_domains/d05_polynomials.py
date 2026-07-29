# polynomials
from idm._solve_core import *  # noqa: F401,F403
from idm.kernel.poly.algebraic import AlgReal, AlgebraicHOLD

@kind("poly_eval", "Th_coqc")
def _pe(p): return _ok("poly_eval", X.poly_eval(p["coeffs"], Fraction(str(p["x"]))), "Horner (exact ℚ)")
@kind("rational_roots", "Th_coqc")
def _rr(p): return _ok("rational_roots", X.rational_roots(p["coeffs"]), "rational-root theorem (exact)")
@kind("poly_roots")
def _prt(p): return _ok("poly_roots", AN.poly_roots(p["coeffs"]), "Durand–Kerner (all complex roots)")


def _alg_out(kindname, ar, method):
    """Serialize an exact real AlgReal: its minimal polynomial, isolating rational interval, a disclosed
    decimal readout, whether it is rational, and the substitute-back certificate."""
    return _ok(kindname,
               {"min_poly": [str(c) for c in ar.min_poly_coeffs()],
                "isolating_interval": [str(ar.lo), str(ar.hi)],
                "approx": float(ar.to_float(20)),
                "is_rational": ar.is_rational,
                "rational_value": (str(ar.as_rational()) if ar.is_rational else None),
                "verified": ar.verify()},
               method, tier="exact")

@kind("real_root", "exact")
def _real_root(p):
    """The k-th real root (0-indexed ascending) of a ℚ-polynomial, as an EXACT algebraic number."""
    try:
        ar = AlgReal.rootof(p["coeffs"], int(p.get("index", 0)))
    except AlgebraicHOLD as ex:
        return {"kind": "real_root", "status": "HOLD", "reason": str(ex)}
    return _alg_out("real_root", ar, "exact real algebraic root (Sturm isolation over ℚ)")

@kind("algebraic_arith", "exact")
def _alg_arith(p):
    """Exact arithmetic (add/sub/mul/div) on two real algebraic numbers, each given as a ℚ-polynomial +
    real-root index. Returns the result's minimal polynomial + isolating interval, verified by
    substitute-back. HOLDs on division by zero or an out-of-range root."""
    try:
        a = AlgReal.rootof(p["a"]["coeffs"], int(p["a"].get("index", 0)))
        b = AlgReal.rootof(p["b"]["coeffs"], int(p["b"].get("index", 0)))
        op = p["op"]
        r = {"add": lambda: a + b, "sub": lambda: a - b,
             "mul": lambda: a * b, "div": lambda: a / b}[op]()
    except AlgebraicHOLD as ex:
        return {"kind": "algebraic_arith", "status": "HOLD", "reason": str(ex)}
    except KeyError as ex:
        return {"kind": "algebraic_arith", "status": "HOLD", "reason": f"missing/invalid field {ex}"}
    return _alg_out("algebraic_arith", r, f"exact algebraic {op} (min-poly via ℚ(α,β) dependency)")
