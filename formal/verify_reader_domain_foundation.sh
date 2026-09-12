#!/usr/bin/env bash
# verify_reader_domain_foundation.sh — compile the Reader-Domain Foundation
# and verify all promoted theorem identifiers are axiom-free.
set -euo pipefail
cd "$(dirname "$0")"

FILE="IDM_ReaderDomainFoundation"
THEOREMS=(
  T1_eq_obs_correspondence
  T2_closure_extensive
  T2_closure_monotone
  T2_eq_closure_invariant
  T2_closure_idempotent
  T3_future_equivalence_dynamic_stability
  T4_dynamic_weld_well_defined
  T4b_quotient_commuting_square
  T5_sufficiency_kernel_inclusion
  T6_question_monotonicity
  T7_joint_question_intersection
  closure_is_closed
  closed_intersection
  closed_join
  future_eq_refl
  future_eq_sym
  future_eq_trans
  future_eq_implies_depth
  stable_depth_exact_future
  finite_strict_refinement_terminates
)

rm -f "${FILE}.vo" "${FILE}.glob" "${FILE}.vos" "${FILE}.vok" ".${FILE}.aux" chk_reader_domain_*.v chk_reader_domain_*.vo chk_reader_domain_*.glob .chk_reader_domain_*.aux 2>/dev/null || true

echo "== Reader-Domain source audit =="
if grep -nE 'Admitted|Axiom |^Axiom|Parameter |\badmit\b' "${FILE}.v"; then
  echo "FOUND Admitted/Axiom/Parameter/admit — FAIL"
  exit 1
fi

echo "== compile ${FILE}.v =="
coqc -q "${FILE}.v"

echo "== Print Assumptions =="
for thm in "${THEOREMS[@]}"; do
  chk="chk_reader_domain_${thm}.v"
  printf 'Require Import %s.\nPrint Assumptions %s.\n' "$FILE" "$thm" > "$chk"
  out=$(coqc -q "$chk" 2>/dev/null)
  if echo "$out" | grep -q "Closed under the global context"; then
    echo "  axiom-free  $thm"
  else
    echo "  NOT-CLOSED  $thm -> $out"
    exit 1
  fi
  rm -f "$chk" "${chk%.v}.vo" "${chk%.v}.glob" ".${chk%.v}.aux" 2>/dev/null || true
done

rm -f "${FILE}.vo" "${FILE}.glob" "${FILE}.vos" "${FILE}.vok" ".${FILE}.aux" 2>/dev/null || true

echo "READER-DOMAIN FOUNDATION FORMAL KERNEL PASS"
