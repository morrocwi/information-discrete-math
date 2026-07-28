# BACKLOG — Information Discrete Mathematics (only work that strengthens the math)

Filtered pending work, newest-planning first. Each item states **why it strengthens the framework** and
its **tier target**. Housekeeping/cosmetic items that do not make the mathematics stronger are excluded
by design. Extensibility contract: see `INDEX.md`; every new chapter derives from `δ_R`/`L_R`/Part VII
operators, tier-tagged, with an executed `validation/*.py` block before prose.

## Tier 1 — full chapters (CLOSED 2026-07-26, v1.7–v1.8; validated 34/34, 4-agent reviewed)

- [x] **Part XVI — Measure theory & functional analysis.** Discrete measure `μ_λ=I_ε(indicator)`
      (§10.6) → σ-additivity as a retained count; `L_R` functional calculus / spectral theorem on the
      finite `ℚ`-space (§13.2); Hilbert-space completeness stays `+ℝ-Open`. *Strengthens:* gives analysis
      its measure-theoretic floor without a continuum σ-algebra. Tier: `Th_coqc-elig` + `+ℝ-Open` fence.
- [x] **Part XVII — Category theory in the readout vocabulary.** `G_λ` = idempotent reflector, `E=Ẽ∘G_λ`
      = Kan-extension/comma factorization, sets-as-fibers = Grothendieck fibration, `=_λ` = coequalizer,
      admissible descriptions = setoids (all sketched in §10.7). *Strengthens:* makes the substrate's
      universal properties explicit; topos completeness stays `+ℝ-Open`. Tier: `Th_coqc-elig`/`Dr`.
- [x] **Part XVIII — Statistics & inference.** Retained-frequency estimation; a hypothesis test **is** a
      `Verdict(ACCEPT/HOLD/BLOCK)` (ties to `idm_discipline`); Bayesian update = retained reweighting;
      confidence = declared-resolution interval. *Strengthens:* closes the gap above probability (§10.6)
      and unifies inference with the fail-closed verdict discipline. Tier: `finite_diagnostic`/`Dr`.
- [x] **Part XIX — Optimization.** Gradient = `D_ε`; convexity = a retained second-difference sign;
      Lagrange multipliers = constrained retained stationarity; linear programming exact over `ℚ`;
      root/optimum via obstruction-zeroing (`solve_obstruction`, `idm_discipline`). *Strengthens:* gives
      the framework its optimization chapter, grounded in tools it already ships. Tier: `Th_coqc-elig`.

## Capstone — the continuum-maya bridge (construct the continuum *as a readout*, then compute with it)

- [x] **Part XX — The continuum-maya bridge — DONE (v1.11).** Written as Part XX; `Λ` map + faithfulness
      (exact FTCC core `Th_coqc` `formal/IDM_Bridge.v`; numeric 100/100) + maya clause. Original scope: *Is it possible to build a formal
      bridge that CONSTRUCTS a continuum layer from the discrete — a continuum that is explicitly a
      readout/appearance (maya), not an ultimate object — and then compute continuum results with it,
      identically?* Yes; the pieces exist and this makes the two-truths a theorem, not a stance:
      - **The construction (discrete → continuum-maya):** the number ladder already does the object
        side (`ℝ` = regular Cauchy of `ℚ`, §III). The bridge adds the *operational* side: a map
        `Λ: (discrete finite-ε data) → (continuum-appearance value)` defined as the **A8-stable readout**
        of the finite-ε computation (`limit_eps`/Euler–Maclaurin/Richardson). `Λ` is total on
        A8-stable inputs and **refuses** (HOLD) where no plateau exists — so the continuum it builds is
        exactly the *computable appearance*, never a completed non-readout.
      - **Faithfulness (compute continuum identically):** prove `Λ` reproduces the classical continuum
        operation on every A8-stable case — derivative, integral, limit, ODE, special value — which is
        already *witnessed* at 100/100 (Appendix E). The bridge upgrades that empirical 100/100 into a
        stated **faithfulness theorem**: `Λ(discrete op) = classical continuum op` wherever the latter
        exists, with the divergence set = exactly the `+ℝ-Open` non-readouts.
      - **Maya clause (honesty):** the constructed continuum is labelled a **readout of the discrete**
        (conventional truth, §0.3), never the ultimate object; the bridge is one-way faithful
        (discrete → appearance) and *predicts* the readout on the Open frontier rather than closing it.
      *Strengthens:* turns the framework's central claim ("the continuum is a readout of the discrete")
      from a discipline/stance into a constructive, testable bridge with a faithfulness theorem — the
      natural capstone. Founder request 2026-07-26.

## Tier 2 — strengthen warrant (proof work; raises existing tiers, no new breadth)

- [x] **Prove the keystone Th 5.1 `B(Φ,Φ)=I(Φ)` in Coq.** DONE (v1.10): `formal/IDM_Keystone.v`,
      `keystone_B_eq_I` (edge assembly `ΦᵀL_RΦ = Σ w(Φi−Φj)²`) + `keystone_nonneg` (L_R PSD), both
      axiom-free. Single most-cited result upgraded in-progress → `Th_coqc` (§5.1/§10.8/§13.2/Roadmap).
- [~] **Machine-check the `Th_coqc-elig` claims → real `.v` witnesses.** DONE (v1.9): `formal/IDM_FiniteWitnesses.v`
      proves 5 axiom-free — Th 10.1 Kuratowski pair injectivity (§10.1), handshake (§15.2), pigeonhole
      (§15.3), finite-Yoneda (§17.2), semiring distributivity (§12.2). DONE too (v1.13): §10.2
      cardinality Th 10.3–10.5 + §12.3 Lagrange (cyclic) — `formal/IDM_FiniteWitnesses2.v`. DONE (v1.16-v1.19): §10.3 `⊨_λ`, §10.4 RDL non-explosion (`IDM_Logic.v`); §4.4/§16.2 Cauchy-Schwarz/
      §16.1/§12.1/§12.2 (`IDM_FiniteWitnesses3.v`); **discrete matrix library `IDM_Matrix.v`** (matrix
      algebra + Laplacian symmetric/rowsum/kernel §15.2 + twirl parameter-reduction §13.4). 26 Coq
      theorems total, all axiom-free (`bash formal/verify.sh`). RECLASSIFIED (frontier, not warrant
      work): real spectral theorem + DPI entropic-form + general Cauchy-Binet matrix-tree = `+ℝ-Open`
      / need heavy machinery — honestly declared, not left as false 'elig'. Nothing tractable remains. *Turns "elig" into `Th_coqc`.*
- [x] **v-proofs edition.** Convert the §10.1–10.6 results-first sketches to checked proofs (the
      edition-note promise). DONE — both tractable sketches now carry real witnesses: **Th 10.2**
      (function ≅ functional-relation coincidence, the "biggest not-standalone blocker") →
      `formal/IDM_SetsFunctions.v`; **Th 10.6 first-order `⊨_λ`** (quantifier-over-finite-domain
      Tarski recursion, `∀↦forallb`/`∃↦existsb`, sound+complete+decidable) → `formal/IDM_FirstOrder.v`.
      Both `Th_coqc`-elig → `Th_coqc`, axiom-free. What remains is genuinely `+ℝ-Open` (NOT convertible,
      correctly fenced not dressed as `Th_coqc`): §10.5 `ε→0` real-analysis quantifier, §10.6
      completed-measure limit — they quantify over a completed continuum.

## Tier 3 — frontier chapters (write as *declared* `+ℝ-Open`; honesty, not new closure)

Writing these as explicit "open by design" chapters strengthens completeness/honesty without claiming
closure — they need the completed continuum, which the philosophy treats as a readout, not a premise.

- [x] **Topology / manifolds / differential geometry** — DONE (v1.11): Part XXI decisive stance +
      paradox dissolution (Banach–Tarski, discrete Gauss–Bonnet), computed 16/16.
- [x] **PDE** — DONE (v1.11): Part XXI, Navier–Stokes/blow-up dissolved, finite-ε heat/wave well-posed.
- [ ] **Named open problems** chapter: Hauptvermutung, strong LLN, topos completeness, exact `π`/`φ`
      objects (all listed in §10.13) — each stated, predicted, fenced.

## Tier 4 — discipline hardening (extracted-but-not-yet-ported from cpg_math MathSolver)

- [x] **Port `consumer_guard` into `idm_discipline.py`** — DONE (v1.13): `VerdictNotAccepted` + `unwrap`
      (payload read only after ACCEPT, else raises) + `resource_admissibility` (pre-tick OOM gate). Self-
      check extended.


## New extraction tasks (queued — translate to information language first, then formalize)

- [x] **Discrete Jacobian, sharper version — DONE (v1.23).** §8.8 + validation/discrete_jacobian.py (9/9): exact constant det J_F=−2, 3-to-1 readout collision, retention lift restores injectivity, told as retained-sensitivity D_ε. ORIGINAL: Extract the discrete Jacobian/retention math from
      `~/Downloads/jacobian_retention_clean_two_turns.m` (exact polynomial images in readout space
      `(P,Q,R)`; retention lift `(P,Q,ψ)`) and `~/Downloads/URR_C_MASTER_0_4_DETAILED.yaml` (URR-C:
      linear hidden-elimination / return-kernel exact algebra). Restate as the **retained sensitivity
      operator** `D_ε` of a readout to its source (§7.0 language first), fold the sharper exact-algebra
      form into Part VIII (discrete calculus), tier-honest. Goal: a Jacobian that does **not** rely on a
      conjecture — a finite exact-algebra readout, per the DGG-conjecture-is-false lesson (finite
      discrete counterexamples settle what continuum conjectures leave open).
- [x] **readout_genesis math harvest — DONE (v1.24).** Pure-math results extracted to formal/IDM_Harvest.v (axiom-free): repeated_event_zero (C=−C⇒C=0), odd_from_cyclic_closure (cyclic closure ⇒ k odd ⇒ 3), sym_skew_reconstruct + skew_diag_zero (operator = self-adjoint metric + load-free skew), folded §4.4/§13.2. Remaining SM-domain .v files are physics, not pure math. ORIGINAL: Scan `~/ANSE.ASIA/readout_genesis` for machine-checked / exact
      mathematical results not yet in the textbook; extract and fold in (info-language first, tier-honest).

## Housekeeping (tracked, low priority — consistency not math)

- [x] Part X: `§10.9` sat physically after §10.10–10.12; renumbered to `§10.13` and updated all 18
      internal `(§10.9)` pointers to `(§10.13)` (consistency review item — DONE). Also corrected a
      pre-existing stale "machine-checked" citation in §10.7 (`formal/InfoCausalPartialOrder_attempt.v`,
      not in-tree → downgraded to `Th_coqc`-eligible with an honesty note).
