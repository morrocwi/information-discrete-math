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
        IDM_FreeRereadGuard.vo IDM_FreeRereadGuard.glob .IDM_FreeRereadGuard.aux \
        IDM_ExistentialProjection.vo IDM_ExistentialProjection.glob .IDM_ExistentialProjection.aux \
        IDM_ResidualCoverCapacity.vo IDM_ResidualCoverCapacity.glob .IDM_ResidualCoverCapacity.aux \
        IDM_ProjectionCollapseGuard.vo IDM_ProjectionCollapseGuard.glob .IDM_ProjectionCollapseGuard.aux \
        IDM_SATRestrictionDefect.vo IDM_SATRestrictionDefect.glob .IDM_SATRestrictionDefect.aux \
        IDM_SATOneSidedAudit.vo IDM_SATOneSidedAudit.glob .IDM_SATOneSidedAudit.aux \
        IDM_CompressedNegativeClosure.vo IDM_CompressedNegativeClosure.glob .IDM_CompressedNegativeClosure.aux \
        2>/dev/null || true
}
trap clean EXIT
clean

coqc -q IDM_DeclarationBound.v >/dev/null

check_closed() {
  local file="$1"
  local expected="$2"
  local label="$3"
  local out
  out=$(coqc -q "$file")
  printf '%s\n' "$out"
  local count
  count=$(printf '%s\n' "$out" | grep -c "Closed under the global context" || true)
  if [ "$count" -lt "$expected" ]; then
    echo "Expected $expected axiom-free $label Print Assumptions results; got $count" >&2
    exit 1
  fi
}

check_closed IDM_SATIntervention.v 2 intervention
check_closed IDM_FutureReadoutWidth.v 7 width
check_closed IDM_TransformPotential.v 3 transform-potential
check_closed IDM_FusionDual.v 4 fusion-dual
check_closed IDM_CircuitGenesisBridge.v 6 CGSL
check_closed IDM_RetainRecomputeResolve.v 6 RRR
check_closed IDM_CircuitLedgerTransfer.v 3 transfer
check_closed IDM_RRRCostLowerBound.v 3 RRR-cost
check_closed IDM_DemandCircuitDominance.v 3 demand-dominance
check_closed IDM_ReadoutUniverseAccessibleCompletion.v 4 Readout-Universe-completion
check_closed IDM_FreeRereadGuard.v 3 free-reread-guard
check_closed IDM_ExistentialProjection.v 3 existential-projection
check_closed IDM_ResidualCoverCapacity.v 3 residual-cover-capacity
check_closed IDM_ProjectionCollapseGuard.v 2 projection-collapse-guard
check_closed IDM_SATRestrictionDefect.v 7 SAT-restriction-defect
check_closed IDM_SATOneSidedAudit.v 2 SAT-one-sided-audit
check_closed IDM_CompressedNegativeClosure.v 5 compressed-negative-closure

echo "P-vs-NP readout witnesses: compiled + axiom-free"
