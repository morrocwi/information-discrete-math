"""The k=1 discrete readout: instruction count, not wall-clock, for singleton requests.

Why this module exists (the philosophy, stated precisely -- corrected after independent
review found the first version overstated its own mechanism; see the note at the end of
this docstring):

``engine.py`` implements two distinct things this project calls "retention," and they do
not both vanish at ``k=1``:

1. **Mesh-level bracket carry-over** (``_native_mesh_readout`` / ``_validated_brackets``,
   the ``hint``/``hint_radius`` machinery): a bracket found at one mesh refinement level is
   passed as a hint to the next, rather than the next level searching from scratch. This
   runs identically regardless of ``modes`` -- it is **not** a no-op at ``k=1``.
2. **Cross-mode batching**: evaluating multiple *requested eigenvalue indices* together in
   one traversal, so index 1's bracket informs index 2's. This has nothing to batch when
   only one index is requested -- **this** is the mechanism with zero structural room at
   ``k=1``, not "retention" as a whole.

The honest claim is therefore narrower than "retention degenerates to the identity at
k=1": cross-mode batching has nothing to act on there, while mesh-level retention still
runs -- and, per the instruction-count measurement below, appears to cost more than it
saves on both k=1 cases (native uses *more* CPU instructions than SciPy, not fewer). That
is a more specific and more interesting finding than "nothing happens": the retention
machinery that does run at k=1 does not pay for itself there. Whether that is because
mesh-level retention's benefit itself scales with request-batch size (plausible, not yet
checked) or is a separate, unrelated overhead is an open question this module does not
resolve -- flagged as such, not glossed over.

**Why instruction count, not wall-clock, at k=1 specifically:** at this scale the two
solvers' algorithmic work is comparably tiny, so wall-clock time is dominated by
microarchitectural noise (CPU frequency scaling, cache/branch-predictor state, thread
scheduling) -- exactly why the bootstrap CI on ``factorized_sextic_ground`` flips between
"tie" and "native_faster" run to run even at ``audit_repeats=30`` (see
``retained-sturm/docs/paper-map.md``). Wall-clock is a legitimate, finite, disclosed
readout of *elapsed physical time on this host* -- it is not a forbidden continuum
injection -- but it is the wrong instrument for a claim about the algorithm's own,
host-independent behavior when the true margin sits at or below its noise floor. CPU
instructions retired (via ``perf stat -e instructions:u``) is the matching instrument for
that narrower, intrinsic question: an exact, hardware-counted integer.

This module reports that comparison as its **own, separate, tiered verdict** for k=1
cases -- it never feeds ``verdict_gates`` or the overall ACCEPT/HOLD in :mod:`.run` (that
gate is scoped to k>1). A k=1 result here is a kernel-implementation data point, never
evidence for or against cross-mode batching in either direction, and says nothing about
mesh-level retention's value at k>1.

**Correction record (tier-honesty, not hidden):** an earlier version of this module and
of ``retained-sturm/docs/paper-map.md``'s companion section stated the reason as
"the retention operator degenerates to the identity on a singleton" without qualification.
Independent review read ``engine.py`` directly and found mesh-level bracket retention
does run at k=1 -- only cross-mode batching does not. The claim above is the corrected
version; the paper-map.md section has been corrected to match.
"""

from __future__ import annotations

import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

_WORKER = Path(__file__).resolve().parent / "_k1_instruction_worker.py"
_INSTR_RE = re.compile(r"([\d,]+)\s+instructions:u")


def _perf_instruction_count(problem_name: str, solver: str, intervals: int, n_repeats: int,
                             timeout: float = 120.0) -> int | None:
    """Run the worker under ``perf stat -e instructions:u``; return the retired instruction
    count, or ``None`` if ``perf`` is unavailable, denied, the worker itself did not exit
    cleanly, or the run fails for any other reason. Fails soft (this is a diagnostic, not a
    gate) -- callers must treat ``None`` as "insufficient-instrumentation", never as zero or
    as a solver failure.

    Checks ``proc.returncode`` explicitly: ``perf`` will happily report an instruction count
    for a process that crashed after a few instructions (e.g. a ``ModuleNotFoundError`` from
    a misconfigured ``PYTHONPATH``) -- a non-zero exit is not "perf failed to measure," it is
    "the thing perf measured did not do the intended work," and must not be returned as if it
    were a valid measurement.
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
    if proc.returncode != 0:
        return None
    match = _INSTR_RE.search(proc.stderr)
    if match is None:
        return None
    return int(match.group(1).replace(",", ""))


def _one_trial_instructions_per_call(problem_name: str, solver: str, *, intervals: int,
                                      n_lo: int, n_hi: int) -> float | None:
    """One (N_lo, N_hi) slope estimate. ``None`` propagates if either point failed."""
    count_lo = _perf_instruction_count(problem_name, solver, intervals, n_lo)
    count_hi = _perf_instruction_count(problem_name, solver, intervals, n_hi)
    if count_lo is None or count_hi is None:
        return None
    return (count_hi - count_lo) / (n_hi - n_lo)


def instructions_per_call(problem_name: str, solver: str, *, intervals: int = 512,
                           n_lo: int = 500, n_hi: int = 2000, trials: int = 3) -> dict | None:
    """Per-call instruction count via the two-point slope (fixed process overhead cancels),
    repeated across ``trials`` independent (N_lo, N_hi) measurements and reported as
    median + range -- this project's own bootstrap-CI discipline applied to instruction
    count instead of wall-clock, since a single point estimate hides real spread (an
    independent review measured 1.49-2.34x run-to-run on one case with the earlier
    single-trial version).

    Returns ``None`` if ``perf`` counters are unavailable (any trial failing is treated as
    the whole measurement being unavailable, not silently dropped from the average).
    """
    estimates = []
    for _ in range(trials):
        estimate = _one_trial_instructions_per_call(
            problem_name, solver, intervals=intervals, n_lo=n_lo, n_hi=n_hi,
        )
        if estimate is None:
            return None
        estimates.append(estimate)
    return {
        "median": statistics.median(estimates),
        "min": min(estimates),
        "max": max(estimates),
        "trials": estimates,
    }


def k1_discrete_verdict(problem_name: str, *, intervals: int = 512, trials: int = 3,
                        peer: str = "SciPy eigh_tridiagonal") -> dict:
    """The k=1 discrete (instruction-count) readout for one k=1 problem.

    Verdict is one of ``native_fewer_instructions`` / ``peer_fewer_instructions`` /
    ``comparable`` (median ratio within 5% of parity) / ``insufficient-instrumentation``
    (no ``perf`` counters available on this host, or a trial failed -- an honest ``[Open]``,
    never a silent skip or a forced guess).
    """
    native = instructions_per_call(problem_name, "native", intervals=intervals, trials=trials)
    scipy_ = instructions_per_call(problem_name, "scipy", intervals=intervals, trials=trials)

    if native is None or scipy_ is None:
        return {
            "problem": problem_name,
            "instrument": "perf stat -e instructions:u",
            "verdict": "insufficient-instrumentation",
            "tier": "Open",
            "note": (
                "perf counters unavailable on this host (missing binary, denied "
                "perf_event access, a trial's worker process did not exit cleanly, or "
                "the run failed) -- this is a disclosed gap, not a pass or a fail."
            ),
        }

    ratio = native["median"] / scipy_["median"]
    if ratio < 0.95:
        verdict = "native_fewer_instructions"
    elif ratio > 1.05:
        verdict = "peer_fewer_instructions"
    else:
        verdict = "comparable"

    return {
        "problem": problem_name,
        "instrument": "perf stat -e instructions:u",
        "trials": trials,
        "native_instructions_per_call": native,
        f"{peer}_instructions_per_call": scipy_,
        "ratio_native_over_peer_median": ratio,
        "verdict": verdict,
        "tier": "finite_diagnostic",
        "note": (
            "k=1 architecture-scope reading: cross-mode batching has nothing to batch "
            "for a singleton request (mesh-level bracket retention still runs at k=1 -- "
            "see this module's docstring for the corrected, narrower claim). This "
            "instruction-count comparison is a kernel-implementation data point, not "
            "evidence for or against the retained architecture at k>1. It does not feed "
            "verdict_gates or the overall ACCEPT/HOLD in run_competition."
        ),
    }


def run_k1_discrete_benchmark(targets, *, intervals: int = 512, trials: int = 3) -> dict:
    """Run :func:`k1_discrete_verdict` for every ``modes == 1`` target. ``targets`` is the
    same list :func:`raw_benchmark_targets` returns (each with a ``.problem`` attribute).
    """
    cases = {}
    for t in targets:
        if t.problem.modes == 1:
            cases[t.problem.name] = k1_discrete_verdict(t.problem.name, intervals=intervals, trials=trials)
    return {
        "scope_note": (
            "k=1 cases (single requested eigenvalue) are evaluated by CPU "
            "instruction count (median of repeated trials), not wall-clock CI -- see "
            "this module's docstring. Reported separately; never gates the overall "
            "verdict."
        ),
        "cases": cases,
    }


__all__ = [
    "instructions_per_call",
    "k1_discrete_verdict",
    "run_k1_discrete_benchmark",
]
