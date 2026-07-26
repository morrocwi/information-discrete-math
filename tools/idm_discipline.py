#!/usr/bin/env python3
"""idm_discipline — the numeric-honesty layer of Information Discrete Mathematics (Yaoharee Lahtee).

This is the operational discipline that sits ON TOP of the classical float/exact substrate: it does not
replace classical computation, it keeps it honest. It is EXTRACTED and merged from the earlier
`cpg_math` MathSolver v0.1.0 discipline (ISSUE-0088, benchmark 6/6 PASS, 2026-06-11) — that work is now
superseded by and folded into this framework. What is kept here is only what the foundation's tool layer
(`idm_tools.py`, which already has D_ε/I_ε/FTCC) did NOT already carry:

  - Verdict (ACCEPT / HOLD / BLOCK), fail-closed by construction — never a silent wrong answer.
  - eq_eps + chain guard — equality at a declared resolution, with the sorites/non-transitivity trap.
  - sum_neumaier + residual_accumulation — residual-carrying summation (beats naive and even Kahan on
    large-swing inputs; Kahan was falsified on benchmark D and replaced — the honest engineering loop).
  - CostLedger — arithmetic is not free; make complexity visible.
  - solve_obstruction — root finding as obstruction-zeroing with a fail-closed verdict.
  - integrate_positive_decay — admissibility by construction: evolve the RECORD in coordinates that
    cannot leave the admissible set; a readout underflow to 0 is a correct zero-at-resolution verdict.

CLAIM BOUNDARY (inherited, non-negotiable): valid-in-discipline ≠ true-about-world. A PASS/ACCEPT is a
readout at the declared resolution, not a truth certificate. Classical mathematics is not replaced.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

ACCEPT, HOLD, BLOCK = "ACCEPT", "HOLD", "BLOCK"


@dataclass
class Verdict:
    """A fail-closed result. Truthy ONLY on ACCEPT — so `if verdict:` cannot pass a HOLD/BLOCK by
    accident, and a consumer must branch on `.status` before trusting `.value`."""
    status: str
    value: object = None
    reason: str = ""
    def __bool__(self) -> bool:
        return self.status == ACCEPT


# ── R1 — equality at a declared resolution (never exact == on resolution-bounded readouts) ──
def eq_eps(a: float, b: float, eps: float, *, relative: bool = False) -> bool:
    """a indistinguishable from b at declared resolution eps. NOT transitive — never chain it."""
    if eps <= 0:
        raise ValueError("eps must be a declared positive resolution")
    tol = eps * max(abs(a), abs(b)) if relative else eps
    return abs(a - b) < tol

def eq_chain_guard(values: Sequence[float], eps: float) -> Verdict:
    """The sorites guard: BLOCK a chain of pairwise-eq_eps steps whose endpoints are distinguishable."""
    pairwise = all(eq_eps(values[i], values[i+1], eps) for i in range(len(values)-1))
    endpoints = eq_eps(values[0], values[-1], eps)
    if pairwise and not endpoints:
        return Verdict(BLOCK, reason="non-transitivity: eq_eps chain with distinguishable endpoints")
    return Verdict(ACCEPT, value=endpoints)


# ── R4 — carry the residual (honest summation) ──
def sum_neumaier(xs: Iterable[float]) -> float:
    """Neumaier summation — retain the translation residual on the larger-magnitude branch, so the
    residual is kept no matter which operand dominates. Replaced Kahan after Kahan was falsified on
    large-swing inputs (benchmark D)."""
    acc, c = 0.0, 0.0
    for x in xs:
        t = acc + x
        c += (acc - t) + x if abs(acc) >= abs(x) else (x - t) + acc
        acc = t
    return acc + c

def residual_accumulation(xs: Sequence[float]) -> dict:
    """How much retained value each readout lost vs the exact reference (math.fsum)."""
    exact = math.fsum(xs)
    def naive(v):
        a = 0.0
        for x in v: a += x
        return a
    return {"naive_loss": abs(naive(xs)-exact), "neumaier_loss": abs(sum_neumaier(xs)-exact), "exact": exact}


# ── R6 — cost ledger (arithmetic is not free) ──
@dataclass
class CostLedger:
    steps: int = 0
    by_op: dict = field(default_factory=dict)
    def charge(self, op: str, n: int = 1) -> None:
        self.steps += n
        self.by_op[op] = self.by_op.get(op, 0) + n


# ── R2 — verdicts, fail-closed (root finding as obstruction zeroing) ──
def solve_obstruction(f: Callable[[float], float], x0: float, eps_res: float, *,
                      max_ticks: int = 200, dx: float = 1e-7, ledger: "CostLedger|None" = None) -> Verdict:
    """ACCEPT only when the residual READS zero at the declared resolution; HOLD (never a silent wrong
    answer) on budget exhaustion or a degenerate step. Newton substrate; the discipline is the verdict."""
    x = x0
    for _ in range(max_ticks):
        if ledger: ledger.charge("f_eval", 2); ledger.charge("newton_step")
        r = f(x)
        if abs(r) < eps_res:
            return Verdict(ACCEPT, value=x, reason=f"residual {r:.3e} < eps_res")
        d = (f(x+dx) - f(x-dx)) / (2*dx)
        if not math.isfinite(d) or abs(d) < 1e-300:
            return Verdict(HOLD, value=x, reason="degenerate step (derivative unreadable) — fail closed")
        x_new = x - r/d
        if not math.isfinite(x_new):
            return Verdict(HOLD, value=x, reason="non-finite update — fail closed")
        x = x_new
    r = f(x)
    return (Verdict(ACCEPT, value=x, reason=f"residual {r:.3e} < eps_res at budget end") if abs(r) < eps_res
            else Verdict(HOLD, value=x, reason=f"budget exhausted, residual {r:.3e} ≥ eps_res — NOT a root claim"))


# ── R3 — admissibility by construction (evolve the record, not the readout) ──
def integrate_positive_decay(gamma: Callable[[float], float], y0: float, dt: float, n: int):
    """y' = -gamma(t)·y with y>0 REQUIRED, evolved in log coordinates g=ln y (g'=-gamma): the RECORD g
    can never leave the admissible set. The readout y=exp(g) may underflow to a correct zero-at-
    resolution verdict — that is a readout fact, not a violation. Returns (readouts, record_g)."""
    if y0 <= 0:
        raise ValueError("y0 must be positive (declared admissible set)")
    g = math.log(y0); ys, gs = [y0], [g]
    for k in range(1, n+1):
        g += -gamma(k*dt)*dt
        ys.append(math.exp(g)); gs.append(g)
    return ys, gs


if __name__ == "__main__":
    # self-check: each discipline rule fires correctly
    assert bool(Verdict(ACCEPT)) and not bool(Verdict(HOLD)) and not bool(Verdict(BLOCK))
    assert eq_eps(1.0, 1.0 + 1e-12, 1e-9) and not eq_eps(1.0, 1.1, 1e-9)
    assert eq_chain_guard([0.0, 0.6, 1.2, 1.8], 1.0).status == BLOCK          # sorites trap caught
    big = [1e16, 1.0, -1e16, 1.0] * 25000
    assert residual_accumulation(big)["neumaier_loss"] <= residual_accumulation(big)["naive_loss"]
    assert solve_obstruction(lambda x: x**3 - x - 2, 1.5, 1e-9).status == ACCEPT
    assert solve_obstruction(lambda x: x*x + 1.0, 0.5, 1e-9).status == HOLD    # rootless → HOLD, not lie
    ys, gs = integrate_positive_decay(lambda t: 2.5, 1.0, 1.0, 2000)
    assert all(math.isfinite(g) for g in gs)                                   # record stays admissible
    print("idm_discipline self-check OK — Verdict · eq_eps+sorites · Neumaier · CostLedger · fail-closed solve · admissible-by-construction")
