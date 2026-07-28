#!/usr/bin/env bash
# verify.sh — compile every local Coq witness and confirm it is axiom-free.
# One-command reproducibility for the formal/ layer. Exit 0 iff all pass and all
# Print Assumptions report "Closed under the global context".
set -u
cd "$(dirname "$0")"

FILES=(IDM_Keystone IDM_Bridge IDM_FiniteWitnesses IDM_FiniteWitnesses2 IDM_Logic IDM_FiniteWitnesses3 IDM_Matrix IDM_Harvest IDM_Calculus IDM_Certified IDM_Tropical IDM_Geometry IDM_Reduction IDM_Hilbert IDM_DeclarationBound IDM_Genesis)

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
  "sq_error_propagation:IDM_Certified"
  "iter_sq_certified:IDM_Certified"
  "abs_tailsum_le:IDM_Certified"
  "refine_stable:IDM_Certified"
  "tmin_assoc:IDM_Tropical"
  "tmin_comm:IDM_Tropical"
  "tmin_idem:IDM_Tropical"
  "tmax_assoc:IDM_Tropical"
  "tmax_comm:IDM_Tropical"
  "tmax_idem:IDM_Tropical"
  "tadd_assoc:IDM_Tropical"
  "tadd_comm:IDM_Tropical"
  "tadd_0_l:IDM_Tropical"
  "minplus_distrib:IDM_Tropical"
  "maxplus_distrib:IDM_Tropical"
  "bottleneck_distrib:IDM_Tropical"
  "orient_swap_bc:IDM_Geometry"
  "orient_swap_ab:IDM_Geometry"
  "orient_cyclic:IDM_Geometry"
  "orient_coincident_ab:IDM_Geometry"
  "orient_coincident_ac:IDM_Geometry"
  "orient_coincident_bc:IDM_Geometry"
  "orient_translation:IDM_Geometry"
  "orient_scale:IDM_Geometry"
  "orient_collinear_mid:IDM_Geometry"
  "orient_collinear_aff:IDM_Geometry"
  "ftcc_Z:IDM_Reduction"
  "foldmin_le_init:IDM_Reduction"
  "foldmin_le_elem:IDM_Reduction"
  "sum_is_fold:IDM_Reduction"
  "path_is_fold:IDM_Reduction"
  "pivot_preserves:IDM_Reduction"
  "witness_sound:IDM_Reduction"
  "witness_complete:IDM_Reduction"
  "decide_dec:IDM_Reduction"
  "witness_composite_sound:IDM_Reduction"
  "composite_has_factor:IDM_Reduction"
  "fold_ext:IDM_Reduction"
  "fold_linear:IDM_Reduction"
  "fold_add_split:IDM_Reduction"
  "foldmax_ge_init:IDM_Reduction"
  "foldmax_ge_elem:IDM_Reduction"
  "dot_is_fold:IDM_Reduction"
  "dot_scale:IDM_Reduction"
  "decide_reflect:IDM_Reduction"
  "witness_power_sound:IDM_Reduction"
  "horner_scaled:IDM_Reduction"
  "horner_is_poly:IDM_Reduction"
  "foldmin_in:IDM_Reduction"
  "fold_add_app:IDM_Reduction"
  "factorial_is_fold:IDM_Reduction"
  "witness_qr_sound:IDM_Reduction"
  "witness_dlog_sound:IDM_Reduction"
  "relax_nonincreasing:IDM_Reduction"
  "relax_idempotent:IDM_Reduction"
  "weak_duality_2:IDM_Reduction"
  "sat_reduces_to_decision:IDM_Reduction"
  "sat_model_sound:IDM_Reduction"
  "op_swap:IDM_Reduction"
  "fold_right_perm:IDM_Reduction"
  "fold_split_even_odd:IDM_Reduction"
  "modpow_is_fold:IDM_Reduction"
  "foldmax_in:IDM_Reduction"
  "sum_list_perm:IDM_Reduction"
  "prod_list_perm:IDM_Reduction"
  "tautology_sound:IDM_Reduction"
  "cnf_tautology_sound:IDM_Reduction"
  "witness_crt_sound:IDM_Reduction"
  "Qsq_nonneg:IDM_Hilbert"
  "inner_sym:IDM_Hilbert"
  "inner_linear_l:IDM_Hilbert"
  "inner_pos:IDM_Hilbert"
  "parallelogram_law:IDM_Hilbert"
  "pythagoras_orthogonal:IDM_Hilbert"
  "cauchy_schwarz_2:IDM_Hilbert"
  "adjoint_involutive:IDM_Hilbert"
  "adjoint_of_product:IDM_Hilbert"
  "hermitian_2x2_discriminant_nonneg:IDM_Hilbert"
  "hermitian_2x2_gap_is_discriminant:IDM_Hilbert"
  "projection_idempotent:IDM_Hilbert"
  "projection_self_adjoint:IDM_Hilbert"
  "primordial_difference_exists:IDM_Genesis"
  "succ_ground_distinct:IDM_Genesis"
  "discrete_floor:IDM_Genesis"
  "no_density_at_root:IDM_Genesis"
  "bit_extraction_exact:IDM_DeclarationBound"
  "profile_injective:IDM_DeclarationBound"
  "bcube_length:IDM_DeclarationBound"
  "bcube_nodup:IDM_DeclarationBound"
  "deferred_record_bits:IDM_DeclarationBound"
  "declared_forgets_tail:IDM_DeclarationBound"
  "declaration_separation:IDM_DeclarationBound"
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
