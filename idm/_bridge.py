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

Only paths that actually exist are inserted, so exactly one layout is active in any given install
(a source checkout never has ``idm/_vendor_*``; an installed wheel never has sibling ``tools/``).

**Why bare imports, not absolute ``idm._vendor_*`` imports?** The vendored files are *dual-use*: they
must run BOTH as **standalone scripts** — each carries a ``__main__`` self-check runnable as
``python3 tools/idm_tools.py`` / ``python3 provefull/…`` (CI gates the ``tools/*.py`` ones; the
``provefull/*.py`` ones are runnable the same way, not CI-gated) — AND as modules ``idm`` re-exports.
They cross-import each other by bare name
(``provefull/*.py: import _kernel``; ``_kernel: import idm_tools``). Bare imports are the only form that
resolves in BOTH modes; rewriting them to ``from idm._vendor_provefull import _kernel`` would break the
standalone-script mode (no ``idm`` package context). So the sys.path bridge is load-bearing, not an
accident — the guard against its one real risk (a vendored name shadowing an unrelated installed
package) is ``tests/test_bridge_no_shadowing.py``, which pins every enabled bare name to a repo-local
file.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))          # the installed/loaded `idm/` directory
_ROOT = os.path.dirname(_HERE)                              # its parent (the repo root, in a checkout)

# (import-name directory) candidates, source-checkout location first then the vendored-in-wheel one.
# Iterated in this FIXED order; only existing dirs are inserted, and the two layouts are mutually
# exclusive, so the resulting sys.path precedence is deterministic per install.
_CANDIDATES = (
    os.path.join(_ROOT, "tools"),
    os.path.join(_ROOT, "provefull"),
    os.path.join(_ROOT, "benchmarks"),                     # source-only; not shipped (idm needs none of it)
    os.path.join(_HERE, "_vendor_tools"),
    os.path.join(_HERE, "_vendor_provefull"),
)
_ACTIVE_DIRS = tuple(_p for _p in _CANDIDATES if os.path.isdir(_p))   # the layout actually present
for _p in _ACTIVE_DIRS:
    if _p not in sys.path:
        sys.path.insert(0, _p)

REPO_ROOT = _ROOT

# The bare top-level module names this bridge makes importable from the bridged directories. Some are
# re-exported by idm today (idm_tools, aggregate, certified_readout, eng_readouts,
# retained_{burden,contraction,energy}_*); the rest live alongside them in tools/ + provefull/ and are
# importable by bare name once the bridge runs. Listing the whole resident set — not only today's
# re-exports — keeps the shadowing surface fully covered: pinned by tests/test_bridge_no_shadowing.py so
# none can silently start resolving to an unrelated installed package of the same name.
_BARE_MODULES = (
    "idm_tools", "aggregate", "certified_readout", "eng_readouts", "framework_compliance",
    "idm_discipline", "retained_burden_algebra", "retained_contraction_protocol",
    "retained_energy_protocol",                            # from tools/
    "_kernel", "biochem", "complexity", "cosmology", "networks", "physics",   # from provefull/
)
