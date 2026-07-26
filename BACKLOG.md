# BACKLOG — Information Discrete Mathematics (only work that strengthens the math)

Filtered pending work, newest-planning first. Each item states **why it strengthens the framework** and
its **tier target**. Housekeeping/cosmetic items that do not make the mathematics stronger are excluded
by design. Extensibility contract: see `INDEX.md`; every new chapter derives from `δ_R`/`L_R`/Part VII
operators, tier-tagged, with an executed `validation/*.py` block before prose.

## Tier 1 — full chapters closeable NOW (breadth; pieces already exist, no contamination)

These four are the answer to "what else can be closed as a full chapter": each already has its parts
scattered in the book and only needs elevation to a dedicated, tier-honest Part.

- [ ] **Part XVI — Measure theory & functional analysis.** Discrete measure `μ_λ=I_ε(indicator)`
      (§10.6) → σ-additivity as a retained count; `L_R` functional calculus / spectral theorem on the
      finite `ℚ`-space (§13.2); Hilbert-space completeness stays `+ℝ-Open`. *Strengthens:* gives analysis
      its measure-theoretic floor without a continuum σ-algebra. Tier: `Th_coqc-elig` + `+ℝ-Open` fence.
- [ ] **Part XVII — Category theory in the readout vocabulary.** `G_λ` = idempotent reflector, `E=Ẽ∘G_λ`
      = Kan-extension/comma factorization, sets-as-fibers = Grothendieck fibration, `=_λ` = coequalizer,
      admissible descriptions = setoids (all sketched in §10.7). *Strengthens:* makes the substrate's
      universal properties explicit; topos completeness stays `+ℝ-Open`. Tier: `Th_coqc-elig`/`Dr`.
- [ ] **Part XVIII — Statistics & inference.** Retained-frequency estimation; a hypothesis test **is** a
      `Verdict(ACCEPT/HOLD/BLOCK)` (ties to `idm_discipline`); Bayesian update = retained reweighting;
      confidence = declared-resolution interval. *Strengthens:* closes the gap above probability (§10.6)
      and unifies inference with the fail-closed verdict discipline. Tier: `finite_diagnostic`/`Dr`.
- [ ] **Part XIX — Optimization.** Gradient = `D_ε`; convexity = a retained second-difference sign;
      Lagrange multipliers = constrained retained stationarity; linear programming exact over `ℚ`;
      root/optimum via obstruction-zeroing (`solve_obstruction`, `idm_discipline`). *Strengthens:* gives
      the framework its optimization chapter, grounded in tools it already ships. Tier: `Th_coqc-elig`.

## Tier 2 — strengthen warrant (proof work; raises existing tiers, no new breadth)

- [ ] **Prove the keystone Th 5.1 `B(Φ,Φ)=I(Φ)` in Coq.** Currently a design target / in-progress
      (§5.1, §13.2, Roadmap). A checked witness would upgrade the single most-cited result from
      "in progress" to `Th_coqc`. *Highest warrant value in the book.*
- [ ] **Machine-check the `Th_coqc-elig` claims → real `.v` witnesses.** Parts XII/XIII/XV finite
      theorems, §10.1 pair–product–function layer (Th 10.1/10.2), §10.3 `⊨_λ`, §10.4 RDL boundary-tie.
      All are finite/decidable over `ℚ` — eligible today, not yet checked. *Turns "elig" into `Th_coqc`.*
- [ ] **v-proofs edition.** Convert the §10.1–10.6 results-first sketches (flagged `[results-first]`) to
      checked proofs; this is the edition-note promise ("proofs next").

## Tier 3 — frontier chapters (write as *declared* `+ℝ-Open`; honesty, not new closure)

Writing these as explicit "open by design" chapters strengthens completeness/honesty without claiming
closure — they need the completed continuum, which the philosophy treats as a readout, not a premise.

- [ ] **Topology / manifolds / differential geometry** as a declared-open frontier chapter (§10.9).
- [ ] **PDE via the continuum limit `L_R→□`** (d'Alembertian) as a declared-open chapter (§10.9).
- [ ] **Named open problems** chapter: Hauptvermutung, strong LLN, topos completeness, exact `π`/`φ`
      objects (all listed in §10.9) — each stated, predicted, fenced.

## Tier 4 — discipline hardening (extracted-but-not-yet-ported from cpg_math MathSolver)

- [ ] **Port `consumer_guard` into `idm_discipline.py`:** the R2-CONSUMER `unwrap` (a payload read only
      after an explicit status branch — a non-ACCEPT read raises) and `resource_admissibility` (the
      pre-tick OOM gate: estimated dominant cost vs measured host envelope at declared headroom).
      *Strengthens:* completes the numeric-honesty layer's consumer/resource side.

## Housekeeping (tracked, low priority — consistency not math)

- [ ] Part X: `§10.9` sits physically after §10.10–10.12; renumber to `§10.13` (or move) and update the
      ~5 internal `(§10.9)` pointers (flagged by the consistency review).
