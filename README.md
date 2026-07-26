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

## Then: 3 steps from surprised → convinced

| step | command | what you get |
|---|---|---|
| **1. Be surprised** | `python3 prove_it.py` | the 10 roots reproduced from finite discrete (above) |
| **2. Be convinced** | `bash formal/verify.sh` | **34 theorems, machine-checked axiom-free** in Coq 8.20 (`Print Assumptions` = *Closed under the global context*) — the keystone `B(Φ,Φ)=I(Φ)`, the exact FTCC bridge, the discrete calculus rules |
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
