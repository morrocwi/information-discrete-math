#!/usr/bin/env python3
"""Reference-blind spectral planning from the same raw input.

Both pipelines in this module receive only::

    (potential family, finite parameters, requested low modes, tolerance)

No per-problem window, mesh, expansion schedule, reference value, or retained
operator is part of the input.  The native path is Retained Multilevel Sturm
(RMS): it locates a finite well, admits boundaries by a finite decay gate,
reuses coarse eigenvalue brackets on finer meshes, evaluates all requested
Sturm counts in one compiled traversal, and stops as soon as mesh and window
witnesses fit the declared tolerance.

The SciPy path is deliberately independent.  It locates its own well, builds
its own windows and meshes, calls ``scipy.linalg.eigh_tridiagonal`` from raw
potential samples, and uses direct adjacent-grid stability (no RSR operator or
plan is passed to it).  SciPy is therefore an execution dependency of the
competitor only, never of the native method.

The continuum/infinite-line expression names the target.  Every executable
object here is a finite array and every verdict is ``finite_diagnostic``.
"""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

try:
    from numba import njit
except ImportError:  # pragma: no cover - exercised on dependency-light CI
    njit = None


@dataclass(frozen=True)
class RawSpectralProblem:
    """The complete solver input; intentionally contains no calibration."""

    name: str
    potential: str
    parameters: tuple[tuple[str, float], ...]
    modes: int
    tolerance: float

    def parameter_dict(self) -> dict[str, float]:
        return dict(self.parameters)


@dataclass(frozen=True)
class RawBenchmarkTarget:
    """Raw input plus a comparator used only after both solvers return."""

    problem: RawSpectralProblem
    reference: tuple[float, ...]
    reference_kind: str


@dataclass(frozen=True)
class RawSpectralResult:
    method: str
    status: str
    values: tuple[float, ...]
    mesh_shift: tuple[float, ...]
    window_shift: tuple[float, ...]
    diagnostic_bounds: tuple[float, ...]
    window: tuple[float, float]
    finest_intervals: int
    solve_count: int
    recurrence_updates: int
    peak_working_bytes: int
    elapsed_seconds: float
    reference_used_for_planning: bool
    per_case_schedule: bool
    tier: str
    reason: str


def raw_benchmark_targets() -> tuple[RawBenchmarkTarget, ...]:
    """Seven targets; references are never exposed to either solver."""

    omega = 16.0
    lam_pt = 3.0
    morse_lambda = 5.0
    morse_a = 1.0
    morse_depth = (morse_lambda * morse_a) ** 2 / 2.0

    def target(
        name: str,
        potential: str,
        parameters: tuple[tuple[str, float], ...],
        modes: int,
        tolerance: float,
        reference: Sequence[float],
        reference_kind: str,
    ) -> RawBenchmarkTarget:
        return RawBenchmarkTarget(
            RawSpectralProblem(
                name=name,
                potential=potential,
                parameters=parameters,
                modes=modes,
                tolerance=tolerance,
            ),
            tuple(float(value) for value in reference),
            reference_kind,
        )

    return (
        target(
            "harmonic_low4",
            "harmonic",
            (("omega", 1.0), ("center", 0.0)),
            4,
            2.0e-8,
            tuple(n + 0.5 for n in range(4)),
            "analytic",
        ),
        target(
            "displaced_harmonic_low4",
            "harmonic",
            (("omega", 1.0), ("center", 7.0)),
            4,
            2.0e-8,
            tuple(n + 0.5 for n in range(4)),
            "analytic",
        ),
        target(
            "squeezed_harmonic_omega16_low4",
            "harmonic",
            (("omega", omega), ("center", 0.0)),
            4,
            4.0e-7,
            tuple(omega * (n + 0.5) for n in range(4)),
            "analytic",
        ),
        target(
            "poschl_teller_lambda3_all_bound",
            "poschl_teller",
            (("lambda", lam_pt),),
            3,
            3.0e-7,
            tuple(-0.5 * (lam_pt - n) ** 2 for n in range(3)),
            "analytic",
        ),
        target(
            "morse_lambda5_all_bound",
            "morse",
            (("a", morse_a), ("depth", morse_depth)),
            5,
            1.0e-6,
            tuple(
                -0.5 * morse_a**2 * (morse_lambda - n - 0.5) ** 2
                for n in range(5)
            ),
            "analytic",
        ),
        target(
            "factorized_sextic_ground",
            "factorized_sextic",
            (("a", 1.0),),
            1,
            2.0e-8,
            (0.0,),
            "factorization",
        ),
        target(
            "pure_quartic_ground",
            "pure_quartic",
            (("coupling", 0.25),),
            1,
            2.0e-8,
            (0.420804974478,),
            "published numerical comparator",
        ),
    )


def potential_values(
    problem: RawSpectralProblem,
    x: np.ndarray,
) -> np.ndarray:
    """Evaluate only the declared finite potential samples."""

    p = problem.parameter_dict()
    if problem.potential == "harmonic":
        return 0.5 * p["omega"] ** 2 * (x - p["center"]) ** 2
    if problem.potential == "poschl_teller":
        lam = p["lambda"]
        return -0.5 * lam * (lam + 1.0) / np.cosh(x) ** 2
    if problem.potential == "morse":
        exponent = np.clip(-p["a"] * x, -350.0, 350.0)
        exp_term = np.exp(exponent)
        return p["depth"] * (exp_term**2 - 2.0 * exp_term)
    if problem.potential == "factorized_sextic":
        a = p["a"]
        wp = x**3 + a * x
        wpp = 3.0 * x**2 + a
        return 0.5 * (wp**2 - wpp)
    if problem.potential == "pure_quartic":
        return p["coupling"] * x**4
    raise ValueError(f"unknown potential: {problem.potential}")


def retained_tridiagonal(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    intervals: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Build one finite second-difference operator from raw potential data."""

    left, right = window
    if not right > left:
        raise ValueError("window must have positive length")
    if intervals < 16:
        raise ValueError("intervals must be at least 16")
    spacing = (right - left) / intervals
    points = left + spacing * np.arange(1, intervals, dtype=np.float64)
    diagonal = 1.0 / spacing**2 + potential_values(problem, points)
    off_diagonal = np.full(
        intervals - 2,
        -0.5 / spacing**2,
        dtype=np.float64,
    )
    return diagonal, off_diagonal, spacing


def _sturm_count_python(
    diagonal: np.ndarray,
    off_diagonal: np.ndarray,
    threshold: float,
) -> int:
    tiny = 1.0e-300
    pivot = diagonal[0] - threshold
    count = int(pivot < 0.0)
    if abs(pivot) < tiny:
        pivot = -tiny
    for index in range(1, diagonal.size):
        coupling = off_diagonal[index - 1]
        pivot = diagonal[index] - threshold - coupling * coupling / pivot
        if pivot < 0.0:
            count += 1
        if abs(pivot) < tiny:
            pivot = -tiny
    return count


def _batched_bisection_python(
    diagonal: np.ndarray,
    off_diagonal: np.ndarray,
    lows: np.ndarray,
    highs: np.ndarray,
    tolerance: float,
    max_steps: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Share one diagonal traversal across all active requested modes."""

    modes = lows.size
    lo = lows.copy()
    hi = highs.copy()
    steps = np.zeros(modes, dtype=np.int64)
    mids = np.empty(modes, dtype=np.float64)
    pivots = np.empty(modes, dtype=np.float64)
    counts = np.empty(modes, dtype=np.int64)
    active = np.empty(modes, dtype=np.int64)
    tiny = 1.0e-300

    for _iteration in range(max_steps):
        active_count = 0
        for mode in range(modes):
            if hi[mode] - lo[mode] > tolerance:
                active[active_count] = mode
                active_count += 1
                mids[mode] = lo[mode] + 0.5 * (hi[mode] - lo[mode])
                pivot = diagonal[0] - mids[mode]
                pivots[mode] = -tiny if abs(pivot) < tiny else pivot
                counts[mode] = int(pivots[mode] < 0.0)
        if active_count == 0:
            break

        for index in range(1, diagonal.size):
            coupling_sq = off_diagonal[index - 1] ** 2
            value = diagonal[index]
            for slot in range(active_count):
                mode = active[slot]
                pivot = value - mids[mode] - coupling_sq / pivots[mode]
                if abs(pivot) < tiny:
                    pivot = -tiny
                pivots[mode] = pivot
                if pivot < 0.0:
                    counts[mode] += 1

        for slot in range(active_count):
            mode = active[slot]
            if counts[mode] <= mode:
                lo[mode] = mids[mode]
            else:
                hi[mode] = mids[mode]
            steps[mode] += 1

    return 0.5 * (lo + hi), steps


if njit is not None:
    _sturm_count_native = njit(cache=True)(_sturm_count_python)
    _batched_bisection_native = njit(cache=True)(
        _batched_bisection_python
    )
else:  # pragma: no cover - dependency-light fallback
    _sturm_count_native = _sturm_count_python
    _batched_bisection_native = _batched_bisection_python

# Whether the native Sturm kernel is actually the Numba/LLVM-compiled path. The pure-Python fallback is
# numerically IDENTICAL (same exact float64 recurrence) but MUCH slower, so any wall-clock speed claim
# holds only when this is True. Benchmarks record it so a run without Numba is self-disclosing rather
# than silently reporting slow numbers as if they were the compiled field.
NATIVE_KERNEL_COMPILED = njit is not None


def warm_native_kernel() -> None:
    diagonal = np.asarray((2.0, 2.0, 2.0), dtype=np.float64)
    off_diagonal = np.asarray((-1.0, -1.0), dtype=np.float64)
    lows = np.asarray((-1.0,), dtype=np.float64)
    highs = np.asarray((3.0,), dtype=np.float64)
    _sturm_count_native(diagonal, off_diagonal, 0.0)
    _batched_bisection_native(
        diagonal,
        off_diagonal,
        lows,
        highs,
        1.0e-8,
        64,
    )


@dataclass(frozen=True)
class _FiniteReadout:
    values: np.ndarray
    intervals: int
    updates: int
    working_bytes: int


def _global_bounds(
    diagonal: np.ndarray,
    off_diagonal: np.ndarray,
) -> tuple[float, float]:
    radius = 2.0 * float(np.max(np.abs(off_diagonal)))
    return float(np.min(diagonal) - radius), float(np.max(diagonal) + radius)


def _validated_brackets(
    diagonal: np.ndarray,
    off_diagonal: np.ndarray,
    modes: int,
    hints: np.ndarray | None,
    hint_radius: np.ndarray | None,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Build valid Sturm brackets without assuming a continuum value."""

    global_low, global_high = _global_bounds(diagonal, off_diagonal)
    if hints is None:
        return (
            np.full(modes, global_low, dtype=np.float64),
            np.full(modes, global_high, dtype=np.float64),
            0,
        )

    lows = np.empty(modes, dtype=np.float64)
    highs = np.empty(modes, dtype=np.float64)
    count_updates = 0
    for mode in range(modes):
        radius = max(
            float(hint_radius[mode]) if hint_radius is not None else 0.0,
            1.0e-5 * (1.0 + abs(float(hints[mode]))),
        )
        low = max(global_low, float(hints[mode]) - radius)
        high = min(global_high, float(hints[mode]) + radius)
        for _ in range(32):
            low_count = int(_sturm_count_native(diagonal, off_diagonal, low))
            high_count = int(
                _sturm_count_native(diagonal, off_diagonal, high)
            )
            count_updates += 2 * diagonal.size
            if low_count <= mode and high_count > mode:
                break
            radius *= 2.0
            low = max(global_low, float(hints[mode]) - radius)
            high = min(global_high, float(hints[mode]) + radius)
        else:
            low, high = global_low, global_high
        lows[mode] = low
        highs[mode] = high
    return lows, highs, count_updates


def _finite_native_readout(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    intervals: int,
    *,
    energy_tolerance: float,
    hints: np.ndarray | None = None,
    hint_radius: np.ndarray | None = None,
) -> _FiniteReadout:
    diagonal, off_diagonal, _spacing = retained_tridiagonal(
        problem,
        window,
        intervals,
    )
    lows, highs, validation_updates = _validated_brackets(
        diagonal,
        off_diagonal,
        problem.modes,
        hints,
        hint_radius,
    )
    values, steps = _batched_bisection_native(
        diagonal,
        off_diagonal,
        lows,
        highs,
        energy_tolerance,
        96,
    )
    updates = validation_updates + int(diagonal.size * np.sum(steps))
    return _FiniteReadout(
        values=np.asarray(values),
        intervals=intervals,
        updates=updates,
        working_bytes=(
            diagonal.nbytes
            + off_diagonal.nbytes
            + lows.nbytes
            + highs.nbytes
            + values.nbytes
        ),
    )


def _locate_native_well(
    problem: RawSpectralProblem,
) -> tuple[float, float, tuple[float, float]]:
    """Finite probe search; no parameter name is treated specially."""

    center = 0.0
    radius = 8.0
    minimum_index = 0
    grid = np.empty(0)
    values = np.empty(0)
    for _ in range(7):
        grid = np.linspace(center - radius, center + radius, 1025)
        values = potential_values(problem, grid)
        minimum_index = int(np.argmin(values))
        edge = 64
        if edge <= minimum_index < grid.size - edge:
            break
        center = float(grid[minimum_index])
        radius *= 2.0
    center = float(grid[minimum_index])
    probe = max(radius / 2048.0, 1.0e-4 * (1.0 + abs(center)))
    samples = potential_values(
        problem,
        np.asarray((center - probe, center, center + probe)),
    )
    curvature = max(
        float((samples[0] - 2.0 * samples[1] + samples[2]) / probe**2),
        0.0,
    )
    # A flat minimum (quartic and higher) has no harmonic length scale.
    # Treat tiny finite-probe curvature as zero instead of amplifying sample
    # roundoff into an enormous initial window.
    scale = curvature ** -0.25 if curvature > 1.0e-3 else 1.0
    half_width = min(max(8.0 * scale, 2.0), 16.0)
    return center, scale, (center - half_width, center + half_width)


def _turning_tail_pass(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    energy: float,
    side: str,
) -> bool:
    """Finite WKB-style decay gate used only to decide window expansion."""

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
    decay_score = 2.0 * math.sqrt(2.0 * barrier) * distance
    required = -math.log(max(problem.tolerance * 0.05, 1.0e-15))
    return decay_score >= required


def _expand_failed_boundaries(
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
    expanded = (
        left if left_pass else left - step,
        right if right_pass else right + step,
    )
    return expanded, left_pass and right_pass


@dataclass(frozen=True)
class _MeshReadout:
    values: np.ndarray
    finest_raw_values: np.ndarray
    mesh_shift: np.ndarray
    finest_intervals: int
    solves: int
    updates: int
    peak_bytes: int


def _native_mesh_readout(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    *,
    initial_intervals: int,
    max_intervals: int,
) -> _MeshReadout:
    """Adaptive h,h/2,h/4 Richardson readout with bracket lineage."""

    energy_tolerance = max(problem.tolerance * 0.01, 2.0e-12)
    intervals = max(64, int(initial_intervals))
    first = _finite_native_readout(
        problem,
        window,
        intervals,
        energy_tolerance=energy_tolerance,
    )
    radius = np.maximum(0.05 * (1.0 + np.abs(first.values)), 0.02)
    second = _finite_native_readout(
        problem,
        window,
        2 * intervals,
        energy_tolerance=energy_tolerance,
        hints=first.values,
        hint_radius=radius,
    )
    radius = np.maximum(4.0 * np.abs(second.values - first.values), radius / 8.0)
    third = _finite_native_readout(
        problem,
        window,
        4 * intervals,
        energy_tolerance=energy_tolerance,
        hints=second.values,
        hint_radius=radius,
    )
    solves = 3
    updates = first.updates + second.updates + third.updates
    peak_bytes = max(first.working_bytes, second.working_bytes, third.working_bytes)

    while True:
        richardson_coarse = (4.0 * second.values - first.values) / 3.0
        richardson_fine = (4.0 * third.values - second.values) / 3.0
        shift = np.abs(richardson_fine - richardson_coarse)
        if float(np.max(shift)) <= 0.45 * problem.tolerance:
            return _MeshReadout(
                values=richardson_fine,
                finest_raw_values=third.values,
                mesh_shift=shift,
                finest_intervals=third.intervals,
                solves=solves,
                updates=updates,
                peak_bytes=peak_bytes,
            )
        if 2 * third.intervals > max_intervals:
            return _MeshReadout(
                values=richardson_fine,
                finest_raw_values=third.values,
                mesh_shift=shift,
                finest_intervals=third.intervals,
                solves=solves,
                updates=updates,
                peak_bytes=peak_bytes,
            )
        first, second = second, third
        radius = np.maximum(
            4.0 * np.abs(second.values - first.values),
            8.0 * energy_tolerance,
        )
        third = _finite_native_readout(
            problem,
            window,
            2 * second.intervals,
            energy_tolerance=energy_tolerance,
            hints=second.values,
            hint_radius=radius,
        )
        solves += 1
        updates += third.updates
        peak_bytes = max(peak_bytes, third.working_bytes)


def retained_raw_input_readout(
    problem: RawSpectralProblem,
    *,
    max_intervals: int = 1_048_576,
    max_window_rounds: int = 8,
) -> RawSpectralResult:
    """Native RMS from raw input, with no reference or per-case schedule."""

    started = time.perf_counter()
    _center, scale, window = _locate_native_well(problem)
    initial_intervals = max(
        64,
        2 ** math.ceil(math.log2(max((window[1] - window[0]) / scale * 8.0, 64.0))),
    )
    total_solves = 0
    total_updates = 0
    peak_bytes = 0
    accepted_mesh: _MeshReadout | None = None
    window_shift = np.full(problem.modes, math.inf)
    reason = "window rounds exhausted"

    for _round in range(max_window_rounds):
        mesh = _native_mesh_readout(
            problem,
            window,
            initial_intervals=initial_intervals,
            max_intervals=max_intervals,
        )
        total_solves += mesh.solves
        total_updates += mesh.updates
        peak_bytes = max(peak_bytes, mesh.peak_bytes)

        expanded, tail_pass = _expand_failed_boundaries(
            problem,
            window,
            float(mesh.values[-1]),
            scale,
        )
        if tail_pass:
            margin = max(2.0 * scale, 0.1 * (window[1] - window[0]))
            expanded = (window[0] - margin, window[1] + margin)

        spacing_ratio = (expanded[1] - expanded[0]) / (window[1] - window[0])
        expanded_initial = max(
            64,
            int(round(initial_intervals * spacing_ratio)),
        )
        if tail_pass:
            # The accepted three-level mesh witness is retained.  Re-read only
            # the boundary change at the SAME finest spacing, then transport
            # the already measured Richardson correction.  If this one
            # boundary witness is not small, the next round recomputes a full
            # mesh ladder on the expanded window.
            expanded_finest = max(
                64,
                int(round(mesh.finest_intervals * spacing_ratio)),
            )
            radius = np.maximum(
                0.02 * (1.0 + np.abs(mesh.finest_raw_values)),
                8.0 * max(problem.tolerance * 0.01, 2.0e-12),
            )
            expanded_raw = _finite_native_readout(
                problem,
                expanded,
                expanded_finest,
                energy_tolerance=max(problem.tolerance * 0.01, 2.0e-12),
                hints=mesh.finest_raw_values,
                hint_radius=radius,
            )
            total_solves += 1
            total_updates += expanded_raw.updates
            peak_bytes = max(peak_bytes, expanded_raw.working_bytes)
            window_shift = np.abs(
                expanded_raw.values - mesh.finest_raw_values
            )
            diagnostic = mesh.mesh_shift + window_shift
            corrected = mesh.values + (
                expanded_raw.values - mesh.finest_raw_values
            )
            if float(np.max(diagnostic)) <= problem.tolerance:
                accepted_mesh = _MeshReadout(
                    values=corrected,
                    finest_raw_values=expanded_raw.values,
                    mesh_shift=mesh.mesh_shift,
                    finest_intervals=expanded_finest,
                    solves=mesh.solves + 1,
                    updates=mesh.updates + expanded_raw.updates,
                    peak_bytes=max(mesh.peak_bytes, expanded_raw.working_bytes),
                )
                window = expanded
                reason = (
                    "mesh and decay gates passed; retained mesh correction "
                    "transported across one same-spacing window witness"
                )
                break
            window = expanded
            initial_intervals = expanded_initial
            accepted_mesh = mesh
            continue

        expanded_mesh = _native_mesh_readout(
            problem,
            expanded,
            initial_intervals=expanded_initial,
            max_intervals=max_intervals,
        )
        total_solves += expanded_mesh.solves
        total_updates += expanded_mesh.updates
        peak_bytes = max(peak_bytes, expanded_mesh.peak_bytes)
        window_shift = np.abs(expanded_mesh.values - mesh.values)
        diagnostic = expanded_mesh.mesh_shift + window_shift

        window = expanded
        initial_intervals = expanded_initial
        accepted_mesh = expanded_mesh

    assert accepted_mesh is not None
    diagnostic = accepted_mesh.mesh_shift + window_shift
    status = (
        "ACCEPT"
        if float(np.max(diagnostic)) <= problem.tolerance
        else "HOLD"
    )
    return RawSpectralResult(
        method="Retained Multilevel Sturm (RMS)",
        status=status,
        values=tuple(float(value) for value in accepted_mesh.values),
        mesh_shift=tuple(float(value) for value in accepted_mesh.mesh_shift),
        window_shift=tuple(float(value) for value in window_shift),
        diagnostic_bounds=tuple(float(value) for value in diagnostic),
        window=window,
        finest_intervals=accepted_mesh.finest_intervals,
        solve_count=total_solves,
        recurrence_updates=total_updates,
        peak_working_bytes=peak_bytes,
        elapsed_seconds=time.perf_counter() - started,
        reference_used_for_planning=False,
        per_case_schedule=False,
        tier="finite_diagnostic",
        reason=reason,
    )


def result_as_dict(result: RawSpectralResult) -> dict[str, object]:
    return asdict(result)


def native_eigvals_from_tridiagonal(diagonal, off_diagonal, k: int, energy_tolerance: float):
    """Lowest-``k`` eigenvalues from a PREBUILT symmetric tridiagonal operator.

    The retained requested-only Sturm-bracket + batched-bisection kernel with NO operator construction
    inside — for a fair kernel-only timing boundary where every solver receives an already-built
    operator representation and only the eigenvalue solve is timed.
    """
    diagonal = np.asarray(diagonal, dtype=np.float64)
    off_diagonal = np.asarray(off_diagonal, dtype=np.float64)
    lows, highs, _ = _validated_brackets(diagonal, off_diagonal, k, None, None)
    values, _steps = _batched_bisection_native(
        diagonal, off_diagonal, lows, highs, energy_tolerance, 96
    )
    return np.asarray(values)


__all__ = [
    "RawBenchmarkTarget",
    "RawSpectralProblem",
    "RawSpectralResult",
    "potential_values",
    "raw_benchmark_targets",
    "result_as_dict",
    "retained_raw_input_readout",
    "retained_tridiagonal",
    "native_eigvals_from_tridiagonal",
    "warm_native_kernel",
]
