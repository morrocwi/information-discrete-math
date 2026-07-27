"""idm.symbolic — compatibility re-export of the symbolic CAS, which now lives in idm.kernel.cas.

P1.7 migration: the algorithms were moved into the kernel package (``idm/kernel/cas.py`` — the one
substrate). This module mirrors that namespace verbatim so every existing ``from idm import symbolic``
and ``SYM.*`` call site (in ``idm.solve``, tests, and the kernel's own ``simplify``/``solution``
modules) keeps working byte-identically. Nothing here computes; it is a re-export.
"""

from __future__ import annotations

from idm.kernel import cas as _cas

# Mirror every public and internal name from kernel.cas (parse/tostr/diff/simplify/expand/evaluate/
# integrate/poly_coeffs/solve/taylor, plus the helper functions and constants that other modules
# reference, e.g. _subst/_mul/_add/Q/FUNCS) so no call site breaks.
globals().update({_k: _v for _k, _v in vars(_cas).items() if not _k.startswith("__")})

del _cas
