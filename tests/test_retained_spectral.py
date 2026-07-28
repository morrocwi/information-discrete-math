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


# ---------------------------------------------------------------- consolidated credibility layer


def test_scipy_pipeline_finds_far_off_center_well():
    """The consolidated SciPy pipeline uses an unbounded expanding well search — a harmonic well
    centred at 80 (far outside the old fixed [-32, 32] box) must still be located and solved."""
    problem = engine.RawSpectralProblem(
        name="c80", potential="harmonic",
        parameters=(("omega", 1.0), ("center", 80.0)), modes=4, tolerance=5e-7,
    )
    result = scipy_pipeline.scipy_raw_input_readout(problem)
    assert result.status == "ACCEPT"
    lo, hi = result.window
    assert lo <= 80.0 <= hi                       # the discovered window brackets the true centre
    for got, want in zip(result.values, (0.5, 1.5, 2.5, 3.5)):
        assert abs(got - want) <= problem.tolerance


def test_credibility_audit_exposes_adversarial_suite():
    """The consolidated credibility audit (imports repointed off the removed *_strict modules)
    must import and declare its adversarial suite, including the far-off-origin well."""
    from retained_spectral.competition import credibility_audit as ca

    targets = ca.adversarial_targets()
    assert len(targets) == 8
    names = {t.problem.name for t in targets}
    assert "audit_harmonic_center80" in names     # the far-centred stressor
    assert "audit_factorized_double_well" in names


def test_negative_controls_winner_instrument_is_falsifiable():
    """The B6 falsifiability control: the SAME bootstrap-CI verdict function that certifies native's
    wins must report a COMPETITOR win when the data shows one — proving the winner is read from data,
    not hardcoded to native. Checked in all three directions on small, fast stress sizes."""
    from retained_spectral.competition import credibility_audit as ca

    # small stress sizes keep the test fast; the winner-selection instrument (part 1) is the real check
    result = ca.run_negative_controls(repeats=5, stress_specs=(("floor", 16, 1), ("small", 128, 127)))
    instrument = result["winner_selection_instrument"]
    assert instrument["competitor_faster_case"] == "competitor_faster"   # not rigged to native
    assert instrument["native_faster_case"] == "native_faster"
    assert instrument["tie_case"] == "tie"
    assert result["winner_logic_honest"] is True
    # part 2: the stress cases ran, agreed with scipy, and each carries a MEASURED (not asserted) verdict
    assert result["all_cross_checks"] is True
    for case in result["stress_cases"].values():
        assert case["cross_check_ok"] is True
        assert case["measured_verdict"] in ("native_faster", "competitor_faster", "tie")


def test_negative_controls_are_a_credibility_gate():
    """The winner-logic honesty + stress cross-checks must be wired into credibility_gates, so a rig
    that always reported native as winner would flip the audit to HOLD, not pass silently."""
    from retained_spectral.competition import credibility_audit as ca

    src = ca.run_credibility_audit.__doc__ or ""
    # the gate keys must exist in the function body (cheap structural check without the slow full run)
    import inspect
    body = inspect.getsource(ca.run_credibility_audit)
    assert "negative_controls_winner_logic_honest" in body
    assert "negative_controls_cross_checks_all" in body
    assert "run_negative_controls(" in body


def test_run_competition_reports_gates_and_provenance(monkeypatch):
    """run_competition records the strict gates (both pipelines must ACCEPT), the source commit,
    the frozen thread environment, and the seeded ordering — the provenance the audit gates on."""
    monkeypatch.setenv("GITHUB_SHA", "unit-test-sha")
    from retained_spectral.competition.run import run_competition

    if not engine.NATIVE_KERNEL_COMPILED:
        pytest.skip("run_competition fails closed without the compiled kernel (no numba)")
    result = run_competition(repeats=2, audit_repeats=1, include_jax=False)
    gates = result["verdict_gates"]
    for key in ("native_correct_all", "scipy_correct_all", "native_accept_all",
                "scipy_accept_all", "speed_ci_native_faster_all"):
        assert key in gates
    assert result["source_commit"] == "unit-test-sha"
    assert result["end_to_end"]["seed"] == 20260727
    assert "thread_environment" in result["environment"]
    # the compiled-path disclosure must be recorded (so a numba-less run is self-disclosing)
    from retained_spectral.engine import NATIVE_KERNEL_COMPILED
    assert result["environment"]["native_kernel_compiled"] == bool(NATIVE_KERNEL_COMPILED)
    assert result["environment"]["kernel_field"] == "compiled"   # guarded above


def test_require_compiled_kernel_fails_closed(monkeypatch):
    """A timing-bearing path must HOLD (raise), not silently run ~70x slower, without the compiled kernel."""
    require_compiled_kernel = engine.require_compiled_kernel
    # available path: no raise
    monkeypatch.setattr(engine, "NATIVE_KERNEL_COMPILED", True)
    require_compiled_kernel("ok-path")
    # absent path: fail closed with a HOLD message pointing at the [spectral-bench] install
    monkeypatch.setattr(engine, "NATIVE_KERNEL_COMPILED", False)
    with pytest.raises(RuntimeError, match="HOLD"):
        require_compiled_kernel("speed test")


def test_three_layer_correctness_passes_declared_cases():
    """B4 — every declared spectrum passes all three independent correctness layers (analytic
    reference, extended-precision same-operator recomputation, Sturm sign-count certificate)."""
    from retained_spectral.competition.correctness import three_layer_case

    for target in engine.raw_benchmark_targets()[:3]:      # a fast representative subset
        rec = three_layer_case(target.problem, target.reference)
        assert rec["ok"], (target.problem.name, rec["layers"])
        assert rec["layers"]["extended_precision_ok"]
        assert rec["layers"]["sturm_certificate_ok"]


def test_sturm_certificate_rejects_a_wrong_eigenvalue():
    """The Sturm index certificate is a real gate: move one eigenvalue off its true position and the
    sign-count must stop bracketing it at the right index (a negative control)."""
    from retained_spectral.competition.correctness import sturm_index_certificate

    target = engine.raw_benchmark_targets()[0]
    native = engine.retained_raw_input_readout(target.problem)
    diag, off, _ = engine.retained_tridiagonal(target.problem, native.window, 768)
    good = list(map(float, engine.native_eigvals_from_tridiagonal(
        diag, off, target.problem.modes, target.problem.tolerance)))
    assert sturm_index_certificate(diag, off, good, abs_delta=1e-6)["ok"]

    bad = list(good)
    bad[-1] = bad[-1] + 5.0                                # a grossly wrong top eigenvalue
    assert not sturm_index_certificate(diag, off, bad, abs_delta=1e-6)["ok"]


def test_charts_render_ci_and_raw_samples(tmp_path, monkeypatch):
    """render_hero / render_detail draw from the measured record: the detail forest plot needs the
    per-case bootstrap CI and the raw samples the run now records."""
    pytest.importorskip("matplotlib")
    monkeypatch.setenv("GITHUB_SHA", "chart-test")
    from retained_spectral.competition.run import run_competition
    from retained_spectral.competition.chart import render_hero, render_detail

    data = run_competition(repeats=3, audit_repeats=2, include_jax=False)
    # the record must carry the raw samples + per-case CI the new charts consume
    a_case = next(iter(data["end_to_end"]["cases"].values()))
    assert a_case["native_stats"]["samples_ms"]
    assert "ci95_low" in a_case["scipy_speedup_over_native"]

    hero = render_hero(data, tmp_path / "hero.png")
    detail = render_detail(data, tmp_path / "detail.png")
    assert hero.stat().st_size > 5000
    assert detail.stat().st_size > 5000


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
