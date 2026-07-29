"""idm.ai — the AI Gateway (Track C, Phase A): a small, deterministic ENTRANCE over the full solver.

A small model (or a human who doesn't want to memorize 269 kind names) drives the solver through a
handful of high-level operations instead of the full registry:

    idm.ai.run("factor", n=360360)          # -> Result, routed to kind "factorize"
    idm.ai.run("roots", coeffs=[-2,0,0,1])  # -> Result, routed to kind "all_roots"
    idm.ai.ops()                            # the ~11 operations + their kind, params, tier

Design principles (from the roadmap — this is an entrance, NEVER a capability reduction):
  * The full ``idm.solve`` registry (all 269 kinds) stays reachable and is the documented escalation
    path — the gateway covers the common ~11 ops, not the whole surface.
  * The route is always exposed: every result carries ``route = {"op", "kind"}`` so the caller sees
    exactly which kind ran.
  * Advanced options pass straight through (any extra kwarg becomes a field on the problem dict).
  * Tiers are never silently downgraded — the gateway does no math; it forwards to ``idm.solve`` and
    returns that verdict and tier verbatim.
  * Failures are structured with an ``error_code`` (``UNKNOWN_OP`` / ``MISSING_PARAM`` /
    ``SOLVER_HOLD``) and, for an unknown op, a ``did_you_mean`` suggestion — so a model can recover
    deterministically instead of guessing.

Phases B (a learned/expression-classifying router that picks the op from free-form input) and C
(a synthetic tool-use dataset + a benchmark against a real 0.5B model) are declared later increments;
Phase A is the deterministic op layer only.
"""
from __future__ import annotations

import difflib
from typing import List

from .solve import solve, _REG
from .results import Result
from . import discovery
from .parse import parse


def _raw_kind_plan(kind, params, source):
    """Plan for a kind OUTSIDE the gateway's ops (op=None) — still routable (never a capability
    reduction), but HOLD if the kind isn't in the registry at all."""
    if kind not in _REG:
        return {"status": "HOLD", "error_code": "UNKNOWN_KIND", "source": source,
                "reason": f"unknown kind {kind!r} (see idm.kinds())"}
    return {"status": "ready", "route": {"op": None, "kind": kind},
            "problem": {"kind": kind, **params}, "source": source,
            "note": "kind is outside the gateway's ops; run via idm.solve({'kind': ...})."}

# The high-level operation vocabulary: a friendly op name -> the registry kind it routes to, with a
# one-line description. Deterministic dictionary routing — no model, no guessing. Kept small (the whole
# point is to shrink the decision space); everything else is reachable via idm.solve (see run()'s HOLD).
_OPS = {
    "factor":         {"kind": "factorize",          "about": "prime-factorize an integer n"},
    "gcd":            {"kind": "gcd",                 "about": "greatest common divisor of integers a, b"},
    "integrate":      {"kind": "integral",           "about": "certified definite integral of f over [a, b]"},
    "integrate_exact":{"kind": "integrate_rational", "about": "exact symbolic ∫ of a rational function num/den"},
    "roots":          {"kind": "all_roots",          "about": "all real+complex roots of a ℚ-polynomial (coeffs low→high)"},
    "solve_linear":   {"kind": "matrix_solve",       "about": "complete exact ℚ solution set of A x = b"},
    "eigenvalues":    {"kind": "eigenvalues",        "about": "eigenvalues of a rational matrix"},
    "determinant":    {"kind": "matrix_determinant", "about": "exact determinant of a rational matrix"},
    "ode":            {"kind": "linear_ode",         "about": "exact general solution of a linear constant-coeff ODE (char coeffs low→high)"},
    "limit":          {"kind": "rational_limit",     "about": "exact limit of a rational function num/den at a point"},
    "shortest_path":  {"kind": "shortest_path",      "about": "all-pairs shortest paths over a weight matrix"},
}


def ops() -> List[dict]:
    """The gateway's operation vocabulary — one entry per high-level op with its target ``kind``, a
    one-line ``about``, the parameter ``fields`` (from :func:`idm.schema`), and the honest ``tier``.
    This is the small, central schema a model reasons over instead of the full 269-kind registry."""
    out = []
    for op, spec in _OPS.items():
        kind = spec["kind"]
        s = discovery.schema(kind)
        out.append({"op": op, "kind": kind, "about": spec["about"],
                    "fields": s["fields"], "tier": s["tier"]})
    return out


def op_names() -> List[str]:
    """Just the op names (the ~11-element decision space)."""
    return list(_OPS)


def run(op: str, dry_run: bool = False, **params) -> Result:
    """Route a high-level ``op`` (see :func:`ops`) with its ``params`` to the matching solver kind and
    return a :class:`idm.results.Result`. The result always carries ``route = {"op", "kind"}``. On an
    unknown op or a HOLD, the Result carries a structured ``error_code`` (``UNKNOWN_OP`` /
    ``MISSING_PARAM`` / ``SOLVER_HOLD``); an unknown op also gets a ``did_you_mean`` suggestion and the
    full op list. Extra kwargs pass straight through to the problem dict (advanced options preserved).

    ``dry_run=True`` returns the PLAN (:func:`plan`) — the route + the exact problem dict that WOULD be
    solved, plus a heuristic field check — WITHOUT executing. Lets a model preview/validate its call."""
    if op not in _OPS:
        suggestion = difflib.get_close_matches(op, _OPS, n=1)
        return Result({
            "status": "HOLD", "error_code": "UNKNOWN_OP",
            "reason": f"unknown gateway op {op!r}",
            "did_you_mean": suggestion[0] if suggestion else None,
            "ops": op_names(),
            "escalate": "for kinds outside the gateway's ~11 ops, call idm.solve({'kind': ...}) directly "
                        "— the full 269-kind registry is always reachable (idm.kinds()).",
        })
    if dry_run:
        return Result(plan(op, **params))            # plan → validate → (execute) — stop after validate
    kind = _OPS[op]["kind"]
    res = solve({"kind": kind, **params})            # forward verbatim — no math, no tier change here
    out = Result(res)
    out["route"] = {"op": op, "kind": kind}
    if out.is_hold:
        reason = out.get("reason", "")
        out.setdefault("error_code",
                       "MISSING_PARAM" if reason.startswith("missing required field") else "SOLVER_HOLD")
    return out


def plan(op: str, **params) -> dict:
    """The PLAN for an op call, WITHOUT executing (the validate step of plan→validate→execute): the
    route, the exact ``problem`` dict that would be solved, and a HEURISTIC field check. ``status`` is
    ``"ready"`` (all known parameter fields supplied) or ``"needs_params"`` (some are missing). Because
    the registry does not declare which fields are required vs optional, ``missing`` lists schema fields
    not supplied and is advisory — a call can still succeed without an "optional" one, so ``run`` is the
    ground truth. An unknown op returns ``status="HOLD"`` with ``error_code="UNKNOWN_OP"``."""
    if op not in _OPS:
        suggestion = difflib.get_close_matches(op, _OPS, n=1)
        return {"status": "HOLD", "error_code": "UNKNOWN_OP", "op": op,
                "did_you_mean": suggestion[0] if suggestion else None, "ops": op_names()}
    kind = _OPS[op]["kind"]
    s = discovery.schema(kind)
    missing = [f for f in s["required"] if f not in params]        # only truly-required (p["x"]) fields
    return {"status": "ready" if not missing else "needs_params",
            "route": {"op": op, "kind": kind}, "problem": {"kind": kind, **params},
            "required": s["required"], "optional": s["optional"], "missing": missing,
            "note": "the required/missing split is heuristic (from handler source); run() is the ground truth.",
            "dry_run": True}


def route(request) -> dict:
    """Deterministically map a free-form or structured ``request`` to a plan (the domain router +
    expression classifier). Accepts:
      * a **string** — translated by :func:`idm.parse` (rule-based world-language → problem dict), then
        the resulting kind is mapped back to a gateway op when one exists;
      * a **dict with ``"op"``** — planned directly;
      * a **dict with ``"kind"``** — mapped to a gateway op when one exists (else routed as a raw kind).
    Returns a plan dict (as :func:`plan`) augmented with ``source``; ``status="HOLD"`` when the request
    can't be classified. This does no NL magic beyond ``idm.parse`` and reports honestly when unsure."""
    if isinstance(request, str):
        parsed = parse(request)
        if not isinstance(parsed, dict) or parsed.get("status") == "HOLD" or "kind" not in parsed:
            return {"status": "HOLD", "error_code": "UNCLASSIFIED", "source": request,
                    "reason": "could not translate the request to a known problem (idm.parse HELD)",
                    "ops": op_names()}
        kind = parsed["kind"]
        params = {k: v for k, v in parsed.items() if not k.startswith("_") and k != "kind"}
        op = _KIND_TO_OP.get(kind)
        if op:
            out = plan(op, **params); out["source"] = request; return out
        return _raw_kind_plan(kind, params, request)
    if isinstance(request, dict):
        if "op" in request:
            p = {k: v for k, v in request.items() if k != "op"}
            out = plan(request["op"], **p); out["source"] = request; return out
        if "kind" in request:
            kind = request["kind"]
            params = {k: v for k, v in request.items() if k != "kind"}
            op = _KIND_TO_OP.get(kind)
            if op:
                out = plan(op, **params); out["source"] = request; return out
            return _raw_kind_plan(kind, params, request)
    return {"status": "HOLD", "error_code": "UNCLASSIFIED", "source": request,
            "reason": "request must be a string, a {'op': ...} dict, or a {'kind': ...} dict", "ops": op_names()}


# reverse index kind -> op, for route() to map a parsed/structured kind back to a gateway op
_KIND_TO_OP = {spec["kind"]: op for op, spec in _OPS.items()}


__all__ = ["run", "ops", "op_names", "plan", "route"]
