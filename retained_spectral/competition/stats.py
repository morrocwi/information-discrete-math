"""Timing statistics for the Retained Spectral competition (B3).

A speed claim needs more than a single median. ``summarize`` reports median / IQR / MAD / n from a
sample of hot calls; ``speedup_ci`` gives a 95% bootstrap confidence interval for the speedup
``median(other) / median(native)`` so a win/tie/loss is read from the interval, not one number:

* native win  — the CI lower bound is > 1,
* statistical tie — the CI straddles 1,
* competitor win — the CI upper bound is < 1.

Deterministic: the bootstrap uses a fixed, recorded seed so the interval reproduces exactly.
"""

from __future__ import annotations

import statistics
from typing import Sequence

import numpy as np

BOOTSTRAP_SEED = 20260727
BOOTSTRAP_RESAMPLES = 4000


def summarize(seconds: Sequence[float]) -> dict:
    s = [x * 1e3 for x in seconds]          # milliseconds
    n = len(s)
    med = float(statistics.median(s))
    if n >= 2:
        q1, q3 = float(np.percentile(s, 25)), float(np.percentile(s, 75))
        mad = float(np.median(np.abs(np.asarray(s) - med)))
    else:
        q1 = q3 = med
        mad = 0.0
    return {"median_ms": med, "iqr_ms": [q1, q3], "mad_ms": mad, "n_samples": n}


def speedup_ci(native_seconds: Sequence[float], other_seconds: Sequence[float], *,
               seed: int = BOOTSTRAP_SEED, resamples: int = BOOTSTRAP_RESAMPLES) -> dict:
    """95% bootstrap CI of median(other)/median(native) — how many times slower ``other`` is."""
    a = np.asarray(native_seconds, dtype=float)
    b = np.asarray(other_seconds, dtype=float)
    point = float(np.median(b) / np.median(a))
    if len(a) < 2 or len(b) < 2:
        return {"ratio_median": point, "ci95_low": point, "ci95_high": point,
                "verdict": "insufficient-samples", "resamples": 0, "seed": seed}
    rng = np.random.default_rng(seed)
    boot = np.empty(resamples)
    for i in range(resamples):
        ra = rng.choice(a, size=len(a), replace=True)
        rb = rng.choice(b, size=len(b), replace=True)
        boot[i] = np.median(rb) / np.median(ra)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    verdict = "native_faster" if lo > 1.0 else ("competitor_faster" if hi < 1.0 else "tie")
    return {"ratio_median": point, "ci95_low": lo, "ci95_high": hi,
            "verdict": verdict, "resamples": resamples, "seed": seed}


__all__ = ["summarize", "speedup_ci", "BOOTSTRAP_SEED", "BOOTSTRAP_RESAMPLES"]
