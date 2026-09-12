#!/usr/bin/env python3
"""F6 Reader-Domain topology calibration.

This is an architecture calibration at the derived finite-readout record layer.
It is deliberately not a universal 3-manifold classifier and not a proof of the
Poincare conjecture. Maker records and checker labels are physically separated.
The maker freezes partitions before checker labels are loaded.

Expected behaviour:
  R0 = structural + homology reader: must FAIL (S3 vs Poincare sphere, lens collision).
  R1 = R0 + pi1 certificate: must improve but still FAIL (L(5,1) vs L(5,2)).
  R2 = R1 + linking-form signature: must match the frozen checker classes exactly.

A PASS means the Reader-Domain refine/falsifier protocol behaves correctly on
this frozen benchmark. It does not establish raw-triangulation encoding or a
universal topology theorem.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

FORBIDDEN_MAKER_KEYS = {
    "topology_label",
    "checker_label",
    "ground_truth",
    "homeomorphism_class",
}

R0 = ("dimension", "closed", "orientable", "homology")
R1 = R0 + ("pi1_certificate",)
R2 = R1 + ("linking_form_signature",)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def assert_no_label_leakage(obj: Any, path: str = "$") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in FORBIDDEN_MAKER_KEYS:
                raise AssertionError(f"label leakage: forbidden key {key!r} at {path}")
            assert_no_label_leakage(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            assert_no_label_leakage(value, f"{path}[{i}]")


def frozen_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def make_partition(records: list[dict[str, Any]], reader_keys: tuple[str, ...]) -> dict[str, str]:
    """Return record id -> maker class id, using reader outputs only."""
    class_for_signature: dict[tuple[str, ...], str] = {}
    partition: dict[str, str] = {}
    for rec in records:
        readouts = rec["readouts"]
        missing = [k for k in reader_keys if k not in readouts]
        if missing:
            raise AssertionError(f"{rec['id']}: missing declared readouts {missing}")
        signature = tuple(frozen_key(readouts[k]) for k in reader_keys)
        if signature not in class_for_signature:
            class_for_signature[signature] = f"C{len(class_for_signature):03d}"
        partition[rec["id"]] = class_for_signature[signature]
    return partition


def compare_partition(partition: dict[str, str], labels: dict[str, str]) -> dict[str, Any]:
    ids = sorted(partition)
    if set(ids) != set(labels):
        missing = sorted(set(ids) ^ set(labels))
        raise AssertionError(f"maker/checker id mismatch: {missing}")
    false_merge: list[list[str]] = []
    false_split: list[list[str]] = []
    for a, b in combinations(ids, 2):
        same_maker = partition[a] == partition[b]
        same_truth = labels[a] == labels[b]
        if same_maker and not same_truth:
            false_merge.append([a, b])
        if not same_maker and same_truth:
            false_split.append([a, b])
    return {
        "false_merge": false_merge,
        "false_split": false_split,
        "false_merge_count": len(false_merge),
        "false_split_count": len(false_split),
    }


def separated(partition: dict[str, str], a: str, b: str) -> bool:
    return partition[a] != partition[b]


def merged(partition: dict[str, str], a: str, b: str) -> bool:
    return partition[a] == partition[b]


def run(maker_path: Path, checker_path: Path) -> dict[str, Any]:
    # Maker phase. Ground-truth labels are intentionally not loaded yet.
    maker = load_json(maker_path)
    assert_no_label_leakage(maker)
    records = maker["records"]
    ids = [r["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate maker record ids")

    p0 = make_partition(records, R0)
    p1 = make_partition(records, R1)
    p2 = make_partition(records, R2)

    # Freeze maker outputs before opening checker labels.
    frozen_maker = {
        "R0": dict(p0),
        "R1": dict(p1),
        "R2": dict(p2),
    }

    # Checker phase.
    checker = load_json(checker_path)
    labels = checker["labels"]
    c0 = compare_partition(frozen_maker["R0"], labels)
    c1 = compare_partition(frozen_maker["R1"], labels)
    c2 = compare_partition(frozen_maker["R2"], labels)

    controls = {
        "same_S3_representations_collapse_R2": merged(p2, "s3_boundary_4simplex", "s3_subdivision_control"),
        "same_Poincare_representations_collapse_R2": merged(p2, "poincare_homology_sphere_a", "poincare_homology_sphere_b"),
        "homology_only_exposes_S3_Poincare_false_merge": merged(p0, "s3_boundary_4simplex", "poincare_homology_sphere_a"),
        "pi1_refines_S3_Poincare": separated(p1, "s3_boundary_4simplex", "poincare_homology_sphere_a"),
        "homology_plus_pi1_still_exposes_lens_collision": merged(p1, "lens_5_1", "lens_5_2"),
        "linking_form_refines_lens_collision": separated(p2, "lens_5_1", "lens_5_2"),
    }

    leakage_count = 0
    unresolved_count = 0
    expected_negative_controls = (
        c0["false_merge_count"] > 0
        and c1["false_merge_count"] > 0
        and all(controls.values())
    )
    final_exact = c2["false_merge_count"] == 0 and c2["false_split_count"] == 0

    passed = expected_negative_controls and final_exact and leakage_count == 0 and unresolved_count == 0
    return {
        "status": "PASS" if passed else "FAIL",
        "scope": "finite derived-readout topology calibration only",
        "not_established": [
            "raw triangulation -> readout encoding",
            "universal 3-manifold homeomorphism classification",
            "a new proof of the Poincare conjecture",
            "any Clay conclusion",
        ],
        "reader_levels": {
            "R0": {"keys": R0, **c0},
            "R1": {"keys": R1, **c1},
            "R2": {"keys": R2, **c2},
        },
        "controls": controls,
        "defect_vector_final": {
            "false_merge": c2["false_merge_count"],
            "false_split": c2["false_split_count"],
            "leakage": leakage_count,
            "unresolved": unresolved_count,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument("--maker", type=Path, default=here / "maker_records.json")
    parser.add_argument("--checker", type=Path, default=here / "checker_labels.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run(args.maker, args.checker)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"F6 Reader-Domain calibration: {result['status']}")
        print("Final defect vector:", result["defect_vector_final"])
        for name, value in result["controls"].items():
            print(f"  {name}: {'PASS' if value else 'FAIL'}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
