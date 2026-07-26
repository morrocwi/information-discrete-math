"""idm.combopt — combinatorial optimization, advanced graphs, exact LP, and decision procedures.

Dynamic programs (knapsack, subset-sum, LCS, edit distance, coin change) as finite tables; single-source
shortest paths with reconstruction (Dijkstra, Bellman–Ford); bipartite maximum matching and the Hungarian
assignment; the spanning-tree count by Kirchhoff's theorem (an exact determinant); graph colouring by
finite backtracking; the simplex method with EXACT rational pivoting; and DPLL satisfiability. All finite
and — the numeric ones — exact.
"""
from fractions import Fraction as Q
from .exact import determinant


# ---------------------------------------------------------------- dynamic programming ----
def knapsack(weights, values, capacity):
    n = len(weights); W = int(capacity)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]
            if weights[i - 1] <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weights[i - 1]] + values[i - 1])
    items = []; w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]: items.append(i - 1); w -= weights[i - 1]
    return {"max_value": dp[n][W], "items": sorted(items)}
def subset_sum(nums, target):
    reach = {0: []}
    for x in nums:
        for s in list(reach):
            if s + x not in reach: reach[s + x] = reach[s] + [x]
    return {"reachable": target in reach, "subset": reach.get(target)}
def lcs(a, b):
    m, n = len(a), len(b); dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    seq = []; i, j = m, n
    while i and j:
        if a[i - 1] == b[j - 1]: seq.append(a[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]: i -= 1
        else: j -= 1
    return {"length": dp[m][n], "lcs": list(reversed(seq))}
def edit_distance(a, b):
    m, n = len(a), len(b); dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] if a[i - 1] == b[j - 1] else 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]
def coin_change(coins, amount):
    INF = float("inf"); dp = [0] + [INF] * amount; ways = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            if dp[a - c] + 1 < dp[a]: dp[a] = dp[a - c] + 1
            ways[a] += ways[a - c]
    return {"min_coins": None if dp[amount] == INF else dp[amount], "num_ways": ways[amount]}


# ---------------------------------------------------------------- shortest paths ----
def dijkstra(n, edges, source):
    import heapq
    adj = [[] for _ in range(n)]
    for u, v, w in edges: adj[u].append((v, w))
    dist = [float("inf")] * n; prev = [-1] * n; dist[source] = 0; pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v, w in adj[u]:
            if d + w < dist[v]: dist[v] = d + w; prev[v] = u; heapq.heappush(pq, (dist[v], v))
    return {"distances": [None if d == float("inf") else d for d in dist], "prev": prev}
def bellman_ford(n, edges, source):
    dist = [float("inf")] * n; dist[source] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]: dist[v] = dist[u] + w
    for u, v, w in edges:
        if dist[u] + w < dist[v]: return {"negative_cycle": True}
    return {"negative_cycle": False, "distances": [None if d == float("inf") else d for d in dist]}


# ---------------------------------------------------------------- matching / assignment ----
def bipartite_matching(nL, nR, edges):
    adj = [[] for _ in range(nL)]
    for u, v in edges: adj[u].append(v)
    matchR = [-1] * nR
    def aug(u, seen):
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                if matchR[v] == -1 or aug(matchR[v], seen): matchR[v] = u; return True
        return False
    m = 0
    for u in range(nL):
        if aug(u, [False] * nR): m += 1
    pairs = [(matchR[v], v) for v in range(nR) if matchR[v] != -1]
    return {"size": m, "pairs": sorted(pairs)}
def hungarian(cost):
    """minimum-cost perfect assignment (square cost matrix) by the Hungarian algorithm — exact if the
    costs are integers/rationals."""
    n = len(cost); INF = float("inf")
    u = [Q(0)] * (n + 1); v = [Q(0)] * (n + 1); p = [0] * (n + 1); way = [0] * (n + 1)
    C = [[Q(cost[i][j]) for j in range(n)] for i in range(n)]
    for i in range(1, n + 1):
        p[0] = i; j0 = 0; minv = [Q(10) ** 18] * (n + 1); used = [False] * (n + 1)
        while True:
            used[j0] = True; i0 = p[j0]; delta = Q(10) ** 18; j1 = -1
            for j in range(1, n + 1):
                if not used[j]:
                    cur = C[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]: minv[j] = cur; way[j] = j0
                    if minv[j] < delta: delta = minv[j]; j1 = j
            for j in range(n + 1):
                if used[j]: u[p[j]] += delta; v[j] -= delta
                else: minv[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while j0:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
    assign = [0] * n
    for j in range(1, n + 1): assign[p[j] - 1] = j - 1
    total = sum(C[i][assign[i]] for i in range(n))
    return {"assignment": assign, "cost": total}


# ---------------------------------------------------------------- spanning trees / colouring ----
def spanning_tree_count(n, edges):
    """number of spanning trees by Kirchhoff's theorem: any cofactor of the graph Laplacian (exact det)."""
    L = [[Q(0)] * n for _ in range(n)]
    for u, v in edges:
        L[u][u] += 1; L[v][v] += 1; L[u][v] -= 1; L[v][u] -= 1
    minor = [[L[i][j] for j in range(1, n)] for i in range(1, n)]
    return int(determinant(minor)) if n > 1 else 1
def chromatic_number(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges: adj[u].add(v); adj[v].add(u)
    def colorable(k):
        color = [-1] * n
        def bt(u):
            if u == n: return True
            for c in range(k):
                if all(color[w] != c for w in adj[u]):
                    color[u] = c
                    if bt(u + 1): return True
                    color[u] = -1
            return False
        return bt(0)
    for k in range(1, n + 1):
        if colorable(k): return k
    return n


# ---------------------------------------------------------------- linear programming (exact simplex) ----
def _lp_pivot(T, cost, basis, m, ncols, allowed):
    """drive a tableau to optimality minimizing cost·vars (Bland's rule, exact ℚ). `allowed` bounds
    which columns may ENTER (used to forbid artificials in Phase II). Returns 'optimal'/'unbounded'."""
    for _ in range(100000):
        cb = [cost[basis[i]] for i in range(m)]
        red = {j: cost[j] - sum(cb[i] * T[i][j] for i in range(m)) for j in allowed}
        col = next((j for j in allowed if red[j] < 0), None)      # Bland: first improving column
        if col is None: return "optimal"
        ratios = [(T[i][-1] / T[i][col], i) for i in range(m) if T[i][col] > 0]
        if not ratios: return "unbounded"
        _, row = min(ratios, key=lambda r: (r[0], basis[r[1]]))
        piv = T[row][col]; T[row] = [x / piv for x in T[row]]; basis[row] = col
        for i in range(m):
            if i != row and T[i][col] != 0:
                f = T[i][col]; T[i] = [T[i][j] - f * T[row][j] for j in range(ncols + 1)]
    return "iteration_limit"

def linear_program(c, A, b, sense="max"):
    """max (or min) cᵀx subject to A x ≤ b, x ≥ 0 — EXACT rational TWO-PHASE simplex (Bland's rule).
    Phase I builds a feasible basis using artificial variables and DETECTS INFEASIBILITY (if the minimal
    artificial sum is > 0 the constraints cannot be satisfied); Phase II optimizes. Returns the optimal x
    and objective, or status 'infeasible' / 'unbounded' — it never reports a bogus 'optimal'."""
    m = len(A); n = len(c); sign = 1 if sense == "max" else -1
    A = [[Q(A[i][j]) for j in range(n)] for i in range(m)]
    b = [Q(bi) for bi in b]
    cvec = [Q(ci) for ci in c]
    # rows: [structural(n) | slack(m)] ; ensure rhs ≥ 0 (flip a row with negative rhs, which flips its slack)
    rows = []
    for i in range(m):
        row = A[i][:] + [Q(1 if k == i else 0) for k in range(m)]
        rhs = b[i]
        if rhs < 0: row = [-v for v in row]; rhs = -rhs
        rows.append([row, rhs])
    need_art = [rows[i][0][n + i] != 1 for i in range(m)]       # own slack no longer +1 ⇒ needs an artificial
    n_art = sum(need_art); ncols = n + m + n_art
    T = []; basis = []; ai = 0
    for i in range(m):
        row, rhs = rows[i]; full = row + [Q(0)] * n_art
        if need_art[i]:
            full[n + m + ai] = Q(1); basis.append(n + m + ai); ai += 1
        else:
            basis.append(n + i)
        T.append(full + [rhs])
    art_cols = set(range(n + m, n + m + n_art))
    if n_art:                                                   # ---- Phase I: minimize Σ artificials ----
        cost1 = [Q(0)] * (n + m) + [Q(1)] * n_art
        _lp_pivot(T, cost1, basis, m, ncols, list(range(ncols)))
        art_sum = sum(cost1[basis[i]] * T[i][-1] for i in range(m))
        if art_sum != 0:
            return {"status": "infeasible", "reason": "the constraints A x ≤ b, x ≥ 0 have no common solution"}
        for i in range(m):                                      # drive any artificial out of the basis (at 0)
            if basis[i] in art_cols:
                j = next((j for j in range(n + m) if T[i][j] != 0), None)
                if j is not None:
                    piv = T[i][j]; T[i] = [x / piv for x in T[i]]; basis[i] = j
                    for r in range(m):
                        if r != i and T[r][j] != 0:
                            f = T[r][j]; T[r] = [T[r][k] - f * T[i][k] for k in range(ncols + 1)]
    # ---- Phase II: optimize the real objective; artificials forbidden from re-entering ----
    cost2 = [(-sign) * cvec[j] if j < n else Q(0) for j in range(ncols)]   # minimize −sign·cᵀx
    st = _lp_pivot(T, cost2, basis, m, ncols, [j for j in range(n + m)])
    if st == "unbounded": return {"status": "unbounded"}
    x = [Q(0)] * n
    for i in range(m):
        if basis[i] < n: x[basis[i]] = T[i][-1]
    return {"status": "optimal", "x": x, "objective": sum(cvec[j] * x[j] for j in range(n))}


# ---------------------------------------------------------------- SAT (DPLL) ----
def sat(clauses, n_vars=None):
    """decide propositional satisfiability of a CNF (clauses = lists of nonzero ints; ±k = literal on var
    |k|) by DPLL with unit propagation. Returns a satisfying assignment or UNSAT."""
    if n_vars is None:
        n_vars = max((abs(l) for cl in clauses for l in cl), default=0)
    assign = {}
    def dpll(cls, a):
        a = dict(a); cls = [list(c) for c in cls]
        while True:                                          # unit propagation
            unit = next((c[0] for c in cls if len(c) == 1), None)
            if unit is None: break
            a[abs(unit)] = unit > 0
            newc = []
            for c in cls:
                if unit in c: continue
                if -unit in c:
                    c2 = [l for l in c if l != -unit]
                    if not c2: return None
                    newc.append(c2)
                else: newc.append(c)
            cls = newc
        if not cls: return a
        if any(len(c) == 0 for c in cls): return None
        v = abs(cls[0][0])
        for val in (True, False):
            r = dpll(cls + [[v if val else -v]], a)
            if r is not None: return r
        return None
    r = dpll(clauses, assign)
    if r is None: return {"satisfiable": False}
    return {"satisfiable": True, "assignment": {k: r.get(k, False) for k in range(1, n_vars + 1)}}
