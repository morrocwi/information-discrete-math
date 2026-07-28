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

## The Five Core Theorems (the spine)

Everything downstream — the 263-kind solver, the certified-readout contract above, the
retained-spectral physics — rests on five statements. Each is given at the precision a referee
checks: an exact statement, its machine-checked witness (run `bash formal/verify.sh`;
`Print Assumptions` = *Closed under the global context* on every `Th_coqc` line), and an honest tier.
**Every finite claim in the spine has a witness in THIS repository's `formal/`** — the section proves
itself from the repository's own formal system; the one external pointer (the heavier *optional*
apparatus of §I) is explicitly marked optional and is not what the spine rests on.

The stance, stated once so nothing is overclaimed: **every quantity a reader ever obtains is a finite
rational *readout* of a retained difference; the continuum (`ℝ`, `+∞`, the point of zero extent) is a
*non-readout* — admissible as a boundary/limit object under an explicit hypothesis, never as a root
primitive.** The five theorems make that stance precise and, where the content is finite,
machine-check it.

### I · The primitive `δ_R` exists — and the discrete floor

**Statement.** A first distinction exists: `∃ a b, a ≠ b`, realized by `succ 0 ≠ 0`. The engine `D`
(ground `0`, successor `succ` = "retain one more distinction") carries a **discrete floor**
`¬∃z, 0 ≺ z ≺ succ 0`. Hence density is provably absent at the root: a continuum can enter only as a
later readout, never as a primitive.

**Witnesses (all local, this repository).** The existence of `δ_R` and the discrete floor are
*exhibited*, not postulated, in `formal/IDM_Genesis.v`: `primordial_difference_exists`
(`∃ a b : ℕ, a ≠ b`), `succ_ground_distinct` (`succ 0 ≠ 0`), and `discrete_floor`
(`¬∃z, 0 < z < succ 0`) — all `Th_coqc`, `Print Assumptions` = *Closed under the global context*.
`D` is modelled as `ℕ` (`0`/`succ` = `0`/`S`), so `D ≅ ℕ` is definitional; `D`-semiring
distributivity is `formal/IDM_FiniteWitnesses.v: semiring_distrib` and the finiteness of every readout
is `formal/IDM_FiniteWitnesses2.v: no_infinite_readout`. **Tier `Th_coqc`.**
*(Optional, not load-bearing: the heavier `D⊨PA` / second-order categoricity apparatus is developed
in the sister repo `research_universal_solver`; the spine's claim needs only the four local genesis
theorems above.)*

**Why it cannot be disputed.** Nothing below `δ_R` is assumed; the object claimed to exist is
*exhibited* (`succ 0`) and machine-checked here, the discrete floor is a one-line `lia` fact over `ℕ`,
and every structural property is an ordinary theorem of a free commutative semiring — not a postulate
about the continuum.

### II · The number tower is a chain of readouts: `D → ℤ → ℚ → ℝ`

**Statement.** `ℤ := (D×D)/∼` with `(a,b)∼(c,d) ⟺ a⊕d = c⊕b` is a commutative ring; `ℚ` is its
field of fractions; each rung is *defined from* and maps homomorphically onto the previous one. `ℝ`
is the **readout rung** — a completion introduced only where a stability (A8) hypothesis licenses it,
and honestly tagged `+ℝ-axioms` (it imports `Coq.Reals`), never `axiom-free`.

**Witnesses.** `ℤ`-ring distributivity is local (`formal/IDM_FiniteWitnesses3.v: ring_distrib_Z`,
`Th_coqc`, axiom-free). The Grothendieck `(D×D)/∼` and the fraction field are the standard elementary
quotient/localization constructions over the local semiring of §I. The `ℝ` rung is the *only* place
axioms enter — imported `Coq.Reals`, tiered `+ℝ-axioms` by construction, never `axiom-free`.

**Why it cannot be disputed.** The ring/field constructions are the standard Grothendieck and
fraction-field completions; the only place axioms enter (`Coq.Reals`) is *named and tiered*, so no
real-analysis assumption is ever passed off as finite.

### III · READOUT (A1): every appearance is `r = O_ε(X) ∈ ℚ` at a declared resolution `ε ≻ 0`

**Statement (definitional substrate, `Dr`).** A reading is a map `O_ε` from an object `X` and a
rational resolution `ε ≻ 0` to a rational `r ∈ ℚ`. `ℝ`, `+∞`, and the point of zero extent are *not*
in the range of any `O_ε`. Realized in code as `Readout(q, bound, status, reason)`
(`tools/certified_readout.py`); its behavioural contract is the Certified-Finite-Readout theorem at
the head of this document — return `CERTIFIED (q,B)` with `|q − T| ≤ B ≤ ε`, or `HOLD`.

**Tier `Dr`.** This is a *definition*, not a theorem — it is what the `Th_coqc` results are theorems
*about*. Declared as such: no proof is claimed for a definition, and it does no illicit work beyond
fixing the type of "a reading".

### IV · The KEYSTONE (A4 · Th 5.1): `B(Φ,Φ) = I(Φ)` — Dirichlet energy **is** retained information

**Statement (`Th_coqc`, axiom-free).** For a weighted graph `g` (edges `(i,j,w)`) and any field
`Φ : ℕ → ℚ`, the assembled Laplacian quadratic form equals the retained-information functional, edge
by edge and in total:

  `Φᵀ L_R Φ  =  Σ_{(i,j,w) ∈ g} w · (Φ_i − Φ_j)²`,   with   `L_R = D_W − W`.

**Proof.** Per edge the identity is `w·Φ_i² + w·Φ_j² − 2w·Φ_iΦ_j = w·(Φ_i − Φ_j)²`, an elementary ring
identity (closed by `ring`); assembly over the edge list is a one-line induction. Positivity: with
`w ≥ 0` on each edge, `Φᵀ L_R Φ ≥ 0` (`keystone_nonneg`) — `L_R` is PSD and the retained metric is a
genuine seminorm.

**Witness.** `formal/IDM_Keystone.v: keystone_B_eq_I`, `keystone_nonneg` — `Th_coqc`,
`Print Assumptions` = *Closed under the global context* over `ℚ` (no `Reals`, no `classic`).

**Why it cannot be disputed.** It is a one-line elementary algebraic fact over an ordered field,
checked by a proof assistant with no axioms; the only definitional input is `L_R = D_W − W`, the
standard graph Laplacian. The interpretive reading — *information*, not length or energy, is the
central invariant, with distances/spectra/mass-ratios read out of `L_R` — is stated *separately* from
the theorem and labelled as interpretation.

### V · FOLD + DECISION (A2/A3) and the exact FTCC: `I_ε(D_ε f)[N] = f[N] − f[0]`

**Statement (`Th_coqc`, axiom-free).** With the causal difference `D_ε f[n] := (f[n] ⊖ f[n−1]) / ε`
and its accumulation `I_ε`, accumulation inverts differencing **exactly**, with no limit taken:

  `I_ε(D_ε f)[N] = f[N] − f[0]`  (FTCC),   and   `Σ_{n<N} (f(n+1)·Δg(n) + g(n)·Δf(n)) = f_N g_N − f_0 g_0`.

**Proof.** Telescoping induction on `N` (`ring` at each step).

**Role.** FOLD (A2) is accumulation over a monoid; DECISION (A3) is search-and-certify; the KEYSTONE
(IV) is exactly what lifts FOLD's difference operator `D_W` into `L_R`. The structural claim "*each
solver branch's kernel is an instance of FOLD or DECISION*" is itself machine-checked
(`formal/IDM_Reduction.v`: `ftcc_Z`, `sum_is_fold`, `dot_is_fold`, `foldmin_le_*`, `foldmax_ge_*`, …),
so the 263-kind surface is not a menu of programs but instances of two certified schemata bridged by
one identity.

**Witnesses.** `formal/IDM_Calculus.v: FTCC_telescope, summation_by_parts`; `formal/IDM_Bridge.v:
FTCC_exact`; the reductions in `formal/IDM_Reduction.v` — all `Th_coqc`, *Closed under the global
context*.

**Why it cannot be disputed.** FTCC is the discrete fundamental theorem of calculus — a telescoping
sum, exact by construction, with no `h → 0`. A referee can only agree that
`Σ_{n<N}(f(n+1) − f(n)) = f(N) − f(0)`.

### What these five do NOT claim (the fence)

- They do **not** dissolve real analysis, topology, or the continuum. `ℝ` remains available as a
  tiered readout (`+ℝ-axioms`); the manifold/PDE frontier is explicitly `+ℝ-Open` (Part XXI). No
  completed-limit theorem is asserted without its stability hypothesis and its tier.
- They do **not** claim physical truth. `L_R`-spectra reproduce physical numbers as `finite_diagnostic`
  readouts to a declared tolerance; the standing law is *correct output ≠ true theory*.
- They make **no** appeal to external authority. Every finite claim is checkable by
  `bash formal/verify.sh` on the reader's own machine (`Print Assumptions` = *Closed under the global
  context*) — the only warrant offered, and the only one needed.

The whole spine: a primitive (I) that forbids the continuum at the root, a number tower (II) that
recovers it only as a tiered readout, a reading contract (III), one exact operator identity (IV)
whose interpretive reading makes *information* the central invariant, and one exact accumulation law
(V) that — bridged by (IV) — generates the solver. The solver surface and the certified-readout
contract above are built as instances and corollaries of these five.

## The readout rule in practice: inertia is the spectral readout

The five theorems have an operational face in numerical linear algebra, stated as one rule:

> **Do not construct an object the requested readout does not require.**

This is the READOUT axiom (§III) turned into an algorithm-design law, and it has a canonical
instance — **spectral counting by inertia**. For a symmetric pencil `(K, M)` with `M` positive
definite and a shift `σ`, the *position of a level in the spectrum* is a readout obtained without ever
forming an eigenvector or the spectrum:

  `#{eigenvalues of (K, M) below σ}  =  #{negative pivots of an LDLᵀ factorization of K − σM}`
  — Sylvester's law of inertia; the count costs one factorization, **independent of the answer**.

Two classical identities carry it, and both are read as retained-information statements:

- **Sylvester inertia** — the sign-count of the `LDLᵀ` pivots *is* the count; the object retained is a
  running inertia, not the modes. This is exactly the Sturm sign-count the repository already uses (the
  native Retained Multilevel Sturm kernel in `retained_spectral/`, the three-layer correctness
  certificate, and the fooling family of the Declaration Bound above).
- **Haynsworth inertia additivity** — inertia is additive across a Schur complement, so *inertia is
  additive across a graph separator*: **the object that must be retained is the boundary, not the
  volume.** Recursive separator counting (nested dissection) replaces the band; the fill a poor
  elimination order creates is "volume the readout never asked for."

This unifies four things under one operator. Reading a level's position (`retained_spectral`), reading
it for a *banded generalized pencil* (transform-free inertia bisection — dropping the split-Cholesky /
congruence / tridiagonalization that only amplify `κ(M)`), reading a *count over an unstructured mesh*
(boundary-recursive Schur counting), and the Declaration Bound's **lower** twin (when the query is
deferred you *cannot* avoid retaining the whole object — `Θ(n log q)` bits) are all the same readout:
inertia. And inertia over a graph is read off the very operator of the KEYSTONE (§IV) — `L_R` and its
separators are that graph's structure.

**Tier, stated honestly.** Sylvester's and Haynsworth's identities are classical (cited as such, not
claimed here). The transform-free and boundary-recursive methods *report* large speedups on
narrow-band / slender-mesh problems — order 10¹–10² in the source packages — *together with* their own
honest limits (a crossover to sparse shift-invert once the bandwidth is no longer narrow; 2-D and 3-D
solid domains not competitive; single host; no eigenvectors). Those figures are **absorbed observations
from the source packages, not reproduced in this repository** (this repo's own machine-checked and
`finite_diagnostic` numbers are elsewhere and are for different problem classes), so they are cited as
the sources' measurements, **not** a machine-checked theorem here and **not** a universal-superiority
claim. What is ours — and what a reader can verify in-repo — is the reading: inertia is the spectral
readout, and the retained object is the boundary/count, never the volume/modes; the Declaration Bound
above (its q-ary core machine-checked in `formal/IDM_DeclarationBound.v`) is its exact lower twin.

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
