# constants & functions
from idm._solve_core import *  # noqa: F401,F403

_CONST = {"pi": F.pi, "e": F.e, "ln2": F.ln2}
@kind("constant")
def _c(p): return _ok("constant", _CONST[p["name"]](), "finite series (Machin/Taylor/atanh)", name=p["name"])
@kind("function")
def _fneval(p):
    fmap = {"exp": F.exp, "log": F.log, "ln": F.log, "sin": F.sin, "cos": F.cos, "erf": F.erf, "gamma": F.gamma, "sqrt": F.sqrt}
    return _ok("function", fmap[p["name"]](_val(p["x"])), f"finite {p['name']}", name=p["name"])
@kind("evaluate")
def _ev(p): return _ok("evaluate", F.evaluate(str(p["expr"]), **{k: _val(v) for k, v in p.get("vars", {}).items()}), "locked finite namespace eval")
