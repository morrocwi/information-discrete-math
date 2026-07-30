"""Public evidence-bearing readout API.

The API separates target certification from finite stability:

``CERTIFIED``
    ``|value - target| <= bound`` is mathematically justified under named
    hypotheses and includes the arithmetic model used by the routine.

``STABLE``
    a finite refinement sequence satisfies an explicitly reported stability
    test; this is not promoted to a proof of distance from a continuum target.

``HOLD``
    the required hypothesis, error enclosure, or resource budget is absent.

See ``docs/READOUT_CERTIFICATION_STANDARD.md`` for the complete claim taxonomy.
"""

from . import _bridge  # noqa: F401
from certified_readout import (
    Readout,
    CERTIFIED,
    STABLE,
    HOLD,
    geom_series_certified as geom_series,
    exp_certified as exp,
    simpson_certified as simpson,
    richardson_certified as richardson,
    richardson_apriori_ratio,
    richardson_apriori_bound,
    richardson_apriori_certified,
    integral_stable_certified as integral,
    integral_nd_stable_certified as integral_nd,
)
from .readout_boundary import (
    Decision,
    DecimalReadout,
    Enclosure,
    parse_decimal_readout,
    certify_threshold,
    exact_det2x2,
    determinant_collision,
)

__all__ = [
    "Readout",
    "CERTIFIED",
    "STABLE",
    "HOLD",
    "geom_series",
    "exp",
    "simpson",
    "richardson",
    "integral",
    "integral_nd",
    "richardson_apriori_ratio",
    "richardson_apriori_bound",
    "richardson_apriori_certified",
    "Decision",
    "DecimalReadout",
    "Enclosure",
    "parse_decimal_readout",
    "certify_threshold",
    "exact_det2x2",
    "determinant_collision",
]
