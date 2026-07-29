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
  * `.readout(ε)` — the ℚ value at the resolution that meets ε, tier-honestly: **CERTIFIED** only when a
                    PROVEN tail bound exists (e.g. `geometric`'s exact rᴺ⁺¹/(1−r), or a proven bound
                    propagated through `+`/`−` by the triangle law); otherwise an OBSERVED plateau is
                    **`finite_diagnostic`** (measured, not proven beyond N); **HOLD** if neither is reached.
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

# A third, HONEST status distinct from CERTIFIED: an OBSERVED plateau over a finite sampled window, with
# NO proof that gaps stay small beyond it. Tier-honesty demands we NOT borrow the project-wide CERTIFIED
# label (which means a *proven* bound |value−target| ≤ bound, e.g. the geometric readout's rᴺ⁺¹/(1−r),
# machine-checked in IDM_Certified.v) for a windowed heuristic. CERTIFIED is emitted ONLY when the
# Continuum carries a proven `tail_bound`; a bare observation is `finite_diagnostic`, never CERTIFIED.
DIAGNOSTIC = "finite_diagnostic"


class Continuum:
    """A continuum value carried as a ℚ readout `g : N → ℚ`. Never an ℝ object; every read is exact ℚ."""
    __slots__ = ("_g", "name", "_tail_bound")

    def __init__(self, gen, name=None, tail_bound=None):
        """`gen` is a callable N(int ≥ 0) → something coercible to Fraction: the exact ℚ readout at
        resolution N (larger N = finer). `name` is a label for reprs only. `tail_bound`, when given, is a
        callable N → ℚ that is a PROVEN bound on |at(N) − (appearance)| — supplying it (and only then) lets
        `.readout` return CERTIFIED; without it a plateau is reported as the honest `finite_diagnostic`."""
        self._g = gen
        self.name = name or "continuum"
        self._tail_bound = tail_bound

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
        """Return the ℚ readout to tolerance `eps`, tier-honestly:

        * If this Continuum carries a PROVEN `tail_bound(N)` (e.g. `geometric`), find the least N with
          `tail_bound(N) ≤ eps` and return **CERTIFIED** `Readout(q=at(N), bound=tail_bound(N))` — a
          genuine proven guarantee, like the geometric readout machine-checked in IDM_Certified.v.
        * Otherwise fall back to an OBSERVED A8 plateau (last `window` successive gaps ≤ eps) and return
          it as **`finite_diagnostic`** (status=DIAGNOSTIC) — honestly labelled 'measured over the sampled
          window, NOT proven beyond N': a flat-then-diverge sequence would land here, never CERTIFIED.
        * If neither a proven bound nor even a windowed plateau is reached within `max_N`, return **HOLD**
          — refusing to emit the completed limit as a number.

        In every case the returned q is 'the ℚ readout at the resolution reached', NOT 'the real limit'
        (which stays +ℝ-Open)."""
        eps = Q(str(eps))
        if eps <= 0:
            return Readout(None, None, HOLD, "tolerance ε must be > 0")

        # proven path — CERTIFIED is legitimate only here (an actual bound, not a heuristic)
        if self._tail_bound is not None:
            for N in range(0, max_N + 1):
                b = Q(str(self._tail_bound(N)))
                if b <= eps:
                    return Readout(self.at(N), b, CERTIFIED,
                                   f"{self.name}: proven tail bound ≤ ε at N={N}; readout at declared "
                                   f"resolution, NOT the completed limit (+ℝ-Open)")
            return Readout(None, None, HOLD,
                           f"{self.name}: proven tail bound never reaches ε within {max_N} refinements")

        # heuristic path — an OBSERVED plateau is finite_diagnostic, never CERTIFIED (no proof beyond N)
        gaps = []
        prev = self.at(0)
        for N in range(1, max_N + 1):
            cur = self.at(N)
            gaps.append(abs(cur - prev))
            if len(gaps) >= window and all(g <= eps for g in gaps[-window:]):
                return Readout(cur, max(gaps[-window:]), DIAGNOSTIC,
                               f"{self.name}: OBSERVED plateau at N={N} (last {window} gaps ≤ ε) — "
                               f"finite_diagnostic, NOT proven beyond N (supply a tail_bound to certify); "
                               f"the completed limit stays +ℝ-Open")
            prev = cur
        return Readout(None, None, HOLD,
                       f"{self.name}: no plateau within {max_N} refinements — the readout does not "
                       f"stabilise to ε (divergence / oscillation / no limit); refusing to emit a number")

    # ---- the ℚ-algebra: every combinator returns another Continuum, exact pointwise over ℚ ---------
    @staticmethod
    def const(q):
        """The constant continuum g(N)=q for all N — the ring's units live here (0 = const(0), 1 = const(1)).
        A constant IS its value, so its proven tail bound is exactly 0 (fully certified, no error)."""
        q = Q(str(q))
        return Continuum(lambda N, _q=q: _q, name=f"const({q})", tail_bound=lambda N: Q(0))

    @staticmethod
    def from_gen(gen, name=None, tail_bound=None):
        """Wrap an arbitrary resolution→ℚ generator as a Continuum. Pass `tail_bound` (a proven N→ℚ bound)
        only if you can prove it — that is what upgrades `.readout` from finite_diagnostic to CERTIFIED."""
        return Continuum(gen, name=name, tail_bound=tail_bound)

    def _coerce(self, other):
        return other if isinstance(other, Continuum) else Continuum.const(other)

    def _combined_tail(self, o):
        """A PROVEN bound for a±b: |(a±b)(N) − (A±B)| ≤ |a(N)−A| + |b(N)−B| (triangle — exactly the
        machine-checked `gap_subadditive`/`Qabs_triangle`). Available only when BOTH sides carry a proven
        bound; otherwise None (the result is an honest finite_diagnostic, never a fabricated certificate)."""
        if self._tail_bound is None or o._tail_bound is None:
            return None
        return lambda N, a=self._tail_bound, b=o._tail_bound: Q(str(a(N))) + Q(str(b(N)))

    def __add__(self, other):
        o = self._coerce(other)
        return Continuum(lambda N: self.at(N) + o.at(N), name=f"({self.name}+{o.name})",
                         tail_bound=self._combined_tail(o))
    __radd__ = __add__

    def __sub__(self, other):
        o = self._coerce(other)
        return Continuum(lambda N: self.at(N) - o.at(N), name=f"({self.name}-{o.name})",
                         tail_bound=self._combined_tail(o))

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
    """The continuum 1/(1−r) built as the partial-sum readout g(N)=Σ_{k≤N} rᵏ (exact ℚ). For 0≤r<1 it
    carries the EXACT PROVEN tail bound |1/(1−r) − g(N)| = rᴺ⁺¹/(1−r) (machine-checked in
    formal/IDM_Certified.v), so `.readout(ε)` returns CERTIFIED. Outside 0≤r<1 there is no proven bound,
    so it is left as a bare (heuristic, finite_diagnostic) readout — honestly not certifiable."""
    r = Q(str(r))
    gen = lambda N, _r=r: sum((_r ** k for k in range(N + 1)), Q(0))
    if 0 <= r < 1:
        tail = lambda N, _r=r: _r ** (N + 1) / (1 - _r)   # exact, proven (IDM_Certified.v geom_series)
        return Continuum(gen, name=f"geometric(r={r})", tail_bound=tail)
    return Continuum(gen, name=f"geometric(r={r})")   # divergent/degenerate → no proven bound, no CERTIFIED


def from_sequence(seq):
    """A continuum whose N-th readout is the N-th term of a ℚ sequence `seq` (callable N→ℚ or a list).
    The completed limit stays +ℝ-Open; `.readout(ε)` certifies the plateau or HOLDs."""
    def g(N, _s=seq):
        return _s(N) if callable(_s) else _s[min(N, len(_s) - 1)]
    return Continuum(g, name="from_sequence")
