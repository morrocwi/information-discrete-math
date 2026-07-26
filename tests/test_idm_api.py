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
