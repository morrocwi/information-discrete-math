"""idm.rcp — the Retained Contraction Protocol (the compute-savings layer).

A fail-closed finite-information contract around a tensor/factor contraction: declared boundary,
resource ledger, tolerance, lineage, preservation witness, ACCEPT/HOLD/BLOCK. (Re-export of the
verified `tools/retained_contraction_protocol.py` and the energy/burden extensions.)
"""
from . import _bridge  # noqa: F401
import retained_contraction_protocol as _rcp
import retained_burden_algebra as _burden

plan_contraction = _rcp.plan_contraction
RCPDeclaration = _rcp.RCPDeclaration
RetainedFactor = _rcp.RetainedFactor
retain_lesser = _burden.retain_lesser

try:
    import retained_energy_protocol as energy   # noqa: F401  (submodule: idm.rcp.energy)
except Exception:  # pragma: no cover
    energy = None
