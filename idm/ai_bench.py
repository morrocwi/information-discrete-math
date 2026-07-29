"""idm.ai_bench — Track C Phase C: a synthetic tool-use dataset + a benchmark harness for the gateway.

A small model driving :mod:`idm.ai` has two jobs per request: pick the right **op** and fill the right
**params**. This module provides:

  * :func:`dataset` — a fixed, hand-authored set of (request → expected op / expected solve status)
    cases spanning all 11 gateway ops, plus free-form-string cases and deliberately-unclassifiable
    ones. Deterministic (no randomness — the repo's results must be reproducible).
  * :func:`score` — run any ``router`` callable (request → an op name, or a plan/route dict) over the
    dataset and report op-selection accuracy AND end-to-end solve accuracy, with the per-case failures.
  * :func:`benchmark_router` — score the built-in deterministic router (:func:`idm.ai.route`) as the
    oracle/ceiling; the test suite asserts it is perfect on the structured cases.

To benchmark a REAL 0.5B model, pass a ``router`` that calls the model and returns the op it chose —
the harness is model-agnostic. The committed artifact is the dataset + harness + the deterministic-
router self-test (no model weights are shipped or required to run the self-test).
"""
from __future__ import annotations

from typing import Callable, List, Optional

from . import ai
from .solve import solve


def dataset() -> List[dict]:
    """The synthetic tool-use dataset: each case is ``{request, expect_op, expect_status}`` where
    ``expect_op`` is the gateway op the request should route to (or ``None`` for an unclassifiable one)
    and ``expect_status`` is the status ``idm.solve`` should return for the routed problem (``"ok"`` /
    ``"CERTIFIED"`` / ``"HOLD"`` / ``None`` when there is nothing to solve). Fixed and deterministic."""
    return [
        # structured {op|kind} requests — a competent router must get every one
        {"request": {"op": "factor", "n": 360360}, "expect_op": "factor", "expect_status": "ok"},
        {"request": {"op": "gcd", "a": 48, "b": 36}, "expect_op": "gcd", "expect_status": "ok"},
        {"request": {"op": "roots", "coeffs": [-2, 0, 0, 1]}, "expect_op": "roots", "expect_status": "ok"},
        {"request": {"op": "solve_linear", "A": [[2, 1], [1, 3]], "b": [3, 5]}, "expect_op": "solve_linear", "expect_status": "ok"},
        {"request": {"op": "eigenvalues", "matrix": [[2, 0], [0, 3]]}, "expect_op": "eigenvalues", "expect_status": "ok"},
        {"request": {"op": "determinant", "matrix": [[2, 1], [1, 3]]}, "expect_op": "determinant", "expect_status": "ok"},
        {"request": {"op": "ode", "coeffs": [2, -3, 1]}, "expect_op": "ode", "expect_status": "ok"},
        {"request": {"op": "limit", "num": [0, 1], "den": [1, 0, 1], "point": 0}, "expect_op": "limit", "expect_status": "ok"},
        {"request": {"op": "integrate_exact", "num": [1], "den": [1, 0, 1]}, "expect_op": "integrate_exact", "expect_status": "ok"},
        {"request": {"op": "shortest_path", "matrix": [[0, 3], [3, 0]]}, "expect_op": "shortest_path", "expect_status": "ok"},
        {"request": {"op": "integrate", "f": "x**2", "a": "0", "b": "1"}, "expect_op": "integrate", "expect_status": "CERTIFIED"},
        # a {kind} request that maps back to an op
        {"request": {"kind": "factorize", "n": 12}, "expect_op": "factor", "expect_status": "ok"},
        # free-form strings — routed via idm.parse (the router does no NL magic beyond it)
        {"request": "factor 360360", "expect_op": "factor", "expect_status": "ok"},
        {"request": "gcd of 48 and 36", "expect_op": "gcd", "expect_status": "ok"},
        # a routed op that HOLDs at solve time (the router is right; the solver honestly HOLDs)
        {"request": {"op": "roots", "coeffs": [9999, -4242, 1313, -77, 1]}, "expect_op": "roots", "expect_status": "HOLD"},
        # unclassifiable — a good router returns no op, does not hallucinate one
        {"request": "what is the meaning of life", "expect_op": None, "expect_status": None},
        {"request": {"kind": "definitely_not_a_kind"}, "expect_op": None, "expect_status": None},
    ]


def _op_of(routed) -> Optional[str]:
    """Extract the chosen op from a router's return value — accepts a bare op string, or a plan/route
    dict carrying ``route.op`` (or a top-level ``op``)."""
    if routed is None or isinstance(routed, str):
        return routed
    if isinstance(routed, dict):
        if isinstance(routed.get("route"), dict):
            return routed["route"].get("op")
        return routed.get("op")
    return None


def score(router: Callable, cases: Optional[List[dict]] = None) -> dict:
    """Run ``router`` (request → op string, or a plan/route dict) over ``cases`` (default
    :func:`dataset`) and report accuracy. Returns ``{n, op_correct, op_accuracy, exec_correct,
    exec_accuracy, failures}``. ``op`` accuracy = chosen op matches ``expect_op``. Execution accuracy
    (only over cases with a non-None ``expect_status``) = solving the routed op's problem yields
    ``expect_status``; the routed problem is rebuilt from the case's params so the score reflects the
    router's op choice, not param-parsing of free-form text."""
    cases = cases if cases is not None else dataset()
    op_correct = exec_correct = exec_total = 0
    failures = []
    for c in cases:
        chosen = _op_of(router(c["request"]))
        ok_op = chosen == c["expect_op"]
        op_correct += ok_op
        if not ok_op:
            failures.append({"request": c["request"], "expected_op": c["expect_op"], "got_op": chosen})
        if c["expect_status"] is not None and c["expect_op"] is not None:
            exec_total += 1
            req = c["request"]
            params = {k: v for k, v in req.items() if k not in ("op", "kind")} if isinstance(req, dict) else {}
            # for free-form string cases there are no structured params here; skip their exec check
            if isinstance(req, dict) and ok_op:
                kind = ai._OPS[c["expect_op"]]["kind"]
                status = solve({"kind": kind, **params}).get("status")
                exec_correct += (status == c["expect_status"])
            else:
                exec_total -= 1  # not a structured-param exec case
    n = len(cases)
    return {"n": n, "op_correct": op_correct, "op_accuracy": op_correct / n if n else 0.0,
            "exec_correct": exec_correct, "exec_total": exec_total,
            "exec_accuracy": exec_correct / exec_total if exec_total else 1.0,
            "failures": failures}


def benchmark_router() -> dict:
    """Score the built-in deterministic router (:func:`idm.ai.route`) against :func:`dataset` — the
    oracle/ceiling. It should be perfect on op-selection for every case (structured and the supported
    free-form ones) and perfect on execution for the structured cases."""
    return score(ai.route)


__all__ = ["dataset", "score", "benchmark_router"]
