# INDEX — Information Discrete Mathematics (structure map)

A world-class discrete-first mathematics text, organized so content is easy to find and easy to extend.
Developed by Yaoharee Lahtee. Read `AI_COMPUTE.md` to compute; read `METHOD.md` for the process; read
the textbook for the theory.

## The spine (each rung is a readout of the one before)

| Part | Title | What it establishes | Tier anchor |
|---|---|---|---|
| **0** | Foundations of the foundation | readout-not-truth; the injected infinities `I1–I4` / zeros `Z1–Z4` | commitment |
| **0.3** | Philosophy of mathematics | what a number / unit / symbol / equation *is* (conventional vs constitutive) | — |
| **0.5** | Reader, resolution, coarse-graining | `G_λ`, `∼_λ`, admissible description `E=Ẽ∘G_λ`, layers, A8/A11 | substrate |
| **I** | Retained-Distinction Logic (RDL) | paraconsistent 4-valued core; non-explosion | `Th_coqc` |
| **II** | The primitive & genesis of number | `δ_R`, RD1–9, the semiring `D` | `Th_coqc` |
| **III** | The number tower | `D→ℤ→ℚ→ℝ`, ℝ as readout, cotransitivity | `Th_coqc` |
| **IV** | Geometry from retained difference | distance, angle=overlap, curvature; **§4.4 π,φ,golden = readout-invariants** | mixed |
| **V** | The retained-information operator | `L_R=D_W−W`, keystone `B(Φ,Φ)=I(Φ)` | `Th_coqc` |
| **VI** | The continuum as a readout | diagnosis of "open/hard" problems | `Dr` |
| **VII** | Complete operator reference | `⊕ ⊗ ÷ ^ √ log =` in the information language | `Th_coqc` |
| **VIII** | Information Discrete Calculus | `D_ε`, `I_ε`, FTCC, causal product rule (exact) | `Th_coqc` |
| **IX** | Powerful tools, re-adapted | regularization, Euler–Maclaurin, transforms, `q`-calculus | mixed |
| **X** | Integrated extensions | sets/functions, cardinality, analysis, probability, reconciliations | mixed |
| **XI** | **Closing the continuum** | discrete derivative/integral/limit/ODE/special-function; closure theorem | `Dr`+ |
| **XII** | **Abstract algebra** | group=`Aut(F,O)`; ring/field=operator algebra; Lagrange; Galois | mixed |
| **XIII** | **Linear algebra** | the algebra of `L_R`; ℚ-vector space; metric; det; exact solve | mixed |
| **XIV** | **Complex analysis** | `i`=quarter-turn; roots of unity; holomorphy=closing transport; residue | mixed |
| **XV** | **Combinatorics & graph theory** | native `δ_R`=edge; `L_R` connectivity; matrix-tree; Euler χ | `Th_coqc`-elig |
| **XVI** | **Measure & functional analysis** | discrete measure `μ_λ=I_ε(1_S)`; `L^p`; finite spectral theorem; Riesz | mixed |
| **XVII** | **Category theory** | `G_λ` reflector; `E=Ẽ∘G_λ` Kan; fibration; setoids; finite Yoneda | `Th_coqc`-elig/`Dr` |
| **XVIII** | **Statistics & inference** | retained-frequency estimation; test = `Verdict`; Bayesian reweighting | `finite_diagnostic` |
| **XIX** | **Optimization** | gradient=`D_ε`; convexity=`D_ε²≥0`; Lagrange; exact-`ℚ` LP | `Th_coqc`-elig |
| **XX** | **Continuum-maya bridge** | `Λ`: discrete→continuum-appearance (A8-stable readout); FTCC exact core; faithfulness | `Th_coqc`+`Dr` |
| **XXI** | **Frontier without the continuum** | paradox dissolution: topology/manifold/PDE need no continuum; maya computes all | `Dr`+`finite_diagnostic` |

## Appendices

- **A** — contaminated-concept → discrete-replacement table (the contamination gate)
- **B** — machine-checked theorem index (tier · witness)
- **C** — axiom-dependence discipline
- **D** — validation: 1000 problems ประถม→ปริญญาเอก (**1000/1000**)
- **E** — validation: 100 continuous problems reproduced from the discrete (**100/100**)

## Validation at a glance

| suite | scope | result |
|---|---|---|
| `validation/thousand_problems.py` | arithmetic → PhD | **1000/1000** |
| `validation/hundred_continuum_problems.py` | integrals/derivatives/limits/ODEs/special | **100/100** |
| `validation/breadth_problems.py` | algebra/linear/complex/combinatorics/graph | **48/48** |
| `validation/breadth2_problems.py` | measure/functional/category/statistics/optimization | **34/34** |
| `validation/paradox_dissolution.py` | topology/manifold/PDE paradoxes dissolved | **21/21** |
| `validation/discrete_jacobian.py` | discrete Jacobian (retained sensitivity) · collision · retention lift | **9/9** |
| `validation/infinity_accuracy.py` | classically-infinite quantities reproduced from finite discrete, ≥10 digits | **12/12** |

## Backlog

Pending work that strengthens the framework (closeable chapters, proof work, frontier, discipline hardening) is tracked in **[BACKLOG.md](BACKLOG.md)** — four full chapters are closeable now (measure/functional analysis · category theory · statistics · optimization).

## Extensibility contract (how to grow this without breaking it)

1. New chapters go as `# Part N — <title>` **before** `# Appendix A`; keep the spine order. **Part XX is
   reserved** for the continuum-maya bridge (BACKLOG capstone) — start new unrelated chapters at Part XXI.
2. Derive from `δ_R` / `L_R` / Part VII operators — **never** import a continuum primitive; if a
   continuum object is unavoidable, tag it `+ℝ-Open` and state it as a declared, predicted frontier.
3. Tier-tag every claim (`Th_coqc` / `finite_diagnostic` / `Dr` / `+ℝ-Open`).
4. Every numeric claim gets an executed check in a `validation/*.py` suite **before** it enters prose.
5. Update this INDEX, `AI_COMPUTE.md`'s file table, and (if a new tool) `tools/idm_tools.py` + its
   self-check.
