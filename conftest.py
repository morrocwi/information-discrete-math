"""Make the repository root importable for the test suite regardless of how pytest is invoked.

pytest loads a rootdir ``conftest.py`` before collecting any test module, so putting the repo root on
``sys.path`` here guarantees ``import idm`` / ``import retained_spectral`` resolve under a bare
``pytest`` (the CI ``verify`` job) exactly as they do under ``PYTHONPATH=. python -m pytest`` — without
depending on pytest's collection order or a per-file path hack. The package is not pip-installed in the
lightweight core CI, so this is the one place the source tree is put on the path.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
