# CFML Formal Root Ledger

This ledger is the admissibility contract for the JIL manuscript. A trusted CFML invariant is allowed only when its source is IDM or Readout Universe and its named Coq theorem is axiom-free (or explicitly documented as the axiom-free discrete core). All rows below satisfy that rule. Educational interpretations do not receive a theorem tag.

| Invariant | Coq root | Permitted architectural consequence |
|---|---|---|
| Declaration before authorization | `declared_forgets_tail`; `deferred_record_bits`; `declaration_separation` (IDM Declaration Bound) | Freeze the requested readout before evidence is accepted; do not infer semantic correctness beyond the declaration. |
| Readout-relative verdict | `readout_monotone`; `tolerance_violation_iff_flip`; `threshold_order` (Readout Universe UPL) | Retain threshold/tolerance with the verdict; the readout is not context-free. |
| Faithful readout | `equivariant_stabilizer_containment`; `faithful_stabilizer_equality` (IDM Equivariant Readout) | Do not erase distinctions required by the declared transformation structure. |
| Exact certificate | `geom_certified_identity`; `geom_certified_defect` (IDM Certified) | Authorize EXACT by an exact identity in the declared finite domain, not by confidence. |
| Bounded certificate | `geom_majorant_tail`; `iter_sq_certified`; `apriori_stable`; `richardson_apriori_stable` (IDM Certified/A-priori) | Authorize CONDITIONAL here only with a Coq-certified finite bound and retained assumptions. |
| HOLD distinct from determinate neutral | `neutral_distinct_from_bottom`; `bottom_unique`; `neutral_is_not_bottom` (IDM Readout Minimality) | Do not collapse unresolved status into a determinate neutral or zero result. |
| Provenance retention | `RD4_succ_inj`; `toNat_inj`; `eval_hom`; `eqn_transfer` (Readout Universe RD) | Keep declaration/proof histories distinguishable; this is an operational instantiation, not a theorem about pedagogy. |

## Exclusions

- No `Dr`, `Open`, or `finite_diagnostic` statement is used as a foundational invariant.
- No learning-effect claim is labeled as proved by Coq.
- No new Coq theorem is claimed in this paper. The manuscript composes already verified roots and keeps their scope fences.
- Candidate generation by an LLM is outside the trusted kernel and receives no theorem status.
