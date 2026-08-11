# Case study — the double pendulum, read through IDM (not part of the `formal/` theorem count)

**Status: illustrative worked example, not a core-library claim.** Nothing here is wired into
`formal/verify.sh`'s curated theorem list or the README/SKILL.md theorem counts. This directory
exists to show the contaminated-concept table, the operator-first discipline, and the
never-take-the-infinite-limit discipline applied end-to-end to a real, well-known chaotic
system — including two predictions that were made *before* running any code and then **failed**,
reported plainly rather than dropped, per this repo's own readout-not-truth honesty standard.

## What's here

| file | what it does |
|---|---|
| `exact_q_double_pendulum.py` | Angle-free Cartesian reformulation (positions placed via exact Pythagorean-triple rational points, no `sqrt`/`cos`/`sin` anywhere), unbounded `fractions.Fraction` arithmetic. **Fails**: denominator bit-length grows ~9x every 2 steps (confirmed independent of spring stiffness `K`, tested at `K=20000` and `K=100`), computationally dead by step ~8. |
| `exact_q_bounded_double_pendulum.py` | The fix: declared, bounded-denominator truncation (`Fraction.limit_denominator`) once per step — exactly what `R := readout of finite Q approximants` already permits, applied *openly* rather than silently. Runs 3000 steps in 1.4s; agrees with float64 to ~1e-15. |
| `idm_operator_first_chaos_fix.py` | Operator-first re-read of "why doesn't this look chaotic": computes the discrete map's one-step Jacobian by finite differences (`h` fixed, never `->0`) and finds its dominant-eigenvalue direction by **200 fixed** power-iteration steps (a declared finite count, not a limit). Prediction based on this (`eigenvalue 1.153 > 1` implies growth) **also failed** — the full nonlinear trajectory stayed flat. Real lesson: a single-point linearization doesn't predict a moving trajectory's actual separation; see the file's docstring. |
| `idm_finite_lyapunov.py` | The corrected method: Benettin block-renormalized **finite-N** growth-rate estimate. Explicitly named contamination risks and how each is handled: (1) the classical Lyapunov exponent needs `t->infinity` — **never taken**; a finite, declared block count (`N_BLOCKS`) is reported instead, honestly labeled as *not* the idealized limit; (2) renormalization needs a Euclidean norm (generically irrational even for rational inputs) — done via `math.sqrt` as a **declared, flagged, finite float64 approximation**, empirically justified by (2)'s own float-vs-bounded-Q agreement check. Result: both a low-energy and a high-energy exact-rational initial condition give a positive finite-N estimate that stabilizes into a fluctuating ~1.6–2.6 band by `N=1000` — real signal, still explicitly not claimed as "the" Lyapunov exponent. |
| `ShakeIrrational.v` | The one `Th_coqc` result in this case study. Standalone (does **not** participate in `formal/verify.sh`). Proves, axiom-free (`Print Assumptions` = *Closed under the global context*), that a specific 21-digit integer — the exact discriminant numerator of the SHAKE rigid-constraint equation for this system's actual first Verlet step — is not a perfect square, i.e. **for this concrete step, SHAKE's Lagrange multiplier is provably irrational**. This is the machine-checked justification for why the case study uses a penalty spring instead of SHAKE to stay closed over `Q` (SHAKE's exact root would generically re-import `R`). Compile: `coqc -q ShakeIrrational.v`. |

## Why this belongs here (repo, not just a private note)

Every one of the five files demonstrates a *different* discipline from this repo's own
contaminated-concept table and pre-write checklist, on a system nobody could accuse of being
cherry-picked to make IDM look good — the double pendulum is a famously hard, famously chaotic,
famously float-sensitive textbook system:

- **angle -> exact rational point** (never `cos`/`sin`/degrees): `exact_q_double_pendulum.py`
- **"R is a readout of finite Q approximants," done openly, not silently**: the bounded-truncation
  fix, `exact_q_bounded_double_pendulum.py`
- **operator-first, not blind empirical search**: `idm_operator_first_chaos_fix.py` — and an
  honest report of where that first attempt still fell short
- **refuse the `t->infinity` limit; report the finite, declared quantity you actually computed**:
  `idm_finite_lyapunov.py`
- **tier the claim; `Th_coqc` only where something is actually machine-checked**: `ShakeIrrational.v`,
  with the bridge back to physical irrationality explicitly marked `Dr` (a cited, not re-derived,
  classical fact), never collapsed into the compiled result's tier

Two predictions made explicitly, before running code, **failed** (documented in
`idm_operator_first_chaos_fix.py`'s docstring and this README's table above) — reported as failures,
not quietly revised after the fact. That is the same discipline this repo asks of every other claim
it ships.

## Reproduce

```bash
python3 -u exact_q_double_pendulum.py              # the unbounded run that blows up
python3 -u exact_q_bounded_double_pendulum.py       # the fix: 3000 steps in 1.4s
python3 -u idm_operator_first_chaos_fix.py          # Jacobian/power-iteration probe
python3 -u idm_finite_lyapunov.py                   # Benettin finite-N growth-rate estimate
coqc -q ShakeIrrational.v                           # the one Th_coqc theorem, compiles clean
```

No dependencies beyond the Python standard library (`fractions`, `math`, `time`) and Coq
(`ZArith`, `Lia` — both standard library).

## What this does NOT claim

- Not a general theorem that SHAKE's multiplier is irrational for *every* rational double-pendulum
  state — only the one concrete step checked here. Named `Open`.
- Not a claim that ~1.6–2.6 is "the" Lyapunov exponent of this system — the finite-N estimate had
  not fully flattened by `N=1000`; a rigorous value would need far more blocks and multiple probe
  directions with variance characterization. Named `Open`.
- Not part of this repo's headline "N machine-checked theorems" count anywhere in README/SKILL.md —
  deliberately kept out of `formal/verify.sh`'s gate so it never silently inflates that number.
