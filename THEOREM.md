# The Certified Finite-Readout Theorem

The `prove_it*` suites establish a `finite_diagnostic`: finite procedures *agree* with the standard
continuum value to many digits. This document states the stronger target the project is built toward —
turning "it computes the right number" into "**it computes a number with a proven error bound, or it
refuses**" — and records what is proved today versus what is still open.

## Statement (schema)

> **Certified Finite-Readout.** Fix a class of inputs `𝒞` (with a named stability hypothesis `H`) and a
> target functional `T` (a derivative, an integral, a limit, a series sum, …). There is a finite
> algorithm `A` such that for every input `x ∈ 𝒞` and every rational tolerance `ε > 0`, `A(x, ε)`
> **terminates** and returns either
>
> - `CERTIFIED (q, B)` with `q, B ∈ ℚ` (or arbitrary-precision), a finite expression in `x`, and a
>   **proof that** `|q − T(x)| ≤ B ≤ ε`; or
> - `HOLD`, when the hypothesis `H` fails — it returns **no number** rather than a fabricated one.
>
> No completed limit is formed: `q` and `B` are finite readouts of the input.

The contract is realized in code by `tools/certified_readout.py` (`Readout(q, bound, status, reason)`)
and probed adversarially by `validation/negative_controls.py`.

## What is proved today

### 1. Geometric series — machine-checked, axiom-free (`Th_coqc`)

Class: `r ∈ ℚ`, hypothesis `H : 0 ≤ r < 1`. Algorithm: `S_N = Σ_{k<N} r^k`. Target: `1/(1−r)`.

- **Exact identity** (`formal/IDM_Certified.v : geom_certified_identity`):
  `(1 − r) · S_N = 1 − r^N`.
- **Exact defect** (`geom_certified_defect`): `1 − (1 − r)·S_N = r^N`, hence on paper
  `1/(1−r) − S_N = r^N/(1−r)` — the shipped error certificate.
- **Termination + tolerance selection**: `r^N/(1−r) → 0`, so the least `N` with `r^N/(1−r) ≤ ε` exists
  and is found by a terminating loop (`geom_series_certified`). Outside `0 ≤ r < 1` the tool returns
  `HOLD`.

Both Coq theorems report `Closed under the global context` under `Print Assumptions` (run
`bash formal/verify.sh`).

### 2. Finite exponential, Simpson quadrature, Richardson limit — derived certificates (`finite_diagnostic`)

Implemented with proven-on-paper bounds in `tools/certified_readout.py`:

| tool | class / hypothesis `H` | error bound `B` | HOLD when |
|---|---|---|---|
| `exp_certified` | `|x| ≤ ½` | `|x|^{N+1} / ((N+1)! (1−|x|))` | `|x| > ½` (range-reduction cert. not yet formalized) |
| `simpson_certified` | `f ∈ C⁴`, bound `M₄ ≥ max|f⁗|` given | `(b−a)⁵ M₄ / (180 N⁴)` | no `M₄` supplied |
| `richardson_certified` | sequence has a `1/n` asymptotic expansion | a-posteriori: the contracted diagonal gap | diagonal fails to contract (e.g. `1/log n`, oscillatory, divergent) |

These are `finite_diagnostic`/`Dr`: the bounds are standard and the code enforces them, but the
remainder inequalities are not yet Coq-checked.

## What is still open (`+ℝ-Open` / next work)

- Formalize in Coq the `exp_certified` Taylor-tail bound and the range-reduction (`exp(x)=exp(x/2)²`)
  certificate, giving a second fully machine-checked end-to-end algorithm over the rationals/reals.
- Formalize the Simpson and Euler–Maclaurin remainder inequalities (needs a real-analysis layer).
- A general Richardson **a-priori** certificate (not just the a-posteriori contraction test).

The honest position: the **geometric-series certified readout is proved end-to-end and axiom-free**; the
other tools **carry derived certificates and a working HOLD discipline**, and their formalization is the
declared next step. This is the lever from "computes the right number" to "certified computation."
