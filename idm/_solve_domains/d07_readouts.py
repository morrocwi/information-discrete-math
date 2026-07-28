# readouts
from idm._solve_core import *  # noqa: F401,F403

@kind("readouts")
def _ro(p):
    data = p["data"]; only = p.get("only"); board = {}
    for name, fn in R.READOUTS.items():
        if only and name not in only: continue
        try: board[name] = _norm(fn(data))
        except Exception as ex: board[name] = {"status": "n/a", "reason": f"{type(ex).__name__}: outside this readout's domain"}
    return {"kind": "readouts", "status": "ok", "value": board, "method": "finite retained aggregations (I_ε with chosen combine rule)"}
