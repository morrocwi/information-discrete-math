#!/usr/bin/env python3
"""Synchronize every registry-derived solver surface.

Source of truth:
- live `idm.kinds()` registry for registered problem kinds;
- `pyproject.toml` for package version.

This tool updates the surfaces whose drift is guarded by CI:
1. tests/test_properties.py valid-input fixtures for the NS retained/turbulence kinds;
2. idm/__init__.py __version__;
3. documented TOTAL registered-kind counts;
4. capabilities.json through tools/gen_capabilities.py;
5. tests/golden/kind_outputs.json from the live registry + fixtures.

It is intentionally deterministic and idempotent.  It does not change solver
semantics or theorem tiers.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import idm  # noqa: E402


NS_FIXTURES = {
    "ns_retained_rk4": {
        "K": 1, "nu": 0.005, "dt": 0.0025, "horizon": 1,
        "target_mode": [1, 0, 0], "verify": True,
    },
    "ns_retained_physical": {
        "K": 1, "nu": 0.005, "dt": 0.0025, "horizon": 1,
        "point": [0.1, 0.2, 0.3], "readout": "velocity",
    },
    "ns_retained_plane_average": {
        "K": 1, "nu": 0.005, "dt": 0.0025, "horizon": 1,
        "axis": "x", "coordinate": 0.2, "verify": True,
    },
    "ns_retained_harmonic_probe": {
        "K": 1, "nu": 0.005, "dt": 0.0025, "horizon": 1,
        "wavevector": [1, 1, 1], "phase": 0.3, "verify": True,
    },
    "ns_turbulence_energy_flux": {
        "K": 1, "nu": 0.005, "dt": 0.0025, "horizon": 1,
        "cutoff": 1.0, "verify": True,
    },
}

KIND_COUNT_DOCS = [
    "README.md", "SOLVER.md", "API.md", "AI_START_HERE.md", "idm/README.md",
    "formal/README.md", "retained_spectral/README.md",
    "docs/CAS_CLOSURE_CHECKLIST.md", "docs/roadmap/README.md",
]

TOTAL_COUNT_PATTERNS = [
    r"(\d{2,4})\s+registered\s+(?:problem\s+)?kinds?",
    r"(\d{2,4})\s+kind names",
    r"(\d{2,4})-kind unified solver",
    r"all\s+(\d{2,4})\s+registered",
    r"over\s+\*{0,2}(\d{2,4})\*{0,2}\s+registered",
    r"unified%20solver-(\d{2,4})%20registered",
    r"this returned\s+\*{0,2}(\d{2,4})\*{0,2}\s+kinds",
    r"→\s+\*{0,2}(\d{2,4})\*{0,2}\s+live",
    r"(\d{2,4})\s+solver kinds",
]


def pyproject_version() -> str:
    txt = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', txt)
    if not m:
        raise RuntimeError("pyproject.toml has no version field")
    return m.group(1)


def sync_version(version: str) -> bool:
    p = ROOT / "idm" / "__init__.py"
    old = p.read_text(encoding="utf-8")
    new, n = re.subn(
        r'(?m)^__version__\s*=\s*"[^"]+"',
        f'__version__ = "{version}"', old, count=1,
    )
    if n != 1:
        raise RuntimeError("could not uniquely update idm.__version__")
    if new != old:
        p.write_text(new, encoding="utf-8")
        return True
    return False


def sync_ns_fixtures() -> bool:
    p = ROOT / "tests" / "test_properties.py"
    old = p.read_text(encoding="utf-8")
    missing = [k for k in NS_FIXTURES if f'"{k}"' not in old]
    if not missing:
        return False

    marker = "    # H1 · Hilbert-space mathematical core"
    if marker not in old:
        raise RuntimeError("fixture insertion marker not found")

    lines = ["    # finite Navier--Stokes retained/readout API fixtures"]
    for kind in missing:
        payload = repr(NS_FIXTURES[kind]).replace("'", '"').replace("True", "True").replace("False", "False")
        lines.append(f'    "{kind}": {payload},')
    block = "\n".join(lines) + "\n"
    new = old.replace(marker, block + marker, 1)
    p.write_text(new, encoding="utf-8")
    return True


def replace_captured_number(text: str, pattern: str, number: int) -> str:
    rx = re.compile(pattern)

    def repl(m: re.Match[str]) -> str:
        a, b = m.span(1)
        rel_a = a - m.start()
        rel_b = b - m.start()
        whole = m.group(0)
        return whole[:rel_a] + str(number) + whole[rel_b:]

    return rx.sub(repl, text)


def sync_doc_counts(count: int) -> list[str]:
    changed = []
    for rel in KIND_COUNT_DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        old = p.read_text(encoding="utf-8")
        new = old
        for pat in TOTAL_COUNT_PATTERNS:
            new = replace_captured_number(new, pat, count)
        if new != old:
            p.write_text(new, encoding="utf-8")
            changed.append(rel)
    return changed


def regenerate_capabilities() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "gen_capabilities.py"),
         "--out", str(ROOT / "capabilities.json")],
        cwd=ROOT, check=True,
    )


def load_fixtures():
    path = ROOT / "tests" / "test_properties.py"
    spec = importlib.util.spec_from_file_location("_surface_fixtures", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.FIXTURES


def regenerate_golden() -> None:
    fixtures = load_fixtures()
    missing = sorted(set(idm.kinds()) - set(fixtures))
    if missing:
        raise RuntimeError(f"cannot generate golden; missing fixtures: {missing}")
    outputs = {
        k: idm.solve(dict(kind=k, **fixtures[k]))
        for k in sorted(idm.kinds())
    }
    path = ROOT / "tests" / "golden" / "kind_outputs.json"
    path.write_text(
        json.dumps(outputs, indent=1, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    count = len(idm.kinds())
    version = pyproject_version()
    sync_ns_fixtures()
    sync_version(version)
    sync_doc_counts(count)
    regenerate_capabilities()
    regenerate_golden()
    print(f"solver surface synchronized: {count} kinds, version {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
