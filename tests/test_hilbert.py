"""Hilbert-space mathematical core — finite-dim exact / finite_diagnostic, and the +ℝ fence."""
import os, sys, ast
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idm


def test_inner_product_and_norm():
    assert idm.solve({"kind": "inner_product", "u": [1, 2, 3], "v": [4, 5, 6]})["value"]["exact"] == "32"
    assert idm.solve({"kind": "norm_squared", "v": [3, 4]})["value"]["exact"] == "25"
    assert idm.solve({"kind": "norm_squared", "v": [[1, 1]]})["value"]["exact"] == "2"   # ‖1+i‖²
    assert idm.solve({"kind": "cauchy_schwarz_check", "u": [1, 2], "v": [3, 4]})["value"]["holds"]
    assert idm.solve({"kind": "is_orthogonal", "u": [1, 0], "v": [0, 1]})["value"]


def test_operators_exact():
    assert idm.solve({"kind": "is_self_adjoint", "M": [[2, [0, 1]], [[0, -1], 3]]})["value"]     # Hermitian
    assert idm.solve({"kind": "is_unitary", "M": [[0, 1], [1, 0]]})["value"]
    assert not idm.solve({"kind": "is_unitary", "M": [[2, 0], [0, 1]]})["value"]
    assert idm.solve({"kind": "is_normal", "M": [[2, 0], [0, 3]]})["value"]
    adj = idm.solve({"kind": "adjoint", "M": [[2, [0, 1]], [[0, -1], 3]]})
    assert adj["tier"] == "exact"
    gb = idm.solve({"kind": "gershgorin_bound", "M": [[2, 1], [1, 3]]})
    assert gb["value"]["exact"] == "4" and gb["tier"] == "exact"


def test_projection_exact():
    P = idm.solve({"kind": "projection_matrix", "basis": [[1, 0, 0]]})["value"]
    assert idm.solve({"kind": "is_idempotent", "M": P})["value"]
    pv = idm.solve({"kind": "project", "v": [1, 2, 3], "basis": [[1, 0, 0], [0, 1, 0]]})["value"]
    assert pv[0]["exact"] == "1" and pv[2]["exact"] == "0"


def test_spectral_per_instance_tier():
    # rational spectrum -> exact
    sd = idm.solve({"kind": "spectral_decomposition", "M": [[2, 1], [1, 2]]})
    assert sd["tier"] == "exact" and sorted(e["exact"] for e in sd["value"]["eigenvalues"]) == ["1", "3"]
    # irrational spectrum -> finite_diagnostic with a certified residual, NEVER exact
    sd2 = idm.solve({"kind": "spectral_decomposition", "M": [[0, 1], [1, 1]]})
    assert sd2["tier"] == "finite_diagnostic" and "error_bound" in sd2
    # non-normal -> HOLD
    assert idm.solve({"kind": "spectral_decomposition", "M": [[1, 1], [0, 1]]})["status"] == "HOLD"
    # operator_norm is ALWAYS finite_diagnostic
    on = idm.solve({"kind": "operator_norm", "M": [[3, 0], [0, 4]]})
    assert on["tier"] == "finite_diagnostic" and abs(on["value"]["float"] - 4) < 1e-9


def test_composite_and_separability():
    tp = idm.solve({"kind": "tensor_product", "a": [1, 2], "b": [3, 4]})["value"]
    assert [x["exact"] for x in tp] == ["3", "4", "6", "8"]
    choi = idm.solve({"kind": "choi_matrix", "cp_map_generators": [[[1, 0], [0, 1]]]})["value"]
    assert idm.solve({"kind": "is_completely_positive", "choi": choi})["value"]["completely_positive"]
    # a maximally-correlated (Bell) state is entangled -> exact negative-PT witness
    bell = [["1/2" if (a, b) in ((0, 0), (0, 3), (3, 0), (3, 3)) else 0 for b in range(4)] for a in range(4)]
    be = idm.solve({"kind": "is_separable_ppt", "rho": bell, "dims": [2, 2]})
    assert be["value"]["separable"] is False


def test_plus_r_fence_enforced_in_code():
    """the +ℝ fence: idm/hilbert.py must NOT import idm/hilbert_open.py (one-directional)."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "idm", "hilbert.py")).read()
    tree = ast.parse(src)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported += [n.name for n in node.names]
        if isinstance(node, ast.Import):
            imported += [n.name for n in node.names]
    assert not any("hilbert_open" in name for name in imported), \
        "fence violated: hilbert.py imports hilbert_open — infinite-dim objects could leak into the exact core"


def test_plus_r_open_never_certified():
    """every hilbert_open kind returns status +R_OPEN with NO plain value field — solve() cannot emit it
    as a certified answer."""
    r = idm.solve({"kind": "infinite_spectral_readout", "operator_description": "d/dx"})
    assert r["status"] == "+R_OPEN" and r["tier"] == "+ℝ-Open" and "value" not in r
    r2 = idm.solve({"kind": "L2_readout", "values_on_mesh": [1, 1, 1], "weights": ["1/3", "1/3", "1/3"]})
    assert r2["status"] == "+R_OPEN" and "approximant" in r2 and "value" not in r2
