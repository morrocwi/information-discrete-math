"""idm.continuum — the continuum as a first-class ℚ readout primitive.

A `Continuum` is not a real-number object. It is a resolution-indexed exact-rational readout
`g : N -> Q` with an explicit evidence discipline:

- `.at(N)` returns the exact rational readout at a declared finite resolution;
- `.readout(eps)` returns `CERTIFIED` only when a proved tail bound is carried;
- otherwise a finite observed plateau returns `STABLE` (historical alias `DIAGNOSTIC`);
- if neither condition is met, it returns `HOLD`.

The exact pointwise algebra is mapped to `formal/IDM_Continuum.v`. Completed-limit interpretation remains
separate from the finite computation.
"""
from fractions import Fraction as Q

from .certified import Readout, CERTIFIED, STABLE, HOLD

WITNESS = "formal/IDM_Continuum.v"

# Compatibility alias. An observed plateau is now represented by the project-wide STABLE status rather
# than an ad-hoc string that the shared Readout type could not validate.
DIAGNOSTIC = STABLE


class Continuum:
    """A continuum-like quantity carried as an exact-rational readout `g : N -> Q`."""

    __slots__ = ("_g", "name", "_tail_bound")

    def __init__(self, gen, name=None, tail_bound=None):
        """Create a readout generator.

        `tail_bound`, when supplied, is a proved callable `N -> Q` bounding distance from the named
        appearance. Without it, a finite plateau can establish only `STABLE` evidence.
        """

        self._g = gen
        self.name = name or "continuum"
        self._tail_bound = tail_bound

    def at(self, N):
        """Return the exact rational readout at non-negative resolution `N`."""

        N = int(N)
        if N < 0:
            raise ValueError("resolution N must be >= 0 (a finite readout index)")
        value = self._g(N)
        return value if isinstance(value, Q) else Q(str(value))

    def readout(self, eps, window=3, max_N=4096):
        """Return a proved target enclosure, a finite stability result, or HOLD.

        If a proved tail bound exists, the least inspected `N` satisfying `tail_bound(N) <= eps` yields
        `CERTIFIED`. Otherwise, `window` successive observed gaps below `eps` yield `STABLE`; this does not
        claim the pattern continues beyond the sampled window. Failure to reach either condition yields
        `HOLD`.
        """

        eps = Q(str(eps))
        if eps <= 0:
            return Readout(None, None, HOLD, "tolerance ε must be > 0")

        if self._tail_bound is not None:
            for N in range(max_N + 1):
                bound = Q(str(self._tail_bound(N)))
                if bound <= eps:
                    return Readout(
                        self.at(N),
                        bound,
                        CERTIFIED,
                        f"{self.name}: proven tail bound <= ε at N={N}; readout at declared resolution, "
                        "not a claim that a completed limit was physically formed",
                    )
            return Readout(
                None,
                None,
                HOLD,
                f"{self.name}: proven tail bound never reaches ε within {max_N} refinements",
            )

        gaps = []
        previous = self.at(0)
        for N in range(1, max_N + 1):
            current = self.at(N)
            gaps.append(abs(current - previous))
            if len(gaps) >= window and all(gap <= eps for gap in gaps[-window:]):
                return Readout(
                    current,
                    max(gaps[-window:]),
                    STABLE,
                    f"{self.name}: OBSERVED plateau at N={N} (last {window} gaps <= ε) — "
                    "finite_diagnostic, NOT proven beyond N (supply a tail_bound to certify); "
                    "the completed limit remains open",
                )
            previous = current
        return Readout(
            None,
            None,
            HOLD,
            f"{self.name}: no plateau within {max_N} refinements; refusing to emit a completed limit",
        )

    @staticmethod
    def const(q):
        """Return the constant exact-rational readout, whose proved tail bound is zero."""

        q = Q(str(q))
        return Continuum(lambda N, _q=q: _q, name=f"const({q})", tail_bound=lambda N: Q(0))

    @staticmethod
    def from_gen(gen, name=None, tail_bound=None):
        """Wrap a resolution-to-rational generator with an optional proved tail bound."""

        return Continuum(gen, name=name, tail_bound=tail_bound)

    def _coerce(self, other):
        return other if isinstance(other, Continuum) else Continuum.const(other)

    def _combined_tail(self, other):
        """Propagate proved additive bounds by the triangle inequality."""

        if self._tail_bound is None or other._tail_bound is None:
            return None
        return lambda N, a=self._tail_bound, b=other._tail_bound: Q(str(a(N))) + Q(str(b(N)))

    def __add__(self, other):
        other = self._coerce(other)
        return Continuum(
            lambda N: self.at(N) + other.at(N),
            name=f"({self.name}+{other.name})",
            tail_bound=self._combined_tail(other),
        )

    __radd__ = __add__

    def __sub__(self, other):
        other = self._coerce(other)
        return Continuum(
            lambda N: self.at(N) - other.at(N),
            name=f"({self.name}-{other.name})",
            tail_bound=self._combined_tail(other),
        )

    def __mul__(self, other):
        other = self._coerce(other)
        return Continuum(lambda N: self.at(N) * other.at(N), name=f"({self.name}*{other.name})")

    __rmul__ = __mul__

    def compose(self, reindex):
        """Reindex the finite resolution: `(a.compose(h)).at(N) == a.at(h(N))`."""

        return Continuum(lambda N: self.at(int(reindex(N))), name=f"{self.name}∘reindex")

    def __repr__(self):
        return f"Continuum({self.name})"


def geometric(r):
    """Exact rational geometric partial sums with a proved tail for `0 <= r < 1`."""

    r = Q(str(r))
    generator = lambda N, _r=r: sum((_r**k for k in range(N + 1)), Q(0))
    if 0 <= r < 1:
        tail = lambda N, _r=r: _r ** (N + 1) / (1 - _r)
        return Continuum(generator, name=f"geometric(r={r})", tail_bound=tail)
    return Continuum(generator, name=f"geometric(r={r})")


def from_sequence(seq):
    """Create a continuum-like readout from a callable or finite sequence."""

    def generator(N, source=seq):
        return source(N) if callable(source) else source[min(N, len(source) - 1)]

    return Continuum(generator, name="from_sequence")
