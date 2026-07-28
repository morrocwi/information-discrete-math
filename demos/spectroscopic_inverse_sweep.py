#!/usr/bin/env python3
"""Spectroscopic inverse problem — many Morse fits, where the native kernel's per-solve speed pays off.

Fitting spectroscopic constants (D_e, a, r_e) to an observed vibrational spectrum is an *inverse*
problem: an optimiser proposes thousands to millions of candidate (D_e, a, r_e) triples, and each
candidate requires re-solving the Morse eigenproblem for the lowest k levels. The cost of the whole
inverse problem is therefore (number of candidates) x (per-solve time). This demo measures the
per-candidate solve time of the native kernel over a small candidate set and, from that measured
rate, projects the wall-clock of realistic inverse sweeps.

Tier: finite_diagnostic for the eigenvalues; the projected sweep hours are a *linear extrapolation*
from a measured per-candidate rate (candidates are independent, so wall-clock is exactly
count x rate up to scheduling overhead) — reported as a projection, not a measured full run.

Run:  PYTHONPATH=. python3 -m demos.spectroscopic_inverse_sweep
"""

from __future__ import annotations

import argparse
import time

import numpy as np

from demos.i2_morse_levels import (
    A,
    DE,
    RE,
    morse_tridiagonal,
    _try_mrrr,
)
from retained_spectral.engine import native_eigvals_from_tridiagonal, warm_native_kernel


def _candidate_operator(n, de, a, re):
    """Morse tridiagonal for a perturbed constant set — reuses the demo's operator but overrides
    the three fitted constants (the inverse problem varies exactly these)."""
    r = np.linspace(3.0, 30.0, n + 2)[1:-1]
    h = r[1] - r[0]
    mu = 115597.0
    potential = de * (1.0 - np.exp(-a * (r - re))) ** 2
    kinetic = 1.0 / (2.0 * mu * h * h)
    return 2.0 * kinetic + potential, np.full(n - 1, -kinetic)


def _sweep_seconds(solver, sets, n):
    started = time.perf_counter()
    for de, a, re in sets:
        d, e = _candidate_operator(n, de, a, re)
        solver(d, e)
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=int, default=40)
    parser.add_argument("--grid", type=int, default=100000)
    parser.add_argument("--modes", type=int, default=40)
    parser.add_argument("--tolerance", type=float, default=1e-12)
    args = parser.parse_args()

    warm_native_kernel()
    k, n = args.modes, args.grid

    # A deterministic spread of candidate constant sets around the I2 values (no Math.random needed).
    rng = np.random.default_rng(1)
    sets = [
        (DE * (1 + 0.02 * rng.standard_normal()),
         A * (1 + 0.02 * rng.standard_normal()),
         RE * (1 + 0.005 * rng.standard_normal()))
        for _ in range(args.candidates)
    ]

    print(f"Spectroscopic inverse sweep: {args.candidates} candidate (D_e,a,r_e) sets, "
          f"n={n}, k={k}")

    solvers = [("native", lambda d, e: native_eigvals_from_tridiagonal(d, e, k, args.tolerance))]
    mrrr = _try_mrrr()
    if mrrr is not None:
        solvers.append(("MRRR", lambda d, e: mrrr(d, e, k)))

    rates = {}
    for name, solver in solvers:
        secs = _sweep_seconds(solver, sets, n)
        rates[name] = secs / args.candidates
        print(f"  {name:>6}: {secs:7.2f} s total   ({rates[name] * 1e3:7.1f} ms / candidate)")

    print("\nProjected inverse-problem wall-clock (count x measured per-candidate rate):")
    for count, label in ((10_000, "10k-candidate local fit"),
                         (1_000_000, "1M-candidate global / Monte-Carlo search")):
        native_h = rates["native"] * count / 3600.0
        line = f"  {label:<42} native {native_h:8.2f} h"
        if "MRRR" in rates:
            mrrr_h = rates["MRRR"] * count / 3600.0
            line += f"   MRRR {mrrr_h:8.2f} h   (saves {mrrr_h - native_h:7.2f} h)"
        print(line)

    print("\nTier: finite_diagnostic eigenvalues; sweep hours are a linear projection from the")
    print("measured per-candidate rate above (independent candidates -> wall-clock = count x rate).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
