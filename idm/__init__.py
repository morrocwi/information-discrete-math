"""Information Discrete Mathematics — the library.

    import idm
    idm.solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
    idm.pi()                         # π as a finite readout
    idm.certified.geom_series(1/3, 1e-12)      # (value, proven bound, ACCEPT/HOLD)
    idm.shortest_path(W)             # min-plus all-pairs

A readout-first foundation: everything read is a finite, discrete, rational readout; the continuum is
reconstructed, never assumed. The finite core is machine-checked axiom-free in `formal/` (120 theorems).
This package is a clean facade over the repository's verified modules — same code CI runs.

Submodules: functions · certified · algebra · readouts · exact · analysis · discrete · integrate ·
diffeq · series · special · transforms · optimize · symbolic · combopt · interval · stats · geometry ·
crypto · parse · rcp · solve · server.
"""
# Single source of truth is pyproject.toml; kept in sync by tests/test_version_consistency.py
# (a CI gate that fails if this string, pyproject, and capabilities.json ever diverge).
__version__ = "1.5.1"

from . import functions, certified, algebra, readouts, exact, analysis, discrete, integrate, diffeq, series, special, transforms, optimize, symbolic, combopt, interval, stats, geometry, crypto, hilbert, hilbert_open, parse as _parse, rcp, solve as _solve

# top-level convenience surface
solve = _solve.solve
kinds = _solve.kinds
parse = _parse.parse                     # world-language → structured problem (or HOLD)
parse_and_solve = _parse.parse_and_solve  # translate, then solve

# typed result + one-call convenience wrappers (Track B — programmer developer-experience)
from .results import Result, SolveHold
from .convenience import (factorize, gcd, solve_integral, integrate_rational, solve_matrix,
                          eigenvalues, solve_roots, solve_ode)
# schema/kind discovery in Python (same introspection as `python -m idm`, returning structured data)
from .discovery import describe, schema, example
# AI Gateway (Track C): a small deterministic entrance over the full solver — idm.ai.run/route/plan,
# plus idm.ai_bench (Phase C: a synthetic tool-use dataset + benchmark harness for a router/model).
from . import ai, ai_bench

# finite elementary + calculus
exp, log, sin, cos, erf, gamma, sqrt = (functions.exp, functions.log, functions.sin, functions.cos,
                                        functions.erf, functions.gamma, functions.sqrt)
pi, e, ln2 = functions.pi, functions.e, functions.ln2
derivative, integral, limit, ode, evaluate = (functions.derivative, functions.integral,
                                              functions.limit, functions.ode, functions.evaluate)

# certified
Readout, CERTIFIED, HOLD = certified.Readout, certified.CERTIFIED, certified.HOLD

# optimization
shortest_path, critical_path, widest_path = (algebra.shortest_path, algebra.critical_path,
                                             algebra.widest_path)
minimax_path, reachability, path_count = algebra.minimax_path, algebra.reachability, algebra.path_count

# readouts
dashboard = readouts.dashboard

def serve(host="127.0.0.1", port=8737):
    """Start the zero-dependency REST solver API (POST /solve, GET /health)."""
    from .server import run
    run(host, port)

__all__ = ["__version__", "solve", "serve", "functions", "certified", "algebra", "readouts", "rcp",
           "exp", "log", "sin", "cos", "erf", "gamma", "sqrt", "pi", "e", "ln2",
           "derivative", "integral", "limit", "ode", "evaluate",
           "Readout", "CERTIFIED", "HOLD",
           "shortest_path", "critical_path", "widest_path", "minimax_path", "reachability",
           "path_count", "dashboard",
           "kinds", "parse", "parse_and_solve",
           "Result", "SolveHold",
           "factorize", "gcd", "solve_integral", "integrate_rational", "solve_matrix",
           "eigenvalues", "solve_roots", "solve_ode",
           "describe", "schema", "example", "ai", "ai_bench"]
