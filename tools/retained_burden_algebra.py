#!/usr/bin/env python3
"""Exact finite algebra for retaining the least-burden readable history.

This module is derived from the repository's readout-first commitments:

* a burden is a finite tuple of rational readouts;
* extending a history adds the newly retained burden;
* histories with the same exposed state are reader-equivalent;
* the declared finite lexicographic lattice retains one representative; and
* an impossible history is absent (``None``), never encoded by ``+infinity``.

The construction is intentionally small.  It does not import a continuum
optimizer or use floating point.  Its conventional algebraic relatives may be
useful comparators, but they are not premises of this implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


RationalLike = int | Fraction


@dataclass(frozen=True)
class BurdenOrder:
    """Names and ordering of the finite readouts compared by a reader."""

    names: tuple[str, ...]
    composition: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError("a retained burden needs at least one readout")
        if any(not isinstance(name, str) or not name.strip() for name in self.names):
            raise ValueError("retained burden names must be non-empty strings")
        if len(set(self.names)) != len(self.names):
            raise ValueError("retained burden names must be unique")
        composition = self.composition or ("sum",) * len(self.names)
        if (
            len(composition) != len(self.names)
            or any(rule not in {"sum", "max"} for rule in composition)
        ):
            raise ValueError("each burden needs a finite sum/max composition rule")
        object.__setattr__(self, "composition", composition)


@dataclass(frozen=True)
class RetainedBurden:
    """A finite exact burden vector in its declared reader order."""

    order: BurdenOrder
    values: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        converted = tuple(Fraction(value) for value in self.values)
        if len(converted) != len(self.order.names):
            raise ValueError("burden value count differs from its declared boundary")
        if any(value < 0 for value in converted):
            raise ValueError("retained burdens must be non-negative")
        object.__setattr__(self, "values", converted)

    @classmethod
    def zero(cls, order: BurdenOrder) -> "RetainedBurden":
        return cls(order, (Fraction(0),) * len(order.names))

    @classmethod
    def from_values(
        cls,
        order: BurdenOrder,
        values: Iterable[RationalLike],
    ) -> "RetainedBurden":
        return cls(order, tuple(Fraction(value) for value in values))

    def extend(self, other: "RetainedBurden") -> "RetainedBurden":
        """Compose two consecutive finite records."""

        if self.order != other.order:
            raise ValueError("cannot compose burdens with different readout orders")
        return RetainedBurden(
            self.order,
            tuple(
                left + right if rule == "sum" else max(left, right)
                for left, right, rule in zip(
                    self.values,
                    other.values,
                    self.order.composition,
                )
            ),
        )

    def named(self) -> tuple[tuple[str, Fraction], ...]:
        return tuple(zip(self.order.names, self.values))


def retain_lesser(
    current: RetainedBurden | None,
    candidate: RetainedBurden | None,
) -> RetainedBurden | None:
    """Retain the lesser readable representative; absence stays explicit."""

    if current is None:
        return candidate
    if candidate is None:
        return current
    if current.order != candidate.order:
        raise ValueError("cannot compare burdens with different readout orders")
    return candidate if candidate.values < current.values else current


def equivalent_readout(
    left: RetainedBurden | None,
    right: RetainedBurden | None,
) -> bool:
    """Exact equality at the declared finite boundary."""

    return left == right
