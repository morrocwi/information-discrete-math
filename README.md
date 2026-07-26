<div align="center">

# 🧮 Information Discrete Mathematics

**The continuum, computed as a readout of the discrete.** _by Yaoharee Lahtee_

[![CI](https://img.shields.io/badge/CI-run%20it%20yourself-brightgreen)](.github/workflows/ci.yml)
[![Coq](https://img.shields.io/badge/Coq-8.20%20axiom--free-blue?logo=coq&logoColor=white)](formal/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

</div>

---

## ⛔ Don't trust the claims. **Run this.**

```bash
pip install mpmath sympy
python3 prove_it.py
```

~2 seconds. It reproduces **10 roots of continuum mathematics** — the constants **π** and **e**, the
**derivative**, the **integral** (1‑D *and* 4‑D), the **limit**, an **infinite series** (ζ(2)=π²/6), an
**ODE**, the **heat PDE**, and even a **divergent series** (1+2+3+…=−1/12) — each to 8–40 correct digits,
using **only finite, discrete, rational operations**. No `exp`, `quad`, `zeta`, `gamma`, or `pi` call ever
produces an answer. The completed continuum is never formed; every value is a *readout of the finite
discrete*.

If those numbers match the textbook constants (they do), the claim **"you don't need continuum
mathematics to compute these"** is demonstrated — by you, on your machine, not by this README.

## The proposition (what is actually new)

This is **not** "do the discrete branch of mathematics." University *discrete mathematics* (logic,
sets, graphs, combinatorics, number theory) is a **subject that sits beside analysis**: the moment you
need a derivative, an integral, or a limit, you leave it and step into the continuum — real numbers,
`h → 0`, `∫`, `∞`. And it is **not** numerical analysis, which *approximates* a continuum believed to
be the real thing.

**We invert it.** The discrete is what is real; **the continuum is a *readout* — a name for the value
you read off a finite discrete process.** Every derivative, integral, limit, series, ODE and PDE here
is computed with finite, discrete, rational operations only. `π`, `e`, `ζ`, `Γ` never *produce* an
answer — the completed infinity is **never formed**. The number you wanted is still there, to 8–40
digits, because it was always a readout, not a place you had to travel to.

> **You do not need continuum mathematics to compute mathematical answers.**
> `prove_it.py` shows it by running; the `formal/` Coq core certifies the discrete laws that make it
> exact (e.g. `I_ε(D_ε f) = f[N] − f[0]`, machine-checked axiom-free). The claim is about
> *computation*, and on that axis it is demonstrated, not asserted.

## Then: 3 steps from surprised → convinced

| step | command | what you get |
|---|---|---|
| **1. Be surprised** | `python3 prove_it.py` | the 10 roots reproduced from finite discrete (above) |
| **2. Be convinced** | `bash formal/verify.sh` | **35 theorems, machine-checked axiom-free** in Coq 8.20 (`Print Assumptions` = *Closed under the global context*) — the keystone `B(Φ,Φ)=I(Φ)`, the exact FTCC bridge, the discrete calculus rules |
| **3. Read the details** | [`textbook/…`](textbook/INFORMATION_DISCRETE_MATHEMATICS.md) | the full derivations, tier-tagged; [`INDEX.md`](INDEX.md) is the map |

More validation you can run: `python3 validation/*.py` (1000 grade-school→PhD, 100 continuous reproduced
from the discrete, breadth, paradox-dissolution, multi-dimensional up to 11-D + dimensional regularization).

## What it is (and what it is not)

**Is:** a readout-first foundation where everything read is a *finite discrete rational readout*, plus a
runnable toolkit (`tools/idm_tools.py`, `tools/idm_discipline.py`) and a machine-checked core (`formal/`).
Every claim carries an honesty tier: `Th_coqc` (machine-checked) · `finite_diagnostic` (numeric, stated
tolerance) · `Dr` (design) · `+ℝ-Open` (honestly unsolved / needs the completed continuum).

**Is not:** a proof that continuum mathematics is *unnecessary for everything*. The claim is about
**computation**: the answers standard analysis names are obtained without forming the completed limit. It
does **not** decide the continuum's existence/uniqueness/cardinality questions — those stay `+ℝ-Open` by
design. That honesty fence is the point.

## Install as a Claude Code skill

```
/plugin marketplace add https://github.com/morrocwi/information-discrete-math.git
/plugin install information-discrete-math@yaoharee-lahtee-math
```

MIT © **Yaoharee Lahtee**. AI-assisted; the core stance and results are the author's.
