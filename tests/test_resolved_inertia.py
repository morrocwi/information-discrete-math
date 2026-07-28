"""P4 — the resolved (four-valued) inertia readout: 0 (determinate) vs ⊥ (unresolved).

The classic ``count_below_banded`` returns a single integer: every pivot inside the floor band is
forced to ``-pivmin`` and counted as *below*.  That silently folds two different situations into one
number — a pivot that is certainly negative and a pivot the declared resolution cannot sign.  The
resolved readout keeps them apart (``retained_spectral/inertia.py``; discrete core machine-checked in
``formal/IDM_ResolvedCount.v``), so the true count is returned as an honest interval
``[certain_below, certain_below + unresolved]`` and the classic single integer is its *upper* end.

This is the operational payoff of the four-valued value algebra (``formal/IDM_ReadoutMinimality.v``):
``0`` is a determinate balance (a fact about the object) while ``⊥`` is unresolved (a fact about the
instrument's resolution).  The tests below run the real numerics and check exactly that.
"""

import pytest

np = pytest.importorskip("numpy")             # bench-only dep (retained_spectral extra)

from retained_spectral.inertia import (
    count_below_banded,
    resolved_count_below,
    resolved_count_dense,
    to_upper_band,
)


def _true_below(K, sigma):
    """Ground truth for M = I: #{eigenvalues of symmetric K strictly below sigma}, via a dense solve."""
    w = np.linalg.eigvalsh((K + K.T) / 2)
    return int(np.count_nonzero(w < sigma))


def _tridiag(diag, off):
    n = len(diag)
    K = np.diag(np.asarray(diag, dtype=float))
    for i in range(n - 1):
        K[i, i + 1] = K[i + 1, i] = off[i]
    return K


# --------------------------------------------------------------------------- #
#  1. The interval always brackets the truth, and its upper end IS the legacy   #
#     count.  When nothing is unresolved, the certain count is already exact.   #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("seed", range(8))
def test_interval_brackets_truth_and_upper_end_is_legacy(seed):
    rng = np.random.default_rng(seed)
    n = 30
    diag = rng.uniform(-2.0, 2.0, n)
    off = rng.uniform(-1.0, 1.0, n - 1)
    K = _tridiag(diag, off)
    I = np.eye(n)
    kb, mb = to_upper_band(K, 1), to_upper_band(I, 1)
    for sigma in rng.uniform(-3.0, 3.0, 12):
        r = resolved_count_below(kb, mb, float(sigma))
        lo, hi = r.count_interval()
        truth = _true_below(K, sigma)
        assert lo <= truth <= hi, (lo, truth, hi, sigma)
        # the classic single-int count is exactly the upper end of the honest interval
        assert hi == count_below_banded(kb, mb, float(sigma))
        # a fully resolved reading (no ⊥) is exact
        if r.unresolved == 0:
            assert r.certain_below == truth


# --------------------------------------------------------------------------- #
#  2. A shift that annihilates the diagonal EXACTLY is the case the pivot floor  #
#     exists for.  The legacy count reports every floored pivot as below (a      #
#     point estimate that is wrong for the true count); the resolved readout     #
#     instead surfaces them as ⊥ — "0 certain, n unresolved" — which honestly    #
#     brackets the truth.  This is the silent-failure mode made visible.        #
# --------------------------------------------------------------------------- #
def test_exact_annihilation_is_reported_as_unresolved_not_folded():
    n = 8
    K = 2.0 * np.eye(n)          # K - 2 I is the exact zero matrix: every pivot annihilated
    I = np.eye(n)
    r = resolved_count_dense(K, I, sigma=2.0)
    truth = _true_below(K, 2.0)  # eigenvalues all == 2, none strictly below -> 0
    assert truth == 0
    assert r.certain_below == 0          # nothing is CERTAINLY below
    assert r.unresolved == n             # every pivot is honestly ⊥ at this resolution
    lo, hi = r.count_interval()
    assert lo <= truth <= hi             # the interval [0, n] brackets the truth
    # the legacy single integer folds all n into "below" — the upper end, honest only as a bound
    assert count_below_dense_equiv(K, I, 2.0) == n


def count_below_dense_equiv(K, I, sigma):
    n = K.shape[0]
    return count_below_banded(to_upper_band(K, 0), to_upper_band(I, 0), sigma)


# --------------------------------------------------------------------------- #
#  3. Monotonicity in the shift: as sigma rises, both the certain-below count    #
#     and the legacy (certain+unresolved) count are non-decreasing.  This is the #
#     behaviour the norm-scaled pivot floor is there to preserve (the founder's  #
#     underflow-floor defect was a SILENT loss of this monotonicity).           #
# --------------------------------------------------------------------------- #
def test_certain_and_legacy_counts_are_monotone_in_sigma():
    rng = np.random.default_rng(11)
    n = 40
    K = _tridiag(rng.uniform(-2, 2, n), rng.uniform(-1, 1, n - 1))
    I = np.eye(n)
    kb, mb = to_upper_band(K, 1), to_upper_band(I, 1)
    sigmas = np.linspace(-4.0, 4.0, 60)
    prev_certain = -1
    prev_legacy = -1
    for s in sigmas:
        r = resolved_count_below(kb, mb, float(s))
        legacy = count_below_banded(kb, mb, float(s))
        assert r.certain_below >= prev_certain          # non-decreasing
        assert legacy >= prev_legacy
        assert r.count_interval()[1] == legacy
        prev_certain, prev_legacy = r.certain_below, legacy


# --------------------------------------------------------------------------- #
#  4. The three counts partition the whole spectrum: certain_below +            #
#     certain_above + unresolved == n, always (S₄ is total on the pivots).      #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("seed", range(5))
def test_counts_partition_all_pivots(seed):
    rng = np.random.default_rng(100 + seed)
    n = 25
    K = _tridiag(rng.uniform(-2, 2, n), rng.uniform(-1, 1, n - 1))
    I = np.eye(n)
    r = resolved_count_dense(K, I, sigma=float(rng.uniform(-3, 3)))
    assert r.certain_below + r.certain_above + r.unresolved == n
