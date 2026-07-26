"""Internal bridge — makes the repository's verified modules importable as one package.

The `idm` package is a clean, world-class facade over the already-verified building blocks in
`tools/`, `provefull/`, `benchmarks/`. Rather than duplicate that audited code, we put those
directories on the path once, here, and re-export named APIs from the submodules. Everything `idm`
exposes therefore runs the exact code that CI checks and Coq underwrites — no reimplementation.
"""
import os, sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in ("tools", "provefull", "benchmarks"):
    _p = os.path.join(_ROOT, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

REPO_ROOT = _ROOT
