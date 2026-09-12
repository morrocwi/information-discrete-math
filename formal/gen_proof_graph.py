#!/usr/bin/env python3
"""
gen_proof_graph.py -- auto-generate a Lemma/Theorem dependency graph from a
Coq source file, so this file/repo stays the single source of truth (no
hand-maintained graph to drift out of sync with the actual proofs).

Usage:
    python3 gen_proof_graph.py IDM_ReaderDomainFoundation.v > proof_graph.json
    python3 gen_proof_graph.py --check IDM_ReaderDomainFoundation.v proof_graph.json

How it works (deliberately simple, text-level, no Coq parser):
1. Find every top-level `Theorem|Lemma|Definition|Corollary NAME ... .` head,
   in source order, recording its byte span from the head to the matching
   `Qed.`/`Defined.`/`Admitted.`/`.` terminator for a bare Definition.
2. For each such node, scan its own body text for whole-word occurrences of
   any OTHER node name already seen earlier in the file (Coq requires a name
   be defined before use, so this is a safe, purely-textual dependency
   proxy -- it is not a full elaborator and can occasionally over- or
   under-count on adversarial naming, but for this file's plain style it is
   exact).
3. Emit {"name": {"kind": ..., "deps": [...]}} in source order.

This is a proxy for "what does the proof body mention", not a guarantee of
logical necessity (a dep could appear in a dead branch) -- treat it as an
architecture map for humans/AI/CI, not as a replacement for coqc itself.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

HEAD_RE = re.compile(
    r'^(Theorem|Lemma|Definition|Corollary|Fixpoint)\s+([A-Za-z_][A-Za-z0-9_\']*)',
    re.MULTILINE,
)
TERMINATORS = ("Qed.", "Defined.", "Admitted.")


def strip_comments(src: str) -> str:
    """Remove (* ... *) comments (non-nesting-safe fallback: nesting-aware)."""
    out = []
    depth = 0
    i = 0
    n = len(src)
    while i < n:
        if src.startswith("(*", i):
            depth += 1
            i += 2
            continue
        if src.startswith("*)", i) and depth > 0:
            depth -= 1
            i += 2
            continue
        if depth == 0:
            out.append(src[i])
        i += 1
    return "".join(out)


def find_body_end(src: str, start: int, kind: str) -> int:
    """From a header match start, find where this declaration's body ends.

    Theorem/Lemma/Corollary always end at Qed./Defined./Admitted. -- the
    statement itself contains a bare terminating '.' before "Proof." that
    must NOT be mistaken for the end (that was a real bug in an earlier
    version of this script: it truncated every Theorem's captured body at
    its own statement-ending period, before the proof, silently hiding
    every dependency actually used inside the proof term).

    Definition/Fixpoint (this file's style: always bare, no Proof block)
    end at the first top-level '.' followed by whitespace/EOF -- but if a
    Qed./Defined./Admitted. appears first (a Program Definition or a
    Definition-via-tactics), prefer that instead.
    """
    i = start
    n = len(src)
    depth = 0
    while i < n:
        c = src[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif depth <= 0:
            for term in TERMINATORS:
                if src.startswith(term, i):
                    return i + len(term)
            if kind in ("Definition", "Fixpoint") and c == "." and (
                i + 1 >= n or src[i + 1] in " \n\t"
            ):
                return i + 1
        i += 1
    return n


def parse_nodes(src: str):
    nodes = []  # list of (name, kind, body_text, start_pos)
    for m in HEAD_RE.finditer(src):
        kind, name = m.group(1), m.group(2)
        end = find_body_end(src, m.end(), kind)
        nodes.append((name, kind, src[m.start():end], m.start()))
    return nodes


def build_graph(path: str) -> dict:
    raw = open(path, encoding="utf-8").read()
    src = strip_comments(raw)
    nodes = parse_nodes(src)
    graph = {}
    seen_names = []
    for name, kind, body, _pos in nodes:
        deps = []
        for other in seen_names:
            if other == name:
                continue
            if re.search(r'\b' + re.escape(other) + r'\b', body):
                deps.append(other)
        graph[name] = {"kind": kind, "deps": deps}
        seen_names.append(name)
    return graph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="path to a .v file")
    ap.add_argument(
        "--check",
        metavar="EXISTING_JSON",
        help="instead of printing, diff against an existing proof_graph.json "
        "and exit 1 if it is stale (CI mode)",
    )
    args = ap.parse_args()

    graph = build_graph(args.source)

    if args.check:
        with open(args.check, encoding="utf-8") as f:
            existing = json.load(f)
        if existing != graph:
            print(f"STALE: {args.check} does not match {args.source}", file=sys.stderr)
            print(
                f"Regenerate with: python3 {sys.argv[0]} {args.source} > {args.check}",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"OK: {args.check} is up to date with {args.source}")
        return

    print(json.dumps(graph, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
