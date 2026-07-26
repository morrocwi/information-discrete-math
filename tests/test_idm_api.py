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
