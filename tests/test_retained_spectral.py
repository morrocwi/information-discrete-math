#!/usr/bin/env python3
"""Contract, correctness, and reproducibility tests for Retained Spectral.

Run with::

    PYTHONPATH=. python3 -m pytest tests/test_retained_spectral.py -q
"""

from __future__ import annotations

import dataclasses
import inspect

import pytest

# numpy / retained_spectral are BENCH-only deps (see requirements-bench.txt); the core solver CI
# installs only mpmath+sympy. Skip this whole module cleanly when numpy is absent, instead of a hard
# collection error — the benchmark suite runs wherever the bench deps are installed.
np = pytest.importorskip("numpy")

import retained_spectral as rs
from retained_spectral import engine
from retained_spectral.competition import scipy_pipeline
from retained_spectral.competition.executor_audit import executor_audit_case


# ---------------------------------------------------------------- correctness
def test_harmonic_matches_analytic_spectrum():
    result = rs.solve(rs.examples()["harmonic_low4"])
    assert result.status == "ACCEPT"
    np.testing.assert_allclose(result.values, [0.5, 1.5, 2.5, 3.5], atol=1e-6)


def test_make_problem_scaled_harmonic():
    problem = rs.make_problem(
        name="w2",
        family="harmonic",
        parameters={"omega": 2.0, "center": 0.0},
        modes=3,
        tolerance=1e-8,
    )
    np.testing.assert_allclose(rs.solve(problem).values, [1.0, 3.0, 5.0], atol=1e-6)


@pytest.mark.parametrize("target", rs.example_targets(), ids=lambda t: t.problem.name)
def test_all_targets_hit_published_references(target):
    result = rs.solve(target.problem)
    assert result.status == "ACCEPT"
    reference = np.asarray(target.reference)
    values = np.asarray(result.values[: len(reference)])
    max_error = float(np.max(np.abs(values - reference)))
    assert max_error <= max(target.problem.tolerance, 1e-6), (
        f"{target.problem.name}: error {max_error:g}"
    )


def test_make_problem_rejects_unknown_family():
    with pytest.raises(ValueError):
        rs.make_problem(
            name="bad", family="not_a_potential", parameters={}, modes=1
        )


# -------------------------------------------------------------------- contract
def test_problem_input_carries_no_calibration():
    fields = {f.name for f in dataclasses.fields(rs.SpectralProblem)}
    assert fields == {"name", "potential", "parameters", "modes", "tolerance"}
    forbidden = {"window", "mesh", "reference", "intervals", "operator", "hint"}
    assert not (fields & forbidden)


def test_native_engine_imports_no_external_solver():
    source = inspect.getsource(engine)
    assert "import scipy" not in source
    assert "from scipy" not in source
    assert "import jax" not in source
    assert "from jax" not in source


def test_scipy_competitor_does_not_receive_native_operator():
    # The independent SciPy pipeline may read raw potential samples, but must
    # not import the native operator builder or the native readout kernel.
    source = inspect.getsource(scipy_pipeline)
    assert "retained_tridiagonal" not in source
    assert "_finite_native_readout" not in source
    assert "retained_raw_input_readout" not in source
    # It solves from the same raw contract.
    sig = inspect.signature(scipy_pipeline.scipy_raw_input_readout)
    assert list(sig.parameters)[0] == "problem"


def test_both_solvers_accept_same_raw_input():
    for name in ("harmonic_low4", "factorized_sextic_ground"):
        problem = rs.examples()[name]
        native = rs.solve(problem)
        competitor = scipy_pipeline.scipy_raw_input_readout(problem)
        assert native.status == "ACCEPT"
        assert competitor.status == "ACCEPT"
        np.testing.assert_allclose(
            native.values, competitor.values, atol=max(problem.tolerance, 1e-6)
        )


# --------------------------------------------------------------- executor audit
def test_executor_audit_cross_checks_agree():
    problem = rs.examples()["harmonic_low4"]
    record = executor_audit_case(problem, intervals=256, repeats=1, jax_bundle=None)
    solvers = record["solvers"]
    # More than one competitor must actually be exercised on the same operator.
    assert len(solvers) >= 3
    # Every competitor that ran must agree with native on the eigenvalues.
    for name, entry in solvers.items():
        if "hot_median_seconds" in entry:
            assert entry["max_abs_difference"] <= 1e-6, name
            assert entry["to_native_time_ratio"] > 0.0, name
    assert record["cross_check_ok"] is True
    # The standard tridiagonal LAPACK call must be one of the competitors.
    assert "SciPy eigh_tridiagonal" in solvers


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
