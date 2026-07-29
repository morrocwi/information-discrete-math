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
        """``True`` iff the solver returned HOLD — no readout was made (the honest "could not read")."""
        return self.get("status") == "HOLD"

    @property
    def is_open(self) -> bool:
        """``True`` iff the result is an **open-tail readout** (``status == "+R_OPEN"``): a finite
        ℚ-approximant plus a certified tail/contraction bound, with *no* plain ``value`` (the
        anti-overclaim fence — see :mod:`idm.hilbert_open`). Read ``r["approximant"]`` and the bound,
        not ``r.value``. Distinct from both ``is_ok`` and ``is_hold``."""
        return self.get("status") == "+R_OPEN"

    @property
    def is_ok(self) -> bool:
        """``True`` iff the solver produced a **definitive resolved result carrying a ``value``** — this
        covers ``"ok"``, a certified ``"CERTIFIED"``, and a definitive ``"REFUTED"`` (a proven
        counterexample with ``value: False`` + witness). It is defined by the presence of a ``value``
        rather than an enumerated status list, so it stays correct as new resolved statuses are added,
        and it deliberately excludes ``+R_OPEN`` (open-tail, no plain value — use :attr:`is_open`) and
        HOLD. Note: ``is_ok`` means "the solve resolved", not "the answer is yes" — the yes/no lives in
        ``value`` (e.g. a REFUTED positivity query is ``is_ok`` with ``value == False``)."""
        return self.get("status") != "HOLD" and "value" in self

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
