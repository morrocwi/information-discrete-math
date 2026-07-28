"""Spectral counting by inertia — the retained readout of a level's position (absorbed method).

For a symmetric pencil ``(K, M)`` with ``M`` positive definite and a real shift ``sigma``, the number
of eigenvalues below ``sigma`` is a *readout*, obtained without ever forming an eigenvector or the
spectrum (Sylvester's law of inertia):

    #{eigenvalues of (K, M) below sigma}  =  #{negative pivots of an LDLᵀ factorization of K - sigma*M}.

One banded ``LDLᵀ`` factorization in ``O(n b^2)`` answers it, and **the cost is independent of the
answer** — counting 0 modes or 10,000 modes takes the same work.  This is the operational face of the
READOUT rule (do not construct an object the readout does not require): the retained object is the
running inertia, never the modes.  It is exactly the Sturm sign-count the native tridiagonal kernel in
``retained_spectral/`` already uses, here generalized to a *banded generalized* pencil.

Validity (measured in the source packages, cross-checked here against dense eigensolves):
  * ``M`` positive definite    — exact eigenvalue count.
  * ``M`` positive semidefinite — the pivot count is still exact where a dense generalized ``eigh``
                                  fails; reported honestly, not as a general guarantee.
  * ``M`` indefinite            — this is the *inertia* of ``K - sigma*M``, which is NOT the pencil
                                  eigenvalue count; the caller must not read it as one.
Tier: ``finite_diagnostic`` — a finite rational/float sign-count on a finite operator, cross-checked
numerically; not a machine-checked theorem and not a continuum claim.  The competitive regime is narrow
bands (it crosses over to sparse shift-invert once the band is no longer narrow); dense/3-D-solid
operators are not competitive — an absorbed method, reported with its own limits.

The pivot floor is the LAPACK ``dstebz`` remedy for a shift that annihilates a diagonal exactly: a
zero pivot is replaced by ``-pivmin`` with ``pivmin = eps * max|K - sigma*M|``, signed so the count is
the limit from below (without it the recurrence silently loses a sign — a real defect in the source
work, found and repaired there).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

_EPS = 2.2204460492503131e-16


def to_upper_band(A: np.ndarray, bandwidth: int) -> np.ndarray:
    """Pack a symmetric ``A`` (n×n) into upper-band storage ``kb`` of shape ``(bandwidth+1, n)`` with
    ``kb[j, i] = A[i, i+j]`` (``kb[0]`` the diagonal).  Entries outside the band must already be zero."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    kb = np.zeros((bandwidth + 1, n))
    for j in range(bandwidth + 1):
        for i in range(n - j):
            kb[j, i] = A[i, i + j]
    return kb


def count_below_banded(kb: np.ndarray, mb: np.ndarray, sigma: float) -> int:
    """#eigenvalues of the banded symmetric pencil ``(K, M)`` below ``sigma``, via the inertia of
    ``K - sigma*M`` (banded ``LDLᵀ``, one pass, ``O(n b^2)``).  ``kb``/``mb`` are upper-band arrays of
    shape ``(b+1, n)``; ``M`` should be positive definite for the count to equal the eigenvalue count
    (see the module docstring for the semidefinite/indefinite cases)."""
    kb = np.asarray(kb, dtype=float)
    mb = np.asarray(mb, dtype=float)
    bp1, n = kb.shape
    b = bp1 - 1
    w = kb - sigma * mb                       # the shifted pencil in band form (a fresh working copy)
    scale = float(np.max(np.abs(w))) if w.size else 0.0
    if scale == 0.0:
        scale = 1.0
    pivmin = _EPS * scale
    count = 0
    for i in range(n):
        piv = w[0, i]
        if abs(piv) < pivmin:
            piv = -pivmin                     # signed floor: the count is the limit from below
        if piv < 0.0:
            count += 1
        hi = b if i + b < n else n - 1 - i
        for j in range(1, hi + 1):
            l = w[j, i] / piv
            for m in range(j, hi + 1):
                w[m - j, i + j] -= l * w[m, i]
            w[j, i] = l
    return count


@dataclass(frozen=True)
class ResolvedInertia:
    """A *resolved* inertia readout at a declared resolution — the four-valued (S₄) count that keeps
    the two neutral cases apart instead of folding them into one integer.

    ``count_below_banded`` returns a single ``int``: every pivot inside the floor band is silently
    forced to ``-pivmin`` and counted as *below*.  That collapses two genuinely different situations
    into one number — a pivot that is *certainly* negative (a ``-``) and a pivot the declared
    resolution simply *cannot sign* (a ``⊥``).  A resolved count reports them separately, so the true
    count is returned as an interval ``[certain_below, certain_below + unresolved]`` rather than a point
    that hides its own uncertainty.  This is the four-valued discipline of
    ``formal/IDM_ReadoutMinimality.v`` (``0`` — determinate neutral — vs ``⊥`` — unresolved) made
    operational, and it is what closes the silent-failure mode behind the non-monotone-count defect the
    pivot floor exists to repair (a shift that annihilates a diagonal exactly).

    At a *positive* resolution the reading never emits a determinate ``0``: an exact null pivot cannot be
    certified as distinct from a tiny ``±`` below the floor, so it is reported honestly as ``⊥``
    (unresolved), never as a certain neutral.  ``certain_below`` and ``certain_above`` are
    resolution-safe — a reported strict sign is a true strict sign (proved for the discrete model in
    ``formal/IDM_ResolvedCount.v``: ``classify_plus_sound`` / ``classify_minus_sound``)."""

    certain_below: int          # pivots certainly negative (a resolution-safe ``-``)
    certain_above: int          # pivots certainly positive (a resolution-safe ``+``)
    unresolved: int             # pivots the declared resolution cannot sign (the ``⊥`` set)
    floor: float                # the norm-scaled pivot floor actually used (the declared resolution)

    def count_interval(self) -> tuple[int, int]:
        """The honest bracket on ``#{eigenvalues below sigma}``: at least ``certain_below`` (the pivots
        already known negative), at most ``certain_below + unresolved`` (if every unresolved pivot were
        in fact negative).  The classic single-int ``count_below_banded`` is the *upper* end."""
        return (self.certain_below, self.certain_below + self.unresolved)


def resolved_count_below(kb: np.ndarray, mb: np.ndarray, sigma: float,
                         rel_eps: float = _EPS) -> ResolvedInertia:
    """Four-valued (S₄) inertia readout of the banded pencil ``(K, M)`` at shift ``sigma`` — same one-
    pass ``O(n b^2)`` banded ``LDLᵀ`` as ``count_below_banded``, but classifying each pivot as a
    certain ``+`` / certain ``-`` / unresolved ``⊥`` at the declared resolution ``rel_eps``, instead of
    folding the band into the count.  ``floor = rel_eps * max|K - sigma*M|`` is the norm-scaled pivot
    floor (the resolution at which a sign is *declared* decidable).  Returns a :class:`ResolvedInertia`;
    its ``count_interval()`` brackets the true ``#below`` and its upper end equals the legacy count."""
    kb = np.asarray(kb, dtype=float)
    mb = np.asarray(mb, dtype=float)
    bp1, n = kb.shape
    b = bp1 - 1
    w = kb - sigma * mb                       # the shifted pencil in band form (a fresh working copy)
    scale = float(np.max(np.abs(w))) if w.size else 0.0
    if scale == 0.0:
        scale = 1.0
    pivmin = rel_eps * scale
    below = above = unresolved = 0
    for i in range(n):
        piv = w[0, i]
        if abs(piv) <= pivmin:
            unresolved += 1                   # ⊥: the declared resolution does not decide this sign
            piv = -pivmin                     # signed floor keeps the recurrence going (limit from below)
        elif piv < 0.0:
            below += 1                        # a certain negative pivot
        else:
            above += 1                        # a certain positive pivot
        hi = b if i + b < n else n - 1 - i
        for j in range(1, hi + 1):
            l = w[j, i] / piv
            for m in range(j, hi + 1):
                w[m - j, i + j] -= l * w[m, i]
            w[j, i] = l
    return ResolvedInertia(below, above, unresolved, pivmin)


def count_below_dense(K, M, sigma: float, bandwidth: int | None = None) -> int:
    """Convenience wrapper: ``count_below_banded`` for dense symmetric ``K, M`` (n×n).  ``bandwidth``
    defaults to the true half-bandwidth of ``K``/``M`` (found from their nonzero structure)."""
    K = np.asarray(K, dtype=float)
    M = np.asarray(M, dtype=float)
    n = K.shape[0]
    if bandwidth is None:
        bandwidth = 0
        for i in range(n):
            for j in range(i + 1, n):
                if K[i, j] != 0.0 or M[i, j] != 0.0:
                    bandwidth = max(bandwidth, j - i)
    return count_below_banded(to_upper_band(K, bandwidth), to_upper_band(M, bandwidth), sigma)


def resolved_count_dense(K, M, sigma: float, bandwidth: int | None = None,
                         rel_eps: float = _EPS) -> ResolvedInertia:
    """Convenience wrapper: :func:`resolved_count_below` for dense symmetric ``K, M`` (n×n)."""
    K = np.asarray(K, dtype=float)
    M = np.asarray(M, dtype=float)
    n = K.shape[0]
    if bandwidth is None:
        bandwidth = 0
        for i in range(n):
            for j in range(i + 1, n):
                if K[i, j] != 0.0 or M[i, j] != 0.0:
                    bandwidth = max(bandwidth, j - i)
    return resolved_count_below(to_upper_band(K, bandwidth), to_upper_band(M, bandwidth),
                                sigma, rel_eps=rel_eps)


def eigenvalues_below_count(kb, mb, lo: float, hi: float, k: int, tol: float = 1e-10):
    """The lowest ``k`` eigenvalues of the pencil in ``[lo, hi)``, by bisection on the inertia count —
    each bracket step is one ``count_below_banded``.  Returns a list of ``k`` bracketing midpoints.
    Demonstrates that the eigenvalue solve is *built from* the count readout, nothing more."""
    values = []
    for t in range(k):
        a, b = lo, hi
        for _ in range(200):
            if b - a <= tol:
                break
            mid = 0.5 * (a + b)
            if count_below_banded(kb, mb, mid) > t:
                b = mid
            else:
                a = mid
        values.append(0.5 * (a + b))
    return values


__all__ = ["to_upper_band", "count_below_banded", "count_below_dense", "eigenvalues_below_count",
           "ResolvedInertia", "resolved_count_below", "resolved_count_dense"]
