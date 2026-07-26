#!/usr/bin/env python3
"""build_pool — RAM-SAFE streaming importer of external math-benchmark problems into a compact pool.

Streams each dataset (streaming=True → examples yielded one at a time, NEVER the whole set in RAM),
extracts only (source, subject, level, problem, answer), writes compact JSONL to exam/data/pool.jsonl,
and stops each source at its quota. Designed for a tight-RAM box (watch: free RAM checked each source).

Usage:  python3 exam/build_pool.py --target 3000
"""
import argparse, json, os, gc, sys, re

OUT = os.path.join(os.path.dirname(__file__), "data", "pool.jsonl")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def free_mb():
    try:
        with open("/proc/meminfo") as f:
            m = {l.split(":")[0]: int(l.split()[1]) for l in f}
        return (m.get("MemAvailable", 0)) // 1024
    except Exception:
        return -1

def boxed(s):
    # extract \boxed{...} answer (MATH), else None
    m = re.search(r"\\boxed\{", s or "")
    if not m: return None
    i = m.end(); depth = 1; out = []
    while i < len(s) and depth:
        c = s[i]
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: break
        out.append(c); i += 1
    return "".join(out).strip()

# (dataset, config, split, quota, extractor) — extractor returns dict or None per streamed example
SOURCES = [
    ("openai/gsm8k", "main", "test", 400,
     lambda e: {"subject": "arithmetic", "level": "1", "problem": e["question"],
                "answer": e["answer"].split("####")[-1].strip().replace(",", "")}),
    ("HuggingFaceH4/MATH-500", None, "test", 500,
     lambda e: {"subject": e.get("subject") or e.get("type") or "math", "level": str(e.get("level", "?")),
                "problem": e["problem"], "answer": (e.get("answer") or boxed(e.get("solution", "")))}),
    ("EleutherAI/hendrycks_math", "algebra", "test", 300,
     lambda e: {"subject": "algebra", "level": str(e.get("level", "?")), "problem": e["problem"],
                "answer": boxed(e.get("solution", ""))}),
    ("EleutherAI/hendrycks_math", "number_theory", "test", 300,
     lambda e: {"subject": "number_theory", "level": str(e.get("level", "?")), "problem": e["problem"],
                "answer": boxed(e.get("solution", ""))}),
    ("EleutherAI/hendrycks_math", "counting_and_probability", "test", 300,
     lambda e: {"subject": "combinatorics", "level": str(e.get("level", "?")), "problem": e["problem"],
                "answer": boxed(e.get("solution", ""))}),
    ("EleutherAI/hendrycks_math", "precalculus", "test", 250,
     lambda e: {"subject": "precalc_analysis", "level": str(e.get("level", "?")), "problem": e["problem"],
                "answer": boxed(e.get("solution", ""))}),
    ("EleutherAI/hendrycks_math", "geometry", "test", 250,
     lambda e: {"subject": "geometry", "level": str(e.get("level", "?")), "problem": e["problem"],
                "answer": boxed(e.get("solution", ""))}),
    ("EleutherAI/hendrycks_math", "intermediate_algebra", "test", 250,
     lambda e: {"subject": "intermediate_algebra", "level": str(e.get("level", "?")), "problem": e["problem"],
                "answer": boxed(e.get("solution", ""))}),
    ("Maxwell-Jia/AIME_2024", None, "train", 60,
     lambda e: {"subject": "olympiad", "level": "AIME", "problem": e.get("Problem") or e.get("problem"),
                "answer": str(e.get("Answer") or e.get("answer"))}),
    ("AI-MO/aimo-validation-aime", None, "train", 100,
     lambda e: {"subject": "olympiad", "level": "AIME", "problem": e.get("problem"),
                "answer": str(e.get("answer"))}),
    ("KbsdJames/Omni-MATH", None, "test", 400,
     lambda e: {"subject": (e.get("domain") or ["olympiad"])[0] if isinstance(e.get("domain"), list)
                           else (e.get("domain") or "olympiad"),
                "level": "olympiad", "problem": e.get("problem"), "answer": str(e.get("answer") or "")}),
]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--target", type=int, default=3000)
    ap.add_argument("--min_free_mb", type=int, default=500); a = ap.parse_args()
    from datasets import load_dataset
    n = 0
    with open(OUT, "w") as out:
        for ds, cfg, split, quota, ext in SOURCES:
            if n >= a.target: break
            fm = free_mb()
            if 0 <= fm < a.min_free_mb:
                print(f"[RAM GUARD] free {fm}MB < {a.min_free_mb}MB — stopping before {ds} (safe)."); break
            got = 0
            try:
                it = load_dataset(ds, cfg, split=split, streaming=True) if cfg else \
                     load_dataset(ds, split=split, streaming=True)
                for e in it:
                    if got >= quota or n >= a.target: break
                    try: rec = ext(e)
                    except Exception: continue
                    if not rec or not rec.get("problem") or not rec.get("answer"): continue
                    rec.update({"id": f"E{n:04d}", "source": f"{ds}:{cfg or split}"})
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1; got += 1
                del it; gc.collect()
                print(f"  {ds} ({cfg or split}): +{got}  [total {n}, free {free_mb()}MB]")
            except Exception as ex:
                print(f"  SKIP {ds} ({cfg}): {str(ex)[:90]}")
    print(f"POOL: {n} problems → {OUT}  (free {free_mb()}MB)")

if __name__ == "__main__":
    main()
