"""Domain-parametrized univariate polynomials (pillar P1.4, Wave 5).

A ``UPoly`` is a coefficient list (low-order first) plus its :mod:`coeffring` domain. Arithmetic is
performed through the domain's operations, so the same call is exact ℚ over ``QRing`` and modular over
``GFRing``. ``divmod_``/``gcd`` require a field domain (they use ``domain.div``); over a non-field
(``ZRing``) they raise rather than silently produce a wrong "field" answer.
"""

from __future__ import annotations

from typing import List, Tuple

from .coeffring import DomainMismatch


class UPoly:
    __slots__ = ("coeffs", "domain")

    def __init__(self, coeffs: List, domain):
        c = [domain.normalize(x) for x in coeffs] or [domain.zero()]
        while len(c) > 1 and domain.is_zero(c[-1]):
            c.pop()
        self.coeffs = c
        self.domain = domain

    def degree(self) -> int:
        return -1 if self.is_zero() else len(self.coeffs) - 1

    def is_zero(self) -> bool:
        return len(self.coeffs) == 1 and self.domain.is_zero(self.coeffs[0])

    def lead(self):
        return self.coeffs[-1]

    def monic(self) -> "UPoly":
        if self.is_zero():
            return self
        lc = self.lead()
        D = self.domain
        return UPoly([D.div(c, lc) for c in self.coeffs], D)

    def __eq__(self, o):
        return isinstance(o, UPoly) and self.domain == o.domain and self.coeffs == o.coeffs

    def __repr__(self):
        return f"UPoly({self.coeffs}, {self.domain!r})"


def _check(a: UPoly, b: UPoly):
    if a.domain != b.domain:
        raise DomainMismatch(f"{a.domain!r} vs {b.domain!r}")


def add(a: UPoly, b: UPoly) -> UPoly:
    _check(a, b)
    D = a.domain
    n = max(len(a.coeffs), len(b.coeffs))
    out = []
    for i in range(n):
        x = a.coeffs[i] if i < len(a.coeffs) else D.zero()
        y = b.coeffs[i] if i < len(b.coeffs) else D.zero()
        out.append(D.add(x, y))
    return UPoly(out, D)


def mul(a: UPoly, b: UPoly) -> UPoly:
    _check(a, b)
    D = a.domain
    out = [D.zero()] * (len(a.coeffs) + len(b.coeffs) - 1)
    for i, x in enumerate(a.coeffs):
        for j, y in enumerate(b.coeffs):
            out[i + j] = D.add(out[i + j], D.mul(x, y))
    return UPoly(out, D)


def divmod_(a: UPoly, b: UPoly) -> Tuple[UPoly, UPoly]:
    _check(a, b)
    D = a.domain
    if not D.is_field:
        raise ValueError(f"divmod_ needs a field; {D!r} is not one")
    if b.is_zero():
        raise ZeroDivisionError("polynomial division by zero")
    r = list(a.coeffs)
    q = [D.zero()] * max(len(a.coeffs) - len(b.coeffs) + 1, 1)
    bl = b.lead()
    while len(r) >= len(b.coeffs) and not (len(r) == 1 and D.is_zero(r[0])):
        shift = len(r) - len(b.coeffs)
        coef = D.div(r[-1], bl)
        q[shift] = coef
        for i in range(len(b.coeffs)):
            r[shift + i] = D.add(r[shift + i], D.neg(D.mul(coef, b.coeffs[i])))
        while len(r) > 1 and D.is_zero(r[-1]):
            r.pop()
        if len(r) < len(b.coeffs):
            break
    return UPoly(q, D), UPoly(r, D)


def gcd(a: UPoly, b: UPoly) -> UPoly:
    _check(a, b)
    D = a.domain
    if not D.is_field:
        raise ValueError(f"gcd needs a field; {D!r} is not one")
    x, y = a, b
    while not y.is_zero():
        _, r = divmod_(x, y)
        x, y = y, r
    return x.monic()


__all__ = ["UPoly", "add", "mul", "divmod_", "gcd"]
