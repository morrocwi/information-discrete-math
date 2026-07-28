# Changelog

All notable changes to Information Discrete Mathematics. Tiers are honest: `Th_coqc` = machine-checked
axiom-free (Coq 8.20, `Print Assumptions` = *Closed under the global context*); `finite_diagnostic` =
finite procedure cross-checked numerically; `exact` = exact over ℚ; `Open`/`+ℝ-Open` = declared open,
never dressed as a theorem.

## [1.4.1]

Quality + integrity release: acts on a world-class multi-discipline review, pays down architectural
debt, and adds the algebraic atom of the inertia boundary-readout — all backward-compatible.

### Formal core → 184 machine-checked axiom-free theorems (from 177)
- **`IDM_Schur.v`** — the exact Schur/boundary congruence over ℚ (`A = Mᵀ·diag(a, c−b²/a)·M` for a 2×2
  block, the `b²/a` cancellation), the algebraic atom of Haynsworth inertia-additivity — machine-checks,
  in this framework's own semantics, that eliminating a boundary node produces exactly the Schur
  complement. Fenced: Sylvester's sign-count invariance stays `+ℝ-Open`.

### P5 (inertia lower bound) — recast in the information language
- `docs/P46_P5_lower_bound_analysis.md` rewritten **purely readout-first** (removing a borrowed
  classical-complexity frame): P5 = "does a BOUNDARY readout require producing the VOLUME?"; the READOUT
  rule predicts against `Ω(fill*)`; info-P5 is a boundary-retention (Declaration-Bound-on-the-separator)
  question, still `+ℝ-Open`. No conjecture formalized.

### World-class review — acted on
- Fixed 4 verified defects: package `__version__` drift (was 1.3.0), stale "127 theorems" docs
  (→ live count), CLI `describe`/`list` now report the **honest runtime tier** (mirroring solve()'s
  downgrade), and `retained_spectral/README` now points to the discovery layer ("do not infer scope").
- New **CI drift gates**: version single-sourced (idm == pyproject == manifest) and documented theorem
  counts (README / formal-README / **SKILL.md**) gated against `formal/verify.sh`.

### Debt paid down
- `idm/solve.py` split from a 924-line monolith into `idm/_solve_core.py` + **30 per-domain modules** +
  a 44-line dispatch facade — verified **byte-identical** for all 263 kinds (golden snapshot).

## [1.4.0]

### Discovery layer — the repository now describes itself (humans + AI)
- **`capabilities.json`** — a machine-readable manifest **generated** from the live `idm.solve` registry
  by `tools/gen_capabilities.py` (all 263 problem kinds classified into 11 domains, none dropped/duplicated).
- **CI gate** `tests/test_capabilities_manifest.py` — fails if `total_problem_kinds != len(idm.kinds())`,
  if any kind is unclassified, or if the manifest is not byte-identical to a fresh regeneration. Adding or
  removing an API without regenerating now breaks CI.
- **CLI discovery** — `python -m idm list | kinds | describe <kind> | example <kind>` (new `idm` console
  script), grounded in the registry; `example` returns a real test fixture or honestly reports none.
- **AI-first docs** — `AI_START_HERE.md` ("do not infer capability from a single module" + a discovery
  order), `llms.txt`, `API_INDEX.md`, a README capability-map + 5-level-platform, and per-folder READMEs.
- **Reproducibility** — `Makefile` (`install`/`discover`/`test`/`prove`/`formal`/`benchmark`/`verify-all`),
  a build-verified core `Dockerfile`, `docker/{spectral,hpc,formal}` profiles + `docker-compose.yml`
  (the PETSc/SLEPc HPC image is authored, honestly marked not-build-verified).
- **Benchmark honesty** — `docs/BENCHMARK_CLAIMS.md` (each claim: scope · native API · peer · run file ·
  committed result artifact · correctness gate · **excluded** claims) and `docs/knowledge_graph.json`
  (claim → API → implementation → tests → benchmark → theory).

### Formal core — grew from 107 to 177 machine-checked, axiom-free theorems
- **`IDM_ReadoutMinimality.v`** — the minimal value-set of a signed readout (Theorem 1: ≥3 values forced,
  the third a neutral) and the four-valued algebra `{+,−,0,⊥}` with `0` (determinate) distinct from `⊥`
  (unresolved) on both the involution and the information-order axes.
- **`IDM_ResolvedCount.v`** — the resolved (four-valued) inertia readout: `⊥` arises **only** from a
  positive declared resolution (a fact about the instrument), `0` **only** at exact resolution on a true
  balance (a fact about the object). Shipped API `retained_spectral/inertia.py: resolved_count_below`
  closes the silent-failure gap (a floored pivot is now reported `⊥`, not folded into `n₀`).
- **`IDM_EquivariantReadout.v`** — the necessary condition behind P1 (general-group minimal readout):
  `Stab_X(x) ⊆ Stab_V(r x)`, equality under faithfulness. The cardinality formula stays **Conjecture P1**.
- **`IDM_Apriori.v`** — the Richardson **a-priori** stability certificate: an order-`p` method has
  contraction ratio `ρ = 2⁻ᵖ` known up front (feeds `refine_stable`), no gap monitoring.
- **`IDM_SetsFunctions.v`** (Th 10.2) and **`IDM_FirstOrder.v`** (finite first-order `⊨_λ` decidable) —
  the v-proofs edition: two `Th_coqc`-eligible sketches converted to real witnesses.
- **`IDM_ApproxCount.v`** — an honest `Ω(log(n/r))` lower bound for approximate deferred counting;
  **P7 (`Θ(n/r)`) and P8 (randomized) stay Open**, not formalized.

### Certified computation
- **Multi-dimensional quadrature** — `idm.certified.integral_nd` (tensor-trapezoid, reuses the
  dimension-agnostic `refine_stable` theorem); certifies with bound `0` when the readout is exact.
- **Richardson a-priori** — `idm.certified.richardson_apriori_{ratio,bound,certified}`.

### Documentation / honesty
- New textbook §10.14 "named-Open-problems frontier" (Hauptvermutung, strong LLN, topos completeness,
  exact π/φ) — each stated, predicted, fenced; no closure claimed.
- Corrected a pre-existing overclaim: a §10.7 "machine-checked witness `formal/InfoCausalPartialOrder_attempt.v`"
  citing a file not in-tree — downgraded to `Th_coqc`-eligible with an honesty note.
- §10.9 renumbered to §10.13 (consistency).

## [1.3.0]
- Genuinely installable self-contained wheel (`pip install .` works from outside the source tree);
  P2 CAS-grade kernel ops (matrix_solve, rational_limit, linear_ode, groebner_basis); the Five Core
  Theorems written into `THEOREM.md` at referee grade with local self-proving witnesses.
