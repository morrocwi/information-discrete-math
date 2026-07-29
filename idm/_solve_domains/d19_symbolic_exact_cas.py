# symbolic (exact CAS)
from idm._solve_core import *  # noqa: F401,F403

@kind("symbolic_diff", "Th_coqc")
def _sdiff(p): return _ok("symbolic_diff", SYM.tostr(SYM.simplify(SYM.diff(SYM.parse(p["expr"]), p["var"]))), "exact symbolic differentiation")
@kind("simplify", "Th_coqc")
def _ssimp(p): return _ok("simplify", SYM.tostr(SYM.simplify(SYM.parse(p["expr"]))), "constant folding + like-term collection")
@kind("expand", "Th_coqc")
def _sexp(p): return _ok("expand", SYM.tostr(SYM.expand(SYM.parse(p["expr"]))), "distribute products/powers over sums, exact ℚ")
@kind("symbolic_integrate")
def _sint(p):
    try:
        return _ok("symbolic_integrate", SYM.tostr(SYM.simplify(SYM.integrate(SYM.parse(p["expr"]), p["var"]))) + " + C",
                   "polynomial + elementary antiderivative")
    except Exception as ex:
        return {"kind": "symbolic_integrate", "status": "HOLD", "reason": f"{ex}"}
@kind("symbolic_solve")
def _ssol(p):
    r = SYM.solve(SYM.parse(p["expr"]), p["var"])
    return {"kind": "symbolic_solve", "status": r.get("status", "ok"), "value": r,
            "method": "exact linear/quadratic radicals; rational roots for higher degree"}
@kind("symbolic_series", "Th_coqc")
def _sser(p): return _ok("symbolic_series", [SYM.tostr(c) for c in SYM.taylor(SYM.parse(p["expr"]), p["var"], p.get("x0", 0), int(p.get("n", 6)))],
                         "exact symbolic Taylor by repeated differentiation")

@kind("integrate_rational", "exact")
def _irat(p):
    """EXACT symbolic integral of a rational function P(x)/Q(x) (coeffs low→high) — partial fractions over
    ℚ → logs + arctans + a rational part. HOLDs on a degree-≥3 irreducible denominator
    (needs algebraic-function/Risch, a later increment)."""
    from idm.kernel.poly.rational_integration import integrate_rational, RationalIntegralHOLD
    try:
        r = integrate_rational(p["num"], p["den"], p.get("var", "x"))
    except (RationalIntegralHOLD, ValueError, KeyError, ZeroDivisionError) as ex:
        return {"kind": "integrate_rational", "status": "HOLD", "reason": str(ex)}
    return _ok("integrate_rational", r, "exact rational-function integration (partial fractions over ℚ)")
