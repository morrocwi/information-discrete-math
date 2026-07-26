"""idm.solve — the finite-discrete SOLVER: one entry point, a registry of finite methods, tier-honest.

`solve(problem)` takes a STRUCTURED problem (translate-first: the caller declares the `kind`, honoring
the rule that a world-language request is translated into the information language before any math is
done) and dispatches to the matching finite method. It always returns a normalized result with the
value, an error bound where one is proven, a `status` (CERTIFIED / HOLD / ok), a tier
(`Th_coqc` / `finite_diagnostic`), and the method used. No continuum library call ever produces the
answer; an unknown kind or a failure returns HOLD, never a crash.

    solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
    solve({"kind": "eigenvalues", "matrix": [[2, 0], [0, 3]]})
    solve({"kind": "factorize", "n": 360360})
"""
from fractions import Fraction
from . import functions as F, certified as C, algebra as A, readouts as R, exact as X, analysis as AN

try:
    import mpmath as mp
    _HAVE = True
except Exception:  # pragma: no cover
    _HAVE = False

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


# ================================================================ constants & functions ============
_CONST = {"pi": F.pi, "e": F.e, "ln2": F.ln2}
@kind("constant")
def _c(p): return _ok("constant", _CONST[p["name"]](), "finite series (Machin/Taylor/atanh)", name=p["name"])
@kind("function")
def _fneval(p):
    fmap = {"exp": F.exp, "log": F.log, "ln": F.log, "sin": F.sin, "cos": F.cos, "erf": F.erf, "gamma": F.gamma, "sqrt": F.sqrt}
    return _ok("function", fmap[p["name"]](_val(p["x"])), f"finite {p['name']}", name=p["name"])
@kind("evaluate")
def _ev(p): return _ok("evaluate", F.evaluate(str(p["expr"]), **{k: _val(v) for k, v in p.get("vars", {}).items()}), "locked finite namespace eval")

# ================================================================ certified computation ============
@kind("geometric_series", "Th_coqc")
def _gs(p): return _readout("geometric_series", C.geom_series(Fraction(str(p["r"])), Fraction(str(p.get("eps", "1/1000000000000")))), "geometric series, exact ℚ error r^N/(1-r) — Th_coqc")
@kind("exp")
def _ex(p): return _readout("exp", C.exp(p["x"], _eps(p)), "finite Taylor tail bound (|x|≤½) — Th_coqc")
@kind("integral")
def _integ(p): return _readout("integral", C.integral(_fn(p["f"]), _val(p["a"]), _val(p["b"]), _eps(p)), "trapezoid refinement stability (refine_stable)")
@kind("certified_limit")
def _cl(p): return _readout("certified_limit", C.richardson(_seq(p["seq"]), _eps(p)), "Richardson with a-posteriori contraction certificate")
def _eps(p, d="1e-9"): return (mp.mpf(str(p["eps"])) if _HAVE else float(p["eps"])) if "eps" in p else (mp.mpf(d) if _HAVE else float(d))

# ================================================================ discrete calculus ================
@kind("derivative")
def _d(p): return _ok("derivative", F.derivative(_fn(p["f"]), _val(p["x"])), "finite central difference D_ε + Richardson")
@kind("limit")
def _lim(p): return _ok("limit", F.limit(_seq(p["seq"])), "Richardson on h=1/n (A8 plateau)")
@kind("ode")
def _ode(p): return _ok("ode", F.ode(_fn2(p["f"]), _val(p["x0"]), _val(p["y0"]), _val(p["xT"])), "finite RK4 (= I_ε of the field)")
@kind("double_integral")
def _di(p): return _ok("double_integral", AN.double_integral(_fn2(p["f"]), _val(p["ax"]), _val(p["bx"]), _val(p["ay"]), _val(p["by"]), int(p.get("N", 200))), "finite 2-D midpoint grid")
@kind("series_sum")
def _ss(p): return _ok("series_sum", AN.series_sum(_seq(p["term"]), int(p.get("N", 2000))), "finite partial sum")
@kind("zeta")
def _z(p): return _ok("zeta", AN.zeta(p["s"]), "ζ: Euler–Maclaurin (s>1) / −B_{n+1}/(n+1) (s≤0)")
@kind("regularized_sum")
def _rs(p): return _ok("regularized_sum", AN.regularized_sum(int(p.get("power", 1))), "smoothed sum Σn^p e^{−εn}, pole removed (ζ(−p))")
@kind("root_find")
def _rf(p): return _ok("root_find", AN.root_find(_fn(p["f"]), p.get("a"), p.get("b"), p.get("x0")), "bisection / finite Newton")
@kind("minimize")
def _mn(p):
    x, fx = AN.minimize_1d(_fn(p["f"]), _val(p["a"]), _val(p["b"])); return _ok("minimize", {"argmin": x, "min": fx}, "golden-section search")
@kind("interpolate")
def _ip(p): return _ok("interpolate", AN.interpolate(p["points"], p["x"]), "Lagrange interpolation (exact ℚ when rational)")

# ================================================================ number theory ====================
@kind("gcd", "Th_coqc")
def _gcd(p): return _ok("gcd", __import__("math").gcd(int(p["a"]), int(p["b"])), "Euclid")
@kind("lcm", "Th_coqc")
def _lcm(p): return _ok("lcm", X.lcm(int(p["a"]), int(p["b"])), "a·b/gcd")
@kind("factorial", "Th_coqc")
def _fac(p): return _ok("factorial", X.factorial(int(p["n"])), "finite product")
@kind("binomial", "Th_coqc")
def _bin(p): return _ok("binomial", X.binomial(int(p["n"]), int(p["k"])), "finite product")
@kind("is_prime", "Th_coqc")
def _isp(p): return _ok("is_prime", X.is_prime(int(p["n"])), "deterministic Miller–Rabin")
@kind("factorize", "Th_coqc")
def _fz(p): return _ok("factorize", {str(k): v for k, v in X.factorize(int(p["n"])).items()}, "trial division + Pollard ρ")
@kind("divisors", "Th_coqc")
def _dv(p): return _ok("divisors", X.divisors(int(p["n"])), "from factorization")
@kind("totient", "Th_coqc")
def _tot(p): return _ok("totient", X.totient(int(p["n"])), "Euler φ from factorization")
@kind("primes", "Th_coqc")
def _pr(p): return _ok("primes", X.primes_up_to(int(p["N"])), "sieve of Eratosthenes")
@kind("modpow", "Th_coqc")
def _mp(p): return _ok("modpow", pow(int(p["base"]), int(p["exp"]), int(p["mod"])), "square-and-multiply")
@kind("mod_inverse", "Th_coqc")
def _mi(p): return _ok("mod_inverse", X.mod_inverse(int(p["a"]), int(p["m"])), "extended Euclid")
@kind("crt", "Th_coqc")
def _crt(p): return _ok("crt", X.crt([int(r) for r in p["residues"]], [int(m) for m in p["moduli"]]), "Chinese remainder")
@kind("fibonacci", "Th_coqc")
def _fib(p): return _ok("fibonacci", X.fibonacci(int(p["n"])), "fast doubling")
@kind("bernoulli", "Th_coqc")
def _ber(p): return _ok("bernoulli", X.bernoulli(int(p["n"])), "finite recurrence ΣC(m+1,k)B_k=0")
@kind("partition", "Th_coqc")
def _par(p): return _ok("partition", X.partition(int(p["n"])), "Euler pentagonal recurrence")
@kind("catalan", "Th_coqc")
def _cat(p): return _ok("catalan", X.catalan(int(p["n"])), "C(2n,n)/(n+1)")
@kind("stirling2", "Th_coqc")
def _st(p): return _ok("stirling2", X.stirling2(int(p["n"]), int(p["k"])), "recurrence")
@kind("bell", "Th_coqc")
def _bel(p): return _ok("bell", X.bell(int(p["n"])), "Σ Stirling2")
@kind("continued_fraction", "Th_coqc")
def _cf(p): return _ok("continued_fraction", X.continued_fraction(int(p["num"]), int(p.get("den", 1)), int(p.get("terms", 20))), "Euclidean CF expansion")

# ================================================================ exact linear algebra =============
@kind("matrix_multiply", "Th_coqc")
def _mm(p): return _ok("matrix_multiply", X.mat_mul(p["A"], p["B"]), "exact ℚ")
@kind("matrix_determinant", "Th_coqc")
def _det(p): return _ok("matrix_determinant", X.determinant(p["matrix"]), "fraction-free Gaussian elimination")
@kind("matrix_inverse", "Th_coqc")
def _inv(p):
    m = X.inverse(p["matrix"]); return {"kind": "matrix_inverse", "status": "ok" if m else "HOLD", "value": _norm(m), "method": "exact ℚ Gauss–Jordan", **({} if m else {"reason": "singular matrix"})}
@kind("solve_linear", "Th_coqc")
def _sl(p):
    x = X.solve_linear(p["A"], p["b"]); return {"kind": "solve_linear", "status": "ok" if x else "HOLD", "value": _norm(x), "method": "exact ℚ Gauss–Jordan", **({} if x else {"reason": "singular / no unique solution"})}
@kind("char_poly", "Th_coqc")
def _cp(p): return _ok("char_poly", AN.char_poly(p["matrix"]), "Faddeev–LeVerrier (exact ℚ)")
@kind("eigenvalues")
def _eig(p): return _ok("eigenvalues", AN.eigenvalues(p["matrix"]), "exact ℚ char-poly + Durand–Kerner roots")

# ================================================================ polynomials ======================
@kind("poly_eval", "Th_coqc")
def _pe(p): return _ok("poly_eval", X.poly_eval(p["coeffs"], Fraction(str(p["x"]))), "Horner (exact ℚ)")
@kind("rational_roots", "Th_coqc")
def _rr(p): return _ok("rational_roots", X.rational_roots(p["coeffs"]), "rational-root theorem (exact)")
@kind("poly_roots")
def _prt(p): return _ok("poly_roots", AN.poly_roots(p["coeffs"]), "Durand–Kerner (all complex roots)")

# ================================================================ optimization / paths =============
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
for _pn in ("shortest_path", "critical_path", "widest_path", "minimax_path", "reachability", "path_count"):
    _make_path(_pn)

# ================================================================ readouts ==========================
@kind("readouts")
def _ro(p):
    data = p["data"]; only = p.get("only"); board = {}
    for name, fn in R.READOUTS.items():
        if only and name not in only: continue
        try: board[name] = _norm(fn(data))
        except Exception as ex: board[name] = {"status": "n/a", "reason": f"{type(ex).__name__}: outside this readout's domain"}
    return {"kind": "readouts", "status": "ok", "value": board, "method": "finite retained aggregations (I_ε with chosen combine rule)"}


# ================================================================ dispatch ==========================
def solve(problem):
    if not isinstance(problem, dict) or "kind" not in problem:
        return {"status": "HOLD", "reason": "problem must be a dict with a 'kind' field"}
    k = problem["kind"]
    if k not in _REG:
        return {"kind": k, "status": "HOLD", "reason": f"unknown problem kind '{k}'",
                "known_kinds": sorted(_REG)}
    fn, tier = _REG[k]
    try:
        res = fn(problem)
    except KeyError as ex:
        return {"kind": k, "status": "HOLD", "reason": f"missing required field {ex}"}
    except Exception as ex:
        return {"kind": k, "status": "HOLD", "reason": f"{type(ex).__name__}: {ex}"}
    res.setdefault("tier", tier)
    return res


def kinds():
    """the catalogue of supported problem kinds."""
    return sorted(_REG)
