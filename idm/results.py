"""idm.results — the typed ``Result`` wrapper returned by :func:`idm.solve`.

``Result`` **is a ``dict``** (it subclasses ``dict``), so every existing pattern keeps working
unchanged — ``r["status"]``, ``r.get("value")``, ``json.dumps(r)``, ``isinstance(r, dict)``, and
``dict``-equality against a plain dict all behave identically. It only *adds* typed accessors on top,
so programmers get ``r.status`` / ``r.value`` / ``r.is_hold`` / ``r.raise_for_hold()`` without giving
up the dict contract the solver, the REST server, and the golden snapshots rely on.
"""
from __future__ import annotations


class SolveHold(Exception):
    """Raised by :meth:`Result.raise_for_hold` when the solver returned ``status == "HOLD"``.

    Carries the solver's own ``reason`` string so a program that prefers exceptions to status-checking
    (``idm.solve(...).raise_for_hold().value``) gets the honest reason the readout could not be made.
    """


class Result(dict):
    """The normalized result of :func:`idm.solve`, as a ``dict`` with typed convenience accessors.

    Keys always present: ``kind``, ``status``. Depending on the kind/outcome: ``value``, ``bound``,
    ``tier``, ``reason``, ``method``, ``coq_theorem``. Accessors never raise on a missing key (they
    return ``None``), so they are safe to read on a HOLD result.
    """

    __slots__ = ()

    @property
    def kind(self):
        """The problem kind that was solved (echoed back), or ``None``."""
        return self.get("kind")

    @property
    def status(self):
        """``"ok"`` / ``"CERTIFIED"`` on success, ``"HOLD"`` when the readout could not be made."""
        return self.get("status")

    @property
    def value(self):
        """The result payload (shape depends on the kind), or ``None`` on HOLD."""
        return self.get("value")

    @property
    def bound(self):
        """The proven error bound where one is attached (certified numeric kinds), else ``None``."""
        return self.get("bound")

    @property
    def tier(self):
        """Honesty tier: ``Th_coqc`` / ``exact`` / ``finite_diagnostic`` / ``+ℝ-Open``."""
        return self.get("tier")

    @property
    def reason(self):
        """Why the solver HELD (present only on a HOLD), else ``None``."""
        return self.get("reason")

    @property
    def method(self):
        """A short description of the method used, where a handler attaches one."""
        return self.get("method")

    @property
    def coq_theorem(self):
        """The named machine-checked theorem governing the result, for ``Th_coqc`` kinds."""
        return self.get("coq_theorem")

    @property
    def is_hold(self) -> bool:
        """``True`` iff the solver returned HOLD (no readout was made)."""
        return self.get("status") == "HOLD"

    @property
    def is_ok(self) -> bool:
        """``True`` iff the solver produced a result (``"ok"`` or a certified ``"CERTIFIED"``)."""
        return self.get("status") in ("ok", "CERTIFIED")

    def raise_for_hold(self) -> "Result":
        """Return ``self`` if a readout was made; raise :class:`SolveHold` (with the solver's reason)
        if the status is HOLD. Lets a caller write ``idm.solve(...).raise_for_hold().value``."""
        if self.is_hold:
            raise SolveHold(self.get("reason") or f"solver returned HOLD for kind {self.get('kind')!r}")
        return self

    def to_dict(self) -> dict:
        """A plain ``dict`` copy (e.g. to hand to code that type-checks ``type(x) is dict``)."""
        return dict(self)

    def __repr__(self) -> str:
        extra = f", tier={self.tier!r}" if self.tier else ""
        tail = f", reason={self.reason!r}" if self.is_hold else ""
        return f"Result(kind={self.kind!r}, status={self.status!r}{extra}{tail})"


__all__ = ["Result", "SolveHold"]
