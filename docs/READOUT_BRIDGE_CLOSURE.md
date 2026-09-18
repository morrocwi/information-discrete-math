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
| Independent adversarial refuters | Phase 1: 3 (design) + critic; Phase 2: 3 (Coq truth / registry / infinity audit); Phase 2b: 2 (seam / tape). Every refuter reproduced the compiles itself. Mathematics: never refuted. Surviving findings: registry shape, wording, framing — 35 + 12 applied, 9 + 5 deferred as open items |
| First executed test (finite_diagnostic) | exact-rational diffusion tape on a path graph (N = 8/16/32, same T): refining midpoint reader κ ≈ 0.272 → CERTIFIED; Dirichlet-energy reader κ ≈ 0.26–0.85 → CERTIFIED; non-refining sum reader κ ≈ 2 → **HOLD**; unstable dt (above h²/2) seen by any global reader κ ≈ 10⁴–10⁹ → **HOLD**. Byte-identical on three re-runs; the S1 gate also evaluated inside Coq by `vm_compute` on the same rationals |

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

1. **No nontrivial Genesis leaf domain has run S1 → S5 end-to-end with quantitative certificate content.** The rows that evidence the full shape are geometry (exact), the number ladder (self-instance) and the toy diffusion tape (one bit). The planned first leaf is the heat/diffusion equation on a longer tape (many resolutions, many windows, a-priori κ from Richardson order with its own FAIL regime), so that ACCEPT and HOLD separate by parameter regime with real quantitative content. That experiment is the paper's main experiment and is queued as Phase 3.
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
bash verify.sh          # full arc, once: expect "ALL WITNESSES OK (compiled + axiom-free)"
# tape test: python3 tape_test.py (script in the private research journal; its record is summarised in §3)
```

Every theorem prints its own `Print Assumptions` at the end of its file; grep the output for `Closed under the global context`.

---

## 8. Links (pinned)

**Public reproducibility status (2026-09-18):** both branches are public. information-discrete-math pull request 137 (branch `formal/readout-bridge`) carries the four IDM files, the theory document and this record; toledo pull request 43 (branch `proposals/readout-bridge`) carries `PROP_BRIDGE_03_certified_radius.v`, the registry proposal lane and a copy of this record. §7 can be followed from the two checkouts. `PROP_BRIDGE_03_certified_radius.v` Requires `IDM_ReadoutTower` from the IDM branch; it is not buildable from a toledo clone alone until the mirror re-sync.

- Theory (per-identifier tables, Open ledger, reuse inventory): `docs/READOUT_BRIDGE_THEORY.md` in the information-discrete-math repository — <https://github.com/morrocwi/information-discrete-math/pull/137>
- Registry proposal lane + S3/S5 Coq: <https://github.com/morrocwi/toledo/pull/43>
- Design document, rulings, Coq ledger and the executed-test records live in the programme's research journal (private); the facts a reader needs from them are restated in §3, §5 and §6 above.
- Concept line and ontology: Readout Genesis (`READOUT_GENESIS_CORE.md`, gates A.4 / A.7 / A.8 / A.12 / A.13); tier discipline: readout_universe

*Every object above: not yet in Toledo.*
