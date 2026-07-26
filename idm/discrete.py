"""idm.discrete — finite discrete structures: graphs, sets, logic, bases.

All exact and finite: union–find, BFS/DFS, Kahn's toposort, Edmonds–Karp max-flow, finite set algebra,
and truth tables over a finite assignment space. The naturally decidable, `Th_coqc`-eligible layer.
"""
from collections import deque
from itertools import product


# ---------------------------------------------------------------- graphs ----
class _DSU:
    def __init__(self, n): self.p = list(range(n))
    def find(self, x):
        while self.p[x] != x: self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        self.p[ra] = rb; return True


def mst(n, edges):
    """minimum spanning tree of an undirected weighted graph (edges = [[u,v,w],…]).
    Returns {weight, edges, connected} — Kruskal."""
    d = _DSU(n); chosen = []; total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if d.union(u, v): chosen.append([u, v, w]); total += w
    comps = len({d.find(i) for i in range(n)})
    return {"weight": total, "edges": chosen, "connected": comps == 1, "components": comps}


def connected_components(n, edges):
    """components of an undirected graph (edges = [[u,v],…]); returns a list of vertex lists."""
    d = _DSU(n)
    for e in edges: d.union(e[0], e[1])
    groups = {}
    for i in range(n): groups.setdefault(d.find(i), []).append(i)
    return sorted(groups.values(), key=lambda g: g[0])


def topological_sort(n, edges):
    """Kahn's algorithm on a directed graph (edges = [[u,v],…]); a linear order, or None if cyclic."""
    adj = [[] for _ in range(n)]; indeg = [0] * n
    for u, v in edges: adj[u].append(v); indeg[v] += 1
    q = deque(i for i in range(n) if indeg[i] == 0); order = []
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    return order if len(order) == n else None


def is_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges: adj[u].append(v); adj[v].append(u)
    color = [-1] * n
    for s in range(n):
        if color[s] != -1: continue
        color[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1: color[v] = color[u] ^ 1; q.append(v)
                elif color[v] == color[u]: return {"bipartite": False}
    return {"bipartite": True, "coloring": color}


def max_flow(n, edges, source, sink):
    """maximum s–t flow (edges = [[u,v,capacity],…]) by Edmonds–Karp — exact integer arithmetic."""
    cap = [[0] * n for _ in range(n)]; adj = [[] for _ in range(n)]
    for u, v, c in edges:
        if v not in adj[u]: adj[u].append(v)
        if u not in adj[v]: adj[v].append(u)
        cap[u][v] += c
    flow = 0
    while True:
        par = [-1] * n; par[source] = source; q = deque([source])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if par[v] == -1 and cap[u][v] > 0: par[v] = u; q.append(v)
        if par[sink] == -1: break
        aug = float("inf"); v = sink
        while v != source: u = par[v]; aug = min(aug, cap[u][v]); v = u
        v = sink
        while v != source: u = par[v]; cap[u][v] -= aug; cap[v][u] += aug; v = u
        flow += aug
    return flow


# ---------------------------------------------------------------- sets ----
def set_op(op, a, b=None):
    A = set(map(_hash, a))
    ops = {"union": lambda: A | set(map(_hash, b)),
           "intersection": lambda: A & set(map(_hash, b)),
           "difference": lambda: A - set(map(_hash, b)),
           "symmetric_difference": lambda: A ^ set(map(_hash, b)),
           "is_subset": lambda: A <= set(map(_hash, b))}
    r = ops[op]()
    return r if isinstance(r, bool) else sorted(r)
def _hash(x): return x
def powerset(a):
    a = list(a); out = [[]]
    for x in a: out += [s + [x] for s in out]
    return out


# ---------------------------------------------------------------- logic ----
def truth_table(expr, variables):
    """evaluate a boolean expression (using and/or/not/^/== over the named variables) across every
    finite assignment; returns the rows and whether it is a tautology/contradiction."""
    rows = []; ns_base = {"__builtins__": {}}
    tvals = []
    for combo in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, combo))
        val = bool(eval(compile(expr, "<truth>", "eval"), ns_base, dict(env)))
        rows.append({**{v: env[v] for v in variables}, "result": val}); tvals.append(val)
    return {"variables": variables, "rows": rows,
            "tautology": all(tvals), "contradiction": not any(tvals), "satisfiable": any(tvals)}
