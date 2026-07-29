"""idm.discovery — programmatic schema/kind discovery over the solver registry.

The same introspection the ``python -m idm`` CLI does, but returning STRUCTURED data (dicts) so a
programmer (or a small model driving the solver) can ask, in Python:

    idm.describe("factorize")   # {kind, tier, coq_theorem?, handler, signature, doc, verify}
    idm.schema("factorize")     # {kind, tier, fields, example} — fields is a best-effort read of the
                                #   parameter names the handler accesses (p["..."]) — honestly heuristic
    idm.example("linear_ode")   # a real problem dict, as a string, pulled from tests/ if one is on file

This layer invents no metadata the registry does not have. The registry carries a handler + a tier per
kind; parameter *names* are not formally declared anywhere, so :func:`schema` derives them heuristically
from the handler source and (preferably) from a real on-file example — it never fabricates a schema.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path
from typing import Optional

from .solve import _REG, _COQ_BACKED


def _effective_tier(name: str) -> str:
    """The HONEST tier :func:`idm.solve` actually returns for ``name`` — a registry ``Th_coqc`` tag is
    kept only for kinds with a named machine-checked theorem (``_COQ_BACKED``); every other
    ``Th_coqc``-tagged handler downgrades to ``exact``."""
    tier = _REG[name][1] if name in _REG else "?"
    if tier == "Th_coqc" and name not in _COQ_BACKED:
        return "exact"
    return tier


def _repo_root() -> Path:
    """Best-effort source root (parent of the ``idm`` package). A pip-installed wheel ships no
    ``tests/``, so example lookup honestly returns ``None`` there rather than fabricating one."""
    return Path(__file__).resolve().parent.parent


def _find_example(name: str) -> Optional[str]:
    """A real ``{"kind": name, ...}`` problem dict found verbatim in ``tests/`` or ``examples/``, as a
    one-line string with its source path, or ``None`` if none is on file."""
    root = _repo_root()
    pattern = re.compile(r'\{[^{}]*"kind"\s*:\s*"' + re.escape(name) + r'"[^{}]*\}', re.DOTALL)
    for d in (root / "tests", root / "examples"):
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            m = pattern.search(text)
            if m:
                snippet = re.sub(r"\s+", " ", m.group(0)).strip()
                return f"{snippet}    # from {path.relative_to(root)}"
    return None


def _field_access(name: str):
    """Heuristically split the handler's parameter reads into (required, optional): a subscript read
    ``p["x"]`` raises ``KeyError`` when absent → treated REQUIRED; a ``p.get("x")`` has a default →
    OPTIONAL. Both are best-effort from source (a field read only inside a branch may be conditional,
    dynamically-built keys are invisible), so this is a guide, not a contract. Returns two sorted lists."""
    fn = _REG[name][0]
    try:
        src = inspect.getsource(fn)
    except (OSError, TypeError):
        return [], []
    optional = set(re.findall(r'\bp\.get\(\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']', src))
    required = set(re.findall(r'\bp\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]', src)) - optional
    return sorted(required), sorted(optional)


def _handler_fields(name: str) -> list:
    """All parameter names the handler reads (required ∪ optional), sorted. Heuristic — see
    :func:`_field_access`."""
    req, opt = _field_access(name)
    return sorted(set(req) | set(opt))


def describe(kind: str) -> dict:
    """A structured description of one kind: ``{kind, tier, coq_theorem?, handler, signature, doc,
    verify}``. Raises ``KeyError`` for an unknown kind (mirrors a dict lookup)."""
    if kind not in _REG:
        raise KeyError(f"unknown kind {kind!r} (see idm.kinds())")
    fn, reg_tier = _REG[kind]
    tier = _effective_tier(kind)
    try:
        signature = str(inspect.signature(fn))
    except (TypeError, ValueError):
        signature = "(signature unavailable)"
    out = {"kind": kind, "tier": tier, "handler": fn.__qualname__, "signature": signature,
           "doc": inspect.getdoc(fn), "verify": f"pytest tests/ -k {kind}"}
    if reg_tier == "Th_coqc" and kind in _COQ_BACKED:
        out["coq_theorem"] = _COQ_BACKED[kind]
    elif reg_tier != tier:
        out["note"] = f"registry default {reg_tier!r} downgrades to {tier!r} (no per-kind Coq witness)"
    return out


def schema(kind: str) -> dict:
    """A best-effort input schema: ``{kind, tier, fields, example}``. ``fields`` is the heuristic list
    of parameter names the handler reads (see :func:`_handler_fields`); ``example`` is a real on-file
    example dict string if one exists. Honestly derived — parameter names are not formally declared in
    this repo, so treat ``fields`` as a guide, not a contract."""
    if kind not in _REG:
        raise KeyError(f"unknown kind {kind!r} (see idm.kinds())")
    required, optional = _field_access(kind)
    return {"kind": kind, "tier": _effective_tier(kind),
            "fields": sorted(set(required) | set(optional)),
            "required": required, "optional": optional, "example": _find_example(kind)}


def example(kind: str) -> Optional[str]:
    """A real ``{"kind": kind, ...}`` example problem dict (as a string, with its source path) pulled
    from ``tests/``/``examples/``, or ``None`` if none is on file. Raises ``KeyError`` for an unknown
    kind."""
    if kind not in _REG:
        raise KeyError(f"unknown kind {kind!r} (see idm.kinds())")
    return _find_example(kind)


__all__ = ["describe", "schema", "example"]
