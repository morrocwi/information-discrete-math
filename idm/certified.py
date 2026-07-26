"""idm.certified — the Certified Finite-Readout contract.

Each call returns a `Readout(value, bound, status, reason)`: `CERTIFIED` ships a proven bound
`|value − target| ≤ bound ≤ ε`; `HOLD` refuses to emit a number when the hypotheses fail. The
geometric-series and finite-exponential cases are machine-checked axiom-free in
`formal/IDM_Certified.v`. (Thin re-export of the verified `tools/certified_readout.py`.)
"""
from . import _bridge  # noqa: F401
from certified_readout import (
    Readout, CERTIFIED, HOLD,
    geom_series_certified as geom_series,
    exp_certified as exp,
    simpson_certified as simpson,
    richardson_certified as richardson,
    integral_stable_certified as integral,
)

__all__ = ["Readout", "CERTIFIED", "HOLD", "geom_series", "exp", "simpson", "richardson", "integral"]
