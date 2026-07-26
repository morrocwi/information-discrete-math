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
| `integral_stable_certified` | refinement gaps contract (ρ<1) | `g_last/(1−ρ)` (see §7, Coq-backed) | gaps don't contract (pole / non-integrable / oscillatory) |
| `richardson_certified` | sequence has a `1/n` asymptotic expansion | a-posteriori: the contracted diagonal gap | diagonal fails to contract (e.g. `1/log n`, oscillatory, divergent) |

`simpson_certified`/`richardson_certified` are `finite_diagnostic`/`Dr`; `integral_stable_certified` is
backed by the Coq theorem in §7. **A note on the integral, on principle:** the classic Simpson bound is
stated as a distance to the *true continuum integral* `∫f`. Under readout-first there is **no** completed
`∫f` to be the target — demanding that distance would smuggle the continuum back in as the primitive. So
`integral_stable_certified` does **not** target `∫f`; it certifies that our *own* readout has stabilized
(§7). The `M₄`-based `simpson_certified` is kept only as an optional continuum-comparator convenience.

### 3. Geometric-majorant tail bound — machine-checked, axiom-free (`Th_coqc`)

The *mechanism* behind the `exp`/Simpson-tail certificates is Coq-checked
(`formal/IDM_Certified.v : geom_majorant_tail`): for any run of nonnegative terms that contracts by a
ratio ρ (`t_{k+1} ≤ ρ·t_k`), every finite tail obeys `(1 − ρ)·Σ_{j<M} t_{N+j} ≤ t_N`, i.e. the tail is
`≤ t_N/(1 − ρ)` — a finite, division-free stability certificate, `Closed under the global context`.

### 4. Finite exponential's Taylor tail — machine-checked, axiom-free (`Th_coqc`)

The exp instance is now fully closed in Coq (`exp_tail_certified`): with the terms
`exp_term x k = x^k/k!` built by the standard recurrence `t_{k+1} = t_k·x/(k+1)`, the lemmas
`exp_term_nonneg` (`0 ≤ x ⇒ 0 ≤ t_k`) and `exp_term_ratio` (`0 ≤ x ⇒ t_{k+1} ≤ x·t_k`, since
`x/(k+1) ≤ x`) discharge the hypotheses of `geom_majorant_tail`, giving

    0 ≤ x  ⇒  (1 − x) · Σ_{j<M} exp_term x (N+j)  ≤  exp_term x N,

i.e. the M-term Taylor tail from index N is `≤ (x^N/N!)/(1 − x)` — the certified remainder of the
finite exponential, machine-checked and axiom-free. This is the second end-to-end certified algorithm
(after the geometric series).

### 5. Range-reduction propagation — machine-checked, axiom-free (`Th_coqc`)

`exp(x) = exp(x/2)²`, so a readout for a large argument is the *square* of a readout for the halved one;
the only question is how error propagates through squaring. Proved in Coq (`sq_error_propagation`),
axiom-free over ℚ:

    |p − v| ≤ e   ⇒   |p² − v²| ≤ (2|v| + e)·e.

Halving `m` times (until the reduced argument is `≤ ½`, where `exp_tail_certified` applies) and squaring
back `m` times therefore keeps a controlled, finite error — the mechanism that extends the exponential's
certificate from `|x| ≤ ½` to any `x`.

### 6. Iterated-squaring assembly — machine-checked, axiom-free (`Th_coqc`)

The `m`-fold range reduction is now a single Coq theorem (`iter_sq_certified`): with `iter_sq p m` =
`p^(2^m)`, if `|p − v| ≤ e` and `|v| ≤ a`, then after `m` squarings

    |iter_sq p m − iter_sq v m| ≤ errbound a e m,

where `errbound` is the finite, computable bound obtained by iterating `sq_error_propagation` `m` times
(`errbound a e (S k) = (2·valbound a k + errbound a e k)·errbound a e k`). Composed with
`exp_tail_certified` at the halved argument (`|x/2^m| ≤ ½`) and the halving identity `exp(x)=exp(x/2)²`,
this carries the finite exponential's certificate from `|x|≤½` to **any** `x`, with a fully finite error
bound — machine-checked, axiom-free.

### 7. Integral by finite stability — machine-checked, axiom-free (`Th_coqc`)

The readout-first way to certify a quadrature — **without ever naming a completed `∫f`**. Refine the
panel count (`N, 2N, 4N, …`); the successive readouts differ by gaps `s_k`. Two Coq theorems
(`formal/IDM_Certified.v`) make the stability rigorous over ℚ:

- `abs_tailsum_le`: `|Σ gaps| ≤ Σ |gaps|` (triangle over a finite tail);
- `refine_stable`: if the gaps contract (`|s_{k+1}| ≤ ρ|s_k|`, `ρ ≤ 1`), then the difference between any
  two refined readouts `M` steps apart obeys `(1 − ρ)·|Σ_{j<M} s_{N+j}| ≤ |s_N|` — i.e. every further
  refinement agrees within `|s_N|/(1 − ρ)`, a **computable rational** (proved by combining
  `abs_tailsum_le` with `geom_majorant_tail` on `|s|`).

So when the refinement gaps contract, the readout has a certified stable plateau; when they do not
(pole, non-integrable, oscillatory), there is no plateau and the tool returns `HOLD`
(`integral_stable_certified`, with the pole/singular cases in `validation/negative_controls.py`). We
never claim a distance to `∫f`; we certify that *our own* finite readout has stopped moving. Both
theorems `Closed under the global context`.

## What is still open (`+ℝ-Open` / next work)

- A general Richardson **a-priori** certificate (deciding contraction from the sequence's form up front,
  not only the a-posteriori contraction test already implemented).
- Extend the finite-stability certificate to more refinement families (multi-dimensional quadrature,
  adaptive grids) — same ℚ-only `refine_stable` mechanism, more instances.

*(Note: we do **not** list "prove the Simpson/Euler–Maclaurin bound against the true `∫f`" as open work.
That is a continuum-first obligation the framework does not accept: the certified object is the stability
of the finite readout, §7, not its distance to a completed integral.)*

The honest position: the **geometric-series certified readout is proved end-to-end and axiom-free**; the
other tools **carry derived certificates and a working HOLD discipline**, and their formalization is the
declared next step. This is the lever from "computes the right number" to "certified computation."
