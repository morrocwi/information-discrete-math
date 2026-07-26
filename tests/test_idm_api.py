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
