"""Consistency gates — the self-describing invariants a world-class review flagged as drift-prone.

These are structural CI gates (like tests/test_capabilities_manifest.py): they FAIL if a human forgets
to keep a hand-maintained number in sync with its real source of truth. Two drifts were caught in the
v1.4.0 review and are now gated so they cannot recur:

  * the package __version__ vs pyproject vs the generated manifest;
  * the documented Coq-theorem count (README badge + formal/README) vs the live formal/verify.sh arc.

Pure stdlib — runs in the core compute job (no numpy).
"""
import json
import re
from pathlib import Path

import idm

ROOT = Path(__file__).resolve().parent.parent


def _pyproject_version() -> str:
    txt = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', txt)
    assert m, "no version = \"...\" in pyproject.toml"
    return m.group(1)


def _manifest_version() -> str:
    return json.loads((ROOT / "capabilities.json").read_text(encoding="utf-8"))["project"]["version"]


def test_version_is_single_sourced():
    """idm.__version__, pyproject.toml, and capabilities.json must all agree — the exact drift
    (idm.__version__ frozen at 1.3.0 while the release was 1.4.0) the review caught."""
    pv = _pyproject_version()
    assert idm.__version__ == pv, (idm.__version__, pv)
    assert _manifest_version() == pv, (_manifest_version(), pv)


def _verify_sh_theorem_count() -> int:
    """The authoritative theorem count: the number of "name:file" entries in formal/verify.sh's THMS
    array (each is one Print-Assumptions-checked, axiom-free theorem)."""
    txt = (ROOT / "formal" / "verify.sh").read_text(encoding="utf-8")
    block = re.search(r"declare -a THMS=\((.*?)\n\)", txt, re.DOTALL)
    assert block, "could not find the THMS=( ... ) array in formal/verify.sh"
    return len(re.findall(r'"\s*[A-Za-z0-9_]+\s*:\s*[A-Za-z0-9_]+\s*"', block.group(1)))


def test_documented_theorem_count_matches_verify_sh():
    """Every "<N> theorem(s) axiom-free" claim in README.md / formal/README.md must equal the live
    verify.sh count — the '127 theorems' staleness (actual 184) the review caught, now gated so a new
    witness added to verify.sh without updating the docs fails CI."""
    actual = _verify_sh_theorem_count()
    for rel in ("README.md", "formal/README.md",
                "plugins/information-discrete-math/skills/information-discrete-math/SKILL.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        # numbers appearing right before the word "theorem(s)" (badge uses %20 as the space)
        claimed = [int(n) for n in re.findall(r"(\d{2,4})(?:%20| )theorems?\b", text)]
        for c in claimed:
            assert c == actual, (
                f"{rel} claims {c} theorems but formal/verify.sh has {actual} "
                f"(update the doc, or the gate will keep failing)"
            )
