#!/usr/bin/env bash
# Focused verification for the P-vs-NP readout research lane.
# This supplements formal/verify.sh while the lane remains a draft PR.
set -euo pipefail
cd "$(dirname "$0")"

rm -f IDM_DeclarationBound.vo IDM_DeclarationBound.glob .IDM_DeclarationBound.aux \
      IDM_SATIntervention.vo IDM_SATIntervention.glob .IDM_SATIntervention.aux 2>/dev/null || true

coqc -q IDM_DeclarationBound.v >/dev/null
out=$(coqc -q IDM_SATIntervention.v)
printf '%s\n' "$out"

count=$(printf '%s\n' "$out" | grep -c "Closed under the global context" || true)
if [ "$count" -lt 2 ]; then
  echo "Expected two axiom-free Print Assumptions results; got $count" >&2
  exit 1
fi

echo "P-vs-NP intervention witnesses: compiled + axiom-free"

rm -f IDM_DeclarationBound.vo IDM_DeclarationBound.glob .IDM_DeclarationBound.aux \
      IDM_SATIntervention.vo IDM_SATIntervention.glob .IDM_SATIntervention.aux 2>/dev/null || true
