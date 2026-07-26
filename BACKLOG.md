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
      cardinality Th 10.3–10.5 + §12.3 Lagrange (cyclic) — `formal/IDM_FiniteWitnesses2.v`. REMAINING (v1.16):
      §10.3 `⊨_λ` + §10.4 RDL non-explosion DONE (`formal/IDM_Logic.v`). Left: more of Part XIII, v-proofs. *Turns "elig" into `Th_coqc`.*
- [ ] **v-proofs edition.** Convert the §10.1–10.6 results-first sketches (flagged `[results-first]`) to
      checked proofs; this is the edition-note promise ("proofs next").

## Tier 3 — frontier chapters (write as *declared* `+ℝ-Open`; honesty, not new closure)

Writing these as explicit "open by design" chapters strengthens completeness/honesty without claiming
closure — they need the completed continuum, which the philosophy treats as a readout, not a premise.

- [x] **Topology / manifolds / differential geometry** — DONE (v1.11): Part XXI decisive stance +
      paradox dissolution (Banach–Tarski, discrete Gauss–Bonnet), computed 16/16.
- [x] **PDE** — DONE (v1.11): Part XXI, Navier–Stokes/blow-up dissolved, finite-ε heat/wave well-posed.
- [ ] **Named open problems** chapter: Hauptvermutung, strong LLN, topos completeness, exact `π`/`φ`
      objects (all listed in §10.9) — each stated, predicted, fenced.

## Tier 4 — discipline hardening (extracted-but-not-yet-ported from cpg_math MathSolver)

- [x] **Port `consumer_guard` into `idm_discipline.py`** — DONE (v1.13): `VerdictNotAccepted` + `unwrap`
      (payload read only after ACCEPT, else raises) + `resource_admissibility` (pre-tick OOM gate). Self-
      check extended.

## Housekeeping (tracked, low priority — consistency not math)

- [ ] Part X: `§10.9` sits physically after §10.10–10.12; renumber to `§10.13` (or move) and update the
      ~5 internal `(§10.9)` pointers (flagged by the consistency review).
