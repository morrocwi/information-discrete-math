# discrete structures
from idm._solve_core import *  # noqa: F401,F403

@kind("mst", "Th_coqc")
def _mst(p): return _ok("mst", D.mst(int(p["n"]), p["edges"]), "Kruskal (union–find)")
@kind("connected_components", "Th_coqc")
def _cc(p): return _ok("connected_components", D.connected_components(int(p["n"]), p["edges"]), "union–find")
@kind("topological_sort", "Th_coqc")
def _ts(p):
    o = D.topological_sort(int(p["n"]), p["edges"])
    return {"kind": "topological_sort", "status": "ok" if o is not None else "HOLD", "value": o, "method": "Kahn's algorithm", **({} if o is not None else {"reason": "graph has a cycle"})}
@kind("is_bipartite", "Th_coqc")
def _bip(p): return _ok("is_bipartite", D.is_bipartite(int(p["n"]), p["edges"]), "BFS 2-coloring")
@kind("max_flow", "Th_coqc")
def _mf(p): return _ok("max_flow", D.max_flow(int(p["n"]), p["edges"], int(p["source"]), int(p["sink"])), "Edmonds–Karp")
@kind("set_operation", "Th_coqc")
def _so(p): return _ok("set_operation", D.set_op(p["op"], p["a"], p.get("b")), f"finite set {p['op']}")
@kind("powerset", "Th_coqc")
def _pw(p): return _ok("powerset", D.powerset(p["set"]), "finite enumeration 2^S")
@kind("truth_table", "Th_coqc")
def _tt(p): return _ok("truth_table", D.truth_table(str(p["expr"]), p["vars"]), "finite assignment enumeration")
