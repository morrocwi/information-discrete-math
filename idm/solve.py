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
from . import functions as F, certified as C, algebra as A, readouts as R, exact as X, analysis as AN, discrete as D, integrate as INT, diffeq as DEQ, series as SER, special as SP, transforms as TR, optimize as OPT, symbolic as SYM, combopt as CO, interval as IVL, stats as ST, geometry as GEO, crypto as CY

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
def _integ(p): return _readout("integral", INT.integrate(_fn(p["f"]), p["a"], p["b"], _eps(p)),
                               "double-exponential DE quadrature (tanh/exp/sinh–sinh), a-posteriori certified")
@kind("improper_integral")
def _iimp(p): return _readout("improper_integral", INT.integrate(_fn(p["f"]), p.get("a", "-inf"), p.get("b", "inf"), _eps(p)),
                              "exp–sinh / sinh–sinh DE (semi/doubly-infinite), a-posteriori certified")
@kind("singular_integral")
def _ising(p): return _readout("singular_integral", INT.integrate(_fn(p["f"]), p["a"], p["b"], _eps(p)),
                               "tanh–sinh DE — clusters nodes so fast it absorbs endpoint singularities")
@kind("oscillatory_integral")
def _iosc(p): return _readout("oscillatory_integral", INT.integrate(_fn(p["f"]), p["a"], p["b"], _eps(p, "1e-10"), max_level=13),
                              "high-level DE quadrature")
@kind("gauss_quadrature")
def _igq(p): return _ok("gauss_quadrature", INT.gauss_legendre(_fn(p["f"]), _val(p["a"]), _val(p["b"]), int(p.get("n", 64))),
                        f"{p.get('n', 64)}-point Gauss–Legendre (finite nodes)")
@kind("residue_integral")
def _ires(p):
    r = INT.residue_sum(p["num"], p["den"])
    return _ok("residue_integral", r, "2πi·Σ residues in the upper half-plane (∫_{-∞}^∞ of a rational function)")
@kind("multidim_integral")
def _ind(p):
    names = p.get("vars") or [f"x{i}" for i in range(len(p["bounds"]))]
    f = lambda *pt: F.evaluate(str(p["f"]), **dict(zip(names, pt)))
    return _ok("multidim_integral", INT.integrate_nd(f, [[_val(a), _val(b)] for a, b in p["bounds"]], int(p.get("n", 40))),
               "nested Gauss–Legendre over the box (RCP for coupled high-D)")
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
def _isp(p):
    n = int(p["n"]); val = X.is_prime(n)
    # a composite verdict is a proof (there is a witness); a prime verdict is a proof only below the
    # deterministic Miller–Rabin bound — above it, "prime" is probabilistic, so tier down honestly.
    certified = (val is False) or (n < X.MR_DET_BOUND)
    tier = "Th_coqc" if certified else "finite_diagnostic"
    method = ("deterministic Miller–Rabin (first 13 primes, n < %d)" % X.MR_DET_BOUND) if certified else \
             "Miller–Rabin strong probable prime (n ≥ %d — beyond the deterministic bound, NOT proven)" % X.MR_DET_BOUND
    return {"kind": "is_prime", "status": "ok", "value": val, "tier": tier, "method": method}
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


# ================================================================ number theory (extended) =========
@kind("num_divisors", "Th_coqc")
def _nd(p): return _ok("num_divisors", X.num_divisors(int(p["n"])), "∏(e+1) from factorization")
@kind("sigma", "Th_coqc")
def _sig(p): return _ok("sigma", X.sigma(int(p["n"]), int(p.get("k", 1))), "sum of divisors' k-th powers")
@kind("next_prime", "Th_coqc")
def _np(p): return _ok("next_prime", X.next_prime(int(p["n"])), "sieve/Miller–Rabin scan")
@kind("prime_pi", "Th_coqc")
def _ppi(p): return _ok("prime_pi", X.prime_pi(int(p["N"])), "π(N) by sieve")
@kind("integer_sqrt", "Th_coqc")
def _isq(p): return _ok("integer_sqrt", X.integer_sqrt(int(p["n"])), "isqrt")
@kind("is_perfect_square", "Th_coqc")
def _ips(p): return _ok("is_perfect_square", X.is_perfect_square(int(p["n"])), "isqrt check")
@kind("integer_root", "Th_coqc")
def _ir(p): return _ok("integer_root", X.integer_root(int(p["n"]), int(p["k"])), "exact k-th root or null")
@kind("digital_root", "Th_coqc")
def _dr2(p): return _ok("digital_root", X.digital_root(int(p["n"]), int(p.get("base", 10))), "repeated digit sum")
@kind("base_convert", "Th_coqc")
def _bc(p): return _ok("base_convert", X.base_convert(int(p["n"]), int(p["base"])), "positional expansion")
@kind("bezout", "Th_coqc")
def _bz(p): g, x, y = X.bezout(int(p["a"]), int(p["b"])); return _ok("bezout", {"gcd": g, "x": x, "y": y}, "extended Euclid (a·x+b·y=g)")
@kind("legendre_symbol", "Th_coqc")
def _leg(p): return _ok("legendre_symbol", X.legendre_symbol(int(p["a"]), int(p["p"])), "Euler's criterion")
@kind("jacobi_symbol", "Th_coqc")
def _jac(p): return _ok("jacobi_symbol", X.jacobi_symbol(int(p["a"]), int(p["n"])), "quadratic reciprocity")
@kind("discrete_log", "Th_coqc")
def _dl(p): return _ok("discrete_log", X.discrete_log(int(p["g"]), int(p["h"]), int(p["p"])), "baby-step giant-step")
@kind("primitive_root", "Th_coqc")
def _prt2(p): return _ok("primitive_root", X.primitive_root(int(p["p"])), "generator of (ℤ/pℤ)*")
@kind("lucas", "Th_coqc")
def _luc(p): return _ok("lucas", X.lucas(int(p["n"])), "Lucas recurrence")
@kind("derangements", "Th_coqc")
def _der(p): return _ok("derangements", X.derangements(int(p["n"])), "!n recurrence")
@kind("perm_count", "Th_coqc")
def _pc(p): return _ok("perm_count", X.perm_count(int(p["n"]), int(p["k"])), "n!/(n−k)!")
@kind("comb_with_rep", "Th_coqc")
def _cwr(p): return _ok("comb_with_rep", X.comb_with_rep(int(p["n"]), int(p["k"])), "multiset coefficient")
@kind("multinomial", "Th_coqc")
def _mul(p): return _ok("multinomial", X.multinomial([int(x) for x in p["ks"]]), "(Σk)!/∏k!")
@kind("faulhaber", "Th_coqc")
def _fh(p): return _ok("faulhaber", X.faulhaber(int(p["power"]), int(p["N"])), "Σ i^p exact ℤ")

# ================================================================ polynomial algebra ===============
@kind("poly_add", "Th_coqc")
def _pa(p): return _ok("poly_add", X.poly_add(p["a"], p["b"]), "exact ℚ")
@kind("poly_mul", "Th_coqc")
def _pmul(p): return _ok("poly_mul", X.poly_mul(p["a"], p["b"]), "exact ℚ convolution")
@kind("poly_divmod", "Th_coqc")
def _pdm(p): q, r = X.poly_divmod(p["a"], p["b"]); return _ok("poly_divmod", {"quotient": q, "remainder": r}, "exact ℚ long division")
@kind("poly_gcd", "Th_coqc")
def _pg(p): return _ok("poly_gcd", X.poly_gcd(p["a"], p["b"]), "Euclid over ℚ[x]")
@kind("poly_derivative", "Th_coqc")
def _pdv(p): return _ok("poly_derivative", X.poly_derivative(p["coeffs"]), "exact ℚ")
@kind("poly_integral", "Th_coqc")
def _pig(p): return _ok("poly_integral", X.poly_integral(p["coeffs"]), "exact ℚ (constant 0)")
@kind("poly_from_roots", "Th_coqc")
def _pfr(p): return _ok("poly_from_roots", X.poly_from_roots(p["roots"]), "∏(x−rᵢ) exact ℚ")

# ================================================================ matrix (extended) ================
@kind("matrix_transpose", "Th_coqc")
def _mt(p): return _ok("matrix_transpose", X.transpose(p["matrix"]), "exact")
@kind("matrix_trace", "Th_coqc")
def _mtr(p): return _ok("matrix_trace", X.trace(p["matrix"]), "Σ diagonal")
@kind("matrix_add", "Th_coqc")
def _ma(p): return _ok("matrix_add", X.mat_add(p["A"], p["B"]), "exact ℚ")
@kind("matrix_power", "Th_coqc")
def _mpw(p): return _ok("matrix_power", X.mat_power(p["matrix"], int(p["k"])), "exact ℚ binary exponentiation")
@kind("matrix_rank", "Th_coqc")
def _mr(p): return _ok("matrix_rank", X.matrix_rank(p["matrix"]), "rank via RREF over ℚ")
@kind("rref", "Th_coqc")
def _rref(p): M, r = X.rref(p["matrix"]); return _ok("rref", {"rref": M, "rank": r}, "reduced row-echelon over ℚ")

# ================================================================ geometry (exact ℚ + √) ===========
@kind("dot", "Th_coqc")
def _dot(p): return _ok("dot", X.dot(p["u"], p["v"]), "Σ uᵢvᵢ exact ℚ")
@kind("cross", "Th_coqc")
def _cr(p):
    u, v = p["u"], p["v"]; r = X.cross2(u, v) if len(u) == 2 else X.cross3(u, v)
    return _ok("cross", r, "cross product exact ℚ")
@kind("polygon_area", "Th_coqc")
def _par2(p): return _ok("polygon_area", X.polygon_area(p["points"]), "shoelace formula exact ℚ")
@kind("triangle_area", "Th_coqc")
def _ta(p): return _ok("triangle_area", X.triangle_area(p["a"], p["b"], p["c"]), "shoelace exact ℚ")
@kind("vector_norm")
def _vn(p): return _ok("vector_norm", mp.sqrt(float(X.dot(p["v"], p["v"]))) if _HAVE else float(X.dot(p["v"], p["v"])) ** 0.5, "√(Σvᵢ²) (squared part exact ℚ)")
@kind("distance")
def _dist(p):
    pv = [Fraction(str(x)) for x in p["p"]]; qv = [Fraction(str(x)) for x in p["q"]]
    d2 = sum((a - b) ** 2 for a, b in zip(pv, qv))
    return _ok("distance", mp.sqrt(float(d2)) if _HAVE else float(d2) ** 0.5, "√Σ(pᵢ−qᵢ)² (squared part exact ℚ)")

# ================================================================ analysis (extended) ==============
@kind("gradient")
def _grad(p):
    names = p["vars"]; pt = [_val(v) for v in p["point"]]
    f = lambda **kw: F.evaluate(str(p["f"]), **kw)
    return _ok("gradient", AN.gradient(f, pt, names), "finite central differences per variable")
@kind("convolution", "Th_coqc")
def _conv(p): return _ok("convolution", AN.convolution(p["a"], p["b"]), "discrete Σ a[i]b[k−i]")
@kind("arc_length")
def _al(p): return _ok("arc_length", AN.arc_length(_fn(p["f"]), _val(p["a"]), _val(p["b"])), "∫√(1+f'²) finite quadrature")
@kind("fixed_point")
def _fp(p): return _ok("fixed_point", AN.fixed_point(_fn(p["g"]), _val(p["x0"])), "finite iteration x=g(x)")
@kind("summation", "Th_coqc")
def _sm(p):
    terms = [F.evaluate(str(p["term"]), n=n) for n in range(int(p["a"]), int(p["b"]) + 1)]
    tot = terms[0]
    for t in terms[1:]: tot = tot + t
    return _ok("summation", tot, "finite Σ")

# ================================================================ discrete structures ==============
@kind("mst", "Th_coqc")
def _mst(p): return _ok("mst", D.mst(int(p["n"]), p["edges"]), "Kruskal (union–find)")
@kind("connected_components", "Th_coqc")
def _cc(p): return _ok("connected_components", D.connected_components(int(p["n"]), p["edges"]), "union–find")
@kind("topological_sort", "Th_coqc")
def _ts(p):
    o = D.topological_sort(int(p["n"]), p["edges"])
    return {"kind": "topological_sort", "status": "ok" if o is not None else "HOLD", "value": o, "method": "Kahn's algorithm", **({} if o is not None else {"reason": "graph has a cycle"})}
@kind("is_bipartite", "Th_coqc")
def _bip(p): return _ok("is_bipartite", D.is_bipartite(int(p["n"]), p["edges"]), "BFS 2-coloring")
@kind("max_flow", "Th_coqc")
def _mf(p): return _ok("max_flow", D.max_flow(int(p["n"]), p["edges"], int(p["source"]), int(p["sink"])), "Edmonds–Karp")
@kind("set_operation", "Th_coqc")
def _so(p): return _ok("set_operation", D.set_op(p["op"], p["a"], p.get("b")), f"finite set {p['op']}")
@kind("powerset", "Th_coqc")
def _pw(p): return _ok("powerset", D.powerset(p["set"]), "finite enumeration 2^S")
@kind("truth_table", "Th_coqc")
def _tt(p): return _ok("truth_table", D.truth_table(str(p["expr"]), p["vars"]), "finite assignment enumeration")


# ================================================================ differential equations ===========
def _expr_fn(s, *names):
    return (lambda *vals: F.evaluate(str(s), **dict(zip(names, vals))))

@kind("ode_system")
def _osys(p):
    vs = p["vars"]
    fs = [(lambda s: (lambda x, *y: F.evaluate(s, x=x, **dict(zip(vs, y)))))(s) for s in p["f"]]
    y = DEQ.ode_system(fs, _val(p["x0"]), [_val(v) for v in p["y0"]], _val(p["xT"]), int(p.get("N", 2000)))
    return _ok("ode_system", y, "vector RK4 (= I_ε of the field)")

@kind("ode_bvp")
def _bvp(p):
    q = _expr_fn(p.get("q", "0"), "x"); r = _expr_fn(p.get("r", "0"), "x")
    sol = DEQ.ode_bvp(q, r, _val(p["a"]), _val(p["b"]), _val(p["alpha"]), _val(p["beta"]), int(p.get("N", 400)))
    if "at" in p:
        xa = _val(p["at"]); i = min(range(len(sol)), key=lambda k: abs(sol[k][0] - xa))
        return _ok("ode_bvp", sol[i][1], "finite-difference tridiagonal", at=p["at"])
    return _ok("ode_bvp", [v for _, v in sol], "finite-difference tridiagonal")

@kind("pde_heat")
def _heat(p):
    init = _expr_fn(p["init"], "x"); L = _val(p["L"])
    u = DEQ.pde_heat(_val(p.get("alpha", 1)), L, _val(p["T"]), init, tuple(p.get("bc", (0, 0))),
                     int(p.get("Nx", 80)), int(p.get("Nt", 400)))
    if "at" in p:
        i = int(round(float(_val(p["at"]) / L) * (len(u) - 1))); return _ok("pde_heat", u[i], "Crank–Nicolson", at=p["at"])
    return _ok("pde_heat", u, "Crank–Nicolson (2nd order, unconditionally stable)")

@kind("pde_wave")
def _wave(p):
    init = _expr_fn(p["init"], "x"); L = _val(p["L"])
    iv = _expr_fn(p["init_vel"], "x") if "init_vel" in p else None
    u = DEQ.pde_wave(_val(p.get("c", 1)), L, _val(p["T"]), init, iv, tuple(p.get("bc", (0, 0))), int(p.get("Nx", 100)))
    if "at" in p:
        i = int(round(float(_val(p["at"]) / L) * (len(u) - 1))); return _ok("pde_wave", u[i], "explicit leapfrog", at=p["at"])
    return _ok("pde_wave", u, "explicit leapfrog (CFL-stable)")

@kind("pde_poisson")
def _pois(p):
    f = _expr_fn(p.get("f", "0"), "x", "y")
    bc = _expr_fn(p["bc"], "x", "y") if isinstance(p.get("bc"), str) else p.get("bc", 0)
    u = DEQ.pde_poisson(f, p["box"], bc, int(p.get("Nx", 40)), int(p.get("Ny", 40)))
    if "at" in p:
        x0, x1, y0, y1 = [_val(v) for v in p["box"]]; ax, ay = _val(p["at"][0]), _val(p["at"][1])
        i = int(round(float((ax - x0) / (x1 - x0)) * (len(u) - 1)))
        j = int(round(float((ay - y0) / (y1 - y0)) * (len(u[0]) - 1)))
        return _ok("pde_poisson", u[i][j], "Gauss–Seidel", at=p["at"])
    return _ok("pde_poisson", u, "Gauss–Seidel relaxation")

@kind("pde_laplace")
def _lap(p): p = {**p, "f": "0"}; return _pois(p) | {"kind": "pde_laplace"}

@kind("sturm_liouville")
def _sl(p):
    V = _expr_fn(p.get("potential", "0"), "x")
    eig = DEQ.sturm_liouville(V, _val(p["L"]), int(p.get("n_eigs", 5)), int(p.get("N", 300)))
    return _ok("sturm_liouville", eig, "finite-difference + Sturm-sequence bisection")


# ================================================================ limits & series ==================
@kind("taylor_series")
def _tay(p): return _ok("taylor_series", SER.taylor_series(_fn(p["f"]), _val(p.get("x0", 0)), int(p.get("n", 8))),
                        "f^(k)(x0)/k! by centered finite differences + Richardson")
@kind("laurent_series")
def _lau(p):
    d = SER.laurent_series(_fn(p["f"]), _val(p.get("x0", 0)), int(p.get("lo", -3)), int(p.get("hi", 3)))
    return _ok("laurent_series", {str(k): v for k, v in d.items()}, "Cauchy coefficient FFT on a circle (complex-evaluable f)")
@kind("fourier_series")
def _fou(p): return _ok("fourier_series", SER.fourier_series(_fn(p["f"]), _val(p["period"]) if "period" in p else None, int(p.get("n", 8))),
                        "finite DFT of one period")
@kind("pade", "Th_coqc")
def _pade(p): return _ok("pade", SER.pade([Fraction(str(c)) for c in p["coeffs"]], int(p["m"]), int(p["n"])),
                         "Padé [m/n] from Taylor coefficients (exact ℚ)")
@kind("series_accelerate")
def _acc(p): return _ok("series_accelerate", SER.series_sum_accelerated(_seq0(p["term"]), int(p.get("N", 30))), "Wynn ε-algorithm")
@kind("convergence_test")
def _conv(p):
    v = SER.convergence_test(_seq(p["term"]), int(p.get("N", 600)))
    return {"kind": "convergence_test", "status": "ok" if v["verdict"] != "HOLD" else "HOLD", "value": v,
            "method": "nth-term → ratio → Raabe cascade (HOLD when genuinely inconclusive)"}
@kind("limit_oneside")
def _l1(p): return _ok("limit_oneside", SER.limit_oneside(_fn(p["f"]), _val(p["a"]), p.get("side", "+")), "Richardson plateau of f(a±1/n)")
@kind("limit_infinity")
def _linf(p): return _ok("limit_infinity", SER.limit_infinity(_fn(p["f"])), "Richardson on 1/n of f(n)")
@kind("lhopital")
def _lh(p): return _ok("lhopital", SER.lhopital(_fn(p["num"]), _fn(p["den"]), _val(p["a"])), "L'Hôpital via finite derivatives")


# ================================================================ special functions ================
def _spec(name, fn, *argnames):
    @kind(name)
    def _h(p, _fn=fn, _an=argnames):
        return _ok(name, _fn(*[_val(p[a]) if a not in ("n",) else int(p[a]) for a in _an]), f"finite series/recurrence — {name}")
    return _h
_spec("gamma", SP.gamma, "z"); _spec("beta", SP.beta, "a", "b"); _spec("digamma", SP.digamma, "x")
_spec("bessel_J", SP.bessel_J, "n", "x"); _spec("bessel_I", SP.bessel_I, "n", "x")
_spec("legendre_P", SP.legendre_P, "n", "x"); _spec("hermite_H", SP.hermite_H, "n", "x")
_spec("chebyshev_T", SP.chebyshev_T, "n", "x"); _spec("chebyshev_U", SP.chebyshev_U, "n", "x")
_spec("erf", SP.erf, "x"); _spec("erfc", SP.erfc, "x")
_spec("Ei", SP.Ei, "x"); _spec("E1", SP.E1, "x"); _spec("li", SP.li, "x")
_spec("Si", SP.Si, "x"); _spec("Ci", SP.Ci, "x"); _spec("fresnel_S", SP.fresnel_S, "x"); _spec("fresnel_C", SP.fresnel_C, "x")
_spec("elliptic_K", SP.elliptic_K, "m"); _spec("elliptic_E", SP.elliptic_E, "m")
_spec("hyp2f1", SP.hyp2f1, "a", "b", "c", "x"); _spec("hyp1f1", SP.hyp1f1, "a", "b", "x")
_spec("airy_Ai", SP.airy_Ai, "x"); _spec("lambert_W", SP.lambert_W, "x")
_spec("polylog", SP.polylog, "s", "x"); _spec("dirichlet_eta", SP.dirichlet_eta, "s")
_spec("dirichlet_beta", SP.dirichlet_beta, "s"); _spec("hurwitz_zeta", SP.hurwitz_zeta, "s", "a")

@kind("laguerre_L")
def _lag(p): return _ok("laguerre_L", SP.laguerre_L(int(p["n"]), _val(p["x"]), _val(p.get("alpha", 0))), "finite recurrence — associated Laguerre")


# ================================================================ transforms & complex ============
_CNS = {"exp": mp.exp, "log": mp.log, "ln": mp.log, "sin": mp.sin, "cos": mp.cos, "sqrt": mp.sqrt,
        "pi": mp.pi, "e": mp.e, "abs": abs, "j": mp.mpc(0, 1)} if _HAVE else {}
def _cfn(expr, var):
    return expr if callable(expr) else (lambda v: eval(compile(str(expr), "<c>", "eval"), {"__builtins__": {}}, {**_CNS, var: v}))
def _fnv(expr, var):
    return expr if callable(expr) else (lambda v: F.evaluate(str(expr), **{var: v}))

@kind("laplace_transform")
def _lap_t(p): return _ok("laplace_transform", TR.laplace_transform(_fnv(p["f"], "t"), _val(p["s"])), "∫_0^∞ f e^{−st} dt (exp–sinh DE)")
@kind("mellin_transform")
def _mel(p): return _ok("mellin_transform", TR.mellin_transform(_fnv(p["f"], "t"), _val(p["s"])), "∫_0^∞ t^{s−1} f dt (exp–sinh DE)")
@kind("fourier_transform")
def _four(p): return _ok("fourier_transform", TR.fourier_transform(_fnv(p["f"], "t"), _val(p["omega"]), int(p.get("T", 30))), "∫ f e^{−iωt} dt (finite window DE)")
@kind("inverse_laplace")
def _ilap(p): return _ok("inverse_laplace", TR.inverse_laplace(_cfn(p["F"], "s"), _val(p["t"])), "fixed-Talbot deformed contour")
@kind("fft")
def _fft(p): return _ok("fft", TR.fft(p["x"]), "radix-2 Cooley–Tukey")
@kind("ifft")
def _ifft(p): return _ok("ifft", TR.ifft(p["x"]), "inverse DFT")
@kind("z_transform")
def _zt(p): return _ok("z_transform", TR.z_transform(p["x"], complex(p["z"]) if isinstance(p["z"], (int, float)) else p["z"]), "Σ x[n] z^{−n}")
@kind("contour_integral")
def _cont(p): return _ok("contour_integral", TR.contour_integral(_cfn(p["f"], "z"), complex(p.get("center", 0)), _val(p["radius"])), "finite sum around |z−c|=r")
@kind("argument_principle", "Th_coqc")
def _argp(p): return _ok("argument_principle", TR.argument_principle(_cfn(p["f"], "z"), complex(p.get("center", 0)), _val(p["radius"])), "(1/2πi)∮ f'/f = #zeros−#poles")


# ================================================================ continuous optimization ==========
def _mfn(expr, vs):
    return (lambda x: F.evaluate(str(expr), **dict(zip(vs, x))))

@kind("gradient_descent")
def _gd(p):
    vs = p["vars"]; f = _mfn(p["f"], vs)
    return _ok("gradient_descent", OPT.gradient_descent(f, [_val(v) for v in p["x0"]]), "steepest descent + backtracking line search")
@kind("newton_min")
def _nmin(p):
    vs = p["vars"]; f = _mfn(p["f"], vs)
    return _ok("newton_min", OPT.newton_min(f, [_val(v) for v in p["x0"]]), "Newton: x ← x − H⁻¹∇f (finite gradient & Hessian)")
@kind("newton_system")
def _nsys(p):
    vs = p["vars"]; Fs = [_mfn(e, vs) for e in p["F"]]
    return _ok("newton_system", OPT.newton_system(Fs, [_val(v) for v in p["x0"]]), "Newton with finite-difference Jacobian")
@kind("least_squares", "Th_coqc")
def _lsq(p): return _ok("least_squares", OPT.least_squares(p["A"], p["b"]), "exact-ℚ normal equations (AᵀA)x=Aᵀb")
@kind("lagrange_min")
def _lag(p):
    vs = p["vars"]; f = _mfn(p["f"], vs); gs = [_mfn(e, vs) for e in p["constraints"]]
    return _ok("lagrange_min", OPT.lagrange_min(f, gs, [_val(v) for v in p["x0"]]), "Newton on the KKT system (Lagrange multipliers)")


# ================================================================ symbolic (exact CAS) ============
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


# ================================================================ P1 — number theory (advanced) ===
@kind("diophantine_linear", "Th_coqc")
def _dio(p):
    r = X.diophantine_linear(int(p["a"]), int(p["b"]), int(p["c"]))
    return {"kind": "diophantine_linear", "status": "ok" if r else "HOLD", "tier": "Th_coqc",
            "value": {"x0": r[0], "y0": r[1], "dx": r[2], "dy": r[3]} if r else None, "method": "extended Euclid",
            **({} if r else {"reason": "no integer solution (gcd(a,b) ∤ c)"})}
@kind("pell", "Th_coqc")
def _pell(p):
    r = X.pell(int(p["D"])); return {"kind": "pell", "status": "ok" if r else "HOLD", "tier": "Th_coqc",
        "value": {"x": r[0], "y": r[1]} if r else None, "method": "continued fraction of √D",
        **({} if r else {"reason": "D is a perfect square — no nontrivial solution"})}
@kind("modular_sqrt", "Th_coqc")
def _msqrt(p):
    r = X.tonelli_shanks(int(p["a"]), int(p["p"])); return {"kind": "modular_sqrt", "status": "ok" if r is not None else "HOLD",
        "tier": "Th_coqc", "value": r, "method": "Tonelli–Shanks", **({} if r is not None else {"reason": "a is a quadratic non-residue mod p"})}
@kind("mobius", "Th_coqc")
def _mob(p): return _ok("mobius", X.mobius(int(p["n"])), "μ(n) from factorization")
@kind("mertens", "Th_coqc")
def _mert(p): return _ok("mertens", X.mertens(int(p["N"])), "Σ μ(k)")
@kind("liouville", "Th_coqc")
def _liou(p): return _ok("liouville", X.liouville(int(p["n"])), "λ(n)=(−1)^Ω(n)")
@kind("von_mangoldt")
def _vm(p): return _ok("von_mangoldt", X.von_mangoldt(int(p["n"])), "Λ(n)=ln p if n=p^k else 0")

# ================================================================ P1 — linear algebra (advanced) ==
@kind("matrix_exp")
def _mexp(p): return _ok("matrix_exp", X.matrix_exp(p["matrix"]), "e^A = Σ A^k/k! (finite series)")
@kind("null_space", "Th_coqc")
def _null(p): return _ok("null_space", X.null_space(p["matrix"]), "kernel basis from RREF (exact ℚ)")
@kind("hermite_normal_form", "Th_coqc")
def _hnf(p): return _ok("hermite_normal_form", X.hermite_normal_form(p["matrix"]), "column HNF (exact ℤ)")
@kind("smith_normal_form", "Th_coqc")
def _snf(p): return _ok("smith_normal_form", X.smith_normal_form(p["matrix"]), "invariant factors d₁|d₂|… (exact ℤ)")

# ================================================================ P1 — DP / combinatorics ==========
@kind("knapsack", "Th_coqc")
def _knap(p): return _ok("knapsack", CO.knapsack(p["weights"], p["values"], int(p["capacity"])), "0/1 knapsack DP")
@kind("subset_sum", "Th_coqc")
def _ss2(p): return _ok("subset_sum", CO.subset_sum(p["nums"], int(p["target"])), "reachability DP")
@kind("lcs", "Th_coqc")
def _lcs(p): return _ok("lcs", CO.lcs(p["a"], p["b"]), "longest common subsequence DP")
@kind("edit_distance", "Th_coqc")
def _ed(p): return _ok("edit_distance", CO.edit_distance(p["a"], p["b"]), "Levenshtein DP")
@kind("coin_change", "Th_coqc")
def _cc2(p): return _ok("coin_change", CO.coin_change(p["coins"], int(p["amount"])), "coin DP (min + #ways)")

# ================================================================ P1 — graph (advanced) ============
@kind("dijkstra", "Th_coqc")
def _dij(p): return _ok("dijkstra", CO.dijkstra(int(p["n"]), p["edges"], int(p["source"])), "Dijkstra (nonneg weights)")
@kind("bellman_ford", "Th_coqc")
def _bf(p): return _ok("bellman_ford", CO.bellman_ford(int(p["n"]), p["edges"], int(p["source"])), "Bellman–Ford (neg-cycle aware)")
@kind("bipartite_matching", "Th_coqc")
def _bm(p): return _ok("bipartite_matching", CO.bipartite_matching(int(p["nL"]), int(p["nR"]), p["edges"]), "augmenting-path matching")
@kind("assignment", "Th_coqc")
def _asg(p): return _ok("assignment", CO.hungarian(p["cost"]), "Hungarian algorithm (exact ℚ)")
@kind("spanning_tree_count", "Th_coqc")
def _stc(p): return _ok("spanning_tree_count", CO.spanning_tree_count(int(p["n"]), p["edges"]), "Kirchhoff (Laplacian cofactor det)")
@kind("chromatic_number", "Th_coqc")
def _chr(p): return _ok("chromatic_number", CO.chromatic_number(int(p["n"]), p["edges"]), "backtracking colouring")

# ================================================================ P1 — LP / logic =================
@kind("linear_program")
def _lp(p):
    r = CO.linear_program(p["c"], p["A"], p["b"], p.get("sense", "max"))
    # the LP verdict (optimal / infeasible / unbounded) is a computed OUTCOME, kept in value; the
    # top-level status is 'ok' because the solve itself succeeded (detecting infeasibility is a result,
    # not a refusal).
    return {"kind": "linear_program", "status": "ok", "value": _norm(r), "tier": "exact",
            "method": "two-phase exact rational simplex (Bland's rule)"}
@kind("sat", "Th_coqc")
def _sat(p):
    r = CO.sat(p["clauses"], p.get("n_vars"))
    return {"kind": "sat", "status": "ok" if r["satisfiable"] else "HOLD", "value": r, "tier": "Th_coqc",
            "method": "DPLL with unit propagation"}


# ================================================================ P1 — rigorous certification =====
@kind("interval_enclose", "Th_coqc")
def _ienc(p): return _ok("interval_enclose", IVL.enclose(p["expr"], {k: tuple(v) for k, v in p["box"].items()}),
                         "single-shot rigorous interval evaluation")
@kind("verified_range", "Th_coqc")
def _vrange(p): return _ok("verified_range", IVL.verified_range(p["expr"], p["var"], p["a"], p["b"]),
                           "rigorous [min,max] enclosure by interval subdivision")
@kind("certified_root")
def _croot(p):
    r = IVL.certified_root(p["expr"], p["var"], p["a"], p["b"])
    return {"kind": "certified_root", "status": r.get("status", "ok"), "value": _norm(r), "tier": "Th_coqc",
            "method": "interval bisection — root proven by the intermediate-value theorem"}
@kind("certified_min", "Th_coqc")
def _cmin(p): return _ok("certified_min", IVL.certified_min(p["expr"], p["var"], p["a"], p["b"]),
                         "rigorous global-minimum bracket by interval branch-and-bound")
@kind("gershgorin", "Th_coqc")
def _gersh(p): return _ok("gershgorin", IVL.gershgorin(p["matrix"]), "Gershgorin discs enclosing every eigenvalue")


# ===================== P2 · statistics & probability (exact ℚ where possible) =======================
@kind("binomial")
def _binom(p): return _ok("binomial", ST.binomial(p["n"], p.get("k"), p.get("p", "1/2")), "exact binomial pmf/cdf over ℚ")
@kind("poisson")
def _pois(p): return _ok("poisson", ST.poisson(p["lam"], p.get("k")), "Poisson pmf/cdf, finite readout of e^{-λ}")
@kind("hypergeometric")
def _hyp(p): return _ok("hypergeometric", ST.hypergeometric(p["N"], p["K"], p["n"], p["k"]), "exact hypergeometric pmf/cdf over ℚ")
@kind("geometric")
def _geo(p): return _ok("geometric", ST.geometric(p["p"], p.get("k")), "exact geometric pmf/cdf over ℚ")
@kind("normal")
def _norm_d(p): return _ok("normal", ST.normal(p["x"], p.get("mu", 0), p.get("sigma", 1)), "normal pdf/cdf via erf (finite readout)")
@kind("describe")
def _desc(p): return _ok("describe", ST.describe(p["data"]), "exact sample moments over ℚ")
@kind("z_test")
def _zt(p): return _ok("z_test", ST.z_test(p["sample_mean"], p["mu0"], p["sigma"], p["n"]), "one-sample z-test, p via erfc")
@kind("t_test")
def _tt(p): return _ok("t_test", ST.t_test(p["sample_mean"], p["mu0"], p["sample_std"], p["n"]), "one-sample t-test, p via regularized incomplete beta")
@kind("chi_square_test")
def _cst(p): return _ok("chi_square_test", ST.chi_square_test(p["observed"], p["expected"]), "Pearson χ², statistic exact ℚ")
@kind("regression")
def _reg(p): return _ok("regression", ST.regression(p["x"], p["y"], p.get("degree", 1)), "exact polynomial least-squares over ℚ")
@kind("multiple_regression")
def _mreg(p): return _ok("multiple_regression", ST.multiple_regression(p["X"], p["y"]), "exact multiple linear least-squares over ℚ")
@kind("markov_absorbing")
def _mabs(p): return _ok("markov_absorbing", ST.markov_absorbing(p["P"], p["absorbing"]), "absorbing chain expected steps, exact ℚ fundamental matrix")
@kind("stationary")
def _stat(p): return _ok("stationary", ST.stationary(p["P"]), "stationary distribution, exact ℚ")
@kind("bayes_update")
def _bayes(p):
    r = ST.bayes_update(p["prior"], p["likelihood"])
    return {"kind": "bayes_update", "status": r.get("status", "ok"), "value": _norm(r), "method": "exact rational Bayes renormalization"}

# ===================== P2 · computational geometry (EXACT rational predicates) =======================
@kind("orient", "Th_coqc")
def _ori(p): return _ok("orient", GEO.orient(p["a"], p["b"], p["c"]), "exact sign of the orientation determinant")
@kind("convex_hull", "Th_coqc")
def _hull(p): return _ok("convex_hull", GEO.convex_hull(p["points"]), "exact monotone-chain hull (rational orientation)")
@kind("point_in_polygon", "Th_coqc")
def _pip(p): return _ok("point_in_polygon", GEO.point_in_polygon(p["point"], p["polygon"]), "exact ray-crossing with boundary test")
@kind("segments_intersect", "Th_coqc")
def _segx(p): return _ok("segments_intersect", GEO.segments_intersect(p["p1"], p["p2"], p["p3"], p["p4"]), "exact orientation-sign intersection test")
@kind("closest_pair", "Th_coqc")
def _cpair(p): return _ok("closest_pair", GEO.closest_pair(p["points"]), "exact squared-distance closest pair")
@kind("in_circle", "Th_coqc")
def _incir(p): return _ok("in_circle", GEO.in_circle(p["a"], p["b"], p["c"], p["d"]), "exact in-circle (Delaunay) determinant sign")

# ===================== P2 · cryptographic number theory (exact, certificate-bearing) ================
@kind("primality_certificate", "Th_coqc")
def _pcert(p):
    v = CY.is_prime(p["n"])
    # certified compositeness/primality → Th_coqc; a probable prime above the bound → finite_diagnostic
    tier = "Th_coqc" if v.get("certified") else "finite_diagnostic"
    return {"kind": "primality_certificate", "status": "ok", "value": _norm(v), "tier": tier,
            "method": "Miller–Rabin (first 13 primes) with a checkable witness; deterministic below "
                      "%d, probable above" % CY.MR_DET_BOUND}
@kind("modinv")
def _minv(p):
    r = CY.modinv(int(p["a"]), int(p["m"]))
    return {"kind": "modinv", "status": r.get("status", "ok"), "value": _norm(r), "method": "extended Euclidean inverse"}
@kind("rsa_keygen")
def _rkg(p):
    r = CY.rsa_keygen(p["p"], p["q"], p.get("e", 65537))
    return {"kind": "rsa_keygen", "status": r.get("status", "ok"), "value": _norm(r), "method": "exact RSA keypair"}
@kind("rsa_encrypt")
def _renc(p): return _ok("rsa_encrypt", CY.rsa_encrypt(p["m"], p["e"], p["n"]), "exact modular exponentiation")
@kind("rsa_decrypt")
def _rdec(p): return _ok("rsa_decrypt", CY.rsa_decrypt(p["c"], p["d"], p["n"]), "exact modular exponentiation")
@kind("ec_add", "Th_coqc")
def _ecadd(p): return _ok("ec_add", CY.ec_add(p["P"], p["Q"], p["a"], p["p"]), "exact elliptic-curve point addition over F_p")
@kind("ec_mul", "Th_coqc")
def _ecmul(p): return _ok("ec_mul", CY.ec_mul(p["k"], p["P"], p["a"], p["p"]), "exact EC scalar multiply (double-and-add) over F_p")


# ================================================================ dispatch ==========================
def _seq0(expr):
    return expr if callable(expr) else (lambda n: F.evaluate(str(expr), n=n))

# Tier honesty — a `Th_coqc` tag is reserved for kinds whose GOVERNING LAW is a named theorem that is
# machine-checked axiom-free in formal/ (attached as `coq_theorem`). Every other exact/decidable ℤ/ℚ
# computation is tier `exact` (the value is exact by construction, but no individual Coq proof of the
# implementation is claimed); numeric-to-tolerance methods stay `finite_diagnostic`. This deliberately
# strips the `Th_coqc` label from the many exact handlers that have no proof mapping (no tier inflation).
_COQ_BACKED = {
    "orient":            "IDM_Geometry.orient_* (orientation determinant, axiom-free)",
    "convex_hull":       "IDM_Geometry.orient_* (branches only on the proven orientation sign)",
    "point_in_polygon":  "IDM_Geometry.orient_* (proven orientation predicate; exact boundary)",
    "segments_intersect":"IDM_Geometry.orient_* (proven orientation predicate)",
    "shortest_path":     "IDM_Tropical.minplus_distrib (min-plus semiring law)",
    "widest_path":       "IDM_Tropical.maxplus_distrib (max-plus semiring law)",
    "minimax_path":      "IDM_Tropical.bottleneck_distrib (bottleneck semiring law)",
    "spanning_tree_count":"IDM_Matrix.laplacian_* (Kirchhoff via the graph Laplacian)",
    "geometric_series":  "IDM_Certified.geom_certified_identity (certified geometric-series bound)",
}

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
    # tier-honesty pass: keep Th_coqc only where a named machine-checked theorem governs the result
    if res.get("tier") == "Th_coqc":
        if k in _COQ_BACKED:
            res["coq_theorem"] = _COQ_BACKED[k]
        else:
            res["tier"] = "exact"   # exact & decidable, but not individually machine-checked in Coq
    return res


def kinds():
    """the catalogue of supported problem kinds."""
    return sorted(_REG)
