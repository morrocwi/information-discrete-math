"""Exact finite feasible-set reconstruction for noisy readouts.

This module gives a native finite alternative to real-root existence claims.

Let A={x_1,...,x_m} be an explicitly declared finite admissible record set and let
S(x_i) be explicitly supplied finite readout records.  For observed readout y with
certified radius sigma (and optional finite model radius tau), define

    F(y) = {x_i in A : ||S(x_i)-y||_inf <= sigma+tau}.

F is a finite object.  Its nonemptiness is witnessed by an actual retained record, and
its state-space diameter/radius can be computed exactly with rational arithmetic.  No
completeness of R, infinite contraction sequence, or completed-infinity object is used.

This primitive does not assert that physical reality belongs to A.  Membership of the
declared target in A is a separate modelling/admissibility statement.  It also does not
make exhaustive search efficient; it is a correctness primitive.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def _q(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def _vec(v: Sequence[object]) -> tuple[Fraction, ...]:
    out = tuple(_q(x) for x in v)
    if not out:
        raise ValueError("vectors must be nonempty")
    return out


def inf_distance(a: Sequence[object], b: Sequence[object]) -> Fraction:
    aa, bb = _vec(a), _vec(b)
    if len(aa) != len(bb):
        raise ValueError("vector dimension mismatch")
    return max(abs(x - y) for x, y in zip(aa, bb))


def certify_finite_feasible_set(
    *,
    records: Sequence[Sequence[object]],
    readouts: Sequence[Sequence[object]],
    observation: Sequence[object],
    measurement_radius: object,
    model_radius: object = 0,
    witness_index: int | None = None,
) -> dict:
    """Return the exact finite set of records consistent with one readout box.

    ``records[i]`` and ``readouts[i]`` are a declared finite lookup relation.  A record
    is feasible when its readout lies within ``measurement_radius + model_radius`` of
    the observation in infinity norm.
    """
    if len(records) != len(readouts):
        raise ValueError("records/readouts length mismatch")
    if not records:
        raise ValueError("finite admissible set must be nonempty")

    rr = [_vec(x) for x in records]
    yy = [_vec(y) for y in readouts]
    obs = _vec(observation)
    state_dim = len(rr[0])
    readout_dim = len(obs)
    if any(len(x) != state_dim for x in rr):
        raise ValueError("state record dimensions must agree")
    if any(len(y) != readout_dim for y in yy):
        raise ValueError("readout dimensions must agree with observation")

    sigma = _q(measurement_radius)
    tau = _q(model_radius)
    if sigma < 0 or tau < 0:
        raise ValueError("uncertainty radii must be nonnegative")
    effective = sigma + tau

    residuals = [inf_distance(y, obs) for y in yy]
    feasible = [i for i, r in enumerate(residuals) if r <= effective]
    if not feasible:
        return {
            "status": "HOLD",
            "finite_native": True,
            "feasible_indices": [],
            "feasible_count": 0,
            "reason": "no declared finite admissible record lies in the readout box",
        }

    if witness_index is None:
        w = feasible[0]
    else:
        if witness_index not in feasible:
            raise ValueError("witness_index must identify a feasible record")
        w = int(witness_index)

    diameter = Fraction(0)
    witness_radius = Fraction(0)
    for i in feasible:
        witness_radius = max(witness_radius, inf_distance(rr[i], rr[w]))
        for j in feasible:
            diameter = max(diameter, inf_distance(rr[i], rr[j]))

    return {
        "status": "CERTIFIED_FINITE_SET",
        "finite_native": True,
        "admissible_count": len(rr),
        "feasible_indices": feasible,
        "feasible_count": len(feasible),
        "witness_index": w,
        "measurement_radius": sigma,
        "model_radius": tau,
        "effective_readout_radius": effective,
        "witness_state_radius": witness_radius,
        "feasible_diameter": diameter,
        "residuals": residuals,
        "reason": "feasible set, nonemptiness witness and state-space spread computed by exhaustive finite rational comparison",
    }


def conditional_inverse_feasible_bound(
    *,
    inverse_factor: object,
    effective_readout_radius: object,
) -> dict:
    """Finite triangle bound for any two feasible records under a supplied inverse factor.

    If a separately certified pairwise inverse inequality on the declared finite domain
    has factor alpha, then two records whose readouts are each within eta of the same
    observation differ by at most 2*alpha*eta.  This is only finite arithmetic; the
    validity/scope of the supplied inverse factor is a caller obligation.
    """
    alpha = _q(inverse_factor)
    eta = _q(effective_readout_radius)
    if alpha < 0 or eta < 0:
        raise ValueError("inverse factor and radius must be nonnegative")
    return {
        "status": "FINITE_BOUND",
        "finite_native": True,
        "inverse_factor": alpha,
        "effective_readout_radius": eta,
        "feasible_diameter_upper_bound": 2 * alpha * eta,
        "reason": "finite readout triangle inequality composed with a separately supplied pairwise inverse factor",
    }
