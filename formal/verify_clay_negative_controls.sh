#!/usr/bin/env bash
# Compile the P2 adversarial controls and verify promoted finite theorems are
# closed under the global context.
set -eu
cd "$(dirname "$0")"

SAFE="IDM_FiniteObstructionSafeCore"
FILE="IDM_FiniteObstructionNegativeControls"
THEOREMS=(
  every_finite_prefix_bounded
  rising_not_globally_bounded
  finite_prefixes_do_not_force_global_boundedness
  unit_step_chain_sum
  local_step_bounds_do_not_give_uniform_chain_bound
  transport_can_fail_without_invariance
  checker_can_accept_without_soundness
)

cleanup() {
  rm -f "${SAFE}.vo" "${SAFE}.glob" "${SAFE}.vos" "${SAFE}.vok" ".${SAFE}.aux" \
        "${FILE}.vo" "${FILE}.glob" "${FILE}.vos" "${FILE}.vok" ".${FILE}.aux" \
        ./chk_p2_*.v ./chk_p2_*.vo ./chk_p2_*.glob ./.*chk_p2_*.aux 2>/dev/null || true
}
trap cleanup EXIT
cleanup

echo "== P2 negative controls: forbidden proof escapes =="
if grep -nE "Admitted|Axiom |^Axiom|Parameter |\\badmit\\b" "${FILE}.v"; then
  echo "FOUND forbidden proof escape"
  exit 1
fi

echo "== P2 negative controls: compile dependencies =="
coqc -q "${SAFE}.v"
coqc -q "${FILE}.v"

echo "== P2 negative controls: Print Assumptions =="
for theorem in "${THEOREMS[@]}"; do
  chk=$(mktemp chk_p2_XXXXXX.v)
  printf 'Require Import %s.\nPrint Assumptions %s.\n' "$FILE" "$theorem" > "$chk"
  out=$(coqc -q "$chk" 2>/dev/null)
  rm -f "$chk" "${chk%.v}.vo" "${chk%.v}.glob" ".${chk%.v}.aux" 2>/dev/null || true
  if echo "$out" | grep -q "Closed under the global context"; then
    echo "axiom-free  $theorem"
  else
    echo "NOT-CLOSED  $theorem -> $out"
    exit 1
  fi
done

echo "CLAY P2 FORMAL NEGATIVE CONTROLS PASS"
