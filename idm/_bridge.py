"""Internal bridge — makes the repository's verified modules importable as one package.

The `idm` package is a facade over already-verified building blocks that live in `tools/` and
`provefull/`. Rather than duplicate that audited code, those modules are put on the import path here,
once, and re-exported by name from the submodules — so everything `idm` exposes runs the exact code CI
checks and Coq underwrites, with no reimplementation.

Two layouts are supported so the package works BOTH from a source checkout and from an installed
wheel:

* source checkout — the sibling directories ``<repo>/tools`` and ``<repo>/provefull`` sit next to the
  ``idm`` package; they are added to ``sys.path`` so bare imports (``import idm_tools``, ``_kernel``)
  resolve.
* installed wheel — those same directories are shipped INSIDE the package as ``idm/_vendor_tools`` and
  ``idm/_vendor_provefull`` (see ``[tool.setuptools.package-dir]`` in ``pyproject.toml``); they are
  added to ``sys.path`` here too, so the identical bare imports resolve without the source tree.

Only paths that actually exist are inserted, so exactly one layout is active in any given install.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))          # the installed/loaded `idm/` directory
_ROOT = os.path.dirname(_HERE)                              # its parent (the repo root, in a checkout)

# (import-name directory) candidates, source-checkout location first then the vendored-in-wheel one.
_CANDIDATES = (
    os.path.join(_ROOT, "tools"),
    os.path.join(_ROOT, "provefull"),
    os.path.join(_ROOT, "benchmarks"),                     # source-only; not shipped (idm needs none of it)
    os.path.join(_HERE, "_vendor_tools"),
    os.path.join(_HERE, "_vendor_provefull"),
)
for _p in _CANDIDATES:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

REPO_ROOT = _ROOT
