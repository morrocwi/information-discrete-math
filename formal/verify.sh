#!/usr/bin/env bash
# verify.sh — compile every local Coq witness and confirm it is axiom-free.
# One-command reproducibility for the formal/ layer. Exit 0 iff all pass and all
# Print Assumptions report "Closed under the global context".
set -u
cd "$(dirname "$0")"

FILES=(IDM_Keystone IDM_Bridge IDM_FiniteWitnesses IDM_FiniteWitnesses2 IDM_Logic IDM_FiniteWitnesses3)

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
)

fail=0

echo "== compiling =="
for f in "${FILES[@]}"; do
  if coqc -q "$f.v" >/dev/null 2>&1; then echo "  ok   $f.v"; else echo "  FAIL $f.v"; fail=1; fi
done

echo "== axiom-freedom (Print Assumptions) =="
for t in "${THMS[@]}"; do
  name="${t%%:*}"; file="${t##*:}"
  printf 'Require Import %s.\nPrint Assumptions %s.\n' "$file" "$name" > _chk_$$.v
  out=$(coqc -q _chk_$$.v 2>/dev/null)
  rm -f _chk_$$.v
  if echo "$out" | grep -q "Closed under the global context"; then
    echo "  axiom-free  $name"
  else
    echo "  NOT-CLOSED  $name -> $out"; fail=1
  fi
done

rm -f ./*.vo ./*.glob ./*.vos ./*.vok ./.*.aux 2>/dev/null

if [ "$fail" -eq 0 ]; then echo "ALL WITNESSES OK (compiled + axiom-free)"; else echo "SOME WITNESSES FAILED"; fi
exit $fail
