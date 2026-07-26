# METHOD — tools vs. process (the sharp solve loop)

> A **tool** is a *noun* you invoke. A **process** is the *verb* that composes tools into a result.
> Keeping them separate is what makes the method light: the tools are fixed and tested; the process is
> a short, repeatable loop. Developed by Yaoharee Lahtee.

## Rule 0 — translate into the information language FIRST (before any formalization)

**Before formalizing any problem — a matrix, an equation, a proof, a physics result — first translate
it into the information (retained-distinction) language of §7.0.** A matrix is a table of *retained
couplings*; an eigenvalue is a *retained mode*; a projector is a *retained selection* (an idempotent
that keeps a sub-distinction and discards the rest); a Jacobian is the *retained sensitivity* `D_ε` of a
readout to its source. Never carry a world-language object (a "real matrix", a "smooth map", a
"probability") straight into the formalism — restate it as a readout of retained distinctions, tier it,
then formalize. This is the contamination gate applied at the *modelling* step, upstream of step 2.
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

> **Note on the top three rows** (`δ_R`/`L_R`, the operator set, the number ladder): these are
> *conceptual / Coq-verified* structures, not callable `idm_tools` functions. When step 2 says "express
> in tools only," use Python's exact substrate for them — `fractions.Fraction` for `ℚ`/the ladder,
> native `+ - * / ** ` and `math.sqrt`/`math.log` for the operator set, `sympy`/`numpy` for `L_R`
> matrices. The callable `idm_tools` functions are the rows from `D_eps` down.

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

## The numeric-honesty discipline (`tools/idm_discipline.py`)

When you compute on a floating substrate (not exact `ℚ`), six operational rules keep the readout
honest. They are extracted and merged from the earlier `cpg_math` MathSolver v0.1.0 (benchmark 6/6),
now folded into this framework:

1. **Declared resolution** — never compare resolution-bounded readouts with `==`; use `eq_eps(a,b,eps)`,
   and never chain it as if transitive (`eq_chain_guard` BLOCKs the sorites trap).
2. **Verdicts, fail-closed** — every solve/fit/convergence returns `Verdict(ACCEPT/HOLD/BLOCK)`; budget
   exhaustion or degeneracy is `HOLD`, never a silent answer. A `Verdict` is truthy only on `ACCEPT`.
3. **Admissibility by construction** — evolve the *record* in coordinates that cannot leave the
   admissible set (log/sigmoid/mod, e.g. `integrate_positive_decay`); a readout underflow to 0 is a
   correct zero-at-resolution verdict, not a violation; clipping is a *reported* repair, never silent.
4. **Carry the residual** — accumulate with `sum_neumaier` (retains the translation residual on the
   dominant branch — beats naive and even Kahan on large-swing inputs); check admissibility at the
   record level, not the readout level.
5. **Discrete-exact first** — sequence/cost bookkeeping via the causal calculus (`D_ε`, `I_ε`, FTCC is
   exact, `idm_tools`); form a continuum only through a declared A8-stability gate.
6. **Cost ledger** — when complexity matters, produce a `CostLedger`, not an adjective.

Boundary (inherited): this is a discipline layer ON the classical substrate — classical mathematics is
not wrong, not replaced. Valid-in-discipline ≠ true-about-world; an ACCEPT is a readout at the declared
resolution, not a truth certificate.
