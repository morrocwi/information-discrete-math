<div align="center">

# 🧮 Information Discrete Mathematics

### _A readout-first mathematical foundation — where the continuum is a **readout**, never a primitive._

<br>

> # ⛔️ There is **no need** for continuum mathematics<br>to solve mathematical problems in the modern world.

<br>

[![Coq](https://img.shields.io/badge/Coq-8.20-blue?logo=coq&logoColor=white)](formal/)
[![axiom--free](https://img.shields.io/badge/proofs-35_theorems_axiom--free-brightgreen)](formal/verify.sh)
[![Closed under the global context](https://img.shields.io/badge/Print_Assumptions-Closed_under_the_global_context-success)](formal/)
[![validation](https://img.shields.io/badge/validation-1212_checks_green-brightgreen)](validation/)
[![continuum](https://img.shields.io/badge/continuum_reproduced-100%2F100-blueviolet)](validation/hundred_continuum_problems.py)
[![chapters](https://img.shields.io/badge/chapters-Parts_0--XXI-orange)](textbook/INFORMATION_DISCRETE_MATHEMATICS.md)
[![tiers](https://img.shields.io/badge/every_claim-tier--tagged-yellow)](textbook/INFORMATION_DISCRETE_MATHEMATICS.md)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![author](https://img.shields.io/badge/by-Yaoharee_Lahtee-ff69b4)](#)

</div>

---

The headline is a claim about **computation**: every mathematical problem that has an answer is answered
by a **finite, discrete, rational** computation — no actual continuum (ℝ-completeness, `h→0`, reached
`+∞`, a zero-size point, a continuum angle) is ever needed as a primitive. **Demonstrated, not asserted:**

| suite | scope | result |
|---|---|---|
| `validation/thousand_problems.py` | arithmetic → PhD | **1000 / 1000** ✅ |
| `validation/hundred_continuum_problems.py` | integrals · derivatives · limits · ODEs · special functions, **reproduced from the discrete** | **100 / 100** ✅ |
| `validation/breadth_problems.py` | algebra · linear · complex · combinatorics / graph | **48 / 48** ✅ |
| `validation/breadth2_problems.py` | measure · functional · category · statistics · optimization | **34 / 34** ✅ |
| `validation/paradox_dissolution.py` | topology · manifolds · PDE paradoxes **dissolved** | **21 / 21** ✅ |
| `validation/discrete_jacobian.py` | discrete Jacobian · readout collision · retention lift | **9 / 9** ✅ |

…plus **35 machine-checked, axiom-free Coq witnesses** under [`formal/`](formal/) — one command verifies
them all:

```bash
bash formal/verify.sh          # compiles every witness + confirms "Closed under the global context"
```

> **🤝 Honest fence.** This is about *computing the answers* and *dissolving the paradoxes* — refusing to
> inject the non-readout — **not** about deciding the classical completed-continuum questions in their own
> terms, which the framework declines to form. See Parts XX–XXI.

---

## ✨ What it gives you

- **🧭 The contaminated-concept → discrete-replacement table** — the exact substitution for each continuum
  concept that tends to sneak in: real numbers, limits, **angles/degrees** (the inverse-trig trap →
  Born-rule overlap fraction), points of zero size, zero, infinity, distance, continuity, π, derivatives.
- **✅ A pre-write checklist** — five checks before committing any equation, proof, or number, so a real
  coordinate, a landing limit, or a singularity never slips through.
- **🔢 The machine-checked number ladder** `D → ℤ → ℚ → ℝ` — the continuum built as a *readout* of the
  discrete root (Bishop regular Cauchy sequences of ℚ); discrete calculus (`Δ`, `Σ`, discrete FTC) with
  no reals.
- **⚙️ Operator-first** — information is the central axis: the retained-information operator is the graph
  Laplacian `L_R`, whose Dirichlet energy **is** the retained-information functional (`B(Φ,Φ)=I(Φ)`,
  machine-checked); geometry and distance are readouts of it.
- **🧩 The keystone, the bridge, and parameter reduction — all axiom-free Coq**: `B(Φ,Φ)=I(Φ)`, the exact
  FTCC continuum-maya bridge, and the idempotent Reynolds/twirl projector that collapses an `n×n` metric to
  one scalar.

## 📖 The textbook

The full treatise — **[textbook/INFORMATION_DISCRETE_MATHEMATICS.md](textbook/INFORMATION_DISCRETE_MATHEMATICS.md)**
— carries the foundation from ONE primitive (the retained difference) up through logic (RDL), the number
tower, discrete analysis, geometry (`π,φ` as readout-invariants), a **philosophy of mathematics** (what a
number/unit/symbol/equation *is*), the **closure of the continuum**, dedicated chapters on abstract
algebra · linear algebra · complex analysis · combinatorics/graph theory · measure & functional analysis ·
category theory · statistics · optimization, the **continuum-maya bridge**, and **paradox dissolution**
(topology · manifolds · PDE) — every claim tier-tagged, with machine-checked witnesses. See
**[INDEX.md](INDEX.md)** for the map.

## 🤖 For AI agents — compute with it directly

- **[AI_COMPUTE.md](AI_COMPUTE.md)** — quick-start: tool decision-table, the 6-step process, copy-paste examples.
- **[METHOD.md](METHOD.md)** — tools (nouns) vs process (verb); **Rule 0: translate into the information language first.**
- **[tools/idm_tools.py](tools/idm_tools.py)** · **[tools/idm_discipline.py](tools/idm_discipline.py)** — the tested tool + numeric-honesty libraries (`python3 tools/idm_tools.py` self-checks).

## 📦 Install (Claude Code plugin)

```
/plugin marketplace add https://github.com/morrocwi/information-discrete-math.git
/plugin install information-discrete-math@yaoharee-lahtee-math
```

Load it every session with `/information-discrete-math` before any mathematical work, or add a pointer in
your `~/.claude/CLAUDE.md`.

## 🏷️ The tier discipline (why every claim carries a tag)

`Th_coqc` (machine-checked, axiom-free) · `finite_diagnostic` (numeric to a declared tolerance) · `Dr`
(design/interpretation) · `+ℝ-Open` (honestly unsolved / needs the completed continuum). **Never** put a
continuum name on a finite analogue; **never** claim to *solve* a continuum question — diagnose it as a
non-readout and predict the readout. The boundary between the provable and the Open **is** the boundary of
the infinity axioms.

## 📜 License

MIT — see [LICENSE](LICENSE). Developed by **Yaoharee Lahtee**. AI-assisted; the core stance and results
are the author's.

<div align="center">

---

_“The continuum is what a finite reader reconstructs — never the primitive it reads.”_

</div>
