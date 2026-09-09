"""Readout Genesis bridge contract for IDM Physics.

This module makes the architectural connection to Readout Genesis explicit and
machine-checkable without pretending that an IDM physics adapter is already a
registered Readout Genesis domain.

Readout Genesis v1.2 requires the order

    Retention -> Structure -> Translation -> Meaning -> Report

and, for a domain, requires sufficiency / quotient / dynamics / readout gates plus
explicit accounting for information loss.  IDM Physics therefore stores a bounded
Genesis link on every adapter and refuses incomplete links.

Registration status is intentionally separate from mapping status:
- MAPPED_NOT_REGISTERED: the adapter has an explicit Genesis-compatible mapping,
  but no completed domain-registration bundle has been admitted in readout_genesis.
- REGISTERED: may be used only when an external Readout Genesis domain release exists
  and its checker/registration gates have passed.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

GENESIS_PIPELINE = (
    "Retention",
    "Structure",
    "Translation",
    "Meaning",
    "Report",
)

_ALLOWED_REGISTRATION_STATUS = {"MAPPED_NOT_REGISTERED", "REGISTERED"}
_REQUIRED_FIELDS = (
    "genesis_root",
    "genesis_domain",
    "quotient",
    "translation_tier",
    "claim_boundary",
    "drift_contract",
    "verification_bundle",
)


@dataclass(frozen=True)
class GenesisLink:
    """Bounded Readout Genesis metadata attached to one physics adapter."""

    genesis_root: str
    genesis_domain: str
    quotient: str
    translation_tier: str
    claim_boundary: str
    drift_contract: str
    verification_bundle: str
    registration_status: str = "MAPPED_NOT_REGISTERED"
    domain_release_path: Optional[str] = None
    encoding_status: str = "FINITE_CALIBRATED_FOR_DECLARED_SOLVER_READOUTS_ONLY"
    loss_accounting: str = "declared_by_adapter_and_solver_result"
    pipeline: tuple = GENESIS_PIPELINE

    def __post_init__(self):
        for name in _REQUIRED_FIELDS:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Genesis link requires non-empty {name}")
        if self.registration_status not in _ALLOWED_REGISTRATION_STATUS:
            raise ValueError(
                "Genesis registration_status must be MAPPED_NOT_REGISTERED or REGISTERED"
            )
        if tuple(self.pipeline) != GENESIS_PIPELINE:
            raise ValueError("Genesis pipeline order may not be changed")
        if self.registration_status == "REGISTERED" and not self.domain_release_path:
            raise ValueError(
                "REGISTERED Genesis links require a concrete domain_release_path"
            )

    def metadata(self) -> dict:
        d = asdict(self)
        d["pipeline"] = list(self.pipeline)
        return d


def validate_result_lineage(result: dict, link: GenesisLink) -> dict:
    """Return a compact Genesis conformance record for one physics result.

    This is structural conformance of the adapter/result boundary, not a claim that
    the physical domain has passed Readout Genesis registration.
    """
    missing = [
        key for key in (
            "physics_model",
            "physics_readout",
            "toledo_root",
            "equation_parent",
            "derivation_tier",
            "continuum_primitive",
            "computation_semantics",
        )
        if key not in result
    ]
    defects = []
    if missing:
        defects.append("missing_result_lineage:" + ",".join(missing))
    if result.get("continuum_primitive") is not False:
        defects.append("continuum_used_as_computation_primitive")
    if result.get("computation_semantics") != "finite_discrete":
        defects.append("non_finite_computation_semantics")

    status = "PASS" if not defects else "FAIL"
    return {
        "status": status,
        "registration_status": link.registration_status,
        "pipeline": list(GENESIS_PIPELINE),
        "defects": defects,
        "bounded_claim": (
            "Genesis-compatible adapter/result lineage only; domain registration is not implied"
            if link.registration_status != "REGISTERED"
            else "registered Genesis domain lineage plus IDM finite execution"
        ),
    }


__all__ = [
    "GENESIS_PIPELINE",
    "GenesisLink",
    "validate_result_lineage",
]
