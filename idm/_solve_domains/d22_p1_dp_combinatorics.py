# P1 — DP / combinatorics
from idm._solve_core import *  # noqa: F401,F403

@kind("knapsack", "Th_coqc")
def _knap(p): return _ok("knapsack", CO.knapsack(p["weights"], p["values"], int(p["capacity"])), "0/1 knapsack DP")
@kind("subset_sum", "Th_coqc")
def _ss2(p): return _ok("subset_sum", CO.subset_sum(p["nums"], int(p["target"])), "reachability DP")
@kind("lcs", "Th_coqc")
def _lcs(p): return _ok("lcs", CO.lcs(p["a"], p["b"]), "longest common subsequence DP")
@kind("edit_distance", "Th_coqc")
def _ed(p): return _ok("edit_distance", CO.edit_distance(p["a"], p["b"]), "Levenshtein DP")
@kind("coin_change", "Th_coqc")
def _cc2(p): return _ok("coin_change", CO.coin_change(p["coins"], int(p["amount"])), "coin DP (min + #ways)")
