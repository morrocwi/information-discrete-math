#!/usr/bin/env python3
"""Exact/finite adversarial controls for the shared Clay bridge programme.

This script does not test a Clay conclusion.  It checks three failure modes
that any generic bridge theorem must explicitly rule out:

1. all finite prefixes can pass while a global property fails;
2. local/adjacent discrepancies can become small without giving a useful
   all-scale compatibility theorem;
3. a defect can exist but generic black-box capture can be exponentially rare.
"""

from __future__ import annotations

from fractions import Fraction


def harmonic(n: int) -> Fraction:
    return sum((Fraction(1, k) for k in range(1, n + 1)), Fraction(0, 1))


def finite_prefix_control(max_n: int = 64) -> None:
    # a_n=n: every tested finite prefix [0,N] is bounded by N.
    for N in range(max_n + 1):
        assert all(n <= N for n in range(N + 1))

    # Any proposed global bound B is defeated at the explicit index B+1.
    for B in range(max_n + 1):
        assert B + 1 > B


def harmonic_compatibility_control(max_power: int = 12) -> None:
    # H_{2^m} >= 1 + m/2, although the adjacent increment near that scale
    # is exactly 1/2^m.  Thus adjacent discrepancies can go to zero while
    # cumulative drift remains unbounded.
    previous_increment = None
    for m in range(1, max_power + 1):
        n = 2**m
        h = harmonic(n)
        lower = Fraction(1, 1) + Fraction(m, 2)
        assert h >= lower

        increment = Fraction(1, n)
        assert harmonic(n) - harmonic(n - 1) == increment
        if previous_increment is not None:
            assert increment < previous_increment
        previous_increment = increment


def black_box_capture_control() -> None:
    # For a universe of M=2^n possible witness locations, any deterministic
    # set of k<M probes leaves at least one possible single defect unseen.
    for n in range(2, 13):
        M = 2**n
        k = min(n * n, M - 1)
        probes = set(range(k))
        hidden = next(i for i in range(M) if i not in probes)
        assert hidden not in probes
        assert len(probes) == k < M

    # Exact calibration of uniform random capture for a polynomial-size
    # support: probability is k/2^n, which is already tiny at moderate n.
    n = 40
    k = n**3
    probability = Fraction(k, 2**n)
    assert probability < Fraction(1, n**3)


def main() -> None:
    finite_prefix_control()
    harmonic_compatibility_control()
    black_box_capture_control()
    print("CLAY P2 NEGATIVE CONTROLS PASS")
    print("finite-prefix global-bound guard: PASS")
    print("adjacent-compatibility harmonic guard: PASS")
    print("black-box defect-capture guard: PASS")


if __name__ == "__main__":
    main()
