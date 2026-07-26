# Hilbert-space Mathematical Core — roadmap & handoff

**Status:** planned future work · `Dr` (design) throughout until pieces are built & tier-tagged
**Requested by the founder (2026-07-27):** treat a Hilbert space as *pure mathematics*, not physics; build
an operator-theoretic **information architecture** provable entirely inside mathematics, with the physical
interpretation an optional detachable layer.
**Execution method:** ultracode (multi-agent Workflow), block by block · **watch RAM** (`free` before any
heavy phase; no simultaneous local embedding/heavy compute).

---

## 1. The thesis (founder's words, restated for our system)

A Hilbert space is a mathematical object of linear algebra / functional analysis / operator theory /
geometry / measure theory — **not** intrinsically physics. Definition:

> a vector space `H` over `ℝ` or `ℂ` with an inner product `⟨x,y⟩`, **complete** under the induced norm
> `‖x‖ = √⟨x,x⟩` (every Cauchy sequence converges in `H`).

The **Mathematical Core** we build is

```
  Core = ( H, ⟨·,·⟩, 𝒪, 𝒯 )
```

`H` = the space, `𝒪` = operator algebra, `𝒯` = information-transformation rules. The **Physical
Interpretation** is a separate map `Core → physical phenomena` that we can delete entirely and still keep
a complete mathematical theory. We claim only the mathematical level: *organize, reduce, and compute
information over complete inner-product spaces* — no particle, wave, measurement, or QM claim.

## 2. Tier discipline (MANDATORY — the honest fence for this domain)

Hilbert space touches the two non-readouts our foundation guards (ℝ-completeness `I1`, infinite
dimension). Register each rung honestly:

| construction | our tier | why |
|---|---|---|
| finite-dim inner-product space `ℝⁿ`, `ℂⁿ`; Gram matrix, projection, adjoint, spectral decomposition of a Hermitian matrix | **`exact` / `Th_coqc`-eligible** | finite, exact ℚ/ℚ[i]; no continuum; machine-checkable |
| unitary / self-adjoint / normal **finite matrices**, spectral theorem for Hermitian `n×n` | **`Th_coqc`-eligible** | finite linear algebra; provable axiom-free |
| the **completeness** step (Cauchy → limit), `ℓ²`, `L²(X,μ)`, infinite orthonormal bases | **`+ℝ` readout / `+ℝ-Open`** | completeness = `I1`; only finite ℚ-approximants ever appear; the completed limit is a readout, never formed |
| infinite-dim spectral theorem, unbounded operators | **`+ℝ-Open`** | genuinely needs the completed continuum; state as target, not result |
| physics→math dictionary (state/observable/evolution/measurement) | **`Dr`** | interpretive, detachable |

**Rule:** everything computable must be produced finite-dimensionally (exact); the infinite-dimensional
objects appear only as *named readouts* of their finite approximants, never as primitive appearances.

## 3. The construction tower (build order)

```
Set → Field → Vector Space → Inner-Product Space → Normed Space → (Complete Space) → Hilbert Space
```
then the operator ladder
```
Linear Operator → Bounded Operator → Adjoint → Self-adjoint → Unitary → Spectral Theory
```
Our build stays on the **finite-dimensional exact** rung for everything computed; `(Complete Space)` and
the infinite-dim ladder are marked `+ℝ` and entered only as readouts.

## 4. Physics → pure-math translation table (`Dr`, detachable)

| physics language | pure-math object |
|---|---|
| quantum state | a vector / equivalence class in `H` (unit norm) |
| observable | self-adjoint operator |
| evolution | unitary transformation `x_{t+1}=U_t x_t`, `U_t* U_t = I` |
| measurement | orthogonal projection / spectral decomposition |
| probability amplitude | a (complex) coefficient |
| superposition | linear combination |
| entanglement | non-separable element of a tensor product |
| gate | unitary operator |
| channel | completely-positive linear map |
| wave function | element of a function space |
| collapse | projection / conditional update |

Naming: call it **Hilbert-space computational architecture** / **operator-theoretic information
architecture** / **information geometry over complete inner-product spaces** — never "quantum
computer / simulates quantum nature" (that claim would require the physics layer + measurement +
experiment, which we do NOT make).

## 5. Deliverables (the detailed todo list)

**Phase H0 — design (ultracode).** Independent designs of the Mathematical-Core architecture; judge &
synthesize; fix the finite-exact vs `+ℝ`-readout boundary; decide the solver-kind surface.

**Phase H1 — `idm` solver kinds (finite-dim, exact ℚ/ℂ).** New module `idm/hilbert.py` + registry kinds:
`inner_product`, `norm`, `gram_matrix`, `gram_schmidt` (exact ℚ), `orthonormal_basis`, `projection`
(onto a subspace), `adjoint`, `is_self_adjoint`, `is_unitary`, `is_normal`, `spectral_decomposition`
(Hermitian `n×n`, real spectrum + orthonormal eigenbasis), `operator_norm` (finite-dim),
`tensor_product` (vectors/operators), `partial_trace`, `is_separable` (small dims),
`completely_positive` check (Choi). All exact/`finite_diagnostic`; property-tested; wired into `solve`.

**Phase H2 — Coq witnesses (`formal/IDM_Hilbert.v`).** Machine-check the finite-dim laws: inner-product
axioms ⇒ Cauchy–Schwarz (finite), parallelogram law, Pythagoras, projection idempotent & self-adjoint,
adjoint properties `(AB)*=B*A*`, unitary preserves inner product, Hermitian ⇒ real diagonal /
orthogonal eigen-structure at `2×2`/`3×3`. Extend `verify.sh`.

**Phase H3 — textbook.** New Part "Hilbert-space mathematical core" with the tower, the operator ladder,
the physics→math table (as `Dr`), and the explicit `+ℝ` fence on completeness/infinite dimension.

**Phase H4 — honest `+ℝ` frontier doc.** `ℓ²`/`L²`/infinite-dim spectral theorem stated as `+ℝ-Open`
targets with finite-ℚ approximant readouts; no overclaim.

## 6. Guardrails (do NOT)

- Do **not** claim a quantum computer, quantum simulation, or any empirical-physics result.
- Do **not** form completeness / infinite bases as primitive appearances — finite approximants only.
- Do **not** tag any infinite-dim spectral result `Th_coqc`; those are `+ℝ-Open`.
- Do **not** run a heavy Workflow while local RAM is low — `free -h` first, keep fan-out modest.

## 7. Resume pointer (handoff)

If this session is interrupted: the RFT/RRP work is committed (`a98cda7`); this roadmap is the plan for
the Hilbert-space core. Start at **Phase H0** via ultracode design, then H1 (`idm/hilbert.py`) block by
block, verifying each (pytest-before-claim) and tier-tagging honestly before any release. Track progress
in the todo list created alongside this file.
