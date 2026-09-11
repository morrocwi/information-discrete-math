#!/usr/bin/env python3
"""Exact finite diagnostic for robust Adaptive Defect Capture.

Imported quantitative pattern (used only in the IDM P-vs-NP lane): a certified
margin must survive uncertainty/remainder before a branch/capture claim is
promoted.

Cleared-denominator ADC form:

    ideal_hit <= approx_hit + err
    total + p*err <= p*ideal_hit

implies

    total <= p*approx_hit,

so the implemented support/sampler still has capture probability at least 1/p
when total > 0.  All arithmetic is exact integer/Fraction arithmetic.

This is a robustness transfer only.  It does NOT construct the unrestricted
candidate-adaptive support whose inverse-polynomial hit margin is the open
SAT-circuit lower-bound problem.
"""
from fractions import Fraction


def robust_capture(total: int, ideal_hit: int, approx_hit: int, err: int, p: int) -> dict:
    vals = (total, ideal_hit, approx_hit, err, p)
    if any(v < 0 for v in vals):
        raise ValueError("all inputs must be nonnegative")
    if total == 0:
        return {"status": "HOLD", "reason": "zero total mass"}
    if p == 0:
        return {"status": "HOLD", "reason": "zero inverse-capture denominator"}

    local_error_ok = ideal_hit <= approx_hit + err
    margin_ok = total + p * err <= p * ideal_hit
    if not (local_error_ok and margin_ok):
        return {
            "status": "HOLD",
            "local_error_ok": local_error_ok,
            "margin_ok": margin_ok,
            "ideal_capture": Fraction(ideal_hit, total),
            "approx_capture": Fraction(approx_hit, total),
        }

    assert total <= p * approx_hit
    return {
        "status": "CERTIFIED",
        "local_error_ok": True,
        "margin_ok": True,
        "ideal_capture": Fraction(ideal_hit, total),
        "approx_capture": Fraction(approx_hit, total),
        "guaranteed_capture": Fraction(1, p),
        "expected_trials_bound": p,
    }


def main() -> None:
    # Exact boundary case: ideal 30/100, certified loss <=5/100; p=4.
    # 100 + 4*5 = 120 = 4*30 and approx_hit=25, hence capture >=1/4.
    good = robust_capture(total=100, ideal_hit=30, approx_hit=25, err=5, p=4)
    assert good["status"] == "CERTIFIED", good
    assert good["approx_capture"] == Fraction(1, 4)

    # Same ideal support but uncertainty consumes too much of the margin.
    hold_margin = robust_capture(total=100, ideal_hit=30, approx_hit=20, err=10, p=4)
    assert hold_margin["status"] == "HOLD", hold_margin
    assert not hold_margin["margin_ok"]

    # Claimed error budget too small to explain the implementation loss.
    hold_error = robust_capture(total=100, ideal_hit=30, approx_hit=20, err=5, p=4)
    assert hold_error["status"] == "HOLD", hold_error
    assert not hold_error["local_error_ok"]

    # Zero-error specialization.
    exact = robust_capture(total=12, ideal_hit=3, approx_hit=3, err=0, p=4)
    assert exact["status"] == "CERTIFIED", exact
    assert exact["approx_capture"] == Fraction(1, 4)

    print(f"robust-good={good}")
    print(f"insufficient-margin={hold_margin}")
    print(f"uncertified-loss={hold_error}")
    print(f"zero-error={exact}")
    print("robust defect capture: PASS")
    print("fail-closed: uncertainty without enough certified margin returns HOLD")
    print("OPEN: construct unrestricted circuit-adaptive support with inverse-polynomial ideal margin")
    print("tier=finite_diagnostic; SAT notin P/poly=NOT CLAIMED; P!=NP=NOT CLAIMED")


if __name__ == "__main__":
    main()
