# METHOD — tools vs. process (the sharp solve loop)

> A **tool** is a *noun* you invoke. A **process** is the *verb* that composes tools into a result.
> Keeping them separate is what makes the method light: the tools are fixed and tested; the process is
> a short, repeatable loop. Developed by Yaoharee Lahtee.

## The tools (nouns — `tools/idm_tools.py`, all finite-ε over ℚ, none takes a continuum limit)

| tool | what it is | replaces |
|---|---|---|
| `δ_R`, `L_R` | retained distinction; retained-information operator (graph Laplacian) | "information", `∂²` on a continuum |
| `⊕ ⊗ ÷ ^ √ log =` | the operator set (Part VII) — accumulation, replication, partition, self-composition, generator, retained-distinction count, indistinguishability | the arithmetic/algebra operators, re-grounded |
| `D_eps` | discrete derivative (Richardson) | the difference-quotient limit |
| `I_eps` | discrete integral (trapezoid + Euler–Maclaurin) | Riemann/Lebesgue continuum integral |
| `limit_eps` | discrete limit (Richardson on `1/n`) | ε–δ limit taken as primitive |
| `ode_rk4` | discrete ODE (RK4 = `I_ε` of the field) | continuous initial-value problem |
| `accelerate_alt`, `em_sum` | Euler transform; Euler–Maclaurin partial sum | "the sum of the infinite series" |
| `reparametrize` | admissible change of variable | improper-integral hand-waving |
| number ladder `D→ℤ→ℚ→ℝ` | each rung a readout of the last; `ℝ` = regular Cauchy of `ℚ` | ℝ as a primitive continuum |

## The process (verb — the one loop; run it top to bottom, then stop)

1. **DECLARE** the resolution `λ` and the layer (`A11`). *What is being read, and how finely?* Every
   later step is relative to this. No declaration ⇒ no computation.
2. **EXPRESS** the problem in tools only — operators (`⊕…log`), `D_ε`, `I_ε`, `L_R`. If a step needs a
   continuum primitive (a real, a completed limit, an angle, `∞`), **stop and re-express**; consult the
   contaminated-concept table (Appendix A). This is the contamination gate.
3. **COMPUTE at finite ε** — never at `ε=0`. Get the readout at declared, finite resolution.
4. **STABILIZE** — take the readout to its `A8` plateau with the right accelerator (`limit_eps`,
   `accelerate_alt`, Euler–Maclaurin). The plateau *is* the value; the `ε→0` object is never formed.
5. **TIER-TAG** the result: `Th_coqc` (exact `ℚ`, machine-checked) / `finite_diagnostic` (numeric
   readout to declared tolerance) / `Dr` (design) / `+ℝ-Open` (honestly unsolved). State the tolerance.
6. **FENCE** the Open — name what stayed `+ℝ-Open` (the completed limit) and predict the readout. Do
   not let a reproduced readout masquerade as a solved continuum theorem.

That is the whole method. Six steps, one pass, no continuum ever formed — validated end-to-end at
**1000/1000** (grade-school→PhD, Appendix D) and **100/100** (continuous problems, Appendix E).

## Why this is "light and sharp"

- **Light:** the tools are frozen and tested once (`idm_tools` self-check); the process is 6 lines with
  no branching. There is nothing to re-derive per problem.
- **Sharp:** the contamination gate (step 2) and the tier-tag (step 5) are the two cuts that keep the
  result honest — every answer states exactly how it is known and where it stops. Same answers as the
  classical pipeline, obtained without the continuum, and *with* an explicit honesty fence the classical
  pipeline lacks.
