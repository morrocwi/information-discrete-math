#!/usr/bin/env bash
# Focused verification for the P-vs-NP readout research lane.
# This supplements formal/verify.sh while the lane remains a draft PR.
set -euo pipefail
cd "$(dirname "$0")"

clean() {
  rm -f IDM_DeclarationBound.vo IDM_DeclarationBound.glob .IDM_DeclarationBound.aux \
        IDM_SATIntervention.vo IDM_SATIntervention.glob .IDM_SATIntervention.aux \
        IDM_FutureReadoutWidth.vo IDM_FutureReadoutWidth.glob .IDM_FutureReadoutWidth.aux \
        2>/dev/null || true
}
trap clean EXIT
clean

coqc -q IDM_DeclarationBound.v >/dev/null

out_intervention=$(coqc -q IDM_SATIntervention.v)
printf '%s\n' "$out_intervention"
count_intervention=$(printf '%s\n' "$out_intervention" | grep -c "Closed under the global context" || true)
if [ "$count_intervention" -lt 2 ]; then
  echo "Expected two axiom-free intervention Print Assumptions results; got $count_intervention" >&2
  exit 1
fi

out_width=$(coqc -q IDM_FutureReadoutWidth.v)
printf '%s\n' "$out_width"
count_width=$(printf '%s\n' "$out_width" | grep -c "Closed under the global context" || true)
if [ "$count_width" -lt 7 ]; then
  echo "Expected seven axiom-free width Print Assumptions results; got $count_width" >&2
  exit 1
fi

echo "P-vs-NP readout witnesses: compiled + axiom-free"
