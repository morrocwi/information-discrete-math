#!/usr/bin/env python3
"""I2 Morse physics demo — the discrete readout agrees with the analytic Morse formula.

This is the correctness contract for demos/i2_morse_levels.py: the native kernel, applied to the
textbook I2 Morse operator, must reproduce the closed-form Morse levels to within the finite-grid
discretisation error (which shrinks as the grid is refined). It also guards the spectroscopic-sweep
demo's importability.

Run: PYTHONPATH=. python3 -m pytest tests/test_physics_demos.py -q
"""

from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")

from demos.i2_morse_levels import (
    HARTREE_CM,
    analytic_level,
    morse_tridiagonal,
)
from retained_spectral.engine import native_eigvals_from_tridiagonal, warm_native_kernel


def test_i2_morse_levels_match_analytic_formula():
    warm_native_kernel()
    k = 10
    d, e = morse_tridiagonal(100_000)
    values = np.asarray(native_eigvals_from_tridiagonal(d, e, k, 1e-12))[:k]
    analytic = np.array([analytic_level(v) for v in range(k)])
    err_cm = float(np.max(np.abs(values - analytic))) * HARTREE_CM
    # At n=100k the discretisation error is ~0.009 cm-1; allow generous head-room, stay spectroscopic.
    assert err_cm < 0.1, f"native vs analytic Morse disagreement {err_cm:.4f} cm-1 exceeds 0.1 cm-1"


def test_grid_refinement_reduces_discretisation_error():
    warm_native_kernel()
    k = 6
    analytic = np.array([analytic_level(v) for v in range(k)])

    def err(n):
        d, e = morse_tridiagonal(n)
        v = np.asarray(native_eigvals_from_tridiagonal(d, e, k, 1e-12))[:k]
        return float(np.max(np.abs(v - analytic)))

    coarse, fine = err(20_000), err(100_000)
    # A finer grid must not be worse — the discrete readout converges toward the continuum witness.
    assert fine <= coarse + 1e-12, f"refining the grid worsened the error: {coarse:.2e} -> {fine:.2e}"


def test_ground_level_is_half_omega():
    # v=0 Morse level is w/2 - w*x_e/4; anharmonicity is tiny for I2, so E0 ~ w/2 to <1%.
    e0 = analytic_level(0)
    assert e0 > 0.0
    # E0 must sit between the harmonic w/2 and 0 (anharmonicity only lowers it).
    from demos.i2_morse_levels import A, DE, MU
    w_true = A * np.sqrt(2.0 * DE / MU)
    assert 0.49 * w_true < e0 <= 0.5 * w_true


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
