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
    if problem.potential == "abs_linear":
        # NON-SMOOTH: V = g|x| has a kink at the origin.  The O(h^2) Richardson
        # expansion assumed by both pipelines is not justified here.
        return p["g"] * np.abs(x)
    if problem.potential == "symmetric_double_well":
        # CLUSTERED: quartic double well; the low levels form tunnelling
        # doublets whose splitting falls exponentially with the barrier.
        return p["lam"] * (x**2 - p["a2"]) ** 2
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
KERNEL_FIELD = "compiled" if NATIVE_KERNEL_COMPILED else "interpreted_fallback"

KERNEL_FALLBACK_NOTICE = (
    "retained_spectral: numba is NOT installed, so the Sturm/bisection kernel is running as interpreted "
    "Python. Correctness is unaffected, but ALL TIMINGS ARE INVALID as a speed claim: the interpreted "
    "kernel measures ~70x SLOWER than scipy.linalg.eigh_tridiagonal, whereas the declared compiled field "
    "measures ~2-3x FASTER. Do not report, chart, or compare timings from this run. Install the declared "
    "field with:  pip install 'information-discrete-math[spectral-bench]'"
)


def require_compiled_kernel(context: str = "speed measurement") -> None:
    """Fail CLOSED when a timing-bearing path runs without the compiled kernel. Correctness paths never
    call this (the interpreted fallback is numerically identical); only speed/benchmark entry points do,
    so an interpreted run raises HOLD instead of silently emitting ~70x-slower numbers as the declared
    compiled field."""
    if not NATIVE_KERNEL_COMPILED:
        raise RuntimeError(f"HOLD ({context}) — {KERNEL_FALLBACK_NOTICE}")


if not NATIVE_KERNEL_COMPILED:  # pragma: no cover - environment dependent
    import warnings as _warnings

    _warnings.warn(KERNEL_FALLBACK_NOTICE, RuntimeWarning, stacklevel=2)


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
    # A fixed 7-round cap (reach ~1024 units by re-centred doubling) was
    # found, in the course of fixing issue #112, to be the same "fixed
    # budget regardless of problem scale" vulnerability class as the
    # coverage-check scans: for a well genuinely centred beyond that reach,
    # this search lands on a bogus non-minimum partway down a monotonic
    # slope. It happened to be masked in every case tested so far (the
    # bogus window's own monotonic tail then fails the coverage check for
    # an unrelated, if directionally correct, reason) -- not a designed
    # guarantee. Each round is one cheap 1025-point vectorised evaluation,
    # so raising the cap substantially costs nothing in the common case
    # (which converges in 1-4 rounds on every declared/adversarial case,
    # confirmed by direct timing) while making the practical reach
    # effectively unbounded for any realistic potential (40 rounds ->
    # ~8 * 2**39, far beyond anything a real declared potential would need).
    #
    # Disclosed residual (found reviewing this same raise): at truly
    # extreme-magnitude problem parameters (e.g. a `center` around 1e13+,
    # unreachable by any declared/adversarial case but not excluded by
    # RawSpectralProblem's own type), float64 samples across the search
    # window can become indistinguishable from roundoff, and `np.argmin`
    # can then satisfy the break condition on noise rather than a genuine
    # minimum -- a false-convergence failure mode, structurally different
    # from (and not fixed by) raising this cap. Currently caught downstream
    # by the coverage check reporting HOLD rather than a silent wrong
    # ACCEPT (verified directly), so not exploitable as a silent-wrong bug
    # today -- but that is the SAME "masked by an independent check, not a
    # designed guarantee" pattern this whole search-cap fix exists to move
    # away from, just at a more extreme scale. Tracked, not fixed here.
    for _ in range(40):
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


def _fine_component_scan(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    energy: float,
    scan_radius: float,
    scale: float,
    min_grid_points: int = 4096,
    max_grid_points: int = 262144,
) -> tuple[bool, str]:
    """Precise, moderate-radius scan for a component straddling or just past
    the window boundary -- the classic "barrier that looks like a tail" case
    (the paper's literal example).

    Grid resolution is tied to ``scale`` (the FOUND well's own local
    curvature length, already known here -- unlike the wide scan's unknown
    second-well curvature) rather than a fixed point count. A fixed
    ``grid_points=4096`` over ``scan_radius`` was independently found, by
    round-3 adversarial review, to spuriously HOLD legitimate single-well
    problems at high curvature (e.g. ``harmonic(omega=10000, modes=1)``):
    the classically-allowed band near threshold there is narrower than the
    fixed grid's spacing, so no sample lands inside it anywhere -- including
    inside the window itself, which the fail-closed "inconsistent" branch
    below then (correctly, given what it could see, but not usefully)
    reports as HOLD. Resolution is now set so spacing is a small fraction
    of ``scale``, capped at ``max_grid_points`` to bound cost.
    """
    left, right = window
    scan_left = left - scan_radius
    scan_right = right + scan_radius
    target_spacing = max(0.01 * scale, 1.0e-12)
    grid_points = int(np.clip(
        math.ceil((scan_right - scan_left) / target_spacing),
        min_grid_points, max_grid_points,
    ))
    grid = np.linspace(scan_left, scan_right, grid_points)
    with np.errstate(over="ignore"):
        values = potential_values(problem, grid)
    allowed = values <= energy

    if not np.any(allowed):
        return False, (
            "no classically-allowed region found in the fine scan range "
            f"[{scan_left:.6g}, {scan_right:.6g}] at energy {energy:.6g} "
            "-- inconsistent with the solver's own released value"
        )

    changes = np.diff(allowed.astype(np.int8))
    component_starts = list(np.flatnonzero(changes == 1) + 1)
    component_ends = list(np.flatnonzero(changes == -1))
    if allowed[0]:
        component_starts = [0] + component_starts
    if allowed[-1]:
        component_ends = component_ends + [len(allowed) - 1]

    for start_index, end_index in zip(component_starts, component_ends):
        component_left = float(grid[start_index])
        component_right = float(grid[end_index])
        if component_left < left or component_right > right:
            return False, (
                f"a classically-allowed component [{component_left:.6g}, "
                f"{component_right:.6g}] lies outside the accepted window "
                f"[{left:.6g}, {right:.6g}] (fine scan over "
                f"[{scan_left:.6g}, {scan_right:.6g}])"
            )

    return True, (
        f"fine scan over [{scan_left:.6g}, {scan_right:.6g}] found no "
        f"classically-allowed component outside [{left:.6g}, {right:.6g}]"
    )


def _refine_local_minimum(
    problem: RawSpectralProblem,
    lo: float,
    hi: float,
    iterations: int = 60,
) -> tuple[float, float]:
    """Golden-section refinement of a local minimum bracketed by ``(lo, hi)``,
    assuming unimodality inside the bracket (reasonable immediately around a
    single coarse-grid dip). No scipy dependency -- this module is kept
    dependency-light on purpose (numpy + stdlib only).
    """
    golden = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi

    def _value(x: float) -> float:
        with np.errstate(over="ignore"):
            return float(potential_values(problem, np.asarray([x]))[0])

    c = b - golden * (b - a)
    d = a + golden * (b - a)
    fc, fd = _value(c), _value(d)
    for _ in range(iterations):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - golden * (b - a)
            fc = _value(c)
        else:
            a, c, fc = c, d, fd
            d = a + golden * (b - a)
            fd = _value(d)
    x_min = 0.5 * (a + b)
    return x_min, _value(x_min)


def _wide_missed_well_scan(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    energy: float,
    scan_radius: float,
    scale: float,
    min_grid_points: int = 4096,
    max_grid_points: int = 1_048_576,
) -> tuple[bool, str]:
    """Coarse, wide search for an entirely separate well far outside
    ``window``. Deliberately NOT a bare "is this coarse sample below energy"
    test: at low ``energy`` (few requested modes -- ``energy`` is close to
    the missed well's own ground state), the classically-allowed band there
    can be far narrower than this scan's grid spacing, so no single coarse
    SAMPLE may ever land below `energy` even though the true continuous
    minimum does. (An earlier version of this function tested exactly that
    and was independently found, by adversarial review, to silently release
    a wrong ground state at ``symmetric_double_well(lam=1, a2=50000,
    modes=1)`` -- error 1.6e-2 against a tolerance of 2e-8, reported ACCEPT.
    Verified directly against an independent 400,000-point full-domain
    SciPy diagonalisation.)

    The fix: use the coarse grid only to locate CANDIDATE dips (any local
    minimum of the sampled values, regardless of how deep it looks at this
    resolution -- finding the SHAPE of a dip is a far less demanding
    resolution requirement than sampling inside a narrow allowed band), then
    refine each candidate's true minimum value with a local golden-section
    search inside its immediate coarse bracket. The comparison against
    `energy` is made on the REFINED value, not the coarse sample.

    A dip whose minimum is still decreasing at either scan edge is treated
    as inconclusive and reported as an uncovered (HOLD) case, the same
    fail-closed policy as the fine scan's boundary handling -- not assumed
    closed just because nothing was sampled past the declared radius.

    Grid resolution (issue #112, follow-up to the fine-scan fix above): tied
    to ``scale`` -- the FOUND well's own curvature length -- rather than a
    fixed point count, on the working assumption that a missed well in the
    same declared potential family has a broadly comparable physical width.
    This is a heuristic, not a guarantee (the missed well's true curvature
    is, by definition, unknown), so the target spacing here is deliberately
    looser than the fine scan's (candidate-SHAPE detection needs far less
    resolution than sampling inside a narrow allowed band, and the
    golden-section refinement above corrects residual coarseness in the
    candidate's location once a dip is found at all) -- but it no longer
    relies purely on ``_locate_native_well``'s own search cap to fail closed
    for well-separations this scan's old fixed grid would have missed.
    """
    left, right = window
    scan_left = left - scan_radius
    scan_right = right + scan_radius
    target_spacing = max(0.1 * scale, 1.0e-9)
    grid_points = int(np.clip(
        math.ceil((scan_right - scan_left) / target_spacing),
        min_grid_points, max_grid_points,
    ))
    grid = np.linspace(scan_left, scan_right, grid_points)
    with np.errstate(over="ignore"):
        values = potential_values(problem, grid)

    is_local_min = np.zeros(grid_points, dtype=bool)
    is_local_min[1:-1] = (values[1:-1] < values[:-2]) & (values[1:-1] < values[2:])
    candidate_indices = np.flatnonzero(is_local_min)

    for index in candidate_indices:
        lo = float(grid[max(index - 1, 0)])
        hi = float(grid[min(index + 1, grid_points - 1)])
        x_min, v_min = _refine_local_minimum(problem, lo, hi)
        if left <= x_min <= right:
            continue  # the located dip is inside the accepted window
        if v_min <= energy:
            return False, (
                f"a refined local minimum of the potential at x={x_min:.6g} "
                f"(V={v_min:.6g}) is below energy {energy:.6g} and lies "
                f"outside the accepted window [{left:.6g}, {right:.6g}] "
                f"(wide scan over [{scan_left:.6g}, {scan_right:.6g}])"
            )

    if values[0] < values[1] or values[-1] < values[-2]:
        # The potential is still decreasing at the scan's own edge -- a
        # deeper minimum may sit just beyond this declared radius. Cannot
        # certify coverage from this scan alone.
        return False, (
            f"the potential is still decreasing at the wide scan boundary "
            f"[{scan_left:.6g}, {scan_right:.6g}] -- a minimum beyond this "
            "declared radius cannot be ruled out from this scan"
        )

    return True, (
        f"wide scan over [{scan_left:.6g}, {scan_right:.6g}] found no "
        f"other refined potential minimum below energy {energy:.6g} "
        f"outside [{left:.6g}, {right:.6g}]"
    )


def _necessary_coverage_check(
    problem: RawSpectralProblem,
    window: tuple[float, float],
    energy: float,
    scale: float,
) -> tuple[bool, str]:
    """Necessary-condition check for a second, missed well.

    ``_turning_tail_pass`` above tests a SUFFICIENT condition only: does the
    boundary lie deep enough in a classically forbidden region to trust a
    decaying tail. A barrier between two wells passes that exact test as
    convincingly as a true decaying tail does -- the boundary looks identical
    from outside. This is the failure mode reported in the paper's
    "silent failure" case (``symmetric_double_well``): the decay gate passes,
    the mesh/window diagnostic bound passes, and the released values are
    simply the spectrum of the wrong (single) well.

    Two complementary scans, both must pass:

    1. ``_fine_component_scan`` -- a moderate-radius, fine-resolution scan
       that catches a component straddling or just past the window boundary
       (the paper's literal example, well separation ~10x the window
       width).
    2. ``_wide_missed_well_scan`` -- a much wider, coarser scan that hunts
       for a local minimum of V below `energy` far outside the window
       (catches macroscopically-separated wells the fine scan's radius
       does not reach). This is a local-minimum search, not a
       connected-components test, specifically because a uniform grid wide
       enough to reach a distant well can have spacing coarser than the
       classically-allowed band's own width -- verified directly against
       this codebase's own declared cases before shipping this design;
       an earlier, single-scan version of this check either missed distant
       wells entirely (scan too narrow) or missed the TRUE well itself
       (scan wide enough but too coarse to resolve the allowed band) before
       this two-tier split was added.

    Either scan finding a definitive miss is reported as HOLD immediately.
    Both scans are still bounded, DECLARED ranges -- never the literal real
    line, which is not a finite readout. Residual gaps, disclosed rather
    than hidden: a classically-allowed component narrower than the fine
    scan's grid spacing can still be missed; a well whose own shape is
    narrower than the wide scan's grid spacing, or that sits beyond either
    scan's declared radius, is invisible to this check. Both are the same
    kind of finite-resolution disclosure the rest of this module already
    makes (e.g. the pivot floor, the decay gate's own tolerance-derived
    threshold).
    """
    left, right = window
    width = right - left

    fine_radius = max(50.0 * scale, 10.0 * width)
    fine_covered, fine_reason = _fine_component_scan(
        problem, window, energy, fine_radius, scale,
    )
    if not fine_covered:
        return False, fine_reason

    wide_radius = max(2000.0 * scale, 200.0 * width)
    wide_covered, wide_reason = _wide_missed_well_scan(
        problem, window, energy, wide_radius, scale,
    )
    if not wide_covered:
        return False, wide_reason

    return True, f"{fine_reason}; {wide_reason}"


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
    diagnostic_ok = float(np.max(diagnostic)) <= problem.tolerance

    # Necessary condition, independent of the diagnostic bound above: does a
    # classically-allowed component lie outside the accepted window? A
    # sufficient boundary-decay pass (already folded into `window` via
    # `_expand_failed_boundaries`) cannot rule this out -- a barrier between
    # two wells passes it exactly as a true decaying tail does. Checked once,
    # against the final accepted window and the highest released eigenvalue
    # estimate, not on every round -- this is the gate that decides ACCEPT.
    covered, coverage_reason = _necessary_coverage_check(
        problem,
        window,
        float(np.max(accepted_mesh.values)),
        scale,
    )

    status = "ACCEPT" if diagnostic_ok and covered else "HOLD"
    if not covered:
        reason = f"necessary coverage check failed: {coverage_reason}"
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


@dataclass(frozen=True)
class RawSpectralModeResult:
    """Raw-input eigenvalues (``eigenvalue_result``) plus retained-mode
    eigenvector readouts for the same finite operator, joined into one
    pipeline. This is a NEW, additive entry point -- it does not change
    ``retained_raw_input_readout``'s own return shape or behaviour, so no
    existing caller is affected by its existence.

    The two readouts are independently gated and never collapsed into one
    number: an eigenvalue can be ACCEPT while its eigenvector readout is
    HOLD (e.g. a near-degenerate cluster the mode selection cannot resolve
    at the declared orthogonality tolerance) or vice versa is not possible
    (a HOLD eigenvalue result means the window/coverage itself is not
    trusted, so vectors are not attempted against it). ``status`` is
    ACCEPT only when both are.
    """
    eigenvalue_result: RawSpectralResult
    vectors: tuple[np.ndarray, ...]
    vector_residuals: tuple[float, ...]
    vector_status: tuple[str, ...]
    vector_verdict: str
    orthogonality_error: float
    vector_notes: tuple[str, ...]
    status: str


def retained_raw_input_readout_with_vectors(
    problem: RawSpectralProblem,
    *,
    max_intervals: int = 1_048_576,
    max_window_rounds: int = 8,
    vector_rho: float = 1e-10,
) -> RawSpectralModeResult:
    """Raw input -> eigenvalues (``retained_raw_input_readout``) AND
    eigenvectors (``retained_spectral.retained_mode.modes``), reusing the
    pivot state the Sturm/bisection kernel already retains rather than a
    separate inverse-iteration pass.

    If the eigenvalue readout itself is HOLD (window/coverage not trusted),
    eigenvector recovery is not attempted -- a vector readout against a
    window that may already be wrong would be meaningless, not merely
    unreliable. ``vectors``/``vector_status``/etc. are then empty and
    ``vector_verdict`` is ``"HOLD"``, with a note explaining why.
    """
    from retained_spectral import retained_mode

    eigen_result = retained_raw_input_readout(
        problem, max_intervals=max_intervals, max_window_rounds=max_window_rounds,
    )

    if eigen_result.status != "ACCEPT":
        return RawSpectralModeResult(
            eigenvalue_result=eigen_result,
            vectors=(),
            vector_residuals=(),
            vector_status=(),
            vector_verdict="HOLD",
            orthogonality_error=float("nan"),
            vector_notes=(
                "eigenvector readout not attempted: the eigenvalue result "
                f"itself is {eigen_result.status} ({eigen_result.reason}) "
                "-- a vector readout against an untrusted window would not "
                "be meaningful",
            ),
            status="HOLD",
        )

    diagonal, off_diagonal, _spacing = retained_tridiagonal(
        problem, eigen_result.window, eigen_result.finest_intervals,
    )
    # The twisted-factorization pivots in retained_mode.modes are only
    # meaningful evaluated at an actual eigenvalue of THIS exact finite
    # operator -- the Richardson-corrected `eigen_result.values` is an
    # extrapolation estimate, not an eigenvalue of any single matrix, so the
    # raw eigenvalues of (diagonal, off_diagonal) are recomputed here for the
    # vector readout rather than reusing the corrected values directly.
    #
    # Converged to a tolerance MUCH tighter than `problem.tolerance` (and
    # tighter than `vector_rho`): independent review found that passing
    # `problem.tolerance` directly (the solver's own declared eigenvalue
    # tolerance, e.g. 1e-6) into a near-degenerate case fed a
    # loosely-converged eigenvalue into `retained_mode.modes`'s much
    # tighter default residual gate (vector_rho=1e-10), producing spurious
    # HOLDs that looked like real orthogonality/degeneracy failures but
    # were actually an eigenvalue-precision mismatch (confirmed directly:
    # the same tunnelling-doublet case flipped from HOLD to ACCEPT purely
    # by re-solving the eigenvalues to 1e-13 instead of 1e-6). The vector
    # residual gate needs eigenvalues resolved well past its own tolerance
    # to give an honest reading of vector quality, not solver precision.
    lam_tolerance = min(problem.tolerance, vector_rho) * 0.01
    raw_lams = native_eigvals_from_tridiagonal(
        diagonal, off_diagonal, problem.modes, lam_tolerance,
    )
    vectors, residuals, vec_status, vec_verdict, orth, notes = retained_mode.modes(
        diagonal, off_diagonal, raw_lams, rho=vector_rho,
    )
    combined_status = (
        "ACCEPT" if eigen_result.status == "ACCEPT" and vec_verdict == "ACCEPT"
        else "HOLD"
    )
    return RawSpectralModeResult(
        eigenvalue_result=eigen_result,
        vectors=tuple(vectors),
        vector_residuals=tuple(float(r) for r in residuals),
        vector_status=tuple(vec_status),
        vector_verdict=vec_verdict,
        orthogonality_error=float(orth),
        vector_notes=tuple(notes),
        status=combined_status,
    )


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
