"""Tests for idm.continuum — the continuum as a first-class ℚ primitive (a readout, never ℝ).

Guards the three things that make it philosophy-sound: every read is EXACT ℚ; the algebra is closed and
exact pointwise (matching the machine-checked laws in formal/IDM_Continuum.v); and it REFUSES (HOLD) at
non-readout points instead of fabricating a completed limit.
"""
import os
import sys
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from idm.continuum import Continuum, geometric, from_sequence, WITNESS, DIAGNOSTIC
from idm.certified import CERTIFIED, HOLD


def test_at_is_always_exact_rational():
    g = geometric("1/2")
    for N in (0, 1, 5, 20):
        assert isinstance(g.at(N), Q)            # never a float / never an ℝ object
    assert g.at(3) == Q(1) + Q(1, 2) + Q(1, 4) + Q(1, 8)   # exact partial sum Σ_{k≤3} (1/2)^k


def test_geometric_is_certified_by_a_PROVEN_tail_bound():
    """geometric(r), 0≤r<1, carries the exact proven bound rᴺ⁺¹/(1−r) (IDM_Certified.v) → CERTIFIED is
    legitimate, and the bound is that exact rational, not a windowed observation."""
    g = geometric("1/2")                          # completed sum = 2 (its +ℝ-Open appearance)
    r = g.readout("1/1000")
    assert r.status == CERTIFIED and isinstance(r.q, Q) and r.bound <= Q(1, 1000)
    assert abs(r.q - 2) <= Q(1, 100)              # the ℚ readout sits near the appearance, exactly rational
    assert "proven tail bound" in r.reason        # certified via the proof, not a heuristic


def test_bare_generator_plateau_is_finite_diagnostic_NOT_certified():
    """A Continuum with NO proven tail_bound may only report an OBSERVED plateau as finite_diagnostic —
    reusing CERTIFIED (a proven-bound label project-wide) for a windowed heuristic would be an overclaim."""
    conv = Continuum.from_gen(lambda N: Q(1, N + 1), name="1/(N+1)")   # → 0, no supplied proof
    r = conv.readout("1/500")
    assert r.status == DIAGNOSTIC and r.status != CERTIFIED
    assert "finite_diagnostic" in r.reason and "NOT proven beyond N" in r.reason


def test_flat_then_diverge_never_certified():
    """Reviewer regression: a sequence flat for a while then diverging must NOT be CERTIFIED. Without a
    proven bound the windowed check can still OBSERVE the flat stretch — but it is labelled
    finite_diagnostic, never CERTIFIED, so no false proof is claimed."""
    trap = Continuum.from_gen(lambda N: Q(0) if N < 5 else Q(N), name="flat-then-diverge")
    r = trap.readout("1/1000")
    assert r.status != CERTIFIED, "a divergent-after-plateau sequence must never be certified"
    assert r.status == DIAGNOSTIC   # honestly a measured observation, explicitly not proven


def test_no_plateau_holds_instead_of_fabricating():
    """A non-convergent readout must HOLD — the honesty fence: no completed limit is ever emitted."""
    osc = Continuum.from_gen(lambda N: Q((-1) ** N), name="osc")   # oscillates, no limit
    assert osc.readout("1/1000").status == HOLD
    assert geometric("1/2").readout("0").status == HOLD           # ε must be > 0


def test_algebra_is_closed_and_exact_pointwise():
    """(a∘b).at(N) is the pointwise ℚ operation — the homomorphism machine-checked as radd_at/rmul_at."""
    a, b = geometric("1/2"), geometric("1/3")
    for N in (0, 2, 7):
        assert (a + b).at(N) == a.at(N) + b.at(N)
        assert (a - b).at(N) == a.at(N) - b.at(N)
        assert (a * b).at(N) == a.at(N) * b.at(N)
        assert (3 * a).at(N) == 3 * a.at(N)          # scalar coercion via const
    # a Continuum + a bare rational coerces (const) and stays exact
    assert (a + Q(1, 5)).at(4) == a.at(4) + Q(1, 5)


def test_const_and_units():
    z, one = Continuum.const(0), Continuum.const("1")
    g = geometric("1/2")
    assert (g + z).at(6) == g.at(6)                  # additive unit
    assert (g * one).at(6) == g.at(6)                # multiplicative unit


def test_sum_of_two_certified_continua_stays_certified_via_propagated_bound():
    """gap_subadditive in action: adding two proven-bounded continua PROPAGATES a proven bound
    (a.tail+b.tail, the triangle inequality) — so the sum is genuinely CERTIFIED, not a heuristic."""
    s = geometric("1/2") + geometric("1/3")          # → 2 + 3/2 = 7/2, both carry proven bounds
    r = s.readout("1/1000")
    assert r.status == CERTIFIED and abs(r.q - Q(7, 2)) <= Q(1, 100)
    assert "proven tail bound" in r.reason

    # but a certified continuum + a BARE one loses the proof → honest finite_diagnostic, never CERTIFIED
    mixed = geometric("1/2") + Continuum.from_gen(lambda N: Q(1, N + 1))
    assert mixed.readout("1/500").status == DIAGNOSTIC


def test_compose_reindexes_resolution():
    g = geometric("1/2")
    faster = g.compose(lambda N: 2 * N)              # read at 2N
    assert faster.at(3) == g.at(6)


def test_from_sequence_and_witness_pointer():
    seq = from_sequence(lambda N: Q(1, N + 1))       # → 0, plateaus but carries no supplied proof
    assert seq.readout("1/500").status == DIAGNOSTIC  # honest: observed, not certified
    # the algebra's soundness is machine-checked; the module names its witness
    assert WITNESS == "formal/IDM_Continuum.v"
    assert os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), WITNESS))


def test_negative_resolution_rejected():
    import pytest
    with pytest.raises(ValueError):
        geometric("1/2").at(-1)
