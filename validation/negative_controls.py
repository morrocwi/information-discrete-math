#!/usr/bin/env python3
"""Adversarial controls for evidence-qualified readouts.

The suite checks three distinct outcomes:

- ``CERTIFIED`` when a named target enclosure is proved;
- ``STABLE`` when only a finite refinement pattern is established; and
- ``HOLD`` when a hypothesis or resource budget is absent.

Run: ``python3 validation/negative_controls.py``.
"""

import math
import os
import sys
from fractions import Fraction as Q

import mpmath as mp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from certified_readout import (  # noqa: E402
    CERTIFIED,
    HOLD,
    STABLE,
    exp_certified,
    geom_series_certified,
    integral_stable_certified,
    richardson_certified,
    simpson_certified,
)

mp.mp.dps = 50

cases = []


def expect(name, got, want_status):
    ok = got.status == want_status
    cases.append((name, ok, got.status, got.reason if got.status == HOLD else ""))


# Negative controls: a required hypothesis or budget is absent -> HOLD.
expect("geom r=3/2 (divergent, r≥1)", geom_series_certified(Q(3, 2), Q(1, 10**6)), HOLD)
expect("geom r=1 (boundary, diverges)", geom_series_certified(Q(1), Q(1, 10**6)), HOLD)
expect("geom r=-1/2 outside declared nonnegative domain", geom_series_certified(Q(-1, 2), Q(1, 10**6)), HOLD)
expect("geom ε=0 (invalid tolerance)", geom_series_certified(Q(1, 3), Q(0)), HOLD)
expect("exp resource budget too small", exp_certified("5", "1e-12", max_terms=1), HOLD)
expect("exp ε=0 (invalid tolerance)", exp_certified("0.3", "0"), HOLD)
expect("simpson with no fourth-derivative bound", simpson_certified(lambda t: t**2, 0, 3, "1e-9"), HOLD)
expect("simpson with inexact floating node values",
       simpson_certified(lambda t: float(t)**2, 0, 3, "1e-9", d4_bound=0), HOLD)

# Richardson sequences that do not pass the declared finite-stability test.
expect("richardson on 1 + 1/ln(n)",
       richardson_certified(lambda n: 1 + 1/mp.log(n + 1), mp.mpf(10)**-8), HOLD)
expect("richardson on sin(n)",
       richardson_certified(lambda n: mp.sin(mp.mpf(n)), mp.mpf(10)**-8), HOLD)
expect("richardson on n",
       richardson_certified(lambda n: mp.mpf(n), mp.mpf(10)**-8), HOLD)

# Integral stability diagnostics refuse sampled singularities or noncontracting refinements.
expect("integral 1/(x−1/2) on [0,1]",
       integral_stable_certified(lambda x: 1/(x - mp.mpf("0.5")), 0, 1, mp.mpf(10)**-6), HOLD)
expect("integral 1/x on [0,1]",
       integral_stable_certified(lambda x: 1/x if x > 0 else mp.mpf(0), 0, 1, mp.mpf(10)**-6), HOLD)

# Positive target certificates.
expect("geom r=1/3 -> 3/2", geom_series_certified(Q(1, 3), Q(1, 10**12)), CERTIFIED)
expect("exp(0.25) target certificate", exp_certified("0.25", "1e-20"), CERTIFIED)
expect("exp(5) target certificate", exp_certified("5", "1e-20"), CERTIFIED)
expect("simpson x² with M4=0", simpson_certified(lambda t: t**2, 0, 3, Q(1, 10**9), d4_bound=0), CERTIFIED)

# Positive finite-stability controls: useful evidence, deliberately not target certificates.
expect("richardson on (1+1/n)^n",
       richardson_certified(lambda n: (1 + mp.mpf(1)/n)**n, mp.mpf(10)**-8), STABLE)
expect("integral x² on [0,1] finite stability",
       integral_stable_certified(lambda x: x*x, 0, 1, mp.mpf(10)**-6), STABLE)

print("=" * 96)
print("  ADVERSARIAL CONTROLS — CERTIFIED / STABLE / HOLD are not interchangeable")
print("=" * 96)
passed = 0
for name, good, status, reason in cases:
    passed += good
    tag = "PASS" if good else "FAIL"
    extra = f"  [{status}]" + (f" {reason[:58]}" if reason else "")
    print(f"  {tag}  {name[:62]:62}{extra}")
print("-" * 96)
print(f"  {passed}/{len(cases)} controls returned the required evidence status.")
print("=" * 96)
raise SystemExit(0 if passed == len(cases) else 1)
