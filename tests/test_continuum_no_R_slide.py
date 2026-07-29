"""Guard against language sliding: the ℚ-primitive continuum must NEVER be described as if it built ℝ.

`idm.continuum` deliberately constructs the continuum as a *readout of the discrete* (Part XX) — a
resolution-indexed exact-ℚ object, with ℝ never a primitive and the completed limit never emitted. That
honesty lives partly in prose, and prose erodes. This test makes the fence ENFORCED, not just intended:

  1. no doc/code surface may make a POSITIVE ℝ-construction / limit-emission claim (negation-aware, so the
     honest "refusing to emit the completed limit" / "ℝ is never a primitive" phrasings pass);
  2. `idm/continuum.py` must keep its explicit fence markers (removing them fails CI, forcing a conscious
     choice, not a silent drift);
  3. at runtime, every non-HOLD readout carries the `+ℝ-Open` fence in its reason, `.at(N)` is always an
     exact `Fraction`, and `.readout` never returns a non-rational value.

Pure stdlib — runs in the core compute job.
"""
import os
import re
from fractions import Fraction as Q

import idm  # noqa: F401
from idm.continuum import Continuum, geometric, from_sequence
from idm.certified import CERTIFIED, HOLD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Doc/code surfaces where a slide toward "we built ℝ" would most plausibly creep in.
_DOC_SET = [
    "idm/continuum.py", "idm/README.md", "CHANGELOG.md", "README.md", "AI_START_HERE.md",
    "textbook/INFORMATION_DISCRETE_MATHEMATICS.md",
]

# A negator anywhere in the short window BEFORE a match means the phrase is used honestly (denied/fenced),
# e.g. "refusing to emit the completed limit", "ℝ is never a primitive", "the completed real stays +ℝ-Open".
_NEGATORS = ("not", "never", " no ", "without", "refus", "cannot", "nor ", "n't", "stays", "avoid",
             "forbid", "reject", "denies", "dispensable", "nowhere", "instead of", "rather than", "'t ")

# POSITIVE assertions that would mean "ℝ is a primitive / we constructed the reals / we handed out the
# completed limit as the value" — the exact slide this guard forbids.
_FORBIDDEN = [
    r"construct\w*\s+(the\s+)?(reals?\b|ℝ)",
    r"build\w*\s+(the\s+)?(reals?\b|ℝ)",
    r"\bℝ\s+(is|as)\s+a\s+primitive",
    r"(returns?|emits?|produces?|yields?|forms?)\s+the\s+completed\s+(limit|real)",
    r"\bis\s+the\s+completed\s+real\b",
    r"\breal[- ]number\s+object",
    r"continuum\s+(is|as)\s+a\s+primitive",
]


def _scan(text):
    low = text.lower()
    out = []
    for pat in _FORBIDDEN:
        for m in re.finditer(pat, low):
            window = low[max(0, m.start() - 26):m.start()]
            if any(n in window for n in _NEGATORS):
                continue                       # negated / fenced → honest usage
            line = text[:m.start()].count("\n") + 1
            out.append((line, text.split("\n")[line - 1].strip()[:100]))
    return out


def test_no_doc_asserts_that_R_was_constructed():
    """No surface may positively claim ℝ is a primitive / the reals were built / the completed limit is
    emitted. Negation-aware, so the framework's honest fenced phrasings are allowed."""
    problems = {}
    for rel in _DOC_SET:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            hits = _scan(open(p, encoding="utf-8").read())
            if hits:
                problems[rel] = hits
    assert not problems, (
        "language slid toward treating ℝ as constructed/primitive (the continuum is a READOUT of the "
        f"discrete, never ℝ built as an object):\n{problems}"
    )


def test_the_guard_actually_has_teeth():
    """A meta-check: the scanner must FLAG a real slide and PASS honest fenced text — otherwise a green
    test above would be meaningless."""
    assert _scan("This constructs ℝ as an object.")
    assert _scan("Now ℝ is a primitive of the system.")
    assert _scan("readout() returns the completed limit as the value.")
    assert not _scan("ℝ is never a primitive here.")
    assert not _scan("refusing to emit the completed limit as a number.")
    assert not _scan("constructs a continuum layer as a readout.")   # continuum≠ℝ, legitimate


def test_continuum_module_keeps_its_fence_markers():
    """`idm/continuum.py` must keep the explicit fence in its own text — removing it should break CI, so
    the honesty can't silently drift out."""
    src = open(os.path.join(ROOT, "idm", "continuum.py"), encoding="utf-8").read()
    for marker in ("never ℝ as an object", "+ℝ-Open", "readout of the discrete"):
        assert marker in src, f"idm/continuum.py lost its fence marker: {marker!r}"


def test_runtime_readouts_carry_the_R_fence_and_stay_rational():
    """Every non-HOLD readout must name the +ℝ-Open fence in its reason and return only exact ℚ; .at(N)
    is always a Fraction. So even if prose drifts, the values themselves never present a completed real."""
    cases = [
        geometric("1/2"),                                    # CERTIFIED (proven bound)
        geometric("1/2") + geometric("1/3"),                 # CERTIFIED (propagated bound)
        from_sequence(lambda N: Q(1, N + 1)),                # finite_diagnostic (observed)
        Continuum.from_gen(lambda N: Q((-1) ** N)),          # HOLD (no limit)
    ]
    for c in cases:
        assert isinstance(c.at(7), Q)                        # never a float / never ℝ
        r = c.readout("1/500")
        assert r.q is None or isinstance(r.q, Q)             # emitted value is exact ℚ or nothing
        if r.status != HOLD:
            assert "+ℝ-Open" in r.reason, f"non-HOLD readout dropped the +ℝ-Open fence: {r.reason!r}"
        if r.status == CERTIFIED:
            assert "NOT the completed limit" in r.reason     # certified value is a readout, not the limit
