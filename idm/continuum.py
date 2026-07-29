"""idm.continuum — the continuum as a first-class ℚ PRIMITIVE (a readout, never ℝ as an object).

Founder question (2026-07-29): *can we build a ℚ-primitive function that behaves like the ℝ-rung
continuum?* Yes — and this is the operational form of the framework's central claim ("the continuum is
a readout of the discrete", Part XX / the machine-checked FTCC bridge `formal/IDM_Bridge.v`). A
`Continuum` is NOT a real number. It is a resolution-indexed EXACT-ℚ readout `g : N → ℚ` together with
the honest refusal discipline: you may read it at any finite resolution (always ℚ), and ask for its
A8-stable plateau to a declared tolerance — but the *completed* limit is never formed, and where no
plateau exists it returns HOLD instead of fabricating a number. ℝ is never a primitive here; only ℚ is.

What makes it continuum-LIKE without being ℝ:
  * `.at(N)`      — the exact ℚ readout at declared resolution N (the primitive operation).
  * `.readout(ε)` — increase N until the readout plateaus (successive gaps ≤ ε across a window):
                    CERTIFIED with an exact ℚ gap bound, or HOLD (divergence / oscillation / no limit).
  * an ALGEBRA closed in ℚ — `a+b`, `a-b`, `a*b`, scalar `c*a`, `a.compose(h)` — every result is again a
    `Continuum` whose `.at(N)` is the pointwise ℚ combination: `(a+b).at(N) == a.at(N) + b.at(N)`,
    exactly. So continuum-readouts form a commutative ℚ-algebra you can compute with directly.

The algebra's soundness laws are machine-checked axiom-free over ℚ in `formal/IDM_Continuum.v`
(pointwise homomorphism; the gap is sub-additive, so combining two plateauing readouts still plateaus;
a constant readout has zero gap). This is "the continuum, computable on ℚ" made a theorem, not a stance.
"""
from fractions import Fraction as Q

from .certified import Readout, CERTIFIED, HOLD

WITNESS = "formal/IDM_Continuum.v"   # machine-checks the ℚ-algebra laws (homomorphism, gap sub-additivity)


class Continuum:
    """A continuum value carried as a ℚ readout `g : N → ℚ`. Never an ℝ object; every read is exact ℚ."""
    __slots__ = ("_g", "name")

    def __init__(self, gen, name=None):
        """`gen` is a callable N(int ≥ 0) → something coercible to Fraction: the exact ℚ readout at
        resolution N (larger N = finer). `name` is a label for reprs only."""
        self._g = gen
        self.name = name or "continuum"

    # ---- the primitive operation: an exact ℚ readout at a declared finite resolution --------------
    def at(self, N):
        """The EXACT ℚ readout at resolution N (N a non-negative int). Always a finite Fraction —
        the continuum is only ever touched as a discrete rational readout, never as a completed real."""
        N = int(N)
        if N < 0:
            raise ValueError("resolution N must be ≥ 0 (a finite readout index)")
        v = self._g(N)
        return v if isinstance(v, Q) else Q(str(v))

    # ---- the honest plateau readout: a ℚ value + certificate, or HOLD (never a fabricated limit) ---
    def readout(self, eps, window=3, max_N=4096):
        """Return the A8-stable ℚ plateau to tolerance `eps`: the least N whose last `window` successive
        gaps are all ≤ eps, as a CERTIFIED `Readout(q=at(N), bound=max recent gap)`. If no such plateau
        appears within `max_N` refinements, return HOLD — we refuse to emit the completed limit as a
        number. The returned q is explicitly 'the readout at the resolution that met your tolerance',
        NOT 'the real limit' (which stays +ℝ-Open)."""
        eps = Q(str(eps))
        if eps <= 0:
            return Readout(None, None, HOLD, "tolerance ε must be > 0")
        gaps = []
        prev = self.at(0)
        for N in range(1, max_N + 1):
            cur = self.at(N)
            gaps.append(abs(cur - prev))
            if len(gaps) >= window and all(g <= eps for g in gaps[-window:]):
                return Readout(cur, max(gaps[-window:]), CERTIFIED,
                               f"{self.name}: A8 plateau at N={N} (last {window} gaps ≤ ε); "
                               f"readout at declared resolution, NOT the completed limit (+ℝ-Open)")
            prev = cur
        return Readout(None, None, HOLD,
                       f"{self.name}: no A8 plateau within {max_N} refinements — the readout does not "
                       f"stabilise to ε (divergence / oscillation / no limit); refusing to emit a number")

    # ---- the ℚ-algebra: every combinator returns another Continuum, exact pointwise over ℚ ---------
    @staticmethod
    def const(q):
        """The constant continuum g(N)=q for all N — the ring's units live here (0 = const(0), 1 = const(1))."""
        q = Q(str(q))
        return Continuum(lambda N, _q=q: _q, name=f"const({q})")

    @staticmethod
    def from_gen(gen, name=None):
        """Wrap an arbitrary resolution→ℚ generator as a Continuum."""
        return Continuum(gen, name=name)

    def _coerce(self, other):
        return other if isinstance(other, Continuum) else Continuum.const(other)

    def __add__(self, other):
        o = self._coerce(other)
        return Continuum(lambda N: self.at(N) + o.at(N), name=f"({self.name}+{o.name})")
    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(other)
        return Continuum(lambda N: self.at(N) - o.at(N), name=f"({self.name}-{o.name})")

    def __mul__(self, other):
        o = self._coerce(other)
        return Continuum(lambda N: self.at(N) * o.at(N), name=f"({self.name}*{o.name})")
    __rmul__ = __mul__

    def compose(self, reindex):
        """Re-index the resolution: (a.compose(h)).at(N) = a.at(h(N)). `h` must be N→int≥0 nondecreasing
        to preserve refinement. Lets you accelerate/retard a readout while staying ℚ-primitive."""
        return Continuum(lambda N: self.at(int(reindex(N))), name=f"{self.name}∘reindex")

    def __repr__(self):
        return f"Continuum({self.name})"


# ---- canonical named ℚ-primitive continuums (each a genuine readout, the completed value +ℝ-Open) ----
def geometric(r):
    """The continuum 1/(1−r) built as the partial-sum readout g(N)=Σ_{k<N} rᵏ (exact ℚ). For 0≤r<1 it
    plateaus; the completed sum is its +ℝ-Open appearance. Mirrors the certified geometric readout."""
    r = Q(str(r))
    return Continuum(lambda N, _r=r: sum((_r ** k for k in range(N + 1)), Q(0)), name=f"geometric(r={r})")


def from_sequence(seq):
    """A continuum whose N-th readout is the N-th term of a ℚ sequence `seq` (callable N→ℚ or a list).
    The completed limit stays +ℝ-Open; `.readout(ε)` certifies the plateau or HOLDs."""
    def g(N, _s=seq):
        return _s(N) if callable(_s) else _s[min(N, len(_s) - 1)]
    return Continuum(g, name="from_sequence")
