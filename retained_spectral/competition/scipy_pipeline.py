#!/usr/bin/env python3
"""Independent SciPy-backed pipeline for the raw-input spectral competition.

This module receives the same ``RawSpectralProblem`` as the native solver but
receives no native window, mesh, bracket, tridiagonal operator, witness, or
reference value.  It owns its minimization, discretization, refinement,
window expansion, and verdict.  Richardson is included so the competitor is
not weakened to a naive direct-grid baseline.
"""

from __future__ import annotations

import math
import time

import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import minimize_scalar

from retained_spectral.engine import (
    RawSpectralProblem,
    RawSpectralResult,
    potential_values,
)


def _scipy_tridiagonal(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    intervals: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Competitor-owned finite-difference construction from raw samples."""

    left, right = window
    spacing = (right - left) / intervals
    points = left + spacing * np.arange(1, intervals, dtype=np.float64)
    diagonal = 1.0 / spacing**2 + potential_values(problem, points)
    off_diagonal = np.full(
        intervals - 2,
        -0.5 / spacing**2,
        dtype=np.float64,
    )
    return diagonal, off_diagonal


def _initial_window(
    problem: RawSpectralProblem,
) -> tuple[float, tuple[float, float]]:
    """SciPy-owned bounded minimization and curvature scale."""

    def scalar_potential(value: float) -> float:
        return float(
            potential_values(problem, np.asarray((value,), dtype=np.float64))[0]
        )

    search = minimize_scalar(
        scalar_potential,
        bounds=(-32.0, 32.0),
        method="bounded",
        options={"xatol": 1.0e-7},
    )
    center = float(search.x)
    step = 1.0e-3 * (1.0 + abs(center))
    curvature = max(
        (
            scalar_potential(center - step)
            - 2.0 * scalar_potential(center)
            + scalar_potential(center + step)
        )
        / step**2,
        0.0,
    )
    scale = curvature ** -0.25 if curvature > 1.0e-3 else 1.0
    half_width = min(max(8.0 * scale, 2.0), 16.0)
    return scale, (center - half_width, center + half_width)


def _turning_tail_pass(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    energy: float,
    side: str,
) -> bool:
    """Competitor-owned finite decay check."""

    left, right = window
    grid = np.linspace(left, right, 1025)
    values = potential_values(problem, grid)
    allowed = values <= energy
    if not np.any(allowed):
        return False
    if side == "left":
        allowed_index = int(np.argmax(allowed))
        boundary_value = float(values[0])
        distance = float(grid[allowed_index] - left)
    else:
        allowed_index = int(len(allowed) - 1 - np.argmax(allowed[::-1]))
        boundary_value = float(values[-1])
        distance = float(right - grid[allowed_index])
    barrier = boundary_value - energy
    if barrier <= 0.0:
        return False
    score = 2.0 * math.sqrt(2.0 * barrier) * distance
    required = -math.log(max(problem.tolerance * 0.05, 1.0e-15))
    return score >= required


def _expanded_window(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    energy: float,
    scale: float,
) -> tuple[tuple[float, float], bool]:
    left, right = window
    width = right - left
    step = max(0.5 * width, 4.0 * scale)
    left_pass = _turning_tail_pass(problem, window, energy, "left")
    right_pass = _turning_tail_pass(problem, window, energy, "right")
    if left_pass and right_pass:
        margin = max(2.0 * scale, 0.1 * width)
        return (left - margin, right + margin), True
    return (
        left if left_pass else left - step,
        right if right_pass else right + step,
    ), False


def _richardson_mesh(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    initial_intervals: int,
    max_intervals: int,
) -> tuple[np.ndarray, np.ndarray, int, int, int]:
    spectra: list[np.ndarray] = []
    solve_intervals: list[int] = []
    intervals = max(64, initial_intervals)
    solves = 0
    peak_bytes = 0
    shift = np.full(problem.modes, math.inf)
    while intervals <= max_intervals:
        diagonal, off_diagonal = _scipy_tridiagonal(
            problem,
            window,
            intervals,
        )
        values = eigh_tridiagonal(
            diagonal,
            off_diagonal,
            select="i",
            select_range=(0, problem.modes - 1),
            eigvals_only=True,
            check_finite=False,
        )
        spectra.append(np.asarray(values))
        solve_intervals.append(intervals)
        solves += 1
        peak_bytes = max(peak_bytes, diagonal.nbytes + off_diagonal.nbytes)
        if len(spectra) >= 3:
            coarse, fine, finest = spectra[-3:]
            richardson_coarse = (4.0 * fine - coarse) / 3.0
            richardson_fine = (4.0 * finest - fine) / 3.0
            shift = np.abs(richardson_fine - richardson_coarse)
            if float(np.max(shift)) <= 0.45 * problem.tolerance:
                return (
                    richardson_fine,
                    shift,
                    solve_intervals[-1],
                    solves,
                    peak_bytes,
                )
        intervals *= 2
    if len(spectra) < 3:
        raise RuntimeError("SciPy mesh cap did not admit three grids")
    coarse, fine, finest = spectra[-3:]
    richardson_coarse = (4.0 * fine - coarse) / 3.0
    richardson_fine = (4.0 * finest - fine) / 3.0
    return (
        richardson_fine,
        np.abs(richardson_fine - richardson_coarse),
        solve_intervals[-1],
        solves,
        peak_bytes,
    )


def scipy_raw_input_readout(
    problem: RawSpectralProblem,
    *,
    max_intervals: int = 1_048_576,
    max_window_rounds: int = 8,
) -> RawSpectralResult:
    """End-to-end SciPy pipeline from the same uncalibrated input."""

    started = time.perf_counter()
    scale, window = _initial_window(problem)
    initial_intervals = max(
        64,
        2 ** math.ceil(
            math.log2(
                max((window[1] - window[0]) / scale * 8.0, 64.0)
            )
        ),
    )
    total_solves = 0
    peak_bytes = 0
    values: np.ndarray | None = None
    mesh_shift = np.full(problem.modes, math.inf)
    window_shift = np.full(problem.modes, math.inf)
    finest = initial_intervals
    reason = "window rounds exhausted"

    for _round in range(max_window_rounds):
        values, mesh_shift, finest, solves, working = _richardson_mesh(
            problem,
            window,
            initial_intervals,
            max_intervals,
        )
        total_solves += solves
        peak_bytes = max(peak_bytes, working)
        expanded, tail_pass = _expanded_window(
            problem,
            window,
            float(values[-1]),
            scale,
        )
        ratio = (expanded[1] - expanded[0]) / (window[1] - window[0])
        expanded_initial = max(64, int(round(initial_intervals * ratio)))
        (
            expanded_values,
            expanded_mesh_shift,
            expanded_finest,
            solves,
            working,
        ) = _richardson_mesh(
            problem,
            expanded,
            expanded_initial,
            max_intervals,
        )
        total_solves += solves
        peak_bytes = max(peak_bytes, working)
        window_shift = np.abs(expanded_values - values)
        diagnostic = expanded_mesh_shift + window_shift
        values = expanded_values
        mesh_shift = expanded_mesh_shift
        finest = expanded_finest
        window = expanded
        if tail_pass and float(np.max(diagnostic)) <= problem.tolerance:
            reason = "Richardson mesh, decay-boundary, and window gates passed"
            break
        initial_intervals = expanded_initial

    assert values is not None
    diagnostic = mesh_shift + window_shift
    status = (
        "ACCEPT"
        if float(np.max(diagnostic)) <= problem.tolerance
        else "HOLD"
    )
    return RawSpectralResult(
        method="Independent SciPy Richardson-stability pipeline",
        status=status,
        values=tuple(float(value) for value in values),
        mesh_shift=tuple(float(value) for value in mesh_shift),
        window_shift=tuple(float(value) for value in window_shift),
        diagnostic_bounds=tuple(float(value) for value in diagnostic),
        window=window,
        finest_intervals=finest,
        solve_count=total_solves,
        recurrence_updates=0,
        peak_working_bytes=peak_bytes,
        elapsed_seconds=time.perf_counter() - started,
        reference_used_for_planning=False,
        per_case_schedule=False,
        tier="finite_diagnostic",
        reason=reason,
    )


__all__ = ["scipy_raw_input_readout"]
