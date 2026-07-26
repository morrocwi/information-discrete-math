#!/usr/bin/env bash
# verify.sh — compile every local Coq witness and confirm it is axiom-free.
# One-command reproducibility for the formal/ layer. Exit 0 iff all pass and all
# Print Assumptions report "Closed under the global context".
set -u
cd "$(dirname "$0")"

FILES=(IDM_Keystone IDM_Bridge IDM_FiniteWitnesses IDM_FiniteWitnesses2 IDM_Logic IDM_FiniteWitnesses3 IDM_Matrix IDM_Harvest IDM_Calculus IDM_Certified)

# theorem -> file, checked for axiom-freedom
declare -a THMS=(
  "keystone_B_eq_I:IDM_Keystone"
  "keystone_nonneg:IDM_Keystone"
  "relaxation_dissipation:IDM_Keystone"
  "FTCC_exact:IDM_Bridge"
  "FTCC_eps_exact:IDM_Bridge"
  "kuratowski_pair_inj:IDM_FiniteWitnesses"
  "handshake_lemma:IDM_FiniteWitnesses"
  "pigeonhole:IDM_FiniteWitnesses"
  "finite_yoneda:IDM_FiniteWitnesses"
  "semiring_distrib:IDM_FiniteWitnesses"
  "no_infinite_readout:IDM_FiniteWitnesses2"
  "tape_count_succ:IDM_FiniteWitnesses2"
  "same_set_same_size:IDM_FiniteWitnesses2"
  "lagrange_order_div:IDM_FiniteWitnesses2"
  "finite_satisfaction_dec:IDM_Logic"
  "rdl_non_explosion:IDM_Logic"
  "no_fibonacci_integer_dim:IDM_FiniteWitnesses3"
  "cauchy_schwarz_2:IDM_FiniteWitnesses3"
  "measure_additive:IDM_FiniteWitnesses3"
  "ring_distrib_Z:IDM_FiniteWitnesses3"
  "aut_inv_left:IDM_FiniteWitnesses3"
  "mid_left:IDM_Matrix"
  "laplacian_symmetric:IDM_Matrix"
  "laplacian_rowsum_zero:IDM_Matrix"
  "laplacian_ones_in_kernel:IDM_Matrix"
  "twirl_image_scalar:IDM_Matrix"
  "twirl_idempotent:IDM_Matrix"
  "repeated_event_zero:IDM_Harvest"
  "odd_from_cyclic_closure:IDM_Harvest"
  "sym_skew_reconstruct:IDM_Harvest"
  "skew_diag_zero:IDM_Harvest"
  "delta_product:IDM_Calculus"
  "Deps_product:IDM_Calculus"
  "FTCC_telescope:IDM_Calculus"
  "summation_by_parts:IDM_Calculus"
  "geom_certified_identity:IDM_Certified"
  "geom_certified_defect:IDM_Certified"
  "geom_majorant_tail:IDM_Certified"
  "exp_tail_certified:IDM_Certified"
)

fail=0

# clean BEFORE compiling: stale/partial .vo from a prior or concurrent run can poison
# Print Assumptions and cause false NOT-CLOSED failures. Idempotent from a fresh tree.
rm -f ./*.vo ./*.glob ./*.vos ./*.vok ./.*.aux ./chk_*.v 2>/dev/null

echo "== no Admitted/Axiom/admit =="
if grep -nE "Admitted|Axiom |^Axiom|Parameter |\badmit\b" ./*.v; then echo "  FOUND Admitted/Axiom/admit — FAIL"; fail=1; else echo "  clean (no Admitted/Axiom/admit)"; fi

echo "== compiling =="
for f in "${FILES[@]}"; do
  if coqc -q "$f.v" >/dev/null 2>&1; then echo "  ok   $f.v"; else echo "  FAIL $f.v"; fail=1; fi
done

echo "== axiom-freedom (Print Assumptions) =="
for t in "${THMS[@]}"; do
  name="${t%%:*}"; file="${t##*:}"
  chk=$(mktemp chk_XXXXXX.v)                 # collision-proof temp (multi-agent workspace safe)
  printf 'Require Import %s.\nPrint Assumptions %s.\n' "$file" "$name" > "$chk"
  out=$(coqc -q "$chk" 2>/dev/null)
  rm -f "$chk" "${chk%.v}.vo" "${chk%.v}.glob" ".${chk%.v}.aux" 2>/dev/null
  if echo "$out" | grep -q "Closed under the global context"; then
    echo "  axiom-free  $name"
  else
    echo "  NOT-CLOSED  $name -> $out"; fail=1
  fi
done

rm -f ./*.vo ./*.glob ./*.vos ./*.vok ./.*.aux 2>/dev/null

if [ "$fail" -eq 0 ]; then echo "ALL WITNESSES OK (compiled + axiom-free)"; else echo "SOME WITNESSES FAILED"; fi
exit $fail
