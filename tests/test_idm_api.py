"""Smoke tests for the idm library + solver API."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idm


def _f(r):
    v = r["value"]
    return v["float"] if isinstance(v, dict) and "float" in v else v


def test_constants_and_functions():
    assert abs(float(idm.pi()) - 3.14159265358979) < 1e-10
    assert abs(float(idm.exp(1)) - 2.718281828) < 1e-6
    assert _f(idm.solve({"kind": "constant", "name": "pi"})) == float(idm.pi())


def test_certified_paths():
    r = idm.solve({"kind": "geometric_series", "r": "1/3", "eps": "1e-12"})
    assert r["status"] == "CERTIFIED" and abs(_f(r) - 1.5) < 1e-9
    r = idm.solve({"kind": "exp", "x": 0.4, "eps": "1e-20"})
    assert r["status"] == "CERTIFIED"
    r = idm.solve({"kind": "exp", "x": 5, "eps": "1e-12"})   # out of certified domain
    assert r["status"] == "HOLD"


def test_integral_certified():
    r = idm.solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": "1e-8"})
    assert r["status"] == "CERTIFIED"
    assert abs(_f(r) - 1.7724538509) < 1e-6                  # √π


def test_calculus():
    assert abs(_f(idm.solve({"kind": "derivative", "f": "exp(x)", "x": 1})) - 2.718281828) < 1e-5
    assert abs(_f(idm.solve({"kind": "limit", "seq": "(1 + 1/n)**n"})) - 2.718281828) < 1e-6
    assert abs(_f(idm.solve({"kind": "ode", "f": "y", "x0": 0, "y0": 1, "xT": 1})) - 2.718281828) < 1e-6


def test_path_algebra():
    W = [[0, 7, 9, None, None, 14], [7, 0, 10, 15, None, None], [9, 10, 0, 11, None, 2],
         [None, 15, 11, 0, 6, None], [None, None, None, 6, 0, 9], [14, None, 2, None, 9, 0]]
    assert idm.solve({"kind": "shortest_path", "matrix": W, "source": 0, "target": 4})["value"] == 20
    assert idm.solve({"kind": "widest_path", "matrix": W, "source": 0, "target": 4})["value"] == 9


def test_readouts_robust():
    r = idm.solve({"kind": "readouts", "data": [3, -1, 4, 1, -5, 9, 2, -6]})
    assert r["status"] == "ok" and "mean(avg)" in r["value"]      # must not crash on mixed-sign data


def test_unknown_kind_holds():
    assert idm.solve({"kind": "nonsense"})["status"] == "HOLD"
    assert idm.solve({})["status"] == "HOLD"


def test_server_module_imports():
    from idm import server
    assert "/solve" in server.OPENAPI["paths"]


def _val(r):
    v = r["value"]
    if isinstance(v, dict):
        return v.get("float", v.get("exact", v))
    return v


def test_number_theory():
    assert idm.solve({"kind": "factorize", "n": 360360})["value"] == {"2": 3, "3": 2, "5": 1, "7": 1, "11": 1, "13": 1}
    assert idm.solve({"kind": "is_prime", "n": 1000003})["value"] is True
    assert idm.solve({"kind": "gcd", "a": 1071, "b": 462})["value"] == 21
    assert idm.solve({"kind": "fibonacci", "n": 50})["value"] == 12586269025
    assert idm.solve({"kind": "partition", "n": 100})["value"] == 190569292
    assert idm.solve({"kind": "catalan", "n": 10})["value"] == 16796
    assert idm.solve({"kind": "totient", "n": 36})["value"] == 12
    assert idm.solve({"kind": "crt", "residues": [2, 3, 2], "moduli": [3, 5, 7]})["value"] == 23
    assert idm.solve({"kind": "mod_inverse", "a": 3, "m": 11})["value"] == 4
    assert idm.solve({"kind": "bernoulli", "n": 6})["value"]["exact"] == "1/42"


def test_linear_algebra():
    assert idm.solve({"kind": "matrix_determinant", "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 10]]})["value"]["exact"] == "-3/1"
    r = idm.solve({"kind": "solve_linear", "A": [[2, 1], [1, 3]], "b": [3, 5]})
    assert r["status"] == "ok"
    assert idm.solve({"kind": "matrix_inverse", "matrix": [[1, 0], [0, 1]]})["value"] == [[{"exact": "1/1", "float": 1.0}, {"exact": "0/1", "float": 0.0}], [{"exact": "0/1", "float": 0.0}, {"exact": "1/1", "float": 1.0}]]
    assert idm.solve({"kind": "matrix_inverse", "matrix": [[1, 1], [1, 1]]})["status"] == "HOLD"  # singular
    eig = idm.solve({"kind": "eigenvalues", "matrix": [[2, 0, 0], [0, 3, 0], [0, 0, 5]]})
    reals = sorted(round(e["re"]["float"]) for e in eig["value"])
    assert reals == [2, 3, 5]
    assert idm.solve({"kind": "rational_roots", "coeffs": [-6, 11, -6, 1]})["value"] == \
        [{"exact": "1/1", "float": 1.0}, {"exact": "2/1", "float": 2.0}, {"exact": "3/1", "float": 3.0}]


def test_analysis():
    assert abs(_val(idm.solve({"kind": "zeta", "s": 2})) - 3.141592653589793 ** 2 / 6) < 1e-6
    assert idm.solve({"kind": "zeta", "s": -1})["value"]["exact"] == "-1/12"
    assert abs(float(_val(idm.solve({"kind": "regularized_sum", "power": 1}))) + 1 / 12) < 1e-4
    assert abs(float(_val(idm.solve({"kind": "root_find", "f": "x*x - 2", "a": 0, "b": 2}))) - 2 ** 0.5) < 1e-9
    assert _val(idm.solve({"kind": "interpolate", "points": [[0, 1], [1, 3], [2, 7]], "x": 3})) == 13
    assert idm.solve({"kind": "minimize", "f": "(x-3)**2 + 1", "a": 0, "b": 6})["status"] == "ok"


def test_registry_size():
    assert len(idm.kinds()) >= 45          # a genuinely comprehensive solver


def test_number_theory_extended():
    assert idm.solve({"kind": "sigma", "n": 28})["value"] == 56
    assert idm.solve({"kind": "prime_pi", "N": 100})["value"] == 25
    assert idm.solve({"kind": "next_prime", "n": 100})["value"] == 101
    assert idm.solve({"kind": "base_convert", "n": 255, "base": 16})["value"] == "ff"
    assert idm.solve({"kind": "derangements", "n": 5})["value"] == 44
    assert idm.solve({"kind": "multinomial", "ks": [2, 2, 1]})["value"] == 30
    assert idm.solve({"kind": "faulhaber", "power": 2, "N": 10})["value"] == 385
    assert idm.solve({"kind": "primitive_root", "p": 7})["value"] == 3
    assert idm.solve({"kind": "bezout", "a": 240, "b": 46})["value"] == {"gcd": 2, "x": -9, "y": 47}


def test_poly_and_matrix_extended():
    assert idm.solve({"kind": "matrix_transpose", "matrix": [[1, 2, 3], [4, 5, 6]]})["value"] == [[1, 4], [2, 5], [3, 6]]
    assert idm.solve({"kind": "matrix_rank", "matrix": [[1, 2], [2, 4]]})["value"] == 1
    assert idm.solve({"kind": "poly_from_roots", "roots": [1, 2, 3]})["value"][0]["exact"] == "-6/1"  # constant term -6
    assert idm.solve({"kind": "convolution", "a": [1, 1, 1], "b": [1, 1]})["value"][1]["exact"] == "2/1"


def test_geometry():
    assert idm.solve({"kind": "polygon_area", "points": [[0, 0], [4, 0], [4, 3], [0, 3]]})["value"]["exact"] == "12/1"
    assert abs(_val(idm.solve({"kind": "distance", "p": [0, 0], "q": [3, 4]})) - 5.0) < 1e-12
    assert idm.solve({"kind": "dot", "u": [1, 2, 3], "v": [4, 5, 6]})["value"]["exact"] == "32/1"


def test_discrete_structures():
    assert idm.solve({"kind": "mst", "n": 4, "edges": [[0, 1, 1], [1, 2, 2], [2, 3, 3], [0, 3, 10]]})["value"]["weight"] == 6
    assert idm.solve({"kind": "max_flow", "n": 4, "edges": [[0, 1, 3], [0, 2, 2], [1, 2, 1], [1, 3, 2], [2, 3, 3]], "source": 0, "sink": 3})["value"] == 5
    assert idm.solve({"kind": "topological_sort", "n": 4, "edges": [[0, 1], [1, 2], [0, 2], [2, 3]]})["value"] == [0, 1, 2, 3]
    assert idm.solve({"kind": "topological_sort", "n": 2, "edges": [[0, 1], [1, 0]]})["status"] == "HOLD"  # cyclic
    assert idm.solve({"kind": "is_bipartite", "n": 4, "edges": [[0, 1], [1, 2], [2, 3], [3, 0]]})["value"]["bipartite"] is True
    assert idm.solve({"kind": "set_operation", "op": "intersection", "a": [1, 2, 3], "b": [2, 3, 4]})["value"] == [2, 3]
    assert idm.solve({"kind": "truth_table", "expr": "a or not a", "vars": ["a"]})["value"]["tautology"] is True


def test_lots_of_kinds():
    assert len(idm.kinds()) >= 100          # comprehensive


def test_integration_flagship():
    import mpmath as mp
    # doubly-infinite: √π
    r = idm.solve({"kind": "integral", "f": "1/exp(x*x)", "a": "-inf", "b": "inf"})
    assert r["status"] == "CERTIFIED" and abs(_val(r) - float(mp.sqrt(mp.pi))) < 1e-8
    # semi-infinite Planck integral = π⁴/15
    r = idm.solve({"kind": "improper_integral", "f": "x**3/(exp(x)-1)", "a": "1e-14", "b": "inf", "eps": "1e-8"})
    assert r["status"] == "CERTIFIED" and abs(_val(r) - float(mp.pi**4 / 15)) < 1e-6
    # endpoint singularity 1/√x on (0,1] = 2
    r = idm.solve({"kind": "singular_integral", "f": "1/sqrt(x)", "a": "1e-30", "b": 1})
    assert r["status"] == "CERTIFIED" and abs(_val(r) - 2) < 1e-8
    # rational via residues = π
    r = idm.solve({"kind": "residue_integral", "num": [1], "den": [1, 0, 1]})
    assert abs(r["value"]["re"]["float"] - float(mp.pi)) < 1e-9
    # Gauss quadrature and multi-D
    assert abs(_val(idm.solve({"kind": "gauss_quadrature", "f": "x*x", "a": 0, "b": 1})) - 1 / 3) < 1e-12
    r = idm.solve({"kind": "multidim_integral", "f": "1/exp(x+y)", "vars": ["x", "y"], "bounds": [[0, 1], [0, 1]]})
    assert abs(_val(r) - float((1 - 1 / mp.e) ** 2)) < 1e-8


def test_ode_pde():
    import mpmath as mp
    # ODE system: harmonic oscillator y0(π) = cos π = -1
    y = idm.solve({"kind": "ode_system", "f": ["y1", "-y0"], "vars": ["y0", "y1"], "x0": 0, "y0": [1, 0], "xT": float(mp.pi), "N": 4000})
    assert y["status"] == "ok" and abs(y["value"][0]["float"] + 1) < 1e-5
    # heat: u(0.5, 0.1) ≈ e^{-π²·0.1}
    h = idm.solve({"kind": "pde_heat", "alpha": 1, "L": 1, "T": 0.1, "init": "sin(pi*x)", "bc": [0, 0], "at": 0.5, "Nx": 100, "Nt": 500})
    assert abs(_val(h) - float(mp.e ** (-mp.pi ** 2 * mp.mpf("0.1")))) < 1e-3
    # wave: u(0.5, 1) = -1
    w = idm.solve({"kind": "pde_wave", "c": 1, "L": 1, "T": 1, "init": "sin(pi*x)", "bc": [0, 0], "at": 0.5, "Nx": 200})
    assert abs(_val(w) + 1) < 5e-2
    # Poisson with harmonic BC x²−y²: interior value exact
    p = idm.solve({"kind": "pde_poisson", "f": "0", "box": [0, 1, 0, 1], "bc": "x*x - y*y", "at": [0.75, 0.25], "Nx": 40, "Ny": 40})
    assert abs(_val(p) - 0.5) < 1e-3
    # BVP u''=u, u(0)=0, u(1)=1 → sinh(x)/sinh(1)
    b = idm.solve({"kind": "ode_bvp", "q": "1", "r": "0", "a": 0, "b": 1, "alpha": 0, "beta": 1, "at": 0.5})
    assert abs(_val(b) - float(mp.sinh(mp.mpf("0.5")) / mp.sinh(1))) < 1e-3
    # Sturm–Liouville −u''=λu on [0,π] → λ_n = n²
    e = idm.solve({"kind": "sturm_liouville", "potential": "0", "L": float(mp.pi), "n_eigs": 3, "N": 400})
    eigs = [round(float(v["float"] if isinstance(v, dict) else v)) for v in e["value"]]
    assert eigs == [1, 4, 9]


def test_limits_series():
    import mpmath as mp
    # Taylor of exp → 1/k!
    t = idm.solve({"kind": "taylor_series", "f": "exp(x)", "x0": 0, "n": 5})
    cs = [c["float"] if isinstance(c, dict) else float(c) for c in t["value"]]
    assert abs(cs[0] - 1) < 1e-6 and abs(cs[2] - 0.5) < 1e-6 and abs(cs[4] - 1 / 24) < 1e-5
    # Fourier of sin → b1 = 1
    fo = idm.solve({"kind": "fourier_series", "f": "sin(x)", "n": 3})
    assert abs((fo["value"]["b"][0]["float"] if isinstance(fo["value"]["b"][0], dict) else float(fo["value"]["b"][0])) - 1) < 1e-6
    # Padé [1/1] of exp = (1 + x/2)/(1 − x/2)
    pa = idm.solve({"kind": "pade", "coeffs": ["1", "1", "1/2", "1/6"], "m": 1, "n": 1})
    assert pa["value"]["num"][1]["exact"] == "1/2" and pa["value"]["den"][1]["exact"] == "-1/2"
    # acceleration of Σ(−1)ⁿ/(n+1) = ln 2
    assert abs(_val(idm.solve({"kind": "series_accelerate", "term": "(-1)**n/(n+1)", "N": 25})) - float(mp.log(2))) < 1e-8
    # convergence with an honest HOLD on the harmonic boundary
    assert idm.solve({"kind": "convergence_test", "term": "1/n**2"})["value"]["verdict"] == "CONVERGES"
    assert idm.solve({"kind": "convergence_test", "term": "2**n"})["value"]["verdict"] == "DIVERGES"
    assert idm.solve({"kind": "convergence_test", "term": "1/n"})["status"] == "HOLD"
    # limits
    assert abs(_val(idm.solve({"kind": "limit_oneside", "f": "sin(x)/x", "a": 0, "side": "+"})) - 1) < 1e-8
    assert abs(_val(idm.solve({"kind": "limit_infinity", "f": "(1+1/x)**x"})) - float(mp.e)) < 1e-6
    assert abs(_val(idm.solve({"kind": "lhopital", "num": "exp(x)-1", "den": "x", "a": 0})) - 1) < 1e-8


def test_special_functions():
    import mpmath as mp
    checks = [
        ({"kind": "gamma", "z": 5}, 24),
        ({"kind": "beta", "a": 2, "b": 3}, float(mp.mpf(1) / 12)),
        ({"kind": "bessel_J", "n": 0, "x": 1}, float(mp.besselj(0, 1))),
        ({"kind": "bessel_I", "n": 0, "x": 1}, float(mp.besseli(0, 1))),
        ({"kind": "legendre_P", "n": 3, "x": 0.5}, float(mp.legendre(3, mp.mpf("0.5")))),
        ({"kind": "hermite_H", "n": 3, "x": 1}, float(mp.hermite(3, 1))),
        ({"kind": "chebyshev_T", "n": 4, "x": 0.5}, float(mp.chebyt(4, mp.mpf("0.5")))),
        ({"kind": "erf", "x": 1}, float(mp.erf(1))),
        ({"kind": "Ei", "x": 1}, float(mp.ei(1))),
        ({"kind": "Si", "x": 1}, float(mp.si(1))),
        ({"kind": "elliptic_K", "m": 0.5}, float(mp.ellipk(mp.mpf("0.5")))),
        ({"kind": "elliptic_E", "m": 0.5}, float(mp.ellipe(mp.mpf("0.5")))),
        ({"kind": "hyp2f1", "a": 1, "b": 1, "c": 2, "x": 0.5}, float(2 * mp.log(2))),
        ({"kind": "hyp1f1", "a": 1, "b": 2, "x": 1}, float(mp.e - 1)),
        ({"kind": "airy_Ai", "x": 1}, float(mp.airyai(1))),
        ({"kind": "lambert_W", "x": 1}, float(mp.lambertw(1))),
        ({"kind": "polylog", "s": 2, "x": 0.5}, float(mp.polylog(2, mp.mpf("0.5")))),
        ({"kind": "dirichlet_eta", "s": 1}, float(mp.log(2))),
        ({"kind": "dirichlet_beta", "s": 2}, float(mp.catalan)),
    ]
    for prob, exact in checks:
        assert abs(_val(idm.solve(prob)) - exact) < 1e-6, prob["kind"]


def test_kind_count_155():
    assert len(idm.kinds()) >= 150


def test_transforms():
    import mpmath as mp
    assert abs(_val(idm.solve({"kind": "laplace_transform", "f": "sin(t)", "s": 2})) - 0.2) < 1e-5
    assert abs(_val(idm.solve({"kind": "laplace_transform", "f": "t", "s": 2})) - 0.25) < 1e-5
    assert abs(_val(idm.solve({"kind": "mellin_transform", "f": "1/exp(t)", "s": 5})) - 24) < 1e-3
    assert abs(_val(idm.solve({"kind": "inverse_laplace", "F": "1/(s-2)", "t": 1})) - float(mp.e ** 2)) < 1e-3
    assert abs(_val(idm.solve({"kind": "inverse_laplace", "F": "1/(s*s+1)", "t": float(mp.pi / 2)})) - 1) < 1e-4
    z = idm.solve({"kind": "z_transform", "x": [1, 1, 1], "z": 2})
    assert abs(z["value"]["re"]["float"] - 1.75) < 1e-9
    assert idm.solve({"kind": "argument_principle", "f": "z*z", "center": 0, "radius": 1})["value"] == 2
    f = idm.solve({"kind": "fft", "x": [1, 1, 1, 1]})
    assert abs(f["value"][0]["re"]["float"] - 4) < 1e-9
    rt = idm.solve({"kind": "ifft", "x": [4, 0, 0, 0]})
    assert abs(rt["value"][0]["re"]["float"] - 1) < 1e-9


def test_optimization():
    def near(v, e, tol=1e-4):
        return all(abs((a["float"] if isinstance(a, dict) else float(a)) - b) < tol for a, b in zip(v, e))
    assert near(idm.solve({"kind": "gradient_descent", "f": "(x-3)**2+(y+1)**2", "vars": ["x", "y"], "x0": [0, 0]})["value"]["argmin"], [3, -1])
    assert near(idm.solve({"kind": "newton_min", "f": "(x-1)**2+3*(y-2)**2", "vars": ["x", "y"], "x0": [0, 0]})["value"]["argmin"], [1, 2])
    assert near(idm.solve({"kind": "newton_system", "F": ["x**2+y**2-1", "x-y"], "vars": ["x", "y"], "x0": [1, 0.5]})["value"]["root"], [2 ** -0.5, 2 ** -0.5])
    r = idm.solve({"kind": "least_squares", "A": [[1, 0], [1, 1], [1, 2]], "b": [1, 3, 5]})
    assert r["value"]["x"][0]["exact"] == "1/1" and r["value"]["x"][1]["exact"] == "2/1"
    assert near(idm.solve({"kind": "lagrange_min", "f": "x**2+y**2", "constraints": ["x+y-1"], "vars": ["x", "y"], "x0": [0.2, 0.9]})["value"]["argmin"], [0.5, 0.5])


def test_symbolic():
    # differentiation (verified by evaluating vs a numeric derivative through the engine)
    import idm.symbolic as S
    import mpmath as mp
    for expr, pt in [("sin(x)*exp(x)", 1.0), ("x**3 + 2*x", 1.5), ("log(x)", 2.0), ("sqrt(x)", 4.0)]:
        d = S.simplify(S.diff(S.parse(expr), "x"))
        num = (float(S.evaluate(S.parse(expr), {"x": pt + 1e-8})) - float(S.evaluate(S.parse(expr), {"x": pt - 1e-8}))) / 2e-8
        assert abs(float(S.evaluate(d, {"x": pt})) - num) < 1e-4, expr
    # expand / simplify / integrate through the solver
    assert idm.solve({"kind": "simplify", "expr": "2*x + 3*x - x"})["value"] == "4*x"
    assert abs(float(S.evaluate(S.parse(idm.solve({"kind": "expand", "expr": "(x+1)**3"})["value"]), {"x": 2})) - 27) < 1e-9
    r = idm.solve({"kind": "symbolic_integrate", "expr": "x**2 + cos(x)", "var": "x"})
    assert r["status"] == "ok" and "sin(x)" in r["value"]
    # honest HOLD: the Gaussian has no elementary antiderivative
    assert idm.solve({"kind": "symbolic_integrate", "expr": "exp(x**2)", "var": "x"})["status"] == "HOLD"
    # symbolic Taylor is exact
    assert [c for c in idm.solve({"kind": "symbolic_series", "expr": "exp(x)", "var": "x", "n": 4})["value"]] == ["1", "1", "1/2", "1/6", "1/24"]
    # solve quadratic
    assert idm.solve({"kind": "symbolic_solve", "expr": "x**2 - 5*x + 6", "var": "x"})["value"]["discriminant"] == "1"


def test_p1_number_theory_linalg():
    assert idm.solve({"kind": "pell", "D": 61})["value"] == {"x": 1766319049, "y": 226153980}
    assert idm.solve({"kind": "modular_sqrt", "a": 10, "p": 13})["value"] == 7
    assert idm.solve({"kind": "modular_sqrt", "a": 5, "p": 7})["status"] == "HOLD"  # non-residue
    assert idm.solve({"kind": "mobius", "n": 30})["value"] == -1
    assert idm.solve({"kind": "diophantine_linear", "a": 3, "b": 5, "c": 1})["value"]["x0"] == 2
    assert idm.solve({"kind": "smith_normal_form", "matrix": [[2, 4, 4], [-6, 6, 12], [10, -4, -16]]})["value"] == [2, 6, 12]
    assert idm.solve({"kind": "null_space", "matrix": [[1, 2, 3], [2, 4, 6]]})["value"]  # nonempty kernel


def test_p1_dp_graph_lp_sat():
    assert idm.solve({"kind": "knapsack", "weights": [2, 3, 4, 5], "values": [3, 4, 5, 6], "capacity": 5})["value"]["max_value"] == 7
    assert idm.solve({"kind": "edit_distance", "a": "kitten", "b": "sitting"})["value"] == 3
    assert idm.solve({"kind": "lcs", "a": "ABCBDAB", "b": "BDCAB"})["value"]["length"] == 4
    assert idm.solve({"kind": "coin_change", "coins": [1, 2, 5], "amount": 11})["value"] == {"min_coins": 3, "num_ways": 11}
    assert idm.solve({"kind": "dijkstra", "n": 4, "edges": [[0, 1, 1], [1, 2, 2], [0, 2, 4], [2, 3, 1]], "source": 0})["value"]["distances"][3] == 4
    assert idm.solve({"kind": "bellman_ford", "n": 3, "edges": [[0, 1, 1], [1, 2, -3], [2, 0, 1]], "source": 0})["value"]["negative_cycle"] is True
    assert idm.solve({"kind": "spanning_tree_count", "n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]})["value"] == 16
    assert idm.solve({"kind": "chromatic_number", "n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]})["value"] == 3
    a = idm.solve({"kind": "assignment", "cost": [[4, 1, 3], [2, 0, 5], [3, 2, 2]]})["value"]["cost"]
    assert (a["exact"] if isinstance(a, dict) else a) in ("5/1", 5)
    lp = idm.solve({"kind": "linear_program", "c": [3, 2], "A": [[1, 1], [1, 3]], "b": [4, 6], "sense": "max"})
    assert lp["value"]["objective"]["exact"] == "12/1"
    assert idm.solve({"kind": "sat", "clauses": [[1, 2], [-1, 3], [-2, -3]]})["value"]["satisfiable"] is True
    assert idm.solve({"kind": "sat", "clauses": [[1], [-1]]})["value"]["satisfiable"] is False


def test_rigorous_certification():
    # verified root enclosure of √2, proven by the intermediate-value theorem
    r = idm.solve({"kind": "certified_root", "expr": "x**2 - 2", "var": "x", "a": 1, "b": 2})
    assert r["status"] == "ok"
    lo, hi = r["value"]["root_lo"]["float"], r["value"]["root_hi"]["float"]
    assert lo <= 2 ** 0.5 <= hi
    # no sign change ⇒ HOLD (refuses to certify a root that isn't verified)
    assert idm.solve({"kind": "certified_root", "expr": "x**2 + 1", "var": "x", "a": -1, "b": 1})["status"] == "HOLD"
    # rigorous outer enclosure of the range (guaranteed to contain the true [min,max])
    rr = idm.solve({"kind": "verified_range", "expr": "x**2 - 2*x", "var": "x", "a": 0, "b": 3})["value"]
    assert rr["min"]["float"] <= -1 + 1e-3 and rr["max"]["float"] >= 3 - 1e-3
    # rigorous global-minimum bracket
    mn = idm.solve({"kind": "certified_min", "expr": "(x-3)**2 + 1", "var": "x", "a": 0, "b": 6})["value"]
    assert abs(mn["min_lower"]["float"] - 1) < 1e-4 and abs(mn["min_upper"]["float"] - 1) < 1e-4
    # Gershgorin discs enclose the spectrum
    g = idm.solve({"kind": "gershgorin", "matrix": [[2, 0.1], [0.1, 3]]})["value"]
    assert g["spectrum_bound"]["lo"]["float"] <= 1.99 and g["spectrum_bound"]["hi"]["float"] >= 3.01
    # single-shot interval enclosure
    e = idm.solve({"kind": "interval_enclose", "expr": "x**2", "box": {"x": [1, 2]}})["value"]
    assert e["lo"]["float"] <= 1 and e["hi"]["float"] >= 4


def test_p2_statistics():
    # exact binomial pmf over ℚ
    assert idm.solve({"kind": "binomial", "n": 10, "k": 3, "p": "1/2"})["value"]["pmf"]["exact"] == "15/128"
    # normal cdf via erf (finite readout) — Φ(1.96)≈0.975
    assert abs(idm.solve({"kind": "normal", "x": 1.96})["value"]["cdf"]["float"] - 0.975) < 1e-3
    # exact linear regression: y=1+2x recovered as rationals with R²=1
    r = idm.solve({"kind": "regression", "x": [0, 1, 2, 3], "y": [1, 3, 5, 7]})["value"]
    assert r["coeffs"][0]["exact"] == "1/1" and r["coeffs"][1]["exact"] == "2/1" and r["r_squared"]["exact"] == "1/1"
    # exact stationary distribution of a 2-state chain
    assert idm.solve({"kind": "stationary", "P": [["1/2", "1/2"], ["1/4", "3/4"]]})["value"]["stationary"][0]["exact"] == "1/3"
    # absorbing chain expected steps (exact ℚ)
    ab = idm.solve({"kind": "markov_absorbing", "P": [[1, 0, 0], ["1/2", 0, "1/2"], [0, 0, 1]], "absorbing": [0, 2]})
    assert ab["status"] == "ok"
    # exact Bayes renormalization
    assert idm.solve({"kind": "bayes_update", "prior": ["1/2", "1/2"], "likelihood": ["9/10", "1/10"]})["value"]["posterior"][0]["exact"] == "9/10"
    # χ² and t-test produce p-values
    assert idm.solve({"kind": "t_test", "sample_mean": 105, "mu0": 100, "sample_std": 15, "n": 30})["status"] == "ok"
    assert idm.solve({"kind": "chi_square_test", "observed": [10, 20, 30, 40], "expected": [25, 25, 25, 25]})["status"] == "ok"


def test_p2_geometry_exact():
    # exact orientation sign (no epsilon)
    assert idm.solve({"kind": "orient", "a": [0, 0], "b": [1, 0], "c": [0, 1]})["value"]["orientation"] == 1
    # exact convex hull: square + interior point → 4 vertices
    assert idm.solve({"kind": "convex_hull", "points": [[0, 0], [1, 0], [1, 1], [0, 1], ["1/2", "1/2"]]})["value"]["vertices"] == 4
    # exact point-in-polygon + boundary
    assert idm.solve({"kind": "point_in_polygon", "point": [2, 1], "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]})["value"]["inside"]
    # exact segment intersection
    assert idm.solve({"kind": "segments_intersect", "p1": [0, 0], "p2": [2, 2], "p3": [0, 2], "p4": [2, 0]})["value"]["intersect"]
    # exact squared-distance closest pair
    assert idm.solve({"kind": "closest_pair", "points": [[0, 0], [5, 5], [1, 0], [10, 10]]})["value"]["distance_squared"]["exact"] == "1/1"
    # exact in-circle (Delaunay) predicate
    assert idm.solve({"kind": "in_circle", "a": [0, 0], "b": [1, 0], "c": [0, 1], "d": ["1/4", "1/4"]})["value"]["in_circle"] == 1


def test_p2_crypto():
    # deterministic primality with a checkable certificate (base set returned for independent checking)
    c97 = idm.solve({"kind": "primality_certificate", "n": 97})["value"]
    assert c97["prime"] and "certificate" in c97
    assert not idm.solve({"kind": "primality_certificate", "n": 91})["value"]["prime"]
    assert idm.solve({"kind": "primality_certificate", "n": 2**61 - 1})["value"]["prime"]   # Mersenne
    assert idm.solve({"kind": "modinv", "a": 3, "m": 11})["value"]["inverse"] == 4
    # RSA round-trip (exact modular arithmetic)
    kp = idm.solve({"kind": "rsa_keygen", "p": 61, "q": 53, "e": 17})["value"]
    ct = idm.solve({"kind": "rsa_encrypt", "m": 65, "e": kp["public"]["e"], "n": kp["public"]["n"]})["value"]["cipher"]
    m = idm.solve({"kind": "rsa_decrypt", "c": ct, "d": kp["private"]["d"], "n": kp["private"]["n"]})["value"]["message"]
    assert m == 65
    # elliptic-curve scalar multiply over F_p
    assert idm.solve({"kind": "ec_mul", "k": 3, "P": [5, 1], "a": 2, "p": 17})["status"] == "ok"
