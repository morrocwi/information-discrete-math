# The Readout Bridge — closure record (theory + process), 2026-09-18

**One link for the paper.** This document closes, in one place, the discrete ↔ continuum Readout Bridge programme as it stands on 2026-09-18: the theory (five lines, each with its Coq identifiers and the tier its own `Print Assumptions` readout earns), the evidence, the honest boundary, the related work it must be positioned against, the process that produced it, and how to reproduce every claim. Everything here is a readout, not truth: each number was printed in front of the agent that recorded it, and each interpretation is marked as such.

**Status of every new object:** PROPOSAL — *not yet in Toledo* (codes `??` pending the registry merge run, Toledo PR #43).

---

## 0. Core Epistemic Structure

| Role | Who |
|---|---|
| Core Respondent / Experience-Based Expert | the founder (role: founder) — owner of the concept line: retained difference δ_R, readout-not-truth, the graph Laplacian L_R = D_W − W as the information operator, the EPSC certificate programme, the Readout Genesis gates |
| Interactional Expert | None |
| AI Model(s) Used | AI assistant (orchestrated multi-agent: readers, designers, judges, Coq builders one file each, adversarial refuters, fixers) — every tier below was taken from a readout the assistant printed, never from memory |

Disclosure is by role only. No AI is an author, co-author or contributor of this document or of any file it describes.

---

## 1. Thesis (one sentence, the founder's line)

> A machine-checked round-trip certification architecture that controls **when a finite exact computation is licensed to support a continuum-level claim** — and that formally **refuses** the claim (HOLD) when no certified radius exists.

The bridge is not a limit theorem and never becomes one. Forward, a resolution-indexed rational tape is kept as a finite ledger of retained differences; a licence (a witnessed contraction ratio) turns the ledger into a certified radius in ℚ; the continuum object returns only as a certified ball; the round trip says what returns exactly, what returns within the radius, and what never returns; the gate is three-valued and fail-closed.

---

## 2. The five lines, with Coq identifiers and actual tiers

Typing (ruling 11b-1): `q_K : X → R_K` is the forward quotient (occurrence of weld/M.02.v1 + weld/M.03.v1), `Λ_K : R_K → Y` a disclosed section, `P_K := Λ_K ∘ q_K`, `res_K : R_{K+1} → R_K`.

| Line | Statement (ASCII) | Coq (file · main identifiers) | Tier (readout) |
|---|---|---|---|
| **S1 LEDGER + LICENCE** | `tailsum(Δg,N,M) = g(N+M) − g(N)` exactly; `ρ<1 ∧ ∀k |Δg(k+1)| ≤ ρ|Δg(k)| ⟹ (1−ρ)|g(N+M)−g(N)| ≤ |Δg(N)|`; tape route on one window; `σ_of g : RR` a Bishop-readout real with an *exhibited* modulus via bounded search `Nidx/N_of` | `IDM_ReadoutTower.v` · `tailsum_delta_telescopes`, `plateau_certificate` (occurrence of R/M.32.v1 `refine_stable`), `plateau_certificate_window`, `sigma_of`, `sigma_readout_exact`, `Pi`, `Pi_certificate`, `N_of_least` | Th_coqc — 50/50 Closed |
| **S2 RETAIN** | `Σ_Q(z) := (O z, [z]_Q)`; admissible iff `DepthStable L`; `Alg_Q := {P : ker q_K ⊆ ker P}` | `IDM_SignatureFunctor.v` · `Sigma`, `sigma_respects_step`, `InAlg`, `exact_on_alg`, `alg_is_fixed_points` (occurrence of EQ-002/M.01.v1, reuses `stable_depth_exact_future`) | Th_coqc — 24/24 Closed |
| **S3 RADIUS** | `r_K := ρ_K + β_K` (triangle) or `r_K² = ρ_K² + β_K²` (Pythagorean, hypothesis carried, occurrence of PROP-EPSC-17); `β_K = |Δg(N)|/(1−ρ)` from S1 | `PROP_BRIDGE_03_certified_radius.v` (Toledo) · `triangle_composition`, `squared_orthogonal`, `contracting_beta`, `bridge_radius` (EPSC-08 lift) | Th_coqc — 31/31 Closed |
| **S4 ROUND TRIP** | EXACT: `P∘Λ_K∘q_K = P ⟺ P ∈ Alg_Q`; WITHIN RADIUS: `P` L_P-Lipschitz ⟹ `|P x − P(P_K x)| ≤ L_P·r_K`; NEVER: `q_K x = q_K x', x ≠ x'` ⟹ no total decoder; level 2: `R_complete` bound + definitional diagonal; fence: unrestricted completeness, LUB, trichotomy never used (+ℝ-Open) | `IDM_BridgeRoundTrip.v` · `roundtrip_exact_iff`, `roundtrip_exact_tape`, `roundtrip_radius`, `roundtrip_never`, `level2_bound`, `level2_diagonal` | Th_coqc — 23/23 Closed |
| **S5 GATE** | `ACCEPT_ε(K) ⇐ cert : δ_K ≤ ε ∧ (ε−δ_K)² ≥ r_K²`; no cert ⟹ ⊥ = HOLD (never 0, never ACCEPT); ACCEPT theorem: cert ∧ `d_Y(x, P_K x) ≤ r_K` ∧ `d_Y(Λ_K(res_K x_{K+1}), Λ_K x_K) ≤ δ_K` ⟹ `d_Y(x, Λ_K(res_K x_{K+1})) ≤ ε` (both orientations, triangle + symmetry declared) | `PROP_BRIDGE_03_certified_radius.v` · `Certificate'`, `gate'`, `fail_closed'`, `no_certificate_holds'`, `accept_theorem` | Th_coqc (in the same 31/31) |
| **Operator seam** (instantiation of the reader O, not a core line) | `−h²Δ_h φ = L_R φ` at interior nodes as a ring identity (h² multiplied through, no division); `Σ_edges (φ_{i+1}−φ_i)² = ⟨φ, L_R φ⟩ = I_form` (Keystone); `I(φ+e_i) − I(φ) = 2(L_Rφ)_i + L_ii`; Rayleigh ceiling `λ ≤ 4` on the path (weld/M.42.v1 at d_max = 2) | `Bridge_Seam.v` · `seam_grid`, `seam_grid_stencil`, `seam_energy`, `seam_energy_names`, `seam_box`, `seam_ceiling`, `seam_ceiling_scaled` | Th_coqc — 19/19 Closed |

Definitions (`Obs`, `Sigma`, `PK`, `sigma_of`, `Certificate'`, …) are tier `definition`; the "one law" sentence, the ρ-supplier, the class ⇄ record identification, and every physical identification are `Dr`; the +ℝ-Open fence is permanent by design. Full per-identifier tables: `docs/READOUT_BRIDGE_THEORY.md` §2 and the journal's `PHASE2_COQ_LEDGER.md`.

---

## 3. Evidence

| Check | Result (readout, 2026-09-18) |
|---|---|
| In-file `Print Assumptions`, five files | 24 + 50 + 31 + 23 + 19 = **147 objects, all `Closed under the global context`**; 0 hits for `Admitted|admit|Axiom|Parameter|Coq.Reals` |
| Full-arc `formal/verify.sh` (run once, after all commits, under a 3 GB memory cap) | **29 files compiled, 207 theorems axiom-free, `ALL WITNESSES OK`** |
| Parents' readouts (housekeeping) | PROP_EPSC_{03,05,08,17,20,21,23,39}: 13/13 Closed in-file; wrappers weld/M.63/64/68 Closed under the live IDM mapping; `R_complete` transparent (`Defined.`), diagonal by `reflexivity` |
| Independent adversarial refuters | Phase 1: 3 (design) + critic; Phase 2: 3 (Coq truth / registry / infinity audit); Phase 2b: 2 (seam / tape). Every refuter reproduced the compiles itself. Mathematics: never refuted. Surviving findings: registry shape, wording, framing — 35 + 12 applied, 9 + 5 deferred as open items |
| First executed test (finite_diagnostic) | exact-rational diffusion tape on a path graph (N = 8/16/32, same T): refining midpoint reader ρ ≈ 0.272 → CERTIFIED; Dirichlet-energy reader ρ ≈ 0.26–0.85 → CERTIFIED; non-refining sum reader ρ ≈ 2 → **HOLD**; unstable dt (above h²/2) seen by any global reader ρ ≈ 10⁴–10⁹ → **HOLD**. Byte-identical on three re-runs; the S1 gate also evaluated inside Coq by `vm_compute` on the same rationals |

What the tape test does **not** show (stated in the record itself): on a three-readout tape the licence instance is an identity in ρ and CERTIFIED carries exactly one bit (the gap shrank once); the midpoint reader at K ≤ N/2 steps is a closed form for every dt and is uninformative about stability; ρ ≈ 1/4 matching a second-order reader is an expectation (Dr), not a result.

---

## 4. What is genuinely ours, what is a credited parent, and how this sits next to prior work

**Ours (the delta that compiled):** the certificate schema as one protocol — retained ledger → licence → radius in ℚ → three-verdict round trip → fail-closed gate — with the NEVER clause and HOLD as first-class outcomes; `σ_of` with an exhibited modulus from a witnessed contraction; the seam as ring identities with h² multiplied through; the declaration pattern (q_K, Λ_K, res_K, (Y, d_Y, axioms per clause), A, graph, ρ-supplier) under which "universal" means the certificate *shape*, with existence per domain defaulting to HOLD.

**Credited parents (by code, reused not re-proved):** refine_stable R/M.32.v1, the telescopes Z/M.06/M.08, reader-domain quotient weld/M.02/M.03, kernel inclusion weld/M.64/M.68, Bishop `R_complete` weld/M.60.v1, EPSC-03/08/17 (fail-closed gate, Lipschitz lift, orthogonal composition), Keystone/M.03 (B = I), L_R/M.20–22, weld/M.41/M.42, the no-decoder theorem of Readout Genesis (PROP-BRIDGE-09).

**Related work (read on 2026-09-18 from the cited pages; positioned as horizontal neighbours, not as validation — no "first" claim is made):**

| Work | What it does (as read) | Where the Readout Bridge differs |
|---|---|---|
| Magaud, Chollet, Fuchs — *Harthong–Reeb line in Coq* | a discrete (nonstandard) model of the continuum from Laugwitz–Schmieden integers; ordered field via Bridges' axioms; **proves the least-upper-bound principle**; extraction to OCaml for arithmetized continuous functions | we never adopt LUB or a nonstandard integer axiom set: ℝ enters only as a *readout* of ℚ-approximants with an exhibited modulus, LUB/trichotomy are fenced +ℝ-Open, and the bridge's output is a certificate or HOLD, not a model of ℝ |
| Tekriwal, Duraisamy, Jeannin — *formal Lax equivalence theorem* (Coq, arXiv:2103.13534) | consistency + stability ⟹ convergence for finite-difference schemes, over continuous linear operators between complete normed spaces, Taylor–Lagrange consistency bounds | the same physical object (a finite-difference tape) but the opposite direction of licence: no h → 0, no complete normed space as substrate; the certificate is a finite ℚ radius from a witnessed ρ on the tape, and the gate can return HOLD for the same scheme in a different parameter regime |
| O'Connor — *Certified exact transcendental real number computation in Coq* (TPHOLs 2008, arXiv:0805.2438) | constructive reals via complete metric spaces, elementary functions with correctness proofs, a tactic proving strict inequalities by computation | closest parent for `σ_of` / `RR`: our level-2 object is the same kind of constructive real, reused from weld/M.60 rather than re-built; what we add is the *licence* layer (when a tape earns a modulus) and the retain/round-trip/gate layers around it |
| Rocq Numerical Analysis (Mayero et al.; FEM Lagrange P_k nodes, RR-9557) | finite-element theory formalized over Coquelicot / Coq reals | a real-analysis-first formalization of the continuum method; the bridge is ℚ-first and treats the continuum method as a readout; the two are complementary, not competing |

Under this workspace's standing rule, none of the above is a lever for legitimacy; they are the neighbours a paper must cite honestly.

---

## 5. Honest boundary (what would make this a result about a scientific domain, and is not yet done)

1. **No nontrivial Genesis leaf domain has run S1 → S5 end-to-end with quantitative certificate content.** The rows that evidence the full shape are geometry (exact), the number ladder (self-instance) and the toy diffusion tape (one bit). The planned first leaf is the heat/diffusion equation on a longer tape (many resolutions, many windows, a-priori ρ from Richardson order with its own FAIL regime), so that ACCEPT and HOLD separate by parameter regime with real quantitative content. That experiment is the paper's main experiment and is queued as Phase 3.
2. Every ρ-supplier is a declared datum; the only compiled β-supplier is the S1 contraction; the Navier–Stokes row is a `+ℝ-axioms` instantiation outside the core typing.
3. Registry: codes `??`, mirror re-sync of IDM inside Toledo, LINEAGE events, row-vs-occurrence for two objects, lane vocabulary — registrar decisions (Toledo PR #43).
4. Genesis A.8 (retraction vs section): the section reading is adopted as `Dr`; the founder's ontology ruling is pending.

---

## 6. Process (so the paper's methods section can be written from one place)

| Step | What happened | Where |
|---|---|---|
| Audit | Toledo (1,333 canonical rows) + IDM + Genesis searched by statement: no registered, domain-neutral, bidirectional bridge object existed; EPSC was NS-specific; round trip only PROP-EPSC-17 (Dr) | journal `HANDOFF.md` |
| Phase 1 — design | 6 readers → 4 designs (Cauchy-readout, EPSC certificate, operator/spectral, Genesis lineage) → 3 judges → synthesis → 3 refuters + completeness critic; winner EPSC-certificate, best ideas grafted; 10 design items ruled under the readout-universe tier discipline (§11b) | `DISCRETE_CONTINUUM_BRIDGE_DESIGN_v0.1.md` |
| Phase 2 — theory in Coq | inventory of IDM's existing round-trip machinery (46 objects) → 4 files built one at a time → housekeeping → registration → 3 refuters → fixer | `PHASE2_COQ_LEDGER.md` §1–10 |
| Phase 2b — first tests | seam file + `N_of_least`; exact-rational tape test with FAIL controls; 2 refuters → fixer | ledger §11, `tape_test/` |
| Incident | three OOM kills earlier the same day, caused by unbounded combinatorial search scripts of another work order running concurrently; the bridge workflows were rebuilt memory-safe (≤ 3 agents, one `coqc` at a time under a 3 GB cgroup cap, RAM reservation, no background jobs) and completed without incident | `HANDOFF.md`, crash-prevention memory |
| Discipline | readout-not-truth; Toledo-first and the reuse pipeline (lookup by statement → Genesis section → reuse as parent → derive only the delta → label PROPOSAL); tier = own `Print Assumptions`; Open never bare; maker-checker with independent refuters before any publish; no AI attribution | workspace rules |

Commits: information-discrete-math `formal/readout-bridge` (ac1df59 … 78801fd); toledo `proposals/readout-bridge` (b712d0a9 … 70620cad, PR #43); research journal `bridge/discrete-continuum-v0.1`.

---

## 7. Reproduce (one `coqc` at a time; `free -g` available ≥ 3 before each)

```
# W = information-discrete-math checkout (branch formal/readout-bridge); T = toledo checkout (branch proposals/readout-bridge)
cd $W/formal
coqc -q IDM_Matrix.v IDM_Keystone.v IDM_Calculus.v IDM_Certified.v IDM_Continuum.v IDM_ReaderDomainFoundation.v   # parents (each alone)
coqc -q IDM_SignatureFunctor.v
coqc -q IDM_ReadoutTower.v
cd $T/coq/canonical && coqc -q -Q . MRC -R $W IDM weld__M_60_v1.v PROP_EPSC_03_fail_closed_gate.v PROP_EPSC_08_lipschitz_tail_lift.v PROP_EPSC_17_orthogonal_composition.v   # each alone
coqc -q -Q . MRC -R $W IDM PROP_BRIDGE_03_certified_radius.v
cd $W/formal && coqc -q -R $W IDM -Q $T/coq/canonical MRC IDM_BridgeRoundTrip.v
coqc -q -R $W IDM -Q $T/coq/canonical MRC Bridge_Seam.v
bash verify.sh          # full arc, once: expect "ALL WITNESSES OK (compiled + axiom-free)"
# tape test (journal repo): cd research/discrete_continuum_bridge/tape_test && python3 tape_test.py
```

Every theorem prints its own `Print Assumptions` at the end of its file; grep the output for `Closed under the global context`.

---

## 8. Links

- Theory (per-identifier tables, Open ledger, reuse inventory): `docs/READOUT_BRIDGE_THEORY.md` (this repository, branch `formal/readout-bridge`)
- Registry proposal lane + S3/S5 Coq: <https://github.com/morrocwi/toledo/pull/43>
- Design, rulings, ledger, tape record: research journal repository, branch `bridge/discrete-continuum-v0.1`, folder `research/discrete_continuum_bridge/`
- Concept line and ontology: Readout Genesis (`READOUT_GENESIS_CORE.md`, gates A.4 / A.7 / A.8 / A.12 / A.13); tier discipline: readout_universe

*Every object above: not yet in Toledo.*
