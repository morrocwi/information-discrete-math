#!/usr/bin/env python3
"""Retained Spectral — a ready-to-use readout-first Schrödinger spectrum solver.

Retained Multilevel Sturm (RMS) computes the lowest requested energy levels of a
1-D Schrödinger operator ``H = -1/2 d^2/dx^2 + V(x)`` from *raw input only*:

    (potential family, finite parameters, number of requested modes, tolerance)

No window, mesh, reference eigenvalue, or pre-built operator is supplied.  The
solver discovers its own finite well, admits the boundaries with a finite decay
gate, brackets each requested level with a signed Sturm count, and refines on a
multilevel mesh until mesh and window witnesses fit the declared tolerance.

Every returned object is a finite rational-arithmetic readout; the verdict tier
is ``finite_diagnostic`` — this is a discrete diagnostic agreement, not a
continuum-limit proof and not an empirical-physics claim.

Quick start
-----------

    >>> from retained_spectral import solve, examples
    >>> result = solve(examples()["harmonic_low4"])
    >>> result.status
    'ACCEPT'
    >>> [round(v, 6) for v in result.values]
    [0.5, 1.5, 2.5, 3.5]

Build your own problem
----------------------

    >>> from retained_spectral import SpectralProblem, solve
    >>> problem = SpectralProblem(
    ...     name="my_harmonic",
    ...     potential="harmonic",
    ...     parameters=(("omega", 2.0), ("center", 0.0)),
    ...     modes=3,
    ...     tolerance=1e-8,
    ... )
    >>> solve(problem).values
    (1.0, 3.0, 5.0)
"""

from __future__ import annotations

from typing import Mapping

from retained_spectral.engine import (
    RawBenchmarkTarget,
    RawSpectralProblem,
    RawSpectralResult,
    potential_values,
    raw_benchmark_targets,
    result_as_dict,
    retained_raw_input_readout,
    retained_tridiagonal,
    warm_native_kernel,
)

__version__ = "0.1.0"

# Public, product-facing aliases over the verified engine names.
SpectralProblem = RawSpectralProblem
SpectralResult = RawSpectralResult

#: Potential families the solver accepts out of the box.
POTENTIAL_FAMILIES = (
    "harmonic",
    "poschl_teller",
    "morse",
    "factorized_sextic",
    "pure_quartic",
)

_WARMED = False


def _ensure_warm() -> None:
    global _WARMED
    if not _WARMED:
        warm_native_kernel()
        _WARMED = True


def solve(problem: SpectralProblem) -> SpectralResult:
    """Solve for the lowest requested energy levels of ``problem``.

    Compiles the native kernel on first use, then returns a
    :class:`SpectralResult` whose ``status`` is ``"ACCEPT"`` when the mesh and
    window witnesses fit ``problem.tolerance`` and ``"HOLD"`` otherwise.
    """

    _ensure_warm()
    return retained_raw_input_readout(problem)


def make_problem(
    *,
    name: str,
    family: str,
    parameters: Mapping[str, float],
    modes: int,
    tolerance: float = 2e-8,
) -> SpectralProblem:
    """Construct a :class:`SpectralProblem` from keyword arguments.

    A convenience wrapper so callers can pass a plain dict of parameters
    instead of the engine's frozen tuple-of-pairs form.
    """

    if family not in POTENTIAL_FAMILIES:
        raise ValueError(
            f"unknown potential family {family!r}; "
            f"choose from {POTENTIAL_FAMILIES}"
        )
    return SpectralProblem(
        name=name,
        potential=family,
        parameters=tuple(sorted(parameters.items())),
        modes=int(modes),
        tolerance=float(tolerance),
    )


def examples() -> dict[str, SpectralProblem]:
    """Return the seven bundled benchmark problems keyed by name."""

    return {target.problem.name: target.problem for target in raw_benchmark_targets()}


def example_targets() -> tuple[RawBenchmarkTarget, ...]:
    """Return the bundled targets with their reference values attached."""

    return raw_benchmark_targets()


__all__ = [
    "__version__",
    "SpectralProblem",
    "SpectralResult",
    "POTENTIAL_FAMILIES",
    "solve",
    "make_problem",
    "examples",
    "example_targets",
    "potential_values",
    "retained_tridiagonal",
    "result_as_dict",
    "warm_native_kernel",
    # Retained Mode Readout (eigenVECTORS from the retained Sturm pivots — no inverse iteration)
    "modes",
    "mode_readout",
    "expectation",
]

from retained_spectral.retained_mode import modes, mode_readout, expectation  # noqa: E402
