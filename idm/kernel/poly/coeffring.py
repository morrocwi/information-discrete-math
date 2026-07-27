"""Coefficient rings for the polynomial tower (pillar P1.4, Wave 5).

Today's polynomial code (idm.exact) is domain-blind — a coefficient list is "just numbers." Here a
polynomial carries its **coefficient ring**, so the *same* operation gives the domain-appropriate
answer: ``gcd(x²+1, x+1)`` is ``1`` over ℚ but ``x+1`` over GF(2). All arithmetic is exact finite
(ℤ/ℚ, or ℤ/pℤ) — no float, no continuum.

Wave-5 scope: ``QRing`` (field), ``ZRing`` (integral domain, no division), ``GFRing(p)`` (prime finite
field). Algebraic-number and rational-function fields are later work.
"""

from __future__ import annotations

from fractions import Fraction as Q


class DomainMismatch(Exception):
    """Two polynomials over different coefficient rings were combined (HOLD at the kind layer)."""


class QRing:
    """The field of rationals ℚ."""

    name = "Q"
    is_field = True

    def zero(self): return Q(0)
    def one(self): return Q(1)
    def from_int(self, n): return Q(n)
    def normalize(self, a): return Q(a)
    def add(self, a, b): return Q(a) + Q(b)
    def neg(self, a): return -Q(a)
    def mul(self, a, b): return Q(a) * Q(b)
    def div(self, a, b): return Q(a) / Q(b)
    def eq(self, a, b): return Q(a) == Q(b)
    def is_zero(self, a): return Q(a) == 0

    def __eq__(self, o): return isinstance(o, QRing)
    def __hash__(self): return hash("Q")
    def __repr__(self): return "ℚ"


class ZRing:
    """The integers ℤ — an integral domain, NOT a field (no general division)."""

    name = "Z"
    is_field = False

    def zero(self): return 0
    def one(self): return 1
    def from_int(self, n): return int(n)
    def normalize(self, a): return int(a)
    def add(self, a, b): return int(a) + int(b)
    def neg(self, a): return -int(a)
    def mul(self, a, b): return int(a) * int(b)
    def div(self, a, b):
        a, b = int(a), int(b)
        if b == 0 or a % b != 0:
            raise ZeroDivisionError("ℤ is not a field: inexact division")
        return a // b
    def eq(self, a, b): return int(a) == int(b)
    def is_zero(self, a): return int(a) == 0

    def __eq__(self, o): return isinstance(o, ZRing)
    def __hash__(self): return hash("Z")
    def __repr__(self): return "ℤ"


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


class GFRing:
    """The prime finite field GF(p) = ℤ/pℤ (p prime — inverse by Fermat's little theorem).

    p MUST be prime: for a composite modulus ℤ/pℤ is not a field, Fermat's ``b^(p-2)`` is not an
    inverse, and both scalar division and the Euclidean polynomial gcd would silently misbehave. So a
    composite p is rejected at construction (the HOLD direction), never accepted with a wrong answer.
    """

    is_field = True

    def __init__(self, p: int):
        if not _is_prime(int(p)):
            raise ValueError(f"GF(p) requires a PRIME p; {p} is not prime")
        self.p = int(p)
        self.name = f"GF({p})"

    def _r(self, a): return int(a) % self.p
    def zero(self): return 0
    def one(self): return 1 % self.p
    def from_int(self, n): return self._r(n)
    def normalize(self, a): return self._r(a)
    def add(self, a, b): return self._r(self._r(a) + self._r(b))
    def neg(self, a): return self._r(-self._r(a))
    def mul(self, a, b): return self._r(self._r(a) * self._r(b))
    def div(self, a, b):
        b = self._r(b)
        if b == 0:
            raise ZeroDivisionError("division by zero in GF(p)")
        return self._r(self._r(a) * pow(b, self.p - 2, self.p))   # b^(p-2) = b^-1 (Fermat, p prime)
    def eq(self, a, b): return self._r(a) == self._r(b)
    def is_zero(self, a): return self._r(a) == 0

    def __eq__(self, o): return isinstance(o, GFRing) and o.p == self.p
    def __hash__(self): return hash(("GF", self.p))
    def __repr__(self): return self.name


__all__ = ["DomainMismatch", "QRing", "ZRing", "GFRing"]
