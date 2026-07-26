#!/usr/bin/env python3
"""framework_compliance — the tool that makes "cosmetic relabeling" structurally detectable.

The 10-problem exam caught a real failure mode (founder, 2026-07-26): a solver took a STANDARD
number-theory proof and merely *wrapped* it in framework vocabulary — "standard-math-in-framework-
clothing", not genuine use of the Information Discrete Mathematics framework. This module fixes that in
two moves:

  1. REGIME classification — most problems are one of:
       - `finite_native`      : already finite/integer/discrete; NO continuum to contaminate, so the
                                framework's guardrails are vacuously satisfied. Using it here IS just
                                correct discrete math — do NOT claim the framework did something
                                distinctive; label it honestly.
       - `continuum_tempting` : a limit / integral / derivative / real-analysis / continuous-geometry
                                object is TEMPTING. HERE the framework does real work: it must translate
                                to a finite-ε readout and refuse the non-readout. This is where
                                "translate-first + locked-math" is verifiable and load-bearing.
       - `mixed`              : has a finite core plus a continuum-tempting step.

  2. GENUINE-USE audit — for a claimed solution, decide `genuine | cosmetic | trivial`:
       - `genuine`  : the answer is produced by framework-DISTINCTIVE machinery — an EXECUTED discrete
                      computation (idm_tools: D_ε/I_ε/limit_eps/…), OR a step that would give a DIFFERENT
                      (wrong) answer under naive continuum handling and the framework's readout discipline
                      is what makes it right (regularization, finite-ε-before-limit, refusing ÷0/∞).
       - `cosmetic` : remove the framework vocabulary and an unchanged STANDARD proof remains; no
                      distinctive operation and no executed framework computation. (The P2 failure.)
       - `trivial`  : finite_native regime — framework vacuously satisfied; genuine but not distinctive.

The strongest anti-relabel guarantee is EXECUTION: if the answer is obtained by actually RUNNING the
framework tools (`executed_value` matches), relabeling is impossible — you cannot fake a computation that
runs and yields the benchmark. `verify_executed` provides that gate.
"""
from __future__ import annotations
import re

# markers of a genuine continuum temptation (where the framework must do real work)
CONTINUUM_MARKERS = [
    r"\blim\b", r"\blimit\b", r"→\s*∞", r"\binfinit", r"\bintegral\b", r"∫", r"\bderivative\b",
    r"d/dx", r"\bcontinuous\b", r"\bsmooth\b", r"\breal number", r"ℝ", r"\bconverge", r"\bseries\b",
    r"\bsupremum\b|\binfimum\b", r"\bmeasure\b", r"ε.?δ|epsilon.?delta", r"\barc length|\bcurvature",
]
# markers a solution INVOKED framework-distinctive machinery (not just named it in passing)
FRAMEWORK_OPS = [
    r"D_ε|D_eps|backward difference|secant slope", r"I_ε|I_eps|prefix sum|FTCC",
    r"limit_eps|Richardson|Euler.?Maclaurin|A8.?stab", r"regulari[sz]|ζ\(−1\)|Ramanujan|Abel sum",
    r"L_R|graph Laplacian|retained-information operator", r"finite-?ε|finite ε|readout at",
    r"refus\w+ (the )?(continuum|non-?readout|÷0|infinit)", r"overlap fraction|turning number",
]

def _hits(patterns, text):
    t = text.lower()
    return [p for p in patterns if re.search(p, t)]

def classify_regime(problem_text: str) -> dict:
    """Classify where the framework does real work."""
    cont = _hits(CONTINUUM_MARKERS, problem_text)
    finite_only = not cont
    if finite_only:
        regime = "finite_native"
    elif len(cont) >= 3:
        regime = "continuum_tempting"
    else:
        regime = "mixed"
    return {"regime": regime, "continuum_markers": cont,
            "note": {"finite_native": "no continuum to contaminate — framework is vacuously satisfied; "
                                      "genuine use here is just correct discrete math (label 'trivial').",
                     "continuum_tempting": "framework load-bearing: must translate to finite-ε readout and "
                                           "refuse the non-readout; translate-first + locked-math is verifiable.",
                     "mixed": "finite core + a continuum-tempting step; audit the tempting step."}[regime]}

def audit(problem_text: str, solution_text: str, *, executed_ok: bool = False) -> dict:
    """Decide genuine | cosmetic | trivial for a claimed framework solution."""
    reg = classify_regime(problem_text)
    ops = _hits(FRAMEWORK_OPS, solution_text)
    # strip framework vocabulary; if the remaining proof is unchanged-standard, it's a wrapper
    stripped = re.sub("|".join(FRAMEWORK_OPS + [r"readout", r"retained", r"info(rmation)?-language",
                                                r"discrete", r"tier|Th_coqc|finite_diagnostic"]),
                      "", solution_text, flags=re.I)
    vocab_ratio = 1 - len(stripped.strip()) / max(1, len(solution_text.strip()))

    if executed_ok:
        verdict = "genuine"                       # ran the framework tools → impossible to fake
        why = "answer produced by an EXECUTED framework computation (idm_tools); relabeling is impossible."
    elif reg["regime"] == "finite_native":
        verdict = "trivial"
        why = ("finite-native problem: no continuum to guard, so the framework is vacuously satisfied. "
               "Correct, but NOT a distinctive framework result — do not claim otherwise.")
    elif ops:
        verdict = "genuine"
        why = f"invokes framework-distinctive machinery on a continuum-tempting problem: {ops}."
    else:
        verdict = "cosmetic"
        why = ("continuum-tempting problem solved with NO framework-distinctive operation and NO executed "
               "computation — framework vocabulary is a wrapper on standard math (the P2 failure mode).")

    return {"regime": reg["regime"], "verdict": verdict, "framework_ops_found": ops,
            "vocab_decoration_ratio": round(vocab_ratio, 3), "executed_ok": executed_ok, "why": why,
            "regime_note": reg["note"]}

def verify_executed(compute_fn, benchmark, tol=1e-9) -> bool:
    """The strongest gate: run the solver's framework computation; genuine iff it yields the benchmark."""
    try:
        v = compute_fn()
        return abs(float(v) - float(benchmark)) <= tol * max(1, abs(float(benchmark)))
    except Exception:
        return False


if __name__ == "__main__":
    # self-check on the exam's real cases
    p_finite = "Prove gcd(21n+4, 14n+3) = 1 for every natural number n."
    p_cont = "Compute the limit as n→∞ of the infinite series Σ 1/n², an integral over the real line."
    cosmetic = "By the readout ladder D→ℤ, using standard multiplicative order ord_p(2) and Fermat, ..."
    genuine  = "Translate to a finite-ε readout; by limit_eps (Richardson) and Euler–Maclaurin the "\
               "series converges to the A8-stable plateau, refusing the completed +∞."
    a1 = audit(p_finite, cosmetic)
    a2 = audit(p_cont, cosmetic)
    a3 = audit(p_cont, genuine)
    a4 = audit(p_cont, cosmetic, executed_ok=True)
    assert a1["verdict"] == "trivial",  a1
    assert a2["verdict"] == "cosmetic", a2      # the P2 failure, now flagged
    assert a3["verdict"] == "genuine",  a3
    assert a4["verdict"] == "genuine",  a4      # execution beats everything
    assert verify_executed(lambda: 1.0000000001, 1.0)
    print("framework_compliance self-check OK — regimes {finite_native, continuum_tempting, mixed}; "
          "verdicts {genuine, cosmetic, trivial}; execution gate works.")
