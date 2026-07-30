"""Exact finite readouts and certified threshold decisions.

This module separates four questions that numerical code often conflates:

1. What finite token was supplied?
2. What exact value does that token denote?
3. What enclosure has the algorithm proved for its target?
4. Does that enclosure determine a discrete decision?

The implementation uses only the Python standard library. Decimal source tokens
are parsed exactly into :class:`fractions.Fraction`; no binary floating-point
conversion is required.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from fractions import Fraction
from typing import Union

RationalLike = Union[int, Fraction]


class Decision(str, Enum):
    """Four-valued result of a threshold predicate."""

    BELOW = "BELOW"
    EQUAL = "EQUAL"
    ABOVE = "ABOVE"
    UNCERTIFIED = "UNCERTIFIED"


@dataclass(frozen=True)
class DecimalReadout:
    """A finite decimal token with exact rational semantics.

    ``scale`` records the decimal scale carried by the token. It is metadata
    about the record, not by itself a measurement-uncertainty statement.
    """

    token: str
    numerator: int
    scale: int
    value: Fraction


@dataclass(frozen=True)
class Enclosure:
    """A closed rational interval proved to contain a target quantity."""

    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("enclosure lower bound exceeds upper bound")

    @classmethod
    def around(cls, estimate: RationalLike, error: RationalLike) -> "Enclosure":
        q = Fraction(estimate)
        e = Fraction(error)
        if e < 0:
            raise ValueError("error radius must be non-negative")
        return cls(q - e, q + e)

    @property
    def radius(self) -> Fraction:
        return (self.upper - self.lower) / 2

    @property
    def midpoint(self) -> Fraction:
        return (self.lower + self.upper) / 2

    def classify(self, threshold: RationalLike = 0) -> Decision:
        """Classify a threshold decision using only the proved enclosure.

        The result is certified exactly when the whole enclosure lies on one
        side of the threshold, or when the enclosure is the singleton threshold.
        Otherwise the correct fail-closed answer is ``UNCERTIFIED``.
        """

        tau = Fraction(threshold)
        if self.upper < tau:
            return Decision.BELOW
        if self.lower > tau:
            return Decision.ABOVE
        if self.lower == self.upper == tau:
            return Decision.EQUAL
        return Decision.UNCERTIFIED


def parse_decimal_readout(token: str) -> DecimalReadout:
    """Parse a finite decimal token without passing through binary float.

    Examples
    --------
    ``"0.350"`` becomes numerator ``350``, scale ``3``, value ``7/20``.
    ``"1.20e-2"`` becomes numerator ``120``, scale ``4``, value ``3/250``.
    """

    if not isinstance(token, str):
        raise TypeError("decimal readout must be supplied as a string token")
    text = token.strip()
    if not text:
        raise ValueError("empty decimal token")
    try:
        dec = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid decimal token: {token!r}") from exc
    if not dec.is_finite():
        raise ValueError("readout token must be finite")

    tup = dec.as_tuple()
    digits = 0
    for digit in tup.digits:
        digits = digits * 10 + digit
    if tup.sign:
        digits = -digits

    if tup.exponent >= 0:
        numerator = digits * (10 ** tup.exponent)
        scale = 0
    else:
        numerator = digits
        scale = -tup.exponent
    value = Fraction(numerator, 10**scale)
    return DecimalReadout(text, numerator, scale, value)


def certify_threshold(
    estimate: RationalLike,
    error: RationalLike,
    threshold: RationalLike = 0,
) -> Decision:
    """Operational decision certificate ``|estimate-threshold| > error``.

    This is the computable form of the sharp enclosure criterion. Failure to
    certify does not imply that the estimate is wrong; it means the supplied
    bound does not determine the discrete decision.
    """

    return Enclosure.around(estimate, error).classify(threshold)


def exact_det2x2(a: RationalLike, b: RationalLike, c: RationalLike, d: RationalLike) -> Fraction:
    """Return the exact determinant ``ad-bc`` over the rational domain."""

    return Fraction(a) * Fraction(d) - Fraction(b) * Fraction(c)


def round_integer_to_binary_precision(value: int, precision: int) -> int:
    """Round an integer to a normalized radix-2 precision, ties-to-even.

    The function models significand rounding only; callers must separately
    ensure that the target floating-point format has sufficient exponent range.
    """

    if not isinstance(value, int):
        raise TypeError("value must be an integer")
    if precision < 2:
        raise ValueError("precision must be at least 2 bits")
    if value == 0:
        return 0

    sign = -1 if value < 0 else 1
    n = abs(value)
    if n.bit_length() <= precision:
        return value

    shift = n.bit_length() - precision
    quantum = 1 << shift
    quotient, remainder = divmod(n, quantum)
    halfway = quantum >> 1
    if remainder > halfway or (remainder == halfway and quotient % 2 == 1):
        quotient += 1
    return sign * (quotient * quantum)


def determinant_collision(precision: int) -> tuple[int, int]:
    """Return exact and directly rounded determinants for a collision witness.

    For ``precision >= 3``, set ``N=2^(precision-1)`` and evaluate
    ``N*N - (N-1)*(N+1)`` after rounding each product to the declared binary
    precision. The exact determinant is 1 while the rounded direct evaluation
    is 0, assuming sufficient exponent range.
    """

    if precision < 3:
        raise ValueError("collision construction requires precision >= 3")
    n = 1 << (precision - 1)
    exact = n * n - (n - 1) * (n + 1)
    ad = round_integer_to_binary_precision(n * n, precision)
    bc = round_integer_to_binary_precision((n - 1) * (n + 1), precision)
    rounded = round_integer_to_binary_precision(ad - bc, precision)
    return exact, rounded


__all__ = [
    "Decision",
    "DecimalReadout",
    "Enclosure",
    "parse_decimal_readout",
    "certify_threshold",
    "exact_det2x2",
    "round_integer_to_binary_precision",
    "determinant_collision",
]
