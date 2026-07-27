#!/usr/bin/env python3
"""Retained Spectral B3 statistics — bootstrap speedup CI verdict logic.

Run: PYTHONPATH=. python3 -m pytest tests/test_benchmark_stats.py -q
"""

from __future__ import annotations

from retained_spectral.competition import stats as ST


def test_summarize_reports_median_iqr_n():
    s = ST.summarize([0.001, 0.002, 0.003, 0.004, 0.005])
    assert s["n_samples"] == 5
    assert abs(s["median_ms"] - 3.0) < 1e-9      # 0.003 s -> 3 ms
    assert s["iqr_ms"][0] <= s["median_ms"] <= s["iqr_ms"][1]


def test_speedup_ci_native_faster_when_ci_above_one():
    # native ~1ms, competitor ~3ms, tight -> CI entirely above 1
    native = [0.0010, 0.0011, 0.0010, 0.0009, 0.0010, 0.0011]
    other = [0.0030, 0.0031, 0.0029, 0.0030, 0.0032, 0.0030]
    r = ST.speedup_ci(native, other)
    assert r["ci95_low"] > 1.0 and r["verdict"] == "native_faster"
    assert 2.5 < r["ratio_median"] < 3.5


def test_speedup_ci_competitor_faster_when_ci_below_one():
    native = [0.0030, 0.0031, 0.0029, 0.0030, 0.0032, 0.0030]
    other = [0.0010, 0.0011, 0.0010, 0.0009, 0.0010, 0.0011]
    r = ST.speedup_ci(native, other)
    assert r["ci95_high"] < 1.0 and r["verdict"] == "competitor_faster"


def test_speedup_ci_tie_when_ci_straddles_one():
    # overlapping distributions -> CI crosses 1 -> tie
    native = [0.0010, 0.0012, 0.0011, 0.0009, 0.0013, 0.0010]
    other = [0.0011, 0.0009, 0.0012, 0.0010, 0.0011, 0.0012]
    r = ST.speedup_ci(native, other)
    assert r["ci95_low"] <= 1.0 <= r["ci95_high"] and r["verdict"] == "tie"


def test_speedup_ci_is_deterministic():
    native = [0.001, 0.002, 0.0015, 0.0012, 0.0018]
    other = [0.003, 0.004, 0.0035, 0.0031, 0.0038]
    a = ST.speedup_ci(native, other)
    b = ST.speedup_ci(native, other)
    assert a == b   # fixed recorded seed


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
