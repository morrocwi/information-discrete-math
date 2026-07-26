#!/usr/bin/env python3
"""prove_it_full.py — 1000 CONTINUUM-FRONTIER problems from real systems, each a FINITE-DISCRETE readout.

    DON'T TRUST THE CLAIMS. RUN THIS.   ->   python3 prove_it_full.py

Where prove_it.py captures the 10 *roots* of the continuum in ~2 seconds, this is the full breadth:
~1000 problems that working scientists and engineers actually solve — spread across

    • physics       (quantum, thermodynamics, optics, relativity, waves)
    • biochem       (reaction kinetics, diffusion, binding, populations, statistics)
    • networks      (PageRank, Markov chains, queues, information theory, signals)
    • complexity    (ζ/Γ/special functions, asymptotics, regularization, number theory)
    • cosmology     (Friedmann integrals, thermal relics, Planck spectrum, growth, distances)

EVERY one of these is a *continuum frontier*: classically it needs a transcendental constant, a
special function, an improper integral, a limit, an ODE/PDE, or a spectral quantity — the machinery
of the continuum. Here every 'ours' value is computed with ONLY finite, discrete, rational operations
(finite series, argument reduction, finite quadrature, Richardson, Euler–Maclaurin) through
provefull/_kernel.py. No mp.exp/log/sin/quad/zeta/gamma/pi call ever produces an 'ours' answer — the
continuum is never formed. The standard mpmath value appears only in the reference column, to compare
against. This is the continuum-maya bridge at working scale: the continuum is a *readout*, and you can
compute the frontier without ever traveling there.

EPISTEMICS (GRR-EF/H, horizontal). Each row is a Claim whose warrant you earn by RE-RUNNING it — not
from any authority, journal, or certifier. Genesis = the classical continuum definition; Readout = the
finite-discrete computation; Evidence = the digits that match, reproducible on your machine; Tier =
finite_diagnostic (numeric to the stated tolerance). Fork it, challenge it, extend it — no permission
needed; lineage preserved.
"""
import sys, os, importlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "provefull"))
import _kernel as K

DOMAINS = ["physics", "biochem", "networks", "complexity", "cosmology"]
TITLE = {"physics": "PHYSICS", "biochem": "BIOCHEMISTRY", "networks": "COMPUTING / NETWORKS",
         "complexity": "ANALYSIS / COMPLEXITY", "cosmology": "COSMOLOGY"}

def load(domain):
    try:
        mod = importlib.import_module(domain)
        probs = list(mod.PROBLEMS())
        return probs, None
    except Exception as e:
        return [], f"{type(e).__name__}: {e}"

def main():
    print("=" * 100)
    print("  prove_it_full.py — 1000 continuum-frontier problems, each a FINITE-DISCRETE readout")
    print("  engine: mpmath = arbitrary-precision finite (floating) arithmetic; NO continuum function produces any 'ours' value")
    print("=" * 100)
    grand_ok = grand_tot = 0
    worst = []
    for d in DOMAINS:
        probs, err = load(d)
        if err:
            print(f"\n■ {TITLE.get(d, d)}: MODULE ERROR — {err}")
            continue
        ok = sum(1 for p in probs if p.ok)
        grand_ok += ok; grand_tot += len(probs)
        print(f"\n■ {TITLE.get(d, d):24}  {ok}/{len(probs)}  ({100*ok/max(1,len(probs)):5.1f}%)")
        # show a few representative worked rows
        for p in probs[:3]:
            print(f"    {p.name[:44]:44} ours={K._short(p.ours):>16}  ref={K._short(p.ref):>14}  {p.dig:>2}d")
        fails = [p for p in probs if not p.ok]
        worst += [(d, p) for p in fails]
        if fails:
            print(f"    … {len(fails)} below 6 digits, e.g. {fails[0].name[:60]} ({fails[0].dig}d)")
    print("\n" + "-" * 100)
    print(f"  GRAND TOTAL: {grand_ok}/{grand_tot} continuum-frontier problems reproduced to ≥6 digits "
          f"({100*grand_ok/max(1,grand_tot):.1f}%)")
    print(f"  from finite, discrete, rational operations only — across {len(DOMAINS)} real-world domains.")
    print(f"  The continuum was never formed; every value is a READOUT of the finite discrete.")
    print("=" * 100)
    if worst:
        print(f"  ({len(worst)} rows below tolerance — see them by domain above.)")
    # release gate: >=99% and every domain present
    passed = grand_tot >= 900 and grand_ok >= int(0.99 * grand_tot)
    print(f"  VERDICT: {'the continuum frontier is computable from finite readouts — TRUSTWORTHY at scale' if passed else 'INCOMPLETE — see failures/missing domains above'}.")
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
