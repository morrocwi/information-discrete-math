"""idm.functions — finite elementary functions and discrete calculus.

Every function is a finite-discrete readout (finite series, finite differences/quadrature, Richardson),
the same primitives the repo proves and tests. `math_namespace()` is the locked, finite evaluation
environment the solver uses for string integrands/expressions — so even a user's `exp(-x**2)` is
computed finitely, never by a continuum library call.
"""
from . import _bridge  # noqa: F401  (sets up the path)

try:
    import mpmath as mp
    _kernel = __import__("_kernel")     # provefull/_kernel.py — finite exp/log/sin/cos/erf/gamma/quad/…
    _HAVE = True
except Exception:                        # pragma: no cover
    _HAVE = False

import idm_tools as _T                    # D_eps, I_eps, richardson_1_over_n, ode_rk4 (shipped, tested)

# ---- finite elementary functions (readouts) ----
if _HAVE:
    def exp(x):  return _kernel.exp_finite(x)
    def log(x):  return _kernel.log_finite(x)
    def sin(x):  return _kernel.sin_finite(x)
    def cos(x):  return _kernel.cos_finite(x)
    def erf(x):  return _kernel.erf_finite(x)
    def gamma(z): return _kernel.gamma_finite(z)
    def sqrt(x): return mp.sqrt(x)
    def pi():    return _kernel.PI_FINITE
    def e():     return _kernel.E_FINITE
    def ln2():   return _kernel.LN2_FINITE
else:  # pragma: no cover
    import math
    exp, log, sin, cos, sqrt = math.exp, math.log, math.sin, math.cos, math.sqrt
    def erf(x): return math.erf(x)
    def gamma(z): return math.gamma(z)
    def pi(): return math.pi
    def e(): return math.e
    def ln2(): return math.log(2)

# ---- discrete calculus (finite operators) ----
def derivative(f, x, h=None):
    """d/dx f at x — finite central difference D_ε with Richardson (the framework's D_ε)."""
    return _T.D_eps(f, x) if h is None else _T.D_eps(f, x, h)

def integral(f, a, b, N=400):
    """∫_a^b f — finite quadrature I_ε (FTCC-exact aggregation)."""
    return _T.I_eps(f, a, b, N)

def limit(seq, M=4, K=13):
    """lim seq(n) — Richardson extrapolation on h=1/n (A8-stable plateau)."""
    return _T.richardson_1_over_n(seq, M, K)

def ode(f, x0, y0, xT, N=400):
    """solve y'=f(x,y), y(x0)=y0 at xT — finite RK4 (= I_ε of the field)."""
    return _T.ode_rk4(f, x0, y0, xT, N)

def math_namespace():
    """The LOCKED finite evaluation namespace for string expressions/integrands used by the solver.
    No builtins, no continuum library — only our finite readouts + arithmetic."""
    ns = {"exp": exp, "log": log, "ln": log, "sin": sin, "cos": cos, "erf": erf,
          "gamma": gamma, "sqrt": sqrt, "pi": pi(), "e": e(), "abs": abs, "pow": pow}
    if _HAVE:
        ns["mpf"] = mp.mpf
    return ns

def evaluate(expr, **vars):
    """Evaluate a string expression at given variables using ONLY the finite namespace. Safe: no builtins."""
    ns = math_namespace(); ns.update(vars)
    return eval(compile(expr, "<idm-expr>", "eval"), {"__builtins__": {}}, ns)
