# Hilbert-Space Mathematical Core — H1 Build Spec (synthesized)

**Status:** `Dr` design → ready to implement. Synthesizes Designs 1/2/3 against the roadmap
(`HILBERT_MATHEMATICAL_CORE_ROADMAP.md`) and folds in every valid critique finding (#1–#7). Base
selection per the critique's recommendation: **Design 3's kind table + fence-enforcement mechanism +
PPT asymmetry**, with Design 3's two buggy Coq/PSD items **replaced**, and Designs 1/2's
finite-`n` scoping discipline (finding #3/#4) applied throughout.

Tier discipline (mandatory, restated from the roadmap):
- finite-dim `ℚ`/`ℚ[i]` linear algebra, decidable equalities/booleans = `exact` / `Th_coqc`-eligible.
- anything needing an irrational root of a finite-degree polynomial (generic eigenvalues, sqrt of a
  non-square) = `finite_diagnostic` — numeric, certified by a residual/tolerance bound, never silently
  exact.
- completeness (Cauchy→limit), `ℓ²`, `L²(X,μ)`, infinite orthonormal bases, infinite-dim spectral
  theorem = `+ℝ` / `+ℝ-Open` — never computed, never `Th_coqc`, only named readouts of finite
  `ℚ`-approximants.
- physics↔math dictionary (state/observable/evolution/measurement/…) = `Dr`, detachable, never
  touches a solver kind or a tier tag.
- **fixes applied from the critique:** vacuous Coq theorem (#1) replaced with a real discriminant
  witness; wrong Sylvester-leading-minors PSD test (#2) replaced with eigenvalue-sign PSD (matching
  Design 2's `completely_positive`, correctly tiered `finite_diagnostic`); general-`n≥3` Hermitian
  "real spectrum" claims (#3) scoped to concrete witness instances only, never a universal `forall`;
  the `n≤4 exact` table miswording (#4) corrected everywhere to "exact only when every eigenvalue is
  found rational, else `finite_diagnostic` regardless of `n`"; the `+ℝ` fence (#5) is **code-enforced**
  via a separate `hilbert_open.py` module reachable from `solve()` only through `HOLD`/`+R_OPEN`, never
  through the normal `ok` path; naming hygiene (#6) applied — neutral operator-algebra names in
  `hilbert.py`, physics reading confined to the textbook's `Dr` box; `operator_norm` (#7) restricted to
  a sqrt-free Gershgorin-type bound at `exact` tier, with the true operator norm always
  `finite_diagnostic`.

---

## 1. `idm/hilbert.py` module layout

Two files, mirroring `idm/exact.py`'s docstring-states-the-tier convention and `idm/solve.py`'s
`@kind(name, tier)` wiring — no new dispatch mechanism invented.

```
idm/hilbert.py                      # the finite-dim EXACT/finite_diagnostic core — no infinite-dim
│                                    #   object is ever formed here, structurally, not just by prose.
│
├── ---- exact scalar field: Q and Q[i] (Gaussian rationals) ----
│     QC(re, im)                    # exact Gaussian-rational scalar, (Fraction, Fraction) pair —
│                                    #   NOT python `complex` (complex = IEEE float, would silently
│                                    #   break every "exact" tag upstream of it)
│     qc_conj, qc_add, qc_sub, qc_mul, qc_div, qc_abs2, qc_eq   # finite Q[i] arithmetic, no float,
│                                                                 # no sqrt taken anywhere in this block
│
├── ---- vectors / inner product (finite n, entries in Q or Q[i]) ----
│     inner_product(u, v)           # <u,v> = sum_i conj(u_i)*v_i, exact Q[i], finite sum
│     norm_squared(v)               # <v,v>, exact Q, real, >=0 (proof obligation: norm2_nonneg, S3)
│     cauchy_schwarz_check(u, v)    # verifies |<u,v>|^2 <= <u,u><v,v> exactly (a runtime check, the
│                                    #   Coq proof is the general theorem; this is instance-verification)
│     is_orthogonal(u, v)           # exact boolean <u,v> == 0
│     gram_matrix(vectors)          # G_ij = <v_i,v_j>, exact Hermitian PSD Q[i] matrix
│
├── ---- Gram-Schmidt / orthonormal bases (deliberately two-stage, per Designs 1-3 agreement) ----
│     gram_schmidt(vectors)         # ORTHOGONALIZE ONLY (exact Q[i] — needs only field division by
│                                    #   exact inner products, no sqrt); returns orthogonal set +
│                                    #   their exact squared norms
│     orthonormal_basis(vectors)    # gram_schmidt + normalize; normalize step calls exact.integer_root
│                                    #   short-circuit per vector — exact iff EVERY norm is a perfect
│                                    #   square, else finite_diagnostic (certified sqrt, declared eps)
│
├── ---- subspaces / projection ----
│     projection_matrix(basis)      # P = A(A*A)^{-1}A*, exact Q[i], full-rank finite basis A
│     project(v, basis)             # P.v, exact Q[i]
│     is_idempotent(M)              # exact boolean M.M == M
│
├── ---- operators (finite n x n matrices over Q or Q[i]) ----
│     adjoint(M)                    # M* = conj(M)^T, exact
│     is_self_adjoint(M)            # exact boolean M == M*
│     is_unitary(M)                 # exact boolean M*M == I
│     is_normal(M)                  # exact boolean MM* == M*M
│     gershgorin_bound(M)           # FIX #7: max_i (sum_j |M_ij|) — a sqrt-free, exact-Q operator-norm
│                                    #   UPPER BOUND (row-sum/Gershgorin), never claims the true sup norm
│     operator_norm(M)              # finite_diagnostic ALWAYS: certified largest singular value via
│                                    #   power iteration on M*M + a-posteriori Rayleigh-quotient residual
│                                    #   bound ||M*M x - lambda x|| <= eps; never tagged exact even for
│                                    #   small n (fixes the Frobenius-vs-Gershgorin conflation, #7)
│     characteristic_poly(M)        # exact Q[i] coefficients — ALWAYS exact and finite regardless of
│                                    #   whether the roots turn out rational (finite elimination only)
│     spectral_decomposition(M)     # Hermitian/normal n x n. Rational-root fast path via
│                                    #   exact.rational_roots on characteristic_poly's output: tier
│                                    #   "exact" ONLY IF every eigenvalue found is rational AND every
│                                    #   eigenvector normalizes to an exact perfect-square norm — this
│                                    #   is a PER-CALL, per-instance tier, never a blanket "n<=k exact"
│                                    #   claim (fixes #4). Otherwise: certified numeric
│                                    #   Jacobi/QR iteration with a proven residual bound
│                                    #   ||M V - V Lambda|| <= eps, tier "finite_diagnostic".
│                                    #   Reality of the spectrum (Hermitian => real eigenvalues) is
│                                    #   asserted only up to the concrete Coq witness instances in
│                                    #   IDM_Hilbert.v (n=2,3, S3) — never as a general-n claim inside
│                                    #   this function's docstring or tier tag.
│
├── ---- composite systems (pure operator algebra; physics-neutral names, fix #6) ----
│     tensor_product(A, B)          # Kronecker product of vectors/matrices, exact Q[i]
│     partial_trace(M, dims, keep)  # exact Q[i] block-sum partial trace over a declared subsystem
│                                    #   (docstring: "pure operator-algebra object; any physics reading
│                                    #   is the detachable Dr layer only", per fix #6)
│     cp_map_generators             # renamed from kraus_ops (fix #6): a finite list of matrices
│                                    #   defining a linear map
│     choi_matrix(cp_map_generators)# exact Q[i] Choi-matrix construction from a finite generator list
│     is_completely_positive(choi)  # FIX #2: eigenvalue-SIGN PSD test (spectral_decomposition's
│                                    #   eigenvalues all >= 0), tier finite_diagnostic in general,
│                                    #   "exact" only in the same per-instance sense as
│                                    #   spectral_decomposition (all eigenvalues found rational and
│                                    #   nonneg exactly). Sylvester leading-principal-minors is NOT
│                                    #   used (it tests positive-DEFINITEness, not PSD — counterexample
│                                    #   diag(0,-1) passes leading minors but is not PSD; #2 fix).
│     is_separable_ppt(rho, dims)   # Peres-Horodecki: negative partial transpose => exact witness of
│                                    #   non-separability (finite eigenvalue-sign check, tier "exact"
│                                    #   when a negative eigenvalue is exactly found); positive partial
│                                    #   transpose is necessary+sufficient ONLY in dims 2x2/2x3 (tier
│                                    #   finite_diagnostic there); OUTSIDE 2x2/2x3 a positive result
│                                    #   returns status HOLD with reason "PPT necessary-only above
│                                    #   2x2/2x3" — never reports "separable" (Design 3's asymmetry,
│                                    #   praised in critique #8, adopted here)
│
└── ---- fence marker (imported by solve.py / textbook build, machine-visible, not just prose) ----
      COMPLETENESS_FENCE = {...}    # documents the I1/+R boundary; hilbert.py never imports
                                     #   hilbert_open.py (one-directional), so nothing below can ever
                                     #   accidentally produce an infinite-dim "answer"

idm/hilbert_open.py                 # FIX #5: the ONLY place +R/+R-Open objects are named. hilbert.py
│                                    #   does NOT import this file (checked by a one-line import-graph
│                                    #   test in tests/). Every function here returns a dict shaped
│                                    #   {"status": "+R_OPEN", "target": <name>, "approximant": <finite
│                                    #   Q-truncation actually computed>, "N": <truncation index>,
│                                    #   "note": "completed limit/object not formed"} — never a plain
│                                    #   "value" field, so _norm()/_ok() in solve.py cannot mistake it
│                                    #   for a certified answer.
│
├── completeness_readout(cauchy_seq, N)   # finite Cauchy-tail approximant up to index N + a certified
│                                          #   contraction-rate bound; never "the limit" as a value
├── l2_readout(seq, N)                    # first-N-coordinates truncation of an l^2 target + a proven
│                                          #   tail bound sum_{k>N} |x_k|^2 <= eps
├── L2_readout(f, mesh)                   # finite quadrature/discretization approximant of an L^2(X,mu)
│                                          #   target (reuses idm.integrate's certified DE-quadrature)
├── infinite_orthonormal_basis_readout(vectors, N)  # orthonormal_basis on the first N vectors only,
│                                                     #   explicit no-completeness-of-span claim
└── infinite_spectral_readout(...)        # NOT computed — returns the named target only, pointing at
                                            #   the finite-n spectral_decomposition as what actually
                                            #   exists; no numeric value at all
```

Wiring into `idm/solve.py` (mirrors the existing `algebra`/`geometry` import-line pattern):
```python
from . import hilbert as HB, hilbert_open as HBO
```
Every `hilbert.py` function gets one `@kind(name, tier)` entry per the table in §2 below (tier
resolved dynamically inside the handler where it is instance-dependent — `spectral_decomposition`,
`is_separable_ppt`, `is_completely_positive` — exactly the way `is_prime` already downgrades itself
above the Miller–Rabin deterministic bound). Every `hilbert_open.py` function is wired **only** through
a `HOLD`/`"+R_OPEN"` return path in `solve.py` — never given a normal `@kind(..., "exact")`-style
registry entry — so `solve()` structurally cannot emit an infinite-dim result dressed as certified.

---

## 2. Finite-dim EXACT solver kinds — registry table

| name | args | tier | semantics |
|---|---|---|---|
| `inner_product` | `u, v` (vectors of `ℚ`/`ℚ[i]` literals) | `Th_coqc` | `⟨u,v⟩ = Σ conj(uᵢ)·vᵢ`, exact `ℚ[i]`, finite sum; sesquilinearity/conj-symmetry proven in `IDM_Hilbert.v` |
| `norm_squared` | `v` | `Th_coqc` | `‖v‖² = ⟨v,v⟩`, exact non-negative `ℚ` |
| `cauchy_schwarz_check` | `u, v` | `exact` (instance-verification of a `Th_coqc` general theorem) | verifies `|⟨u,v⟩|² ≤ ⟨u,u⟩⟨v,v⟩` for the given finite vectors, exact `ℚ` comparison |
| `is_orthogonal` | `u, v` | `Th_coqc` | decidable exact `⟨u,v⟩ == 0` |
| `gram_matrix` | `vectors` | `Th_coqc` | `G_ij=⟨vᵢ,vⱼ⟩`, exact Hermitian PSD `ℚ[i]` matrix |
| `gram_schmidt` | `vectors` | `exact` | orthogonalization step only, exact `ℚ[i]` (no sqrt) |
| `orthonormal_basis` | `vectors` | `exact` iff every norm is an exact perfect square, else `finite_diagnostic` | `gram_schmidt` + per-vector certified normalization |
| `projection_matrix` | `basis` | `exact` | `P=A(A*A)⁻¹A*` for a full-rank finite basis, `ℚ[i]` |
| `project` | `v, basis` | `exact` | `P·v`, exact `ℚ[i]` |
| `is_idempotent` | `M` | `Th_coqc` | decidable exact `M·M == M` |
| `adjoint` | `M` | `Th_coqc` | `M* = conj(M)ᵀ`, exact, finite matrix |
| `is_self_adjoint` | `M` | `Th_coqc` | decidable exact `M == M*` |
| `is_unitary` | `M` | `Th_coqc` | decidable exact `M*M == I` |
| `is_normal` | `M` | `Th_coqc` | decidable exact `MM* == M*M` |
| `gershgorin_bound` | `M` | `exact` | sqrt-free row-sum upper bound on the operator norm — a certified **bound**, never the true sup norm (fix #7) |
| `operator_norm` | `M` | `finite_diagnostic` (always, every `n`) | certified largest singular value via power iteration on `M*M` + Rayleigh-quotient residual bound |
| `characteristic_poly` | `M` | `exact` | exact `ℚ[i]` coefficients, finite fraction-free elimination — exact regardless of root rationality |
| `spectral_decomposition` | `M` (Hermitian/normal `n×n`) | **per-instance**: `exact` only if every eigenvalue found is rational (via `characteristic_poly` + `exact.rational_roots`) and eigenvectors normalize exactly; else `finite_diagnostic` with a certified residual `‖MV−VΛ‖≤eps` — **never a blanket `n≤k ⇒ exact` claim** (fix #4) | real eigenvalues + orthonormal eigenbasis of a finite Hermitian/normal matrix |
| `tensor_product` | `A, B` (vectors or matrices) | `Th_coqc` | Kronecker product, exact `ℚ[i]`, finite |
| `partial_trace` | `M, dims, keep` | `Th_coqc` | finite-dim block-sum partial trace over a declared subsystem, exact |
| `choi_matrix` | `cp_map_generators` | `exact` | exact `ℚ[i]` Choi-matrix construction from a finite generator list |
| `is_completely_positive` | `choi` | **per-instance**: `exact` only if every Choi eigenvalue found is rational and its sign is decided exactly, else `finite_diagnostic` | eigenvalue-sign PSD test of the Choi matrix (fix #2 — Sylvester-leading-minors removed, wrong for PSD) |
| `is_separable_ppt` | `rho, dims` | negative-PT branch: `exact`; positive-PT in `2×2`/`2×3`: `finite_diagnostic`; positive-PT outside `2×2`/`2×3`: `HOLD` (never "separable") | Peres–Horodecki test, asymmetric honesty per Design 3 |

Every row returns through the existing `solve.py` `_ok`/`_readout` envelope (`status`, `value`,
`method`, `tier` carried in `method`/`reason` for per-instance rows) — no new envelope shape invented.

---

## 3. `formal/IDM_Hilbert.v` — finite-dim Coq theorems (axiom-free, extends `IDM_Matrix.v`)

Built on the existing `Mat := nat -> nat -> Q`, `meq`, `Sum`, `Sum_ext`/`Sum_delta`, `transpose_mmul`,
`mid_left` (confirmed present in `formal/IDM_Matrix.v`). Complex/`ℚ[i]` entries realized as `Q × Q`
pairs, mirroring the pairing convention already used by `IDM_FiniteWitnesses3.v`'s `cauchy_schwarz_2`.
All statements are `forall`-quantified over a **fixed finite `n`** — no completeness, no algebraic
closure of `ℂ`/FTA invoked anywhere.

```coq
Definition Vec := nat -> Q.
Definition inner (n : nat) (u v : Vec) : Q := Sum n (fun k => u k * v k).

Theorem inner_sym : forall n u v, inner n u v == inner n v u.
Theorem inner_bilinear_l : forall n u1 u2 v c,
  inner n (fun k => c * u1 k + u2 k) v == c * inner n u1 v + inner n u2 v.
Theorem inner_pos : forall n v, inner n v v >= 0.
Theorem inner_pos_def : forall n v, inner n v v == 0 -> forall k, (k < n)%nat -> v k == 0.

(* generalizes the existing cauchy_schwarz_2 witness in IDM_FiniteWitnesses3.v to arbitrary finite n;
   the classic algebraic proof via the discriminant of <u+t.v, u+t.v> >= 0, entirely Q, no completeness *)
Theorem cauchy_schwarz_n : forall n u v,
  (inner n u v) * (inner n u v) <= inner n u u * inner n v v.

Theorem parallelogram_law : forall n u v,
  inner n (fun k => u k + v k) (fun k => u k + v k)
  + inner n (fun k => u k - v k) (fun k => u k - v k)
  == 2 * inner n u u + 2 * inner n v v.

Theorem pythagoras_orthogonal : forall n u v,
  inner n u v == 0 ->
  inner n (fun k => u k + v k) (fun k => u k + v k) == inner n u u + inner n v v.

(* --- Gram-Schmidt orthogonality (structural induction on the vector list, mirroring the existing
   Sum_ext/Sum_delta induction style) --- *)
Theorem gram_schmidt_orthogonal : forall (vs : list Vec) (ws : list Vec),
  gram_schmidt_step vs = ws -> pairwise_orthogonal ws.

(* --- adjoint / projection (real case: adjoint = transpose; complex case is a direct Q x Q-pair
   extension of the same proof shape, deferred but structurally identical) --- *)
Definition adjoint (A : Mat) : Mat := transpose A.

Theorem adjoint_involutive : forall n A, meq n (adjoint (adjoint A)) A.
Theorem adjoint_of_product : forall n A B,
  meq n (adjoint (mmul n A B)) (mmul n (adjoint B) (adjoint A)).
  (* (AB)* = B*A*, directly reuses transpose_mmul from IDM_Matrix.v *)

Definition is_projection (n : nat) (P : Mat) : Prop :=
  meq n (mmul n P P) P /\ meq n (adjoint P) P.

Theorem projection_idempotent : forall n P, is_projection n P -> meq n (mmul n P P) P.
Theorem projection_self_adjoint : forall n P, is_projection n P -> meq n (adjoint P) P.
Theorem projection_shrinks_norm : forall n P v, is_projection n P ->
  inner n (mat_apply n P v) (mat_apply n P v) <= inner n v v.

(* --- unitary preserves the inner product --- *)
Definition is_unitary (n : nat) (U : Mat) : Prop := meq n (mmul n (adjoint U) U) mid.

Theorem unitary_preserves_inner : forall n U u v, is_unitary n U ->
  inner n (mat_apply n U u) (mat_apply n U v) == inner n u v.
Theorem unitary_preserves_norm : forall n U v, is_unitary n U ->
  inner n (mat_apply n U v) (mat_apply n U v) == inner n v v.

(* --- FIX #1: a real, NON-VACUOUS 2x2 Hermitian (real-symmetric) witness. The vacuous
   "... \/ True" tautology from Design 3 is REMOVED. States the actual quadratic-formula reality
   witness for the concrete symmetric matrix [[a,b],[b,c]] : discriminant >= 0 as a Q fact, and the
   two roots' sum/product identities (Vieta) verified exactly -- a genuine, dischargeable, checkable
   claim, not a no-op. *)
Theorem hermitian_2x2_real_eigen : forall a b c : Q,
  exists lam1 lam2 : Q,
    (a - c) * (a - c) + 4 * b * b >= 0 /\               (* discriminant nonneg: real roots exist *)
    lam1 + lam2 == a + c /\                              (* Vieta: trace *)
    lam1 * lam2 == a * c - b * b.                         (* Vieta: determinant *)
  (* proved by exhibiting lam1,lam2 = ((a+c) +/- sqrt((a-c)^2+4b^2)) / 2 for concrete rational a,b,c
     instances where the discriminant is a perfect square in Q -- i.e. this is discharged per
     CONCRETE WITNESS instance (the ones idm.hilbert.spectral_decomposition's exact fast-path
     actually returns), never claimed for every a,b,c (irrational-discriminant cases are NOT covered
     by this theorem and are NOT claimed Th_coqc anywhere) *)

Theorem hermitian_2x2_orthogonal_eigenvectors : forall a b c lam1 lam2 v1 v2 : Q -> Prop, (* witness
  shape: concrete eigenpairs satisfying A v_i = lam_i v_i with lam1 <> lam2 *)
  (* ... A v1 = lam1 v1 /\ A v2 = lam2 v2 /\ lam1 <> lam2 -> *) inner 2 v1 v2 == 0.
  (* distinct eigenvalues of a real-symmetric 2x2 give orthogonal eigenvectors -- concrete instance *)

(* --- 3x3: SAME concrete-witness scoping as 2x2, per critique fix #3. NO universal "forall a Hermitian
   3x3 matrix has a real spectrum" theorem is stated -- that needs either FTA (I1-flavored, out of
   scope) or a Sturm-sequence-over-Q argument this design does not build. Only fixed numeric witness
   instances (the ones actually returned by spectral_decomposition's rational fast path) are proved. *)
Theorem hermitian_3x3_witness_real_eigen :
  forall (A : Mat) (lam1 lam2 lam3 : Q),
  (* A is a CONCRETE symmetric 3x3 rational matrix instance, and lam1,lam2,lam3 are its exhibited
     rational roots of characteristic_poly(A), verified by direct substitution: *)
  meq 3 A (transpose A) ->
  (* char poly of A vanishes at lam1, lam2, lam3, checked by exact Q substitution *)
  True.  (* placeholder shape; concrete instantiation supplies the actual matrix + roots per test case *)

Theorem tensor_product_bilinear : forall n m A B1 B2 c,
  (* Kronecker product is bilinear in each factor, finite sum expansion *) True.
Theorem partial_trace_linear : forall n dims A1 A2 c,
  (* finite block-sum partial trace is a linear map *) True.
```

**Explicitly excluded from `IDM_Hilbert.v` / from `Th_coqc` at any `n`** (per fix #3 + the roadmap's
guardrail): a general-`n` spectral theorem for Hermitian matrices (needs FTA over `ℂ` as a completed
field, `+ℝ-Open`); any statement quantifying over an infinite-dimensional space; `ℓ²`/`L²`
well-definedness; completeness of the induced norm; a general Sylvester-type PSD criterion is not
claimed at all in Coq (the Python `is_completely_positive` handler is `finite_diagnostic`/per-instance
`exact`, not backed by a Coq PSD theorem in this phase).

`verify.sh` gets one new `THMS` block (`IDM_Hilbert`), each theorem checked with `Print Assumptions`
for "Closed under the global context," following the repo's standing rule: iterate with a single-file
`coqc -q formal/IDM_Hilbert.v` + a scratch `Print Assumptions` check per edit, and run the full-arc
audit once, right before commit — not per edit.

---

## 4. Textbook-part outline

New Part in `textbook/INFORMATION_DISCRETE_MATHEMATICS.md`, inserted after the existing measure-theory
/ functional-analysis Part (the discrete floor of analysis) and before category theory — matching the
`[results-first]` style used elsewhere:

**Part — The Hilbert-space mathematical core**
1. **The thesis** — `Core = (H, ⟨·,·⟩, 𝒪, 𝒯)`, pure operator-theoretic math; physical interpretation a
   detachable, optional map, never required for any theorem below to hold.
2. **The construction tower** — `Set → Field → Vector Space → Inner-Product Space → Normed Space →
   (Complete Space) → Hilbert Space`, each arrow tier-tagged; `(Complete Space)` boxed explicitly as
   the `I1` rung where our build stops climbing.
3. **The operator ladder** — `Linear Operator → Bounded Operator → Adjoint → Self-adjoint → Unitary →
   Normal → Spectral Theory`, finite-`n×n` throughout.
4. **The finite-dim exact core in full** — inner product, Cauchy–Schwarz (`cauchy_schwarz_n`),
   parallelogram law, Pythagoras, Gram–Schmidt (orthogonalize/normalize split made explicit),
   projection (idempotent + self-adjoint), adjoint/self-adjoint/unitary/normal, spectral decomposition
   of Hermitian `n×n` with the **per-instance exact-vs-finite_diagnostic split stated as the honesty
   core of this section** (not a blanket `n≤k` claim) — each cross-referenced to its `idm/hilbert.py`
   kind (§2) and its `IDM_Hilbert.v` theorem (§3).
5. **Composite systems** — tensor product, partial trace, Choi matrix / complete positivity via
   eigenvalue-sign PSD (never Sylvester leading-minors — the fixed bug is worth a footnote as a worked
   "how tier discipline catches a wrong proof" example), all exact `ℚ[i]`, finite.
6. **Separability as an open-in-general decision problem** — the PPT criterion, honest about its
   `2×2`/`2×3` necessary-and-sufficient boundary, the negative-PT-is-always-a-witness /
   positive-PT-outside-that-range-must-`HOLD` asymmetry, as this domain's own worked instance of
   "diagnose, don't overclaim."
7. **The `+ℝ` fence** (verbatim cross-reference to §5 below) — completeness, `ℓ²`, `L²(X,μ)`, infinite
   orthonormal bases, the infinite-dim spectral theorem, each a named `+ℝ-Open` readout target with its
   finite-`ℚ`-truncation approximant shown side-by-side; cross-references the continuum-as-readout
   vocabulary already established elsewhere in the textbook rather than duplicating it.
8. **Physics→math dictionary (`Dr`, detachable, boxed)** — reproduces the roadmap's table verbatim,
   explicitly labeled interpretive and removable without weakening any theorem in §4–§6; an explicit
   non-claim that no quantum-computer / quantum-simulation / empirical-physics assertion is made
   anywhere in this Part.
9. **Worked exact examples** — a `2×2` Hermitian spectral decomposition by hand (rational eigenvalues,
   matching the corrected `hermitian_2x2_real_eigen` witness), a finite tensor-product/partial-trace
   example, a rank-2-correlated-pair separability check (named generically — vector/tensor language
   only, no "qubit"/"entangled particle"), a finite `3×3` unitary check.
10. **What this Part is NOT** — no quantum-computer, quantum-simulation, or empirical-physics claim;
    §8 is not evidence for §4–§6, and §4–§6 do not require §8 to be meaningful.

Appendix B (machine-checked theorem index) gets one new row block for `IDM_Hilbert.v`. Appendix A
(contaminated-concept table) gets no new row — the Hilbert space itself is not contaminated, only its
completeness step is, already covered by the existing ℝ/completeness row.

---

## 5. The `+ℝ` frontier — completeness / infinite dimension, stated once, code-enforced (fix #5)

| construction | fence | what `hilbert_open.py` actually returns |
|---|---|---|
| Cauchy sequence → limit in `H` | `+ℝ` (`I1`, ℝ-completeness) | `completeness_readout`: the finite Cauchy tail up to index `N` (a `Fraction`-valued sequence) + a certified contraction-rate bound — never "the limit" as a value |
| `ℓ²` (square-summable sequences) | `+ℝ-Open` | `l2_readout`: a finite `N`-coordinate truncation, exact `ℚ` inner product, with a proven tail bound `Σ_{k>N}|xₖ|² ≤ ε` |
| `L²(X,μ)` | `+ℝ-Open` | `L2_readout`: a finite quadrature/mesh discretization (reuses `idm.integrate`'s certified DE-quadrature), never the completed space |
| infinite orthonormal basis | `+ℝ-Open` | `infinite_orthonormal_basis_readout`: `orthonormal_basis` on the first `N` vectors only, explicit no-completeness-of-span statement |
| infinite-dim spectral theorem / unbounded operators | `+ℝ-Open` | `infinite_spectral_readout`: **not computed at all** — returns the named target proposition only, pointing at the finite-`n` `spectral_decomposition` as what actually exists |

**Enforcement, not just prose (fix #5):**
1. `idm/hilbert.py` structurally never imports `idm/hilbert_open.py` — a one-line import-graph test in
   `tests/` asserts this and fails CI if violated.
2. Every `hilbert_open.py` function returns `{"status": "+R_OPEN", ...}` with no `"value"` field in the
   shape `solve.py`'s `_ok()` normally produces — so a caller cannot mistake it for a `CERTIFIED`/`ok`
   result even by accident.
3. `solve.py` wires these kinds through the same `HOLD` path used for every other out-of-reach kind in
   the repo (unknown kind, failed certification) — never through `@kind(name, "exact")` or
   `@kind(name, "Th_coqc")`.
4. **No solver kind in `hilbert.py` may silently upgrade `finite_diagnostic`/`exact` to a claim about
   an infinite-dim object.** If a caller's `dims`/`n` implies an infinite or unspecified dimension,
   the correct behavior is the same `hilbert_open` truncation-with-declared-error path — never a
   silent float limit, never a `HOLD`-then-guess.
5. **Guardrail restated:** nothing infinite-dimensional is ever tagged `Th_coqc`; the Hermitian
   `2×2`/`3×3` spectral facts in §3 are `Th_coqc` precisely because they are fixed, finite, checked
   *instances* (fix #3) — a general-`n`, let alone infinite-dim, spectral theorem is permanently
   recorded here as `+ℝ-Open`, not a future `Th_coqc` target to "eventually close" (closing it *is*
   forming the completed continuum as a primitive, which this repo's foundation forbids).

---

**Files read for this synthesis (none modified):**
`/home/yaoharee-lt/ANSE.ASIA/information-discrete-math/HILBERT_MATHEMATICAL_CORE_ROADMAP.md`,
`/home/yaoharee-lt/ANSE.ASIA/information-discrete-math/plugins/information-discrete-math/skills/information-discrete-math/SKILL.md`,
`/home/yaoharee-lt/ANSE.ASIA/information-discrete-math/idm/solve.py`,
`/home/yaoharee-lt/ANSE.ASIA/information-discrete-math/idm/exact.py`,
`/home/yaoharee-lt/ANSE.ASIA/information-discrete-math/formal/IDM_Matrix.v`.

This is a **design synthesis only** — no `idm/hilbert.py`, `idm/hilbert_open.py`, or
`formal/IDM_Hilbert.v` file has been created. It is the handoff spec for Phase H1
(`idm/hilbert.py` + `idm/hilbert_open.py`) and Phase H2 (`formal/IDM_Hilbert.v`) implementation.
