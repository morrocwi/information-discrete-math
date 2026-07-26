#!/usr/bin/env python3
"""negative_controls.py — the framework must know when to say HOLD, not emit a fake number.

A method that always returns a plausible-looking value is untrustworthy. Here we feed the certified
tools inputs that VIOLATE their stated hypotheses and assert each one returns HOLD (refuses), plus a
few POSITIVE controls to show the tools are not merely always-HOLD. This is the adversarial half of the
evidence: a finite readout is trustworthy partly because it declines the cases it cannot certify.

Run: python3 validation/negative_controls.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from certified_readout import (geom_series_certified, exp_certified, simpson_certified,
                               richardson_certified, HOLD, CERTIFIED)
from fractions import Fraction as Q
import mpmath as mp
mp.mp.dps = 50

cases = []
def expect(name, got, want_status):
    ok = (got.status == want_status)
    cases.append((name, ok, got.status, got.reason if got.status == HOLD else ""))

# ---- NEGATIVE controls: hypotheses violated → must HOLD ----
expect("geom r=3/2 (divergent, r≥1)", geom_series_certified(Q(3, 2), Q(1, 10**6)), HOLD)
expect("geom r=1 (boundary, diverges)", geom_series_certified(Q(1), Q(1, 10**6)), HOLD)
expect("geom r=-1/2 (|r|<1 ok but code requires 0≤r; honest scope)", geom_series_certified(Q(-1, 2), Q(1, 10**6)), HOLD)
expect("geom ε=0 (invalid tolerance)", geom_series_certified(Q(1, 3), Q(0)), HOLD)
expect("exp(x=5) out of certified domain |x|≤½", exp_certified(mp.mpf(5), mp.mpf(10)**-12), HOLD)
expect("exp ε=0 (invalid tolerance)", exp_certified(mp.mpf("0.3"), mp.mpf(0)), HOLD)
expect("simpson with NO 4th-derivative bound", simpson_certified(lambda t: t**2, 0, 3, mp.mpf(10)**-9), HOLD)
# Richardson on sequences that LACK a 1/n asymptotic expansion → must refuse
expect("richardson on 1 + 1/ln(n)  (no 1/n expansion)",
       richardson_certified(lambda n: 1 + 1/mp.log(n + 1), mp.mpf(10)**-8), HOLD)
expect("richardson on sin(n)  (oscillatory, no limit)",
       richardson_certified(lambda n: mp.sin(mp.mpf(n)), mp.mpf(10)**-8), HOLD)
expect("richardson on n  (divergent)",
       richardson_certified(lambda n: mp.mpf(n), mp.mpf(10)**-8), HOLD)

# ---- POSITIVE controls: hypotheses met → must CERTIFY (proves the tools aren't just always-HOLD) ----
expect("geom r=1/3 → 3/2 (certified)", geom_series_certified(Q(1, 3), Q(1, 10**12)), CERTIFIED)
expect("exp(0.25) certified", exp_certified(mp.mpf("0.25"), mp.mpf(10)**-20), CERTIFIED)
expect("simpson x² with M₄=0 certified", simpson_certified(lambda t: t**2, 0, 3, mp.mpf(10)**-9, d4_bound=0), CERTIFIED)
expect("richardson on (1+1/n)^n → e (genuine 1/n asymptotic)",
       richardson_certified(lambda n: (1 + mp.mpf(1)/n)**n, mp.mpf(10)**-8), CERTIFIED)

print("=" * 88)
print("  NEGATIVE CONTROLS — the framework refuses (HOLD) when its hypotheses are not met")
print("=" * 88)
ok = 0
for name, good, status, reason in cases:
    ok += good
    tag = "PASS" if good else "FAIL"
    extra = f"  [{status}]" + (f" {reason[:54]}" if reason else "")
    print(f"  {tag}  {name[:58]:58}{extra}")
print("-" * 88)
print(f"  {ok}/{len(cases)} controls behaved correctly (refused what it must, certified what it could).")
print("=" * 88)
raise SystemExit(0 if ok == len(cases) else 1)
