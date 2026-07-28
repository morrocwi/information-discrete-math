"""idm.solve — the finite-discrete SOLVER: one entry point, a registry of finite methods, tier-honest.

`solve(problem)` takes a STRUCTURED problem (translate-first: the caller declares the `kind`, honoring
the rule that a world-language request is translated into the information language before any math is
done) and dispatches to the matching finite method. It always returns a normalized result with the
value, an error bound where one is proven, a `status` (CERTIFIED / HOLD / ok), and a tier — one of
`Th_coqc` (a named theorem in formal/ governs the result; a `coq_theorem` reference is attached),
`exact` (exact, finite, decidable ℤ/ℚ computation — no floating point in the result, but no individual
Coq proof of the implementation), or `finite_diagnostic` (numeric to a declared tolerance). The
`Th_coqc` label is applied only where a proof mapping exists — exact-but-unproven handlers are `exact`,
never inflated. No continuum library call ever produces the answer; an unknown kind or a failure
returns HOLD, never a crash.

    solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
    solve({"kind": "eigenvalues", "matrix": [[2, 0], [0, 3]]})
    solve({"kind": "factorize", "n": 360360})
"""
from fractions import Fraction
from . import functions as F, certified as C, algebra as A, readouts as R, exact as X, analysis as AN, discrete as D, integrate as INT, diffeq as DEQ, series as SER, special as SP, transforms as TR, optimize as OPT, symbolic as SYM, combopt as CO, interval as IVL, stats as ST, geometry as GEO, crypto as CY, hilbert as HB, hilbert_open as HBO

try:
    import mpmath as mp
    _HAVE = True
except Exception:  # pragma: no cover
    _HAVE = False

# One canonical working precision for the whole solver. Every kind is dispatched under
# ``mp.workdps(_CANON_DPS)`` so a numeric readout depends ONLY on its own method, never on the
# ambient global mpmath precision a sibling module's import or a prior call happened to leave.
# Without this the mpmath global (mp.mp.dps) is shared process-wide state that different modules set
# to different values, making dps-sensitive readouts (e.g. E1) order-dependent across a test suite.
_CANON_DPS = 40

_REG = {}
def kind(name, tier="finite_diagnostic"):
    def deco(fn): _REG[name] = (fn, tier); return fn
    return deco


# ---------------- value normalization ----------------
def _norm(x):
    if x is None or isinstance(x, (bool, int, str)):
        return x
    if isinstance(x, Fraction):
        return {"exact": f"{x.numerator}/{x.denominator}", "float": float(x)}
    if isinstance(x, (list, tuple)):
        return [_norm(v) for v in x]
    if isinstance(x, dict):
        return {k: _norm(v) for k, v in x.items()}
    if _HAVE and isinstance(x, mp.mpf):
        return {"digits": mp.nstr(x, 30), "float": float(x)}
    if _HAVE and isinstance(x, mp.mpc):
        return {"re": _norm(x.real), "im": _norm(x.imag)}
    if isinstance(x, complex):
        return {"re": x.real, "im": x.imag}
    if isinstance(x, float):
        return x
    return str(x)

def _val(x):
    return mp.mpf(str(x)) if _HAVE else float(x)
def _fn(expr):
    return expr if callable(expr) else (lambda x: F.evaluate(str(expr), x=x))
def _fn2(expr, v1="x", v2="y"):
    if callable(expr): return expr
    return lambda a, b: F.evaluate(str(expr), **{v1: a, v2: b})
def _seq(expr):
    return expr if callable(expr) else (lambda n: F.evaluate(str(expr), n=n))
def _ok(kindname, value, method, **extra):
    d = {"kind": kindname, "status": "ok", "value": _norm(value), "method": method}; d.update(extra); return d
def _readout(kindname, r, method):
    return {"kind": kindname, "status": r.status, "value": _norm(r.q), "bound": _norm(r.bound),
            "method": method, "reason": r.reason}



# ---- hoisted shared helpers (used across domains) ----
def _eps(p, d="1e-9"): return (mp.mpf(str(p["eps"])) if _HAVE else float(p["eps"])) if "eps" in p else (mp.mpf(d) if _HAVE else float(d))
def _pathfn(name):
    return {"shortest_path": A.shortest_path, "critical_path": A.critical_path, "widest_path": A.widest_path,
            "minimax_path": A.minimax_path, "reachability": A.reachability, "path_count": A.path_count}[name]
def _make_path(name):
    @kind(name, "Th_coqc")
    def _h(p, _n=name):
        D = _pathfn(_n)(p["matrix"]); s, t = p.get("source"), p.get("target")
        ans = D if s is None or t is None else D[s][t]
        return {"kind": _n, "status": "ok", "value": _norm(ans) if isinstance(ans, Fraction) else ans,
                "all_pairs": (_norm(D) if s is None else None),
                "method": f"generalized Floyd–Warshall over the {_n.replace('_path','')} semiring (IDM_Tropical)"}
    return _h
def _expr_fn(s, *names):
    return (lambda *vals: F.evaluate(str(s), **dict(zip(names, vals))))
def _spec(name, fn, *argnames):
    @kind(name)
    def _h(p, _fn=fn, _an=argnames):
        return _ok(name, _fn(*[_val(p[a]) if a not in ("n",) else int(p[a]) for a in _an]), f"finite series/recurrence — {name}")
    return _h
_CNS = {"exp": mp.exp, "log": mp.log, "ln": mp.log, "sin": mp.sin, "cos": mp.cos, "sqrt": mp.sqrt,
        "pi": mp.pi, "e": mp.e, "abs": abs, "j": mp.mpc(0, 1)} if _HAVE else {}
def _cfn(expr, var):
    return expr if callable(expr) else (lambda v: eval(compile(str(expr), "<c>", "eval"), {"__builtins__": {}}, {**_CNS, var: v}))
def _fnv(expr, var):
    return expr if callable(expr) else (lambda v: F.evaluate(str(expr), **{var: v}))
def _mfn(expr, vs):
    return (lambda x: F.evaluate(str(expr), **dict(zip(vs, x))))
def _hb(name, fn, *argnames, tier="exact"):
    @kind(name, tier)
    def _h(p, _fn=fn, _an=argnames):
        r = _fn(*[p[a] for a in _an])
        if isinstance(r, dict) and r.get("status") in ("HOLD", "+R_OPEN"):
            return {"kind": name, "status": r["status"], **{k: v for k, v in r.items() if k != "status"},
                    "tier": r.get("tier", "finite_diagnostic")}
        out = {"kind": name, "status": "ok", "value": r["value"], "method": r["method"]}
        if "tier" in r: out["tier"] = r["tier"]                 # per-instance tier wins over the registry default
        if "error_bound" in r: out["error_bound"] = r["error_bound"]
        return out
    return _h
def _hbo(name, fn, *argnames):
    @kind(name, "+ℝ-Open")
    def _h(p, _fn=fn, _an=argnames):
        r = _fn(*[p[a] for a in _an])
        return {"kind": name, **r}
    return _h
def _seq0(expr):
    return expr if callable(expr) else (lambda n: F.evaluate(str(expr), n=n))

__all__ = ['A', 'AN', 'C', 'CO', 'CY', 'D', 'DEQ', 'F', 'Fraction', 'GEO', 'HB', 'HBO', 'INT', 'IVL', 'OPT', 'R', 'SER', 'SP', 'ST', 'SYM', 'TR', 'X', '_CANON_DPS', '_CNS', '_HAVE', '_REG', '_cfn', '_eps', '_expr_fn', '_fn', '_fn2', '_fnv', '_hb', '_hbo', '_make_path', '_mfn', '_norm', '_ok', '_pathfn', '_readout', '_seq', '_seq0', '_spec', '_val', 'kind', 'mp']
