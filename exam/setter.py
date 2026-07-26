#!/usr/bin/env python3
"""setter — normalize subjects to MSC top-level areas, freeze a stratified exam set (deterministic, RAM-free)."""
import json, os, collections
POOL=os.path.join(os.path.dirname(__file__),"data","pool.jsonl")
OUT=os.path.join(os.path.dirname(__file__),"data","exam3000.jsonl")
def top_area(s):
    s=s.lower()
    if "number theory" in s: return "number_theory"
    if "combinator" in s or "counting" in s or "graph" in s or "probability" in s: return "combinatorics"
    if "geometry" in s: return "geometry"
    if "abstract algebra" in s or "group" in s or "ring" in s or "field" in s: return "abstract_algebra"
    if "linear algebra" in s or "matrices" in s or "linear transform" in s: return "linear_algebra"
    if "calculus" in s or "derivative" in s or "precalc" in s or "analysis" in s or "trigonom" in s: return "analysis"
    if "algebra" in s: return "algebra"
    if "arithmetic" in s: return "arithmetic"
    return "olympiad"
recs=[json.loads(l) for l in open(POOL)]
for r in recs:
    r["area"]=top_area(r["subject"])
    r["band"]= "olympiad" if r["level"] in ("AIME","olympiad") else ("floor" if r["level"] in ("1","Level 1") else
               ("hard" if r["level"] in ("5","Level 5","4","Level 4") else "mid"))
with open(OUT,"w") as f:
    for r in recs: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print("frozen",len(recs),"→",OUT)
print("by area:",dict(collections.Counter(r["area"] for r in recs)))
print("by band:",dict(collections.Counter(r["band"] for r in recs)))
