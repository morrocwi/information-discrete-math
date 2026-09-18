# The Readout Bridge — closure record (theory + process), 2026-09-18

**One link for the paper.** This document closes, in one place, the discrete ↔ continuum Readout Bridge programme as it stands on 2026-09-18: the theory (five lines, each with its Coq identifiers and the tier its own `Print Assumptions` readout earns), the evidence, the honest boundary, the related work it must be positioned against, the process that produced it, and how to reproduce every claim. Everything here is a readout, not truth: each number was printed in front of the agent that recorded it, and each interpretation is marked as such.

**Status of every new object:** PROPOSAL — *not yet in Toledo* (codes `??` pending the registry merge run; the proposal lane entered Toledo's `registry/proposals/` through pull request 43, which assigns no code).

**Revision 2 (2026-09-18, same day):** Phase 3 — the heat/diffusion leaf — added to §3 (evidence), §5 item 1 (boundary), §6, §7 and §8. Nothing in §1, §2 or §4 changed.

---

## 0. Core Epistemic Structure

| Role | Who |
|---|---|
| Core Respondent / Experience-Based Expert | the founder (role: founder) — owner of the concept line: retained difference δ_R, readout-not-truth, the graph Laplacian L_R = D_W − W as the information operator, the EPSC certificate programme, the Readout Genesis gates |
| Interactional Expert | None |
| AI Model(s) Used | AI assistant (orchestrated multi-agent: readers, designers, judges, Coq builders one file each, adversarial refuters, fixers) — every tier below was taken from a readout the assistant printed, never from memory |

Disclosure is by role only. AI systems are not listed as authors; their roles in design assistance, implementation and adversarial checking are disclosed in the table above and in §6. Authorship and contribution are separate questions: the concept line, the rulings and the accountability are the founder's.

---

## 1. Thesis (one sentence, the founder's line)

> A machine-checked round-trip certification architecture that controls **when a finite exact computation is licensed to support a continuum-level claim** — and that formally **refuses** the claim (HOLD) when no certified radius exists.

The bridge is not a limit theorem and never becomes one. Forward, a resolution-indexed rational tape is kept as a finite ledger of retained differences; a licence (a witnessed contraction ratio) turns the ledger into a certified radius in ℚ; the continuum object returns only as a certified ball; the round trip says what returns exactly, what returns within the radius, and what never returns; the gate is a fail-closed **ACCEPT / HOLD** gate (the compiled object is `Inductive Verdict := ACCEPT (beta_K : Q) | HOLD.`, two constructors), embedded in the three-valued admissibility discipline `{1, 0, ⊥}` of its conceptual parent (Genesis A.13 Gate 2), which is not itself the compiled verdict type.

**"Licensed" is a technical term here.** A continuum-level statement is *licensed* iff it is derivable under the explicitly declared bridge hypotheses (the declaration pattern of §4) together with a certificate that the gate accepts. Licensed does not by itself establish the adequacy of the physical model, the choice of reader, or the truth of an external scientific interpretation. **HOLD is not FALSE and not REJECT**: it means the required certified evidence is not present.

**Notation.** `κ` is the contraction ratio of the ledger (S1; named `rho` in the Coq files and in the tape record). `ρ_K` is the inner reconstruction radius of S3. They are different objects; this document never uses a bare `ρ`.

---

## 2. The five lines, with Coq identifiers and actual tiers

Typing (ruling 11b-1): `q_K : X → R_K` is the forward quotient (occurrence of weld/M.02.v1 + weld/M.03.v1), `Λ_K : R_K → Y` a disclosed section, `P_K := Λ_K ∘ q_K`, `res_K : R_{K+1} → R_K`.

| Line | Statement (ASCII) | Coq (file · main identifiers) | Tier (readout) |
|---|---|---|---|
| **S1 LEDGER + LICENCE** | `tailsum(Δg,N,M) = g(N+M) − g(N)` exactly; `κ<1 ∧ ∀k |Δg(k+1)| ≤ κ|Δg(k)| ⟹ (1−κ)|g(N+M)−g(N)| ≤ |Δg(N)|`; tape route on one window; `σ_of g : RR` a Bishop-readout real with an *exhibited* modulus via bounded search `Nidx/N_of` | `IDM_ReadoutTower.v` · `tailsum_delta_telescopes`, `plateau_certificate` (occurrence of R/M.32.v1 `refine_stable`), `plateau_certificate_window`, `sigma_of`, `sigma_readout_exact`, `Pi`, `Pi_certificate`, `N_of_least` | Th_coqc — 38/38 theorem-like statements Closed in-file (the earlier 50 counted definitions, read in scratch) |
| **S2 RETAIN** | `Σ_Q(z) := (O z, [z]_Q)`; admissible iff `DepthStable L`; `Alg_Q := {P : ker q_K ⊆ ker P}` | `IDM_SignatureFunctor.v` · `Sigma`, `sigma_respects_step`, `InAlg`, `exact_on_alg`, `alg_is_fixed_points` (occurrence of EQ-002/M.01.v1, reuses `stable_depth_exact_future`) | Th_coqc — 18/18 theorem-like statements Closed in-file (the earlier 24 counted definitions, read in scratch) |
| **S3 RADIUS** | `r_K := ρ_K + β_K` (triangle) or `r_K² = ρ_K² + β_K²` (Pythagorean, hypothesis carried, occurrence of PROP-EPSC-17); `β_K = |Δg(N)|/(1−κ)` from S1 | `PROP_BRIDGE_03_certified_radius.v` (Toledo) · `triangle_composition`, `squared_orthogonal`, `contracting_beta`, `bridge_radius` (EPSC-08 lift) | Th_coqc — 31/31 Closed |
| **S4 ROUND TRIP** | EXACT: `P∘Λ_K∘q_K = P ⟺ P ∈ Alg_Q`; WITHIN RADIUS: `P` L_P-Lipschitz ⟹ `|P x − P(P_K x)| ≤ L_P·r_K`; NEVER: `q_K x = q_K x', x ≠ x'` ⟹ there is no `D : R_K → X` with `D(q_K x) = x ∧ D(q_K x') = x'` (`roundtrip_never`), hence no total **left-inverse** decoder `∀y, D(q_K y) = y` (`roundtrip_never_total`) — total functions `R_K → X` exist (constants, sections); what is refuted is recovery of merged states; level 2: `R_complete` bound + definitional diagonal; fence: unrestricted completeness, LUB, trichotomy never used (+ℝ-Open) | `roundtrip_exact_iff` (declared in `IDM_SignatureFunctor.v`); `IDM_BridgeRoundTrip.v` · `roundtrip_exact_tape`, `roundtrip_radius`, `roundtrip_never`, `roundtrip_never_total`, `level2_bound`, `level2_diagonal` | Th_coqc — 23/23 Closed |
| **S5 GATE** | `ACCEPT_ε(K) ⇐ cert : δ_K ≤ ε ∧ (ε−δ_K)² ≥ r_K²`; no cert ⟹ HOLD, never ACCEPT (`Verdict` has exactly two constructors; HOLD is the gate-level image of the parent alphabet's ⊥, not a third value and not 0); ACCEPT theorem, literal premises: **`0 ≤ r_K`** (`r_K_nonneg`), `d_Y(x, Λ_K(q_K x)) ≤ r_K`, `d_Y(Λ_K(q_K x), Λ_K(res_K x_{K+1})) ≤ δ_K` (`defect_cert`), `δ_K ≤ ε`, `(ε−δ_K)² ≥ r_K²`, triangle inequality on `d_Y` ⟹ `d_Y(x, Λ_K(res_K x_{K+1})) ≤ ε` (`accept_certified`); the ruling's orientation additionally declares symmetry of `d_Y` (`accept_certified_ruling_11b4`) | `PROP_BRIDGE_03_certified_radius.v` · `Certificate'`, `gate'`, `fail_closed'`, `no_certificate_holds'`, `accept_certified`, `accept_certified_ruling_11b4` | Th_coqc (in the same 31/31) |
| **Operator seam** (instantiation of the reader O, not a core line) | `−h²Δ_h φ = L_R φ` at interior nodes as a ring identity (h² multiplied through, no division); `Σ_edges (φ_{i+1}−φ_i)² = ⟨φ, L_R φ⟩ = I_form` (Keystone); `I(φ+e_i) − I(φ) = 2(L_Rφ)_i + L_ii`; Rayleigh ceiling `λ ≤ 4` on the path (weld/M.42.v1 at d_max = 2) | `Bridge_Seam.v` · `seam_grid`, `seam_grid_stencil`, `seam_energy`, `seam_energy_names`, `seam_box`, `seam_ceiling`, `seam_ceiling_scaled` | Th_coqc — 46/46 Closed in-file (12 headline theorems + support lemmas) |

Definitions (`Obs`, `Sigma`, `PK`, `sigma_of`, `Certificate'`, …) are tier `definition`; the "one law" sentence, the ρ_K-supplier, the class ⇄ record identification, and every physical identification are `Dr`; the +ℝ-Open fence is permanent by design. Full per-identifier tables: `docs/READOUT_BRIDGE_THEORY.md` §2 in the information-discrete-math repository and the programme's Coq ledger (research journal, private).

---

## 3. Evidence

| Check | Result (readout, 2026-09-18) |
|---|---|
| In-file `Print Assumptions`, five files (recompiled 2026-09-18 after the pre-merge review added the missing in-file lines to the first two files and to the seam's support lemmas) | 18 + 38 + 31 + 23 + 46 = **156 in-file readouts, all `Closed under the global context`** (theorem-like statements; definitions were additionally read Closed in scratch files during the build); 0 hits for `Admitted|admit|Axiom|Parameter|Coq.Reals` |
| Full-arc `formal/verify.sh` (run once, after all commits, under a 3 GB memory cap) | **29 files compiled, 205 listed theorems axiom-free, `ALL WITNESSES OK`** (an earlier "207" was a miscount of the log) |
| Parents' readouts (housekeeping) | PROP_EPSC_{03,05,08,17,20,21,23,39}: 13/13 Closed in-file; wrappers weld/M.63/64/68 Closed under the live IDM mapping; `R_complete` transparent (`Defined.`), diagonal by `reflexivity` |
| Independent adversarial refuters | Phase 1: 3 (design) + critic; Phase 2: 3 (Coq truth / registry / infinity audit); Phase 2b: 2 (seam / tape). Every refuter reproduced the compiles itself. Mathematics: never refuted. Surviving findings: registry shape, wording, framing — 35 + 12 applied, 9 + 5 deferred as open items (Phases 1–2b; Phase 3 has its own row below) |
| First executed test (finite_diagnostic) | exact-rational diffusion tape on a path graph (N = 8/16/32, same T): refining midpoint reader κ ≈ 0.272 → CERTIFIED; Dirichlet-energy reader κ ≈ 0.26–0.85 → CERTIFIED; non-refining sum reader κ ≈ 2 → **HOLD**; unstable dt (above h²/2) seen by any global reader κ ≈ 10⁴–10⁹ → **HOLD**. Byte-identical on three re-runs; the S1 gate also evaluated inside Coq by `vm_compute` on the same rationals |

| **Phase 3 heat/diffusion leaf — executed run** (`finite_diagnostic`, 2026-09-18; protocol and predictions frozen and committed before the script; the script committed before its first execution and unchanged afterwards; each coarse-window certificate file committed before the finer level of that tape was computed) | explicit stepper `φ ← φ − dt·L_R φ` on the unit path, nested grids `N_K = 8·2^K`, `K = 0..4` (at most 129 nodes, at most 256 steps), exact rationals, six tapes (free / pinned ends; `dt` = 1/4, 1/2, 1; one rough datum), seven readers, 40 (tape, reader) rows, no level dropped. Window certificates from 3 and from 4 coarse levels (C3, C4) tested against the held-out finer levels; the gate `gate'` evaluated on two frozen tolerance grids under the full-tape window certificate (C5). **Matched pairs (same reader, two regimes): 4**, all from the pinned tapes — e.g. `O_near`: κ = 0.155, 0.215, 0.240 at `dt = 1/4` (C4 certified, held-out value inside at 0.973 of the radius, ACCEPT up to `j*(K) = 4, 6, 8` on the relative grid) against κ_0 = 161011 at `dt = 1` (no licence, HOLD at every cell). Held-out MISS of the one-ratio certificate C3: 5 of 10 tested PASS-candidate rows and 2 of 3 tested FAIL rows; of C4: 0 of 10. **Two declared FAIL controls (rough datum × `O_near`, `O_bdry`) are certified at C4, pass the held-out test and have ACCEPT cells** — reported first by the run itself. Outcome against the frozen predictions, stratified: theorem-instance / hand-derivation / regression / forced-by-arithmetic classes 172 items, 0 misses (plus 9,434 executed assertion instances, none violated); open predictions 225 tallied, **42 misses** (227 / 44 if two untallied out-of-bracket κ values are counted) |
| **Phase 3 heat/diffusion leaf — Coq** (`formal/Leaf_HeatPath.v`, information-discrete-math; numerals copied by a generator from the run's exact rationals) | one `coqc`, exit 0: **348 in-file `Print Assumptions` lines, 348 `Closed under the global context`** (346 theorem-like statements + the two computing definitions `cert_dec`, `leaf_gate`); 0 hits for `Admitted|admit|Axiom|Parameter|Coq.Reals`. Tier: `Th_coqc` **for theorems about the run's numbers** — the numbers themselves stay `finite_diagnostic`. Seven of the 40 rows; levels 1–4 of the tapes are not recomputed in Coq (level 0 is, for six rows, through `seam_grid`) |
| Phase 3 refuters (three independent lenses, each re-running what it judged) | numbers: **not refuted** (full 56-command re-run byte-identical; an independent stepper with no shared code matched 30/30 states and 34/34 scalar ledgers); Coq: **not refuted** (recompile 346/346, numerals 218/218 against the run, gate shown fail-able); prose-vs-formal: **refuted the description, not a theorem** — the leaf's header re-introduced "third value" for HOLD, and `leaf_gate` is window-local and parametric in κ whereas the protocol licenses on the full tape. Fixed in a fixer pass (§5 item 1 (f)); no false theorem was found by any lens |

What the tape test does **not** show (stated in the record itself): on a three-readout tape the licence instance is an identity in κ and CERTIFIED carries exactly one bit (the gap shrank once); the midpoint reader at K ≤ N/2 steps is a closed form for every dt and is uninformative about stability; κ ≈ 1/4 matching a second-order reader is an expectation (Dr), not a result.

---

## 4. What is genuinely ours, what is a credited parent, and how this sits next to prior work

**Ours (the delta that compiled):** the certificate schema as one protocol — retained ledger → licence → radius in ℚ → three-clause (exact / within-radius / never) round trip → fail-closed gate — with the NEVER clause and HOLD as first-class outcomes; `σ_of` with an exhibited modulus from a witnessed contraction; the seam as ring identities with h² multiplied through; the declaration pattern (q_K, Λ_K, res_K, (Y, d_Y, axioms per clause), A, graph, ρ_K-supplier) under which "universal" means the certificate *shape*, with existence per domain defaulting to HOLD.

**Credited parents (by code, reused not re-proved):** refine_stable R/M.32.v1, the telescopes Z/M.06/M.08, reader-domain quotient weld/M.02/M.03, kernel inclusion weld/M.64/M.68, Bishop `R_complete` weld/M.60.v1, EPSC-03/08/17 (fail-closed gate, Lipschitz lift, orthogonal composition), Keystone/M.03 (B = I), L_R/M.20–22, weld/M.41/M.42, the no-decoder theorem of Readout Genesis (PROP-BRIDGE-09).

**Related work (read on 2026-09-18 from the cited pages; positioned as horizontal neighbours, not as validation — no "first" claim is made):**

| Work | What it does (as read) | Where the Readout Bridge differs |
|---|---|---|
| Magaud, Chollet, Fuchs — *Harthong–Reeb line in Coq* | a discrete (nonstandard) model of the continuum from Laugwitz–Schmieden integers; ordered field via Bridges' axioms; **proves the least-upper-bound principle**; extraction to OCaml for arithmetized continuous functions | we never adopt LUB or a nonstandard integer axiom set: ℝ enters only as a *readout* of ℚ-approximants with an exhibited modulus, LUB/trichotomy are fenced +ℝ-Open, and the bridge's output is a certificate or HOLD, not a model of ℝ |
| Tekriwal, Duraisamy, Jeannin — *formal Lax equivalence theorem* (Coq, arXiv:2103.13534) | consistency + stability ⟹ convergence for finite-difference schemes, over continuous linear operators between complete normed spaces, Taylor–Lagrange consistency bounds | the same physical object (a finite-difference tape) but the opposite direction of licence: no h → 0, no complete normed space as substrate; the certificate is a finite ℚ radius from a witnessed κ on the tape, and the gate can return HOLD for the same scheme in a different parameter regime |
| O'Connor — *Certified exact transcendental real number computation in Coq* (TPHOLs 2008, arXiv:0805.2438) | constructive reals via complete metric spaces, elementary functions with correctness proofs, a tactic proving strict inequalities by computation | closest parent for `σ_of` / `RR`: our level-2 object is the same kind of constructive real, reused from weld/M.60 rather than re-built; what we add is the *licence* layer (when a tape earns a modulus) and the retain/round-trip/gate layers around it |
| Gappa (with Flocq) — validated numerical certification (read: gappa.gitlabpages.inria.fr, tools page) | a tool proving bounds on floating-/fixed-point computations and simple real inequalities, invoked from Coq by a tactic built on Flocq's formats and rounding operators | the nearest neighbour for "certificate + checker": Gappa certifies *rounding/enclosure bounds of an expression*; the bridge certifies *when a finite exact tape licenses a statement about a different-level object* and carries HOLD, the NEVER clause and the retain quotient, none of which is an enclosure problem. CoqInterval (certified bounds of real expressions) belongs here too — **not read in this pass; cited from general knowledge, to be read before the paper** |
| Necula — *Proof-carrying code* (POPL 1997) — **source page not readable in this pass (HTTP 403); cited from bibliographic knowledge, `Dr`, to be read before the paper** | a producer ships evidence with the artefact; the consumer checks it against a policy before use | an architectural relative of "result + certificate + gate": same producer/consumer shape, entirely different semantics — the policy here is a declared bridge hypothesis set and the refused outcome is a scientific claim, not code execution |
| Rocq Numerical Analysis (Mayero et al.; FEM Lagrange P_k nodes, RR-9557) | finite-element theory formalized over Coquelicot / Coq reals | a real-analysis-first formalization of the continuum method; the bridge is ℚ-first and treats the continuum method as a readout; the two are complementary, not competing |

Under this workspace's standing rule, none of the above is a lever for legitimacy; they are the neighbours a paper must cite honestly.

---

## 5. Honest boundary (what would make this a result about a scientific domain, and is not yet done)

1. **One heat/diffusion leaf now instantiates the five lines on the exact rationals of one executed run. It is a window-certificate instance on one graph family and one scheme — not a domain closure, and not a continuum-limit theorem.** Before Phase 3 the rows that evidenced the full shape were geometry (exact), the number ladder (self-instance) and the toy diffusion tape (one bit). Phase 3 (2026-09-18) adds the run and the Coq file of §3.
   **What the leaf shows** (numbers `finite_diagnostic`; theorems `Th_coqc` about those numbers):
   (a) ACCEPT and HOLD separate by parameter regime with quantitative content on the pinned pair: same reader `O_near`, `dt = 1/4` → licensed, ACCEPT at the protocol's cell; `dt = 1` → the compiled gate returns HOLD at every scored cell `K ≤ 2`, for every κ and every tolerance (`matched_pair_near`, `TD_near.C5_HOLD_scored_cells`). Four such pairs in the run, all from the pinned tapes; the FAIL half of each is a blow-up (κ_0 between 2.7·10³ and 4.4·10⁹), not a subtle control.
   (b) The one-ratio coarse window is regime-blind for the midpoint reader: κ̂_3 = 1/4 exactly on the stable and on the unstable free tape (`trap_same_C3_ratio`); the unstable one is caught only by the held-out levels (both values outside the ball, by more than 10²²; `TB_mid.C3_heldout_g3_MISS`, `_g4_MISS`) and by the absence of a licence at C4 / C5.
   (c) HOLD is not FALSE, as compiled cells: the gate HOLDs at cells where the inequality it would have certified is true on the tape (`hold_is_not_false_*`), and a licensed tape with κ̂_5 ≈ 0.9989 HOLDs from the largest tolerance of either grid downwards (`TR_state`).
   (d) A held-out MISS refutes the persistence of the contraction on the window (`heldout_miss_refutes_persistence`, the contrapositive of the windowed division-form radius `plateau_radius_window`).
   **What it does not show** (each item is in the run record or compiled on purpose):
   (e) It does not show that the gate detects a bad datum or a bad model. Two declared FAIL controls on the rough datum are certified, pass the informative held-out test and are ACCEPTed (`TR_near` is compiled as exactly that); by the letter of the frozen protocol's power section this is a control not caught. A conserved reader certifies and HITs on the unstable tape with a ledger identical, rational by rational, to the stable tape's. **An ACCEPT certifies the ledger it is given — not the model, the datum or the reader.**
   (f) The Coq leaf is two layers that are not composed: S1, S3, S5 on scalar ledgers (constant `q_K`, identity `Λ_K`, `res_K`; `ρ_K` not instantiated, `r_K := β_K`), and S2, S4 on a separate 5-fine / 3-coarse tuple grid whose data are small declared vectors, not heat states of the run. `leaf_gate` is window-local and parametric in κ; the protocol's full-tape gate is its instance κ := κ̂_5, and the file compiles the two ways the definition is weaker (`gate_is_window_local`; `K3_licensed_by_padding_only`: at `K = top − 1` the only premise is the padded index, so that cell is excluded). Under the full-tape certificate the conclusion of an ACCEPT, `|g_4 − g_{K+1}| ≤ ε`, concerns two values already on the tape and has no predictive content; the only held-out statements are the C3 / C4 observations. `HOLD` remains the gate-level image of the parent alphabet's ⊥ — `Verdict` has two constructors.
   (g) The one-ratio certificate C3 is not a regime classifier on this family (held-out MISS on 5 of 10 tested PASS-candidate rows); the free-end tapes contribute no matched pair; 42 of 225 tallied open predictions missed.
   (h) Scope: every certificate is a WINDOW certificate on witnessed levels of a five-level tape; one graph family (the unit path), one scheme (the explicit stepper above), one datum family plus one rough datum. Nothing is stated about a level beyond 4, a tail or a limit; the continuum heat equation appears only as a `Dr` readout; **no convergence or continuum-limit theorem is stated or follows**; `h → 0` is never formed.
   **Not yet done, and what would make this a result about the domain:** the state-layer ledger (`O_state`, a path-length ledger of the state tape) as a Coq object, so that the two layers compose; levels 1–4 recomputed inside Coq; a full-tape licence inside `leaf_cert`; a second graph family and a second scheme; a separately frozen amplitude series for the rough datum; a domain `ρ_K`-supplier.
2. Every ρ_K-supplier is a declared datum (and κ is witnessed per tape or declared a priori); the only compiled β-supplier is the S1 contraction; the Navier–Stokes row is a `+ℝ-axioms` instantiation outside the core typing.
3. Registry: codes `??`, mirror re-sync of IDM inside Toledo, LINEAGE events, row-vs-occurrence for two objects, lane vocabulary — registrar decisions (Toledo PR #43).
4. Genesis A.8 (retraction vs section): the section reading is adopted as `Dr`; the founder's ontology ruling is pending.

---

## 5a. What ACCEPT does not mean (threats to validity)

- ACCEPT certifies the stated finite-to-readout bound under the declared hypotheses, and nothing else.
- It does not certify the physical model, the choice of reader `O`, or the existence of a domain-specific `ρ_K` / `β_K` / `κ` supplier.
- HOLD means insufficient certified evidence — not falsity, not rejection of the claim.
- No convergence or continuum-limit theorem follows unless a domain leaf supplies one separately; the bridge never forms `h → 0`.

---

## 6. Process (so the paper's methods section can be written from one place)

| Step | What happened | Where |
|---|---|---|
| Audit | Toledo (1,333 canonical rows) + IDM + Genesis searched by statement: no registered, domain-neutral, bidirectional bridge object existed; EPSC was NS-specific; round trip only PROP-EPSC-17 (Dr) | programme handoff (private journal) |
| Phase 1 — design | 6 readers → 4 designs (Cauchy-readout, EPSC certificate, operator/spectral, Genesis lineage) → 3 judges → synthesis → 3 refuters + completeness critic; winner EPSC-certificate, best ideas grafted; 10 design items ruled under the readout-universe tier discipline (§11b) | design document (private journal) |
| Phase 2 — theory in Coq | inventory of IDM's existing round-trip machinery (46 objects) → 4 files built one at a time → housekeeping → registration → 3 refuters → fixer | Coq ledger §1–10 (private journal) |
| Phase 2b — first tests | seam file + `N_of_least`; exact-rational tape test with FAIL controls; 2 refuters → fixer | Coq ledger §11 and the tape record (private journal) |
| Phase 3 — heat/diffusion leaf | protocol + predictions frozen after two critic passes → script committed before its first execution → 56 campaign commands with certificate files committed before the finer levels (temporal blinding) → record with every miss before any hit → Coq leaf generated from the run's exact rationals and compiled → 3 refuters (numbers / Coq / prose-vs-formal) → fixer pass (header and gate description corrected, two disclosure Examples compiled, record addendum) | Coq ledger §12–13 and the leaf's run record (private journal) |
| Build discipline | every Coq build was run one `coqc` at a time under a memory cap, with no background jobs; the orchestration was rebuilt this way after an unrelated resource incident on the workstation | programme handoff |
| Discipline | readout-not-truth; Toledo-first and the reuse pipeline (lookup by statement → Genesis section → reuse as parent → derive only the delta → label PROPOSAL); tier = own `Print Assumptions`; Open never bare; maker-checker with independent refuters before any publish; no AI attribution | workspace rules |

Commits: information-discrete-math `formal/readout-bridge` (ac1df59 … 78801fd); toledo `proposals/readout-bridge` (b712d0a9 … 70620cad, PR #43); research journal (private).

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
coqc -q -R $W IDM -Q $T/coq/canonical MRC Leaf_HeatPath.v   # Phase 3 leaf: expect 348 x "Closed under the global context"
bash verify.sh          # full arc, once: expect "ALL WITNESSES OK (compiled + axiom-free)"; it does NOT build IDM_BridgeRoundTrip.v, Bridge_Seam.v or
                        # Leaf_HeatPath.v (they need the MRC mapping) and it removes *.vo -- rebuild those three by the commands above afterwards
# tape test: python3 tape_test.py (script in the private research journal; its record is summarised in §3)
# heat leaf: the run script, its frozen protocol, the 56 verbatim logs and the generator of Leaf_HeatPath.v are in the private research journal;
#            the numerals in Leaf_HeatPath.v are the run's exact rationals (sha256 of the source JSON is in the file header)
```

Every theorem prints its own `Print Assumptions` at the end of its file; grep the output for `Closed under the global context`.

---

## 8. Links (pinned)

**Public reproducibility status (2026-09-18):** information-discrete-math pull request 137 (the four IDM files, the theory document, the first revision of this record) and toledo pull request 43 (`PROP_BRIDGE_03_certified_radius.v`, the registry proposal lane, a copy of this record) were merged into the two `main` branches on 2026-09-18. Phase 3 — `formal/Leaf_HeatPath.v`, this revision of the record, the theory-document update and the leaf's occurrence record `PROP-BRIDGE-21` in `registry/proposals/discrete_continuum_bridge.occurrences.json` — enters through follow-up pull requests to the same two repositories (numbers pending at the time of writing). §7 can be followed from the two checkouts. No CI job compiles `Leaf_HeatPath.v` (it needs both mappings); its tier rests on the manual command of §7. `PROP_BRIDGE_03_certified_radius.v` Requires `IDM_ReadoutTower` from the IDM branch; it is not buildable from a toledo clone alone until the mirror re-sync.

- Theory (per-identifier tables, Open ledger, reuse inventory): `docs/READOUT_BRIDGE_THEORY.md` in the information-discrete-math repository — <https://github.com/morrocwi/information-discrete-math/pull/137>
- Registry proposal lane + S3/S5 Coq: <https://github.com/morrocwi/toledo/pull/43>
- Heat/diffusion leaf: `formal/Leaf_HeatPath.v` in the information-discrete-math repository (its header states the tier split, the rows instantiated, what is left out, and the two disclosures about `leaf_gate`); occurrence record `PROP-BRIDGE-21` in the toledo proposal lane.
- Design document, rulings, Coq ledger, the frozen heat-leaf protocol and the executed-test records live in the programme's research journal (private); the facts a reader needs from them are restated in §3, §5 and §6 above.
- Concept line and ontology: Readout Genesis (`READOUT_GENESIS_CORE.md`, gates A.4 / A.7 / A.8 / A.12 / A.13); tier discipline: readout_universe

*Every object above: not yet in Toledo.*
