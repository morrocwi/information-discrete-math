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

from .solve import solve
from .results import Result
from . import discovery

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


def run(op: str, **params) -> Result:
    """Route a high-level ``op`` (see :func:`ops`) with its ``params`` to the matching solver kind and
    return a :class:`idm.results.Result`. The result always carries ``route = {"op", "kind"}``. On an
    unknown op or a HOLD, the Result carries a structured ``error_code`` (``UNKNOWN_OP`` /
    ``MISSING_PARAM`` / ``SOLVER_HOLD``); an unknown op also gets a ``did_you_mean`` suggestion and the
    full op list. Extra kwargs pass straight through to the problem dict (advanced options preserved)."""
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
    kind = _OPS[op]["kind"]
    res = solve({"kind": kind, **params})            # forward verbatim — no math, no tier change here
    out = Result(res)
    out["route"] = {"op": op, "kind": kind}
    if out.is_hold:
        reason = out.get("reason", "")
        out.setdefault("error_code",
                       "MISSING_PARAM" if reason.startswith("missing required field") else "SOLVER_HOLD")
    return out


__all__ = ["run", "ops", "op_names"]
