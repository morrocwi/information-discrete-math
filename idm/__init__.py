"""Information Discrete Mathematics — the library.

    import idm
    idm.solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
    idm.pi()                                      # π as a finite readout
    idm.certified.geom_series("0.333333", "1e-12")
    idm.certified.certify_threshold(11, 1, 9)     # Decision.ABOVE
    idm.shortest_path(W)                          # min-plus all-pairs

A readout-first foundation: finite source semantics, exact arithmetic where available,
evidence-qualified numerical readouts, and fail-closed decisions. The formal core is in
``formal/``; public numerical results distinguish ``CERTIFIED``, ``STABLE``, and ``HOLD``.

Submodules: functions · certified · readout_boundary · algebra · readouts · exact · analysis ·
discrete · integrate · diffeq · series · special · transforms · optimize · symbolic · combopt ·
interval · stats · geometry · crypto · parse · rcp · solve · server.
"""
# Single source of truth is pyproject.toml; kept in sync by tests/test_version_consistency.py
# (a CI gate that fails if this string, pyproject, and capabilities.json ever diverge).
__version__ = "1.5.1"

from . import (
    functions,
    certified,
    readout_boundary,
    algebra,
    readouts,
    exact,
    analysis,
    discrete,
    integrate,
    diffeq,
    series,
    special,
    transforms,
    optimize,
    symbolic,
    combopt,
    interval,
    stats,
    geometry,
    crypto,
    hilbert,
    hilbert_open,
    parse as _parse,
    rcp,
    solve as _solve,
)

# top-level convenience surface
solve = _solve.solve
kinds = _solve.kinds
parse = _parse.parse
parse_and_solve = _parse.parse_and_solve

# typed result + one-call convenience wrappers
from .results import Result, SolveHold
from .convenience import (
    factorize,
    gcd,
    solve_integral,
    integrate_rational,
    solve_matrix,
    eigenvalues,
    solve_roots,
    solve_ode,
)
from .discovery import describe, schema, example
from . import ai, ai_bench

# finite elementary + calculus
exp, log, sin, cos, erf, gamma, sqrt = (
    functions.exp,
    functions.log,
    functions.sin,
    functions.cos,
    functions.erf,
    functions.gamma,
    functions.sqrt,
)
pi, e, ln2 = functions.pi, functions.e, functions.ln2
derivative, integral, limit, ode, evaluate = (
    functions.derivative,
    functions.integral,
    functions.limit,
    functions.ode,
    functions.evaluate,
)

# evidence-qualified readouts
Readout = certified.Readout
CERTIFIED, STABLE, HOLD = certified.CERTIFIED, certified.STABLE, certified.HOLD
Decision = certified.Decision
DecimalReadout = certified.DecimalReadout
Enclosure = certified.Enclosure
parse_decimal_readout = certified.parse_decimal_readout
certify_threshold = certified.certify_threshold

# optimization
shortest_path, critical_path, widest_path = (
    algebra.shortest_path,
    algebra.critical_path,
    algebra.widest_path,
)
minimax_path, reachability, path_count = (
    algebra.minimax_path,
    algebra.reachability,
    algebra.path_count,
)

# readouts
dashboard = readouts.dashboard


def serve(host="127.0.0.1", port=8737):
    """Start the zero-dependency REST solver API (POST /solve, GET /health)."""

    from .server import run

    run(host, port)


__all__ = [
    "__version__",
    "solve",
    "serve",
    "functions",
    "certified",
    "readout_boundary",
    "algebra",
    "readouts",
    "rcp",
    "exp",
    "log",
    "sin",
    "cos",
    "erf",
    "gamma",
    "sqrt",
    "pi",
    "e",
    "ln2",
    "derivative",
    "integral",
    "limit",
    "ode",
    "evaluate",
    "Readout",
    "CERTIFIED",
    "STABLE",
    "HOLD",
    "Decision",
    "DecimalReadout",
    "Enclosure",
    "parse_decimal_readout",
    "certify_threshold",
    "shortest_path",
    "critical_path",
    "widest_path",
    "minimax_path",
    "reachability",
    "path_count",
    "dashboard",
    "kinds",
    "parse",
    "parse_and_solve",
    "Result",
    "SolveHold",
    "factorize",
    "gcd",
    "solve_integral",
    "integrate_rational",
    "solve_matrix",
    "eigenvalues",
    "solve_roots",
    "solve_ode",
    "describe",
    "schema",
    "example",
    "ai",
    "ai_bench",
]
