"""Guard for the one real risk of idm/_bridge.py's sys.path bridge: SHADOWING.

The bridge puts tools/ and provefull/ (or their vendored-in-wheel mirrors) on sys.path so the audited
files there resolve by bare name — which is load-bearing (those files are dual-use: standalone scripts
AND idm imports; see the _bridge.py docstring). Its one genuine failure mode, flagged by a world-class
review, is that a vendored bare name could silently start resolving to an *unrelated installed package*
of the same name. This pins every enabled bare name to a repo-local file, so that can never happen
silently.

Pure stdlib — runs in the core compute job.
"""
import importlib
import importlib.util
import os

import idm  # noqa: F401  (triggers the bridge)
from idm._bridge import _BARE_MODULES, _ACTIVE_DIRS


def _under_active_dir(path: str) -> bool:
    real = os.path.realpath(path)
    return any(real.startswith(os.path.realpath(d) + os.sep) for d in _ACTIVE_DIRS)


def test_every_bridged_bare_name_resolves_to_a_repo_local_file():
    """Each name the bridge enables must import from one of the bridge's own active directories
    (tools/ · provefull/ · the vendored mirrors) — never from site-packages or anywhere else."""
    assert _ACTIVE_DIRS, "the bridge inserted no directories — layout detection is broken"
    assert _BARE_MODULES, "no bare names to guard — the loop below would pass vacuously"
    for name in _BARE_MODULES:
        spec = importlib.util.find_spec(name)
        assert spec is not None, f"bridged bare module {name!r} does not resolve — bridge broken"
        origin = spec.origin
        assert origin and origin not in ("built-in", "namespace"), f"{name!r} has no file origin: {origin}"
        assert _under_active_dir(origin), (
            f"bridged name {name!r} resolves to {origin} — OUTSIDE the bridge's active dirs "
            f"{_ACTIVE_DIRS}; it is shadowing an unrelated installed package"
        )


def test_bridged_names_actually_import():
    """Sanity: the enabled bare names import without error (the bridge is live and complete)."""
    for name in _BARE_MODULES:
        importlib.import_module(name)   # raises if the bridge didn't make it importable
