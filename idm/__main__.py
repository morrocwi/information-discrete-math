"""idm.__main__ — command-line discovery for the finite-discrete solver registry.

    python -m idm list                  # every kind (idm.kinds())
    python -m idm list --tier exact     # filter by registry tier
    python -m idm list --domain fourier # substring filter over kind names (see `describe -h`)
    python -m idm describe factorize    # tier + handler doc/signature + how to verify
    python -m idm kinds                 # count of registered kinds
    python -m idm example linear_ode    # a real problem dict pulled from tests/, if one exists

This is a discovery/introspection layer over `idm.solve._REG` — it does not invent metadata the
registry does not have. In particular the registry carries no "domain" taxonomy, so `--domain`
is an honest substring match against kind names, not a curated category system.
"""
from __future__ import annotations

import argparse
import inspect
import re
import sys
from pathlib import Path

import idm
from idm.solve import _REG, _COQ_BACKED


def _effective_tier(name: str) -> str:
    """The HONEST tier the solver would actually return for this kind — mirrors idm.solve()'s
    tier-honesty pass: a registry `Th_coqc` tag is kept only for kinds with a named machine-checked
    theorem (`_COQ_BACKED`); every other `Th_coqc`-tagged handler downgrades to `exact`. So the CLI
    reports what `idm.solve` really emits, not the raw decorator tag."""
    tier = _REG[name][1] if name in _REG else "?"
    if tier == "Th_coqc" and name not in _COQ_BACKED:
        return "exact"
    return tier

# The four tiers actually assigned in idm/solve.py's registry (grep-verified, not assumed):
# Th_coqc / exact / +ℝ-Open explicit; finite_diagnostic is the @kind() default.
_KNOWN_TIERS = ("Th_coqc", "finite_diagnostic", "exact", "+ℝ-Open")


def _repo_root() -> Path:
    """Best-effort source root: the parent of the installed/checked-out `idm` package.

    Works for a source checkout (repo root has tests/). For a pip-installed wheel there is no
    tests/ directory shipped, so `example` will honestly report no example on file rather than
    fabricate one.
    """
    return Path(__file__).resolve().parent.parent


def _cmd_list(args: argparse.Namespace) -> int:
    names = idm.kinds()
    if args.tier:
        names = [n for n in names if n in _REG and _effective_tier(n) == args.tier]
    if args.domain:
        needle = args.domain.lower()
        names = [n for n in names if needle in n.lower()]
    for n in names:
        print(f"{n}\t{_effective_tier(n)}")
    return 0


def _cmd_kinds(args: argparse.Namespace) -> int:
    print(len(idm.kinds()))
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    name = args.kind
    if name not in _REG:
        print(f"unknown kind: {name!r} (not in idm.solve._REG; see 'idm list')", file=sys.stderr)
        return 1
    fn, reg_tier = _REG[name]
    tier = _effective_tier(name)
    print(f"kind: {name}")
    print(f"tier: {tier}")                       # the tier idm.solve actually returns for this kind
    if reg_tier == "Th_coqc" and name in _COQ_BACKED:
        print(f"coq_theorem: {_COQ_BACKED[name]}")
    elif reg_tier != tier:
        print(f"note: registry default '{reg_tier}' downgrades to '{tier}' (no per-kind Coq witness)")
    try:
        sig = str(inspect.signature(fn))
    except (TypeError, ValueError):
        sig = "(signature unavailable)"
    print(f"handler: {fn.__qualname__}{sig}")
    doc = inspect.getdoc(fn)
    if doc:
        print(f"doc: {doc}")
    else:
        print("doc: (none on file for this handler)")
    print(f"verify: pytest tests/ -k {name}")
    return 0


def _find_example(name: str) -> str | None:
    root = _repo_root()
    tests_dir = root / "tests"
    examples_dir = root / "examples"
    pattern = re.compile(
        r'\{[^{}]*"kind"\s*:\s*"' + re.escape(name) + r'"[^{}]*\}', re.DOTALL
    )
    for d in (tests_dir, examples_dir):
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*.py")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            m = pattern.search(text)
            if m:
                snippet = re.sub(r"\s+", " ", m.group(0)).strip()
                return f"{snippet}    # from {path.relative_to(root)}"
    return None


def _cmd_example(args: argparse.Namespace) -> int:
    name = args.kind
    if name not in _REG:
        print(f"unknown kind: {name!r} (not in idm.solve._REG; see 'idm list')", file=sys.stderr)
        return 1
    found = _find_example(name)
    if found:
        print(found)
    else:
        print(f"no example on file for {name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="idm", description="Discovery CLI over idm.solve's finite-method registry.")
    sub = p.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="print all kinds, optionally filtered")
    p_list.add_argument("--domain", help="substring filter over kind names (no real domain taxonomy exists)")
    p_list.add_argument("--tier", choices=_KNOWN_TIERS, help="filter by registry tier")
    p_list.set_defaults(func=_cmd_list)

    p_describe = sub.add_parser("describe", help="describe one kind: tier, handler signature/doc, verify hint")
    p_describe.add_argument("kind")
    p_describe.set_defaults(func=_cmd_describe)

    p_kinds = sub.add_parser("kinds", help="print the count of registered kinds")
    p_kinds.set_defaults(func=_cmd_kinds)

    p_example = sub.add_parser("example", help="print a real example problem dict for a kind, if one is on file")
    p_example.add_argument("kind")
    p_example.set_defaults(func=_cmd_example)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
