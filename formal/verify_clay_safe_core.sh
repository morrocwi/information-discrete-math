#!/usr/bin/env bash
# Compile the shared finite-obstruction safe core and verify every promoted
# theorem is closed under the global context.
set -eu
cd "$(dirname "$0")"

FILE="IDM_FiniteObstructionSafeCore"
THEOREMS=(
  strict_margin_pass_sound
  strict_margin_pass_complete
  strict_margin_hold_when_not_strict
  missing_certificate_holds
  gated_pass_requires_certificate_and_margin
  error_budget_monotone
  error_budget_additive
  finite_chain_budget_composition
  compatibility_two_step
  symmetry_transport_pass
  verified_local_defect_sound
)

cleanup() {
  rm -f "${FILE}.vo" "${FILE}.glob" "${FILE}.vos" "${FILE}.vok" ".${FILE}.aux" ./chk_clay_*.v ./chk_clay_*.vo ./chk_clay_*.glob ./.*chk_clay_*.aux 2>/dev/null || true
}
trap cleanup EXIT
cleanup

echo "== Clay safe core: forbidden proof escapes =="
if grep -nE "Admitted|Axiom |^Axiom|Parameter |\\badmit\\b" "${FILE}.v"; then
  echo "FOUND forbidden proof escape"
  exit 1
fi

echo "== Clay safe core: compile =="
coqc -q "${FILE}.v"

echo "== Clay safe core: Print Assumptions =="
for theorem in "${THEOREMS[@]}"; do
  chk=$(mktemp chk_clay_XXXXXX.v)
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

echo "CLAY SAFE CORE PASS"
