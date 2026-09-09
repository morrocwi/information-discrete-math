"""IDM Physics — lineage-preserving physics adapters over :func:`idm.solve`.

This module does not introduce a second numerical engine.  It is a thin, fail-closed
physics facade over the existing IDM solver kinds.  Every registered physics adapter
must declare the equation lineage fields

    toledo_root / equation_parent / derivation_tier

before it can be used.  Physics results echo those fields so the equation river does
not disappear at the API boundary.

Computational policy
--------------------
The physics layer is discrete-native.  A continuum law may be the source description
of a model, but an adapter must translate it to a declared finite computation before
execution.  The registry therefore records ``continuum_primitive=False`` for every
adapter admitted here.

Current model
-------------
``navier_stokes`` is the first physics model.  Its finite Fourier-Galerkin dynamics are
derived from Navier--Stokes itself.  Toledo supplies the retained-operator structural
lineage; Toledo is *not* claimed to be the source of the Navier--Stokes dynamics.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from .results import Result

_REQUIRED_LINEAGE = ("toledo_root", "equation_parent", "derivation_tier")


@dataclass(frozen=True)
class PhysicsAdapter:
    model: str
    readout: str
    kind: str
    toledo_root: str
    equation_parent: str
    derivation_tier: str
    source_equation: str
    equation_parent_alias: Optional[str] = None
    lineage_note: str = ""
    continuum_primitive: bool = False
    computation_semantics: str = "finite_discrete"

    def __post_init__(self):
        for name in _REQUIRED_LINEAGE:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"physics adapter requires non-empty {name}")
        if self.continuum_primitive:
            raise ValueError("IDM Physics adapters may not declare the continuum as a computation primitive")
        if self.computation_semantics != "finite_discrete":
            raise ValueError("IDM Physics currently admits only computation_semantics='finite_discrete'")

    def metadata(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


_REGISTRY: Dict[Tuple[str, str], PhysicsAdapter] = {}
_MODEL_ALIASES = {
    "ns": "navier_stokes",
    "navier-stokes": "navier_stokes",
    "navier_stokes": "navier_stokes",
    "navierstokes": "navier_stokes",
}
_READOUT_ALIASES = {
    "mode": "fourier_mode",
    "fourier": "fourier_mode",
    "fourier_mode": "fourier_mode",
    "point": "point_velocity",
    "velocity": "point_velocity",
    "point_velocity": "point_velocity",
    "physical_velocity": "point_velocity",
    "plane": "plane_average_velocity",
    "plane_average": "plane_average_velocity",
    "plane_average_velocity": "plane_average_velocity",
    "harmonic": "harmonic_probe",
    "harmonic_probe": "harmonic_probe",
    "harmonic_velocity_correlation": "harmonic_probe",
}


def _norm_model(model: str) -> str:
    key = str(model).strip().lower().replace(" ", "_")
    return _MODEL_ALIASES.get(key, key)


def _norm_readout(readout: str) -> str:
    key = str(readout).strip().lower().replace(" ", "_")
    return _READOUT_ALIASES.get(key, key)


def register_adapter(adapter: PhysicsAdapter) -> PhysicsAdapter:
    """Register one physics adapter after validating mandatory equation lineage.

    Duplicate ``(model, readout)`` registrations are rejected rather than silently
    overwritten; the equation river must have one explicit active route per readout.
    """
    if not isinstance(adapter, PhysicsAdapter):
        raise TypeError("adapter must be a PhysicsAdapter")
    key = (_norm_model(adapter.model), _norm_readout(adapter.readout))
    if key in _REGISTRY:
        raise ValueError(f"physics adapter already registered for {key[0]}/{key[1]}")
    _REGISTRY[key] = adapter
    return adapter


def adapters() -> tuple:
    """Return immutable metadata records for all registered physics adapters."""
    return tuple(_REGISTRY[k].metadata() for k in sorted(_REGISTRY))


def models() -> dict:
    """Return ``{model: [readouts...]}`` for the admitted physics surface."""
    out: Dict[str, list] = {}
    for model, readout in sorted(_REGISTRY):
        out.setdefault(model, []).append(readout)
    return out


def describe(model: str, readout: Optional[str] = None):
    """Describe one model or one concrete readout adapter."""
    m = _norm_model(model)
    if readout is None:
        rows = [a.metadata() for (mm, _), a in sorted(_REGISTRY.items()) if mm == m]
        if not rows:
            return {"status": "HOLD", "reason": f"unknown physics model '{model}'", "known_models": sorted(models())}
        return {"status": "ok", "model": m, "adapters": rows}
    r = _norm_readout(readout)
    adapter = _REGISTRY.get((m, r))
    if adapter is None:
        return {"status": "HOLD", "reason": f"unknown physics adapter '{m}/{r}'",
                "known_readouts": models().get(m, [])}
    return {"status": "ok", **adapter.metadata()}


def solve(problem: Optional[Mapping[str, Any]] = None, /, *, model: Optional[str] = None,
          readout: Optional[str] = None, state: Any = None, horizon: Optional[int] = None,
          **params) -> Result:
    """Solve a physics readout through a lineage-preserving adapter.

    Accepted forms::

        physics.solve({"model": "navier_stokes", "readout": "fourier_mode", ...})
        physics.solve(model="navier_stokes", readout="harmonic_probe", K=3, ...)

    ``state`` is forwarded as ``initial_state``.  The selected adapter dispatches to the
    already-registered ``idm.solve`` kind; this layer does not duplicate the solver.
    """
    data: Dict[str, Any] = {}
    if problem is not None:
        if not isinstance(problem, Mapping):
            return Result({"kind": "physics", "status": "HOLD",
                           "reason": "physics problem must be a mapping"})
        data.update(dict(problem))
    data.update(params)
    if model is not None:
        data["model"] = model
    if readout is not None:
        data["readout"] = readout
    if state is not None:
        if "initial_state" in data:
            return Result({"kind": "physics", "status": "HOLD",
                           "reason": "provide state or initial_state, not both"})
        data["initial_state"] = state
    if horizon is not None:
        data["horizon"] = horizon

    if "model" not in data or "readout" not in data:
        return Result({"kind": "physics", "status": "HOLD",
                       "reason": "physics.solve requires model and readout",
                       "known_models": models()})

    m = _norm_model(data.pop("model"))
    r = _norm_readout(data.pop("readout"))
    adapter = _REGISTRY.get((m, r))
    if adapter is None:
        return Result({"kind": "physics", "status": "HOLD",
                       "reason": f"unknown physics adapter '{m}/{r}'",
                       "known_readouts": models().get(m, []),
                       "known_models": sorted(models())})

    # The physics facade owns the kind; callers cannot route around its registered lineage.
    data.pop("kind", None)
    data["kind"] = adapter.kind

    # Lazy import avoids a package-initialization cycle while keeping idm.solve the one engine.
    from .solve import solve as idm_solve
    raw = idm_solve(data)
    out = Result(dict(raw))
    out["physics_model"] = m
    out["physics_readout"] = r
    out["physics_adapter_kind"] = adapter.kind
    out["toledo_root"] = adapter.toledo_root
    out["equation_parent"] = adapter.equation_parent
    if adapter.equation_parent_alias:
        out["equation_parent_alias"] = adapter.equation_parent_alias
    out["derivation_tier"] = adapter.derivation_tier
    out["source_equation"] = adapter.source_equation
    out["continuum_primitive"] = False
    out["computation_semantics"] = adapter.computation_semantics
    out["lineage_note"] = adapter.lineage_note
    out["equation_lineage"] = {
        "toledo_root": adapter.toledo_root,
        "equation_parent": adapter.equation_parent,
        "equation_parent_alias": adapter.equation_parent_alias,
        "derivation_tier": adapter.derivation_tier,
        "source_equation": adapter.source_equation,
        "note": adapter.lineage_note,
    }
    return out


_NS_COMMON = dict(
    model="navier_stokes",
    toledo_root="root/EQ-008",
    equation_parent="PROP-URCF-01",
    equation_parent_alias="EQ-URCF-TURB-004",
    derivation_tier="derived_finite_galerkin",
    source_equation="periodic incompressible Navier-Stokes -> declared finite Fourier-Galerkin dynamics",
    lineage_note=(
        "Navier-Stokes supplies the physical dynamics. Toledo root/EQ-008 and PROP-URCF-01 supply "
        "the retained-operator structural lineage; this is a structural adapter, not a claim that "
        "Navier-Stokes was derived from Toledo."
    ),
)

register_adapter(PhysicsAdapter(readout="fourier_mode", kind="ns_retained_rk4", **_NS_COMMON))
register_adapter(PhysicsAdapter(readout="point_velocity", kind="ns_retained_physical", **_NS_COMMON))
register_adapter(PhysicsAdapter(readout="plane_average_velocity", kind="ns_retained_plane_average", **_NS_COMMON))
register_adapter(PhysicsAdapter(readout="harmonic_probe", kind="ns_retained_harmonic_probe", **_NS_COMMON))


__all__ = ["PhysicsAdapter", "register_adapter", "adapters", "models", "describe", "solve"]
