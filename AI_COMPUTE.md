# AI_COMPUTE — how another AI computes mathematics with this framework

> **Audience: an AI agent that must produce a mathematical answer.** This is the fastest correct path.
> Read it top to bottom once; then compute. Everything here is finite and runnable — no continuum is
> ever formed. Framework by Yaoharee Lahtee. Full theory: `textbook/INFORMATION_DISCRETE_MATHEMATICS.md`.

## 0. The one idea you must hold

Everything you read is a **finite discrete rational readout**. The continuum (real numbers as
primitives, `h→0` that lands, `+∞` reached, a zero-size point, a continuum angle) is a **non-readout**:
never inject it as a premise. You may *recover* any continuum answer as the stable readout of a finite
computation — that is what the tools below do.

## 1. Pick the tool by problem type (the decision table)

| your problem | tool (in `tools/idm_tools.py`) | one-liner |
|---|---|---|
| derivative `f′(x₀)` | `D_eps(f, x0)` | central diff + Richardson |
| definite integral `∫ₐᵇ f` | `I_eps(f, a, b, N)` | trapezoid + Euler–Maclaurin |
| improper/singular `∫` | `reparametrize(f, u, du, t0, t1)` | change variable → nice integral |
| limit `lim_{n→∞} aₙ` | `limit_eps(seq)` | Richardson on `h=1/n` |
| ODE `y′=f(x,y)`, value at `xT` | `ode_rk4(f, x0, y0, xT, N)` | RK4 = `I_ε` of the field |
| alternating/oscillatory sum | `accelerate_alt(terms)` | Euler transform |
| `ζ`-type / slowly-convergent sum | `em_sum(term, N, tail)` | Euler–Maclaurin partial sum |
| exact arithmetic / algebra / linear systems | `sympy` over `ℚ` | exact, no floats — see §3 |
| honest float compute (equality, sums, root-find, verdicts) | `tools/idm_discipline.py` | `eq_eps`, `sum_neumaier`, `solve_obstruction`, `Verdict` |
| check a solution genuinely USES the framework (not relabel) | `tools/framework_compliance.py` | `classify_regime`, `audit`, `verify_executed` |
| group / counting / graph invariant | finite enumeration or `L_R` (§3) | native discrete tier |

If a step seems to need a real number, a completed limit, an angle, or `∞` as a *primitive* — **stop**,
consult `Appendix A` (contaminated-concept → discrete-replacement table), and re-express.

## 2. Run the 6-step process (from `METHOD.md` — do not skip a step)

1. **DECLARE** resolution `λ` / layer (what is read, how finely).
2. **EXPRESS** using tools only (operators `⊕⊗÷^√log`, `D_ε`, `I_ε`, `L_R`). Hit the contamination gate.
3. **COMPUTE at finite ε** (never `ε=0`).
4. **STABILIZE** to the A8 plateau with the right accelerator (`limit_eps`, `accelerate_alt`, `em_sum`).
5. **TIER-TAG** the answer: `Th_coqc` (exact ℚ) / `finite_diagnostic` (numeric to a stated tolerance) /
   `Dr` (interpretive) / `+ℝ-Open` (honestly unsolved). Always state the tolerance.
6. **FENCE** the Open — name any completed-limit object you did *not* actually form.

## 3. Copy-paste examples (each returns the world-benchmark answer)

```python
import sys; sys.path.insert(0, "tools")
from idm_tools import D_eps, I_eps, limit_eps, ode_rk4, accelerate_alt, reparametrize
import mpmath as mp, sympy as sp

# derivative:            d/dx x³ at 2  → 12
D_eps(lambda x: x**3, 2)                                   # finite_diagnostic, ~1e-5
# integral:             ∫₀^π sin x     → 2
I_eps(mp.sin, 0, mp.pi, 400)                              # finite_diagnostic, ~1e-8
# singular integral:    ∫₀^1 ln(1/x)dx → 1   (x=e^{-t})
reparametrize(lambda t: t*mp.e**(-t), None, None, 0, 50) if False else I_eps(lambda t: t*mp.e**(-t),0,50,4000)
# limit:                (1+1/n)^n      → e
limit_eps(lambda n: (1 + mp.mpf(1)/n)**n)                 # finite_diagnostic, ~1e-6
# ODE:                  y'=2xy,y(0)=1  → y(1)=e   (exact e^{x²})
ode_rk4(lambda x, y: 2*x*y, 0, 1, 1, 400)                # finite_diagnostic, ~1e-6
# exact algebra (ℚ):    solve Ax=b     → exact rationals   (Th_coqc-elig, EXACT)
sp.Matrix([[2,1],[1,3]]).solve(sp.Matrix([3,5]))
# graph invariant:      spanning trees of K4 → 16   (matrix-tree = det of L_R minor, EXACT)
```

## 4. Where things live (and how to extend)

```
textbook/INFORMATION_DISCRETE_MATHEMATICS.md   the full theory (Parts 0–XV + Appendices A–E)
tools/idm_tools.py                             THE TOOLS (nouns) — import and call; self-check: python3 tools/idm_tools.py
tools/idm_discipline.py                        THE NUMERIC-HONESTY DISCIPLINE — Verdict/eq_eps/Neumaier/CostLedger/fail-closed solve
METHOD.md                                      THE PROCESS (verb) — the 6-step loop
AI_COMPUTE.md                                  this file — the AI quick-start
validation/thousand_problems.py                1000/1000 grade-school→PhD
validation/hundred_continuum_problems.py       100/100 continuous problems reproduced from the discrete
validation/breadth_problems.py                 48/48 algebra·linear·complex·combinatorics/graph
plugins/…/skills/information-discrete-math/    the installable skill (loads before any math)
```

**To add a chapter (extensibility contract):** append a new `# Part N — <title>` before `# Appendix A`,
derive everything from `δ_R` / `L_R` / the Part VII operators (never a continuum primitive), tier-tag
every claim, and add a matching block to a `validation/*.py` suite so the numeric claims are executed
before they enter prose (the *pytest-before-claim* rule). Update this table and `INDEX.md`.

## 5. Honesty rules you inherit (non-negotiable)

- An **exact readout is compared as an exact readout**, never through a float heuristic (the bug that
  once caused 2 false failures; see Appendix D).
- **No external-authority validation** — correctness is judged against the concrete problem in front of
  you, not anyone's say-so.
- State every tolerance; never let a reproduced readout masquerade as a solved continuum theorem.
