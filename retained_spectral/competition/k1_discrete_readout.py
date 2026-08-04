"""The k=1 discrete readout: instruction count, not wall-clock, for singleton requests.

Why this module exists (the philosophy, stated precisely, not decoration):

Retention -- this architecture's own contribution -- is defined over retaining
a distinction across *at least two related readouts*: a Sturm/inertia bracket
computed for one requested eigenvalue is kept and reused for the next, rather
than recomputed (see ``sec:retain`` in the paper; ``engine.py``'s bracket
retention machinery). At ``k=1`` there is only one requested eigenvalue --
no second member of the request set for anything to be retained *across*.
The retention operator degenerates to the identity on a singleton, and its
own definition predicts zero expected structural advantage there.

That does not mean k=1 has nothing honest to say. It means wall-clock time is
the wrong instrument for it: at this scale the two solvers' *algorithmic* work
is comparably tiny, so wall-clock is dominated by microarchitectural noise
(CPU frequency scaling, cache/branch-predictor state, thread scheduling) --
exactly why the bootstrap CI on ``factorized_sextic_ground`` flips between
"tie" and "native_faster" run to run even at ``audit_repeats=30`` (see
``retained-sturm/docs/paper-map.md``). Wall-clock seconds are a continuum
readout contaminated by physical noise; they are not the *discrete* quantity
this project's own philosophy asks for.

The discrete, retained-information-honest quantity at k=1 is not seconds but
**CPU instructions retired** -- an exact, hardware-counted integer, measured
via ``perf stat -e instructions:u`` on an isolated worker process
(``_k1_instruction_worker.py``) running each solver N times on the identical
prebuilt operator. Fixed process-startup cost is removed by measuring at two
repeat counts and taking the slope (``(instructions(N_hi) - instructions(N_lo))
/ (N_hi - N_lo)``), not by subtracting a noisy single N=1 baseline.

This module reports that comparison as its **own, separate, tiered verdict**
for k=1 cases -- it never feeds ``verdict_gates`` or the overall ACCEPT/HOLD
in :mod:`.run` (that gate is scoped to k>1, where retention actually applies).
A k=1 "native_fewer_instructions" or "peer_fewer_instructions" result is a
kernel-implementation data point, never evidence for or against the retained
architecture.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

_WORKER = Path(__file__).resolve().parent / "_k1_instruction_worker.py"
_INSTR_RE = re.compile(r"([\d,]+)\s+instructions:u")


def _perf_instruction_count(problem_name: str, solver: str, intervals: int, n_repeats: int,
                             timeout: float = 120.0) -> int | None:
    """Run the worker under ``perf stat -e instructions:u``; return the retired instruction
    count, or ``None`` if ``perf`` is unavailable, denied, or the run fails for any reason.
    Fails soft (this is a diagnostic, not a gate) -- callers must treat ``None`` as
    "insufficient-instrumentation", never as zero or as a solver failure.
    """
    if shutil.which("perf") is None:
        return None
    cmd = [
        "perf", "stat", "-e", "instructions:u", "--",
        sys.executable, str(_WORKER), problem_name, solver, str(intervals), str(n_repeats),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _INSTR_RE.search(proc.stderr)
    if match is None:
        return None
    return int(match.group(1).replace(",", ""))


def instructions_per_call(problem_name: str, solver: str, *, intervals: int = 512,
                           n_lo: int = 500, n_hi: int = 2000) -> float | None:
    """Per-call instruction count via the two-point slope (fixed process overhead cancels).
    Returns ``None`` if ``perf`` counters are unavailable on this host.
    """
    count_lo = _perf_instruction_count(problem_name, solver, intervals, n_lo)
    count_hi = _perf_instruction_count(problem_name, solver, intervals, n_hi)
    if count_lo is None or count_hi is None:
        return None
    return (count_hi - count_lo) / (n_hi - n_lo)


def k1_discrete_verdict(problem_name: str, *, intervals: int = 512,
                        peer: str = "SciPy eigh_tridiagonal") -> dict:
    """The k=1 discrete (instruction-count) readout for one k=1 problem.

    Verdict is one of ``native_fewer_instructions`` / ``peer_fewer_instructions`` /
    ``comparable`` (within 5% of parity) / ``insufficient-instrumentation`` (no ``perf``
    counters available on this host -- an honest ``[Open]``, never a silent skip or a
    forced guess).
    """
    native_per_call = instructions_per_call(problem_name, "native", intervals=intervals)
    scipy_per_call = instructions_per_call(problem_name, "scipy", intervals=intervals)

    if native_per_call is None or scipy_per_call is None:
        return {
            "problem": problem_name,
            "instrument": "perf stat -e instructions:u",
            "verdict": "insufficient-instrumentation",
            "tier": "Open",
            "note": (
                "perf counters unavailable on this host (missing binary, denied "
                "perf_event access, or the run failed) -- this is a disclosed gap, "
                "not a pass or a fail."
            ),
        }

    ratio = native_per_call / scipy_per_call
    if ratio < 0.95:
        verdict = "native_fewer_instructions"
    elif ratio > 1.05:
        verdict = "peer_fewer_instructions"
    else:
        verdict = "comparable"

    return {
        "problem": problem_name,
        "instrument": "perf stat -e instructions:u",
        "native_instructions_per_call": native_per_call,
        f"{peer}_instructions_per_call": scipy_per_call,
        "ratio_native_over_peer": ratio,
        "verdict": verdict,
        "tier": "finite_diagnostic",
        "note": (
            "This is the k=1 architecture-scope reading: retention has nothing to "
            "retain across a singleton request, so this instruction-count comparison "
            "is a kernel-implementation data point, not evidence for or against the "
            "retained architecture. It does not feed verdict_gates or the overall "
            "ACCEPT/HOLD in run_competition."
        ),
    }


def run_k1_discrete_benchmark(targets, *, intervals: int = 512) -> dict:
    """Run :func:`k1_discrete_verdict` for every ``modes == 1`` target. ``targets`` is the
    same list :func:`raw_benchmark_targets` returns (each with a ``.problem`` attribute).
    """
    cases = {}
    for t in targets:
        if t.problem.modes == 1:
            cases[t.problem.name] = k1_discrete_verdict(t.problem.name, intervals=intervals)
    return {
        "scope_note": (
            "k=1 cases (single requested eigenvalue) are evaluated by CPU "
            "instruction count, not wall-clock CI -- see this module's docstring. "
            "Reported separately; never gates the overall verdict."
        ),
        "cases": cases,
    }


__all__ = [
    "instructions_per_call",
    "k1_discrete_verdict",
    "run_k1_discrete_benchmark",
]
