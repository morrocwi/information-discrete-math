"""idm.solve — the finite-discrete SOLVER: one entry point, tier-honest, certified where possible.

`solve(problem)` takes a STRUCTURED problem (translate-first: the caller declares the `kind`, honoring
the framework's rule that a world-language request is translated into the information language before
any math is done) and dispatches to the right finite method. It always returns a normalized result
carrying the value, an error bound where one is proven, a `status` (CERTIFIED / HOLD / ok), and a
tier (`Th_coqc` / `finite_diagnostic`). No continuum library call ever produces the answer.

Example:
    solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
    solve({"kind": "constant", "name": "pi"})
    solve({"kind": "shortest_path", "matrix": W, "source": 0, "target": 4})
"""
from fractions import Fraction
from . import functions as F
from . import certified as C
from . import algebra as A
from . import readouts as R

try:
    import mpmath as mp
    _HAVE = True
except Exception:  # pragma: no cover
    _HAVE = False


def _num(x):
    """JSON-friendly rendering that preserves precision as a string alongside a float."""
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    try:
        if isinstance(x, Fraction):
            return {"exact": f"{x.numerator}/{x.denominator}", "float": float(x)}
        if _HAVE and isinstance(x, mp.mpf):
            return {"digits": mp.nstr(x, 30), "float": float(x)}
        if isinstance(x, (int, float)):
            return x
        return {"digits": mp.nstr(mp.mpf(x), 30), "float": float(x)} if _HAVE else float(x)
    except Exception:
        return str(x)


def _readout(kind, r, method):
    return {"kind": kind, "status": r.status, "tier": "finite_diagnostic",
            "value": _num(r.q), "bound": _num(r.bound), "method": method, "reason": r.reason}


def _eps(problem, default="1e-9"):
    return (mp.mpf(str(problem["eps"])) if _HAVE else float(problem["eps"])) if "eps" in problem \
        else (mp.mpf(default) if _HAVE else float(default))


_CONSTANTS = {"pi": F.pi, "e": F.e, "ln2": F.ln2}


def solve(problem):
    """Dispatch a structured problem to its finite-discrete method. Returns a normalized result dict."""
    if not isinstance(problem, dict) or "kind" not in problem:
        return {"status": "HOLD", "reason": "problem must be a dict with a 'kind' field"}
    k = problem["kind"]

    # ---- constants (finite readouts of the named continuum constants) ----
    if k == "constant":
        name = problem.get("name")
        if name not in _CONSTANTS:
            return {"kind": k, "status": "HOLD", "reason": f"unknown constant '{name}'"}
        v = _CONSTANTS[name]()
        return {"kind": k, "status": "ok", "tier": "finite_diagnostic", "name": name,
                "value": _num(v), "method": "finite series (Machin / Taylor / atanh)"}

    # ---- certified geometric series: limit of Σ r^k = 1/(1-r) ----
    if k == "geometric_series":
        r = C.geom_series(Fraction(str(problem["r"])), Fraction(str(problem.get("eps", "1/1000000000000"))))
        return _readout(k, r, "geometric series, exact ℚ error r^N/(1-r) — Th_coqc")

    # ---- certified finite exponential ----
    if k == "exp":
        r = C.exp(problem["x"], _eps(problem))
        out = _readout(k, r, "finite Taylor tail bound (|x|≤½) — Th_coqc")
        if r.status == C.CERTIFIED:
            out["tier"] = "finite_diagnostic"
        return out

    # ---- integral by finite stability (no reference to a completed ∫f) ----
    if k == "integral":
        f = _fn(problem["f"])
        a, b = _val(problem["a"]), _val(problem["b"])
        r = C.integral(f, a, b, _eps(problem))
        return _readout(k, r, "trapezoid refinement stability (refine_stable) — Th_coqc mechanism")

    # ---- derivative / limit / ode (finite operators; finite_diagnostic) ----
    if k == "derivative":
        v = F.derivative(_fn(problem["f"]), _val(problem["x"]))
        return {"kind": k, "status": "ok", "tier": "finite_diagnostic",
                "value": _num(v), "method": "finite central difference D_ε + Richardson"}
    if k == "limit":
        v = F.limit(_seq(problem["seq"]))
        return {"kind": k, "status": "ok", "tier": "finite_diagnostic",
                "value": _num(v), "method": "Richardson on h=1/n (A8 plateau)"}
    if k == "ode":
        v = F.ode(_fn2(problem["f"]), _val(problem["x0"]), _val(problem["y0"]), _val(problem["xT"]))
        return {"kind": k, "status": "ok", "tier": "finite_diagnostic",
                "value": _num(v), "method": "finite RK4 (= I_ε of the field)"}

    # ---- optimization / path algebra over the tropical semirings ----
    if k in ("shortest_path", "critical_path", "widest_path", "minimax_path", "reachability", "path_count"):
        W = problem["matrix"]
        fn = {"shortest_path": A.shortest_path, "critical_path": A.critical_path,
              "widest_path": A.widest_path, "minimax_path": A.minimax_path,
              "reachability": A.reachability, "path_count": A.path_count}[k]
        D = fn(W)
        s, t = problem.get("source"), problem.get("target")
        answer = D if s is None or t is None else D[s][t]
        return {"kind": k, "status": "ok", "tier": "Th_coqc",
                "value": answer if not isinstance(answer, Fraction) else _num(answer),
                "all_pairs": None if s is not None else D,
                "method": f"generalized Floyd–Warshall over the {k.replace('_path','')} semiring (IDM_Tropical)"}

    # ---- engineering scalar readouts over a finite series ----
    if k == "readouts":
        data = problem["data"]
        only = problem.get("only")            # optional list of readout names to compute
        board = {}
        for name, fn in R.READOUTS.items():
            if only and name not in only:
                continue
            try:                              # a readout outside its domain (e.g. geometric mean of
                board[name] = _num(fn(data))  # non-positive data) is reported n/a, never a crash
            except Exception as ex:
                board[name] = {"status": "n/a", "reason": f"{type(ex).__name__}: outside this readout's domain"}
        return {"kind": k, "status": "ok", "tier": "finite_diagnostic", "value": board,
                "method": "finite retained aggregations (I_ε with chosen combine rule)"}

    return {"kind": k, "status": "HOLD", "reason": f"unknown problem kind '{k}'"}


# ---- helpers: turn declared strings/numbers into finite callables/values ----
def _val(x):
    if _HAVE:
        return mp.mpf(str(x)) if not isinstance(x, (int, float)) or True else x
    return float(x)

def _fn(expr):
    if callable(expr):
        return expr
    return lambda x: F.evaluate(str(expr), x=x)

def _fn2(expr):
    if callable(expr):
        return expr
    return lambda x, y: F.evaluate(str(expr), x=x, y=y)

def _seq(expr):
    if callable(expr):
        return expr
    return lambda n: F.evaluate(str(expr), n=n)
