"""Shared status/tier vocabulary for the IDM kernel (Symbolic Kernel v2, pillar P1.1).

Every ``kernel.*`` result speaks exactly these words — no pillar introduces a private status string
downstream. The `CERTIFIED`/`HOLD` constants are reused verbatim from :mod:`idm.certified` (not
redefined), and `OK` is `idm.solve`'s existing plain-success string, so the kernel plugs into the
existing verdict shape without inventing a parallel vocabulary.
"""

from __future__ import annotations

from enum import Enum

from ..certified import CERTIFIED, HOLD  # reused verbatim (R5)

OK = "ok"  # idm.solve's existing plain-success status, reused verbatim


class Tier(str, Enum):
    """The five honesty tiers. Order is significance, not comparability."""

    TH_COQC = "Th_coqc"           # a named machine-checked Coq theorem governs the result
    EXACT = "exact"               # exact finite ℤ/ℚ computation, no float in the answer
    FINITE_DIAGNOSTIC = "finite_diagnostic"  # numeric to a declared tolerance
    R_OPEN = "+R-Open"            # depends on an open real-analysis question, honestly fenced
    DR = "Dr"                     # design-narrative / interpretive


class HoldError(Exception):
    """INTERNAL control-flow only — raised and caught within a single ``kernel.*`` function body.

    It must NEVER propagate across the public ``idm.kernel`` boundary: a public function that would
    otherwise let it escape catches it and returns a ``status=HOLD`` result instead (return-not-raise
    at the public boundary, R9).
    """

    def __init__(self, reason: str = ""):
        super().__init__(reason)
        self.reason = reason


class DomainUnsafeRewrite(HoldError):
    """A rewrite would only be valid under a domain assumption that is not entailed."""


class ResourceBudgetExceeded(HoldError):
    """A bounded search/rewrite exhausted its declared budget before converging."""


__all__ = [
    "Tier", "OK", "CERTIFIED", "HOLD",
    "HoldError", "DomainUnsafeRewrite", "ResourceBudgetExceeded",
]
