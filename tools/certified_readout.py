#!/usr/bin/env python3
"""Certified and stability-qualified finite readouts.

The module deliberately distinguishes two kinds of evidence:

``CERTIFIED``
    A mathematical target is enclosed by a proved bound. Every source of
    arithmetic error used by the routine is included in the contract, or the
    routine returns ``HOLD``.

``STABLE``
    A finite refinement sequence exhibits a declared stability pattern. This
    is useful diagnostic evidence, but it is not silently promoted to a proof
    of distance from a continuum target.

``HOLD``
    The hypotheses or resource budget required for either claim are absent.

The distinction is essential: observed contraction can justify a conditional
stability envelope, but finite observations alone do not prove the asymptotic
model continues forever.
"""

from __future__ import annotations

from fractions import Fraction as Q
from numbers import Rational

try:
    import mpmath as mp

    mp.mp.dps = 50
    _HAVE_MP = True
except Exception:  # pragma: no cover - optional dependency
    mp = None
    _HAVE_MP = False

CERTIFIED, STABLE, HOLD = "CERTIFIED", "STABLE", "HOLD"


class Readout:
    """A value, an evidence bound, a status, and a human-readable reason."""

    __slots__ = ("q", "bound", "status", "reason")

    def __init__(self, q, bound, status, reason):
        if status not in (CERTIFIED, STABLE, HOLD):
            raise ValueError(f"unknown readout status: {status!r}")
        self.q, self.bound, self.status, self.reason = q, bound, status, reason

    def __repr__(self):
        if self.status == HOLD:
            return f"Readout(HOLD — {self.reason})"
        label = "target certified" if self.status == CERTIFIED else "finite stability"
        return f"Readout(q={self.q}, bound={self.bound}, {self.status} — {label}: {self.reason})"

    @property
    def certified(self):
        """True only for a proved target enclosure."""

        return self.status == CERTIFIED

    @property
    def stable(self):
        """True only for a finite-stability diagnostic."""

        return self.status == STABLE

    @property
    def accepted(self):
        """True for either explicit evidence-bearing success status."""

        return self.status in (CERTIFIED, STABLE)


def _fraction(value):
    """Convert a finite input to an exact rational representation.

    Strings and decimal-like objects are interpreted through their text.
    Python floats are converted to their exact dyadic value; callers who want
    exact decimal source semantics should pass a string such as ``"0.1"``.
    """

    if isinstance(value, Q):
        return value
    if isinstance(value, Rational):
        return Q(value)
    if isinstance(value, float):
        return Q.from_float(value)
    return Q(str(value))


def geom_series_certified(r, eps, max_terms=1_000_000):
    """Certify ``sum(r**k, k>=0)`` for ``0 <= r < 1`` using exact rationals."""

    try:
        r, eps = _fraction(r), _fraction(eps)
    except Exception as exc:
        return Readout(None, None, HOLD, f"inputs are not finite rationals: {exc}")
    if not (0 <= r < 1):
        return Readout(None, None, HOLD, f"geometric series needs 0≤r<1 (got r={r})")
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")

    n = 1
    power = r
    while power / (1 - r) > eps:
        if n >= max_terms:
            return Readout(None, None, HOLD, f"resource limit reached at {max_terms} terms")
        n += 1
        power *= r
    total = Q(0)
    term = Q(1)
    for _ in range(n):
        total += term
        term *= r
    bound = power / (1 - r)
    return Readout(total, bound, CERTIFIED, f"exact rational tail r^{n}/(1-r)")


def exp_certified(x, eps, max_terms=100_000):
    """Certify the exponential power series for a finite rational input.

    The partial sum is evaluated exactly in ``Q``. If the first omitted term
    is ``t`` and ``rho = |x|/(N+2) < 1``, all later term ratios are at most
    ``rho``; therefore the absolute tail is at most ``t/(1-rho)``.
    """

    try:
        x, eps = _fraction(x), _fraction(eps)
    except Exception as exc:
        return Readout(None, None, HOLD, f"inputs are not finite rationals: {exc}")
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")

    total = Q(1)
    term = Q(1)
    ax = abs(x)
    n = 0
    while True:
        first_omitted = abs(term * x / (n + 1))
        rho = ax / (n + 2)
        if rho < 1:
            bound = first_omitted / (1 - rho)
            if bound <= eps:
                return Readout(total, bound, CERTIFIED,
                               f"exact Taylor sum through N={n}; geometric majorant of the tail")
        if n >= max_terms:
            return Readout(None, None, HOLD, f"resource limit reached at {max_terms} Taylor terms")
        n += 1
        term = term * x / n
        total += term


def simpson_certified(f, a, b, eps, d4_bound=None, max_panels=1_000_000):
    """Composite Simpson rule with an exact arithmetic and truncation certificate.

    Certification requires a caller-supplied bound ``M4 >= max |f''''|`` and
    exact-rational function values at every quadrature node. If the callable
    returns a float or another inexact type, the routine fails closed.
    """

    try:
        a, b, eps = _fraction(a), _fraction(b), _fraction(eps)
    except Exception as exc:
        return Readout(None, None, HOLD, f"endpoints/tolerance are not finite rationals: {exc}")
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if d4_bound is None:
        return Readout(None, None, HOLD, "a proved bound on max|f''''| is required")
    try:
        m4 = _fraction(d4_bound)
    except Exception as exc:
        return Readout(None, None, HOLD, f"invalid fourth-derivative bound: {exc}")
    if m4 < 0:
        return Readout(None, None, HOLD, "fourth-derivative magnitude bound must be non-negative")

    length = abs(b - a)
    panels = 2
    while length**5 * m4 / (180 * panels**4) > eps:
        panels += 2
        if panels > max_panels:
            return Readout(None, None, HOLD, f"resource limit exceeded ({max_panels} panels)")

    h = (b - a) / panels
    try:
        values = [f(a + i * h) for i in range(panels + 1)]
        if not all(isinstance(v, Rational) for v in values):
            return Readout(None, None, HOLD,
                           "function values are not exact rationals; use interval arithmetic or a diagnostic path")
        values = [Q(v) for v in values]
    except Exception as exc:
        return Readout(None, None, HOLD, f"function evaluation failed: {exc}")

    total = values[0] + values[-1]
    total += sum((Q(4) if i % 2 else Q(2)) * values[i] for i in range(1, panels))
    estimate = total * h / 3
    bound = length**5 * m4 / (180 * panels**4)
    return Readout(estimate, bound, CERTIFIED,
                   f"exact-rational composite Simpson, N={panels}, supplied M4 hypothesis")


def richardson_certified(seq, eps, M=2, K=12):
    """Historical API: return a finite-stability diagnostic, never a target proof.

    The name is retained for compatibility. Finite observed contraction is
    reported as ``STABLE`` because it does not prove that the asymptotic model
    continues beyond the observed refinements.
    """

    if not _HAVE_MP:
        return Readout(None, None, HOLD, "Richardson diagnostic needs mpmath")
    eps = mp.mpf(eps)
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if K < 3:
        return Readout(None, None, HOLD, "at least three Richardson levels are required")
    try:
        col = [mp.mpf(seq(M * 2**j)) for j in range(K)]
    except Exception as exc:
        return Readout(None, None, HOLD, f"sequence evaluation failed: {exc}")

    diag = [col[-1]]
    for p in range(1, K):
        col = [((1 << p) * col[i + 1] - col[i]) / ((1 << p) - 1) for i in range(len(col) - 1)]
        diag.append(col[-1])
    gaps = [abs(diag[i + 1] - diag[i]) for i in range(len(diag) - 1)]
    tail = gaps[len(gaps) // 2 :]
    ratios = [tail[i + 1] / tail[i] for i in range(len(tail) - 1) if tail[i] > 0]
    if not tail or tail[-1] > eps or not ratios or max(ratios) >= 1:
        return Readout(None, None, HOLD, "observed Richardson tail is not contracting below ε")
    rho = max(ratios)
    model_bound = tail[-1] / (1 - rho)
    return Readout(diag[-1], model_bound, STABLE,
                   f"observed Richardson contraction; bound is conditional on continued ratio ≤ {mp.nstr(rho, 4)}")


def richardson_apriori_ratio(order):
    """Nominal ratio ``2**(-order)`` for an order-p asymptotic model."""

    if order < 1:
        raise ValueError("method order must be at least 1")
    return Q(1, 2**order)


def richardson_apriori_bound(gap, order):
    """Conditional geometric-tail envelope under an explicitly assumed ratio."""

    gap = _fraction(gap)
    if gap < 0:
        raise ValueError("gap magnitude must be non-negative")
    rho = richardson_apriori_ratio(order)
    return gap / (1 - rho)


def richardson_apriori_certified(gap, order, eps):
    """Return ``STABLE`` when the conditional model envelope is below ε.

    Method order alone does not prove that a concrete sequence has entered its
    asymptotic regime, so this routine does not issue ``CERTIFIED``.
    """

    try:
        gap, eps = _fraction(gap), _fraction(eps)
        bound = richardson_apriori_bound(gap, order)
    except Exception as exc:
        return Readout(None, None, HOLD, str(exc))
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if bound <= eps:
        return Readout(None, bound, STABLE,
                       f"conditional order-{order} geometric-tail model; asymptotic entry not proved")
    return Readout(None, bound, HOLD, f"conditional model bound {bound} exceeds ε")


def _trapezoid(f, a, b, n):
    h = (b - a) / n
    return h * (f(a) / 2 + f(b) / 2 + sum(f(a + i * h) for i in range(1, n)))


def _stability_readout(values, eps, label):
    gaps = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    tail = gaps[len(gaps) // 2 :]
    if len(tail) < 2:
        return Readout(None, None, HOLD, "too few refinements to assess finite stability")
    if max(tail) == 0:
        return Readout(values[-1], mp.mpf(0), STABLE,
                       f"{label}: observed refinement gaps vanished; no target-exactness claim")
    ratios = [tail[i + 1] / tail[i] for i in range(len(tail) - 1) if tail[i] > 0]
    if not ratios or max(ratios) >= 1:
        return Readout(None, None, HOLD, f"{label}: observed refinement gaps do not contract")
    rho = max(ratios)
    model_bound = gaps[-1] / (1 - rho)
    if model_bound <= eps:
        return Readout(values[-1], model_bound, STABLE,
                       f"{label}: finite contraction observed; envelope conditional on continuation")
    return Readout(None, model_bound, HOLD, f"{label}: conditional stability envelope exceeds ε")


def integral_stable_certified(f, a, b, eps, n0=8, refines=14):
    """Finite trapezoid stability diagnostic (historical name retained)."""

    if not _HAVE_MP:
        return Readout(None, None, HOLD, "integral stability diagnostic needs mpmath")
    a, b, eps = mp.mpf(a), mp.mpf(b), mp.mpf(eps)
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if n0 < 1 or refines < 3:
        return Readout(None, None, HOLD, "n0>=1 and at least three refinements are required")
    values, n = [], n0
    for _ in range(refines):
        try:
            values.append(_trapezoid(f, a, b, n))
        except Exception as exc:
            return Readout(None, None, HOLD, f"integrand is not finitely samplable: {exc}")
        n *= 2
    return _stability_readout(values, eps, "trapezoid refinement")


def _tensor_trapezoid(f, box, n):
    import itertools

    dimensions = len(box)
    hs = [(mp.mpf(b) - mp.mpf(a)) / n for a, b in box]
    lows = [mp.mpf(a) for a, _ in box]
    total = mp.mpf(0)
    for index in itertools.product(range(n + 1), repeat=dimensions):
        weight = mp.mpf(1)
        point = []
        for axis, i in enumerate(index):
            point.append(lows[axis] + i * hs[axis])
            if i in (0, n):
                weight /= 2
        total += weight * f(tuple(point))
    volume = mp.mpf(1)
    for h in hs:
        volume *= h
    return total * volume


def integral_nd_stable_certified(f, box, eps, n0=4, refines=6):
    """Finite tensor-trapezoid stability diagnostic (historical name retained)."""

    if not _HAVE_MP:
        return Readout(None, None, HOLD, "n-D integral stability diagnostic needs mpmath")
    eps = mp.mpf(eps)
    if eps <= 0:
        return Readout(None, None, HOLD, "tolerance ε must be > 0")
    if not box:
        return Readout(None, None, HOLD, "empty integration box")
    if n0 < 1 or refines < 3:
        return Readout(None, None, HOLD, "n0>=1 and at least three refinements are required")
    values, n = [], n0
    for _ in range(refines):
        try:
            values.append(_tensor_trapezoid(f, box, n))
        except Exception as exc:
            return Readout(None, None, HOLD, f"integrand is not finitely samplable: {exc}")
        n *= 2
    return _stability_readout(values, eps, f"{len(box)}-D tensor trapezoid")


if __name__ == "__main__":
    checks = []

    geometric = geom_series_certified(Q(1, 3), Q(1, 10**12))
    checks.append(("geometric target certificate", geometric.certified and abs(geometric.q - Q(3, 2)) <= geometric.bound))

    exponential = exp_certified("0.4", "1e-20")
    if _HAVE_MP:
        checks.append(("exponential target certificate",
                       exponential.certified and abs(mp.mpf(exponential.q.numerator) / exponential.q.denominator - mp.e**mp.mpf("0.4"))
                       <= mp.mpf(exponential.bound.numerator) / exponential.bound.denominator))
    else:
        checks.append(("exponential exact-rational path", exponential.certified))

    simpson = simpson_certified(lambda t: t**2, 0, 3, Q(1, 10**9), d4_bound=0)
    checks.append(("Simpson exact-rational target certificate", simpson.certified and simpson.q == 9))

    conditional = richardson_apriori_certified(Q(1, 10**8), 2, Q(1, 10**6))
    checks.append(("a-priori Richardson is STABLE, not CERTIFIED", conditional.status == STABLE))

    if _HAVE_MP:
        integral = integral_stable_certified(lambda t: t*t, 0, 1, mp.mpf("1e-6"))
        checks.append(("integral refinement is STABLE, not CERTIFIED", integral.status == STABLE))
        pole = integral_stable_certified(lambda t: 1 / (t - mp.mpf("0.5")), 0, 1, mp.mpf("1e-6"))
        checks.append(("integral with sampled pole -> HOLD", pole.status == HOLD))

    for name, ok in checks:
        print(f"  {'ok ' if ok else 'FAIL'} {name}")
    passed = all(ok for _, ok in checks)
    print(f"certified_readout self-check: {'PASS' if passed else 'FAIL'} ({sum(ok for _, ok in checks)}/{len(checks)})")
    raise SystemExit(0 if passed else 1)
