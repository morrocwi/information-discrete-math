#!/usr/bin/env bash
# Focused verification for the P-vs-NP readout research lane.
# This supplements formal/verify.sh while the lane remains a draft PR.
set -euo pipefail
cd "$(dirname "$0")"

clean() {
  rm -f IDM_DeclarationBound.vo IDM_DeclarationBound.glob .IDM_DeclarationBound.aux \
        IDM_SATIntervention.vo IDM_SATIntervention.glob .IDM_SATIntervention.aux \
        IDM_FutureReadoutWidth.vo IDM_FutureReadoutWidth.glob .IDM_FutureReadoutWidth.aux \
        IDM_TransformPotential.vo IDM_TransformPotential.glob .IDM_TransformPotential.aux \
        IDM_FusionDual.vo IDM_FusionDual.glob .IDM_FusionDual.aux \
        IDM_CircuitGenesisBridge.vo IDM_CircuitGenesisBridge.glob .IDM_CircuitGenesisBridge.aux \
        IDM_RetainRecomputeResolve.vo IDM_RetainRecomputeResolve.glob .IDM_RetainRecomputeResolve.aux \
        IDM_CircuitLedgerTransfer.vo IDM_CircuitLedgerTransfer.glob .IDM_CircuitLedgerTransfer.aux \
        IDM_RRRCostLowerBound.vo IDM_RRRCostLowerBound.glob .IDM_RRRCostLowerBound.aux \
        IDM_DemandCircuitDominance.vo IDM_DemandCircuitDominance.glob .IDM_DemandCircuitDominance.aux \
        IDM_ReadoutUniverseAccessibleCompletion.vo IDM_ReadoutUniverseAccessibleCompletion.glob .IDM_ReadoutUniverseAccessibleCompletion.aux \
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

out_potential=$(coqc -q IDM_TransformPotential.v)
printf '%s\n' "$out_potential"
count_potential=$(printf '%s\n' "$out_potential" | grep -c "Closed under the global context" || true)
if [ "$count_potential" -lt 3 ]; then
  echo "Expected three axiom-free transform-potential Print Assumptions results; got $count_potential" >&2
  exit 1
fi

out_dual=$(coqc -q IDM_FusionDual.v)
printf '%s\n' "$out_dual"
count_dual=$(printf '%s\n' "$out_dual" | grep -c "Closed under the global context" || true)
if [ "$count_dual" -lt 4 ]; then
  echo "Expected four axiom-free fusion-dual Print Assumptions results; got $count_dual" >&2
  exit 1
fi

out_cgsl=$(coqc -q IDM_CircuitGenesisBridge.v)
printf '%s\n' "$out_cgsl"
count_cgsl=$(printf '%s\n' "$out_cgsl" | grep -c "Closed under the global context" || true)
if [ "$count_cgsl" -lt 6 ]; then
  echo "Expected six axiom-free CGSL Print Assumptions results; got $count_cgsl" >&2
  exit 1
fi

out_rrr=$(coqc -q IDM_RetainRecomputeResolve.v)
printf '%s\n' "$out_rrr"
count_rrr=$(printf '%s\n' "$out_rrr" | grep -c "Closed under the global context" || true)
if [ "$count_rrr" -lt 6 ]; then
  echo "Expected six axiom-free RRR Print Assumptions results; got $count_rrr" >&2
  exit 1
fi

out_transfer=$(coqc -q IDM_CircuitLedgerTransfer.v)
printf '%s\n' "$out_transfer"
count_transfer=$(printf '%s\n' "$out_transfer" | grep -c "Closed under the global context" || true)
if [ "$count_transfer" -lt 3 ]; then
  echo "Expected three axiom-free transfer Print Assumptions results; got $count_transfer" >&2
  exit 1
fi

out_rrr_cost=$(coqc -q IDM_RRRCostLowerBound.v)
printf '%s\n' "$out_rrr_cost"
count_rrr_cost=$(printf '%s\n' "$out_rrr_cost" | grep -c "Closed under the global context" || true)
if [ "$count_rrr_cost" -lt 3 ]; then
  echo "Expected three axiom-free RRR-cost Print Assumptions results; got $count_rrr_cost" >&2
  exit 1
fi

out_dominance=$(coqc -q IDM_DemandCircuitDominance.v)
printf '%s\n' "$out_dominance"
count_dominance=$(printf '%s\n' "$out_dominance" | grep -c "Closed under the global context" || true)
if [ "$count_dominance" -lt 3 ]; then
  echo "Expected three axiom-free demand-dominance Print Assumptions results; got $count_dominance" >&2
  exit 1
fi

out_ru_completion=$(coqc -q IDM_ReadoutUniverseAccessibleCompletion.v)
printf '%s\n' "$out_ru_completion"
count_ru_completion=$(printf '%s\n' "$out_ru_completion" | grep -c "Closed under the global context" || true)
if [ "$count_ru_completion" -lt 4 ]; then
  echo "Expected four axiom-free Readout-Universe completion Print Assumptions results; got $count_ru_completion" >&2
  exit 1
fi

echo "P-vs-NP readout witnesses: compiled + axiom-free"
