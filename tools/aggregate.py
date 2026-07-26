#!/usr/bin/env python3
"""aggregate.py — the finite retained-readout toolkit engineers actually read values with.

Two families, both purely FINITE and discrete (the retained-information / I_ε aggregation with a chosen
combine rule — no continuum, no completed infinity):

  A. SEMIRING PATH ALGEBRAS — minimization/optimization on a network is linear algebra over a discrete
     semiring (⊕, ⊗). One generalized Floyd–Warshall solves ALL of them by swapping the operations:
        min-plus     ⊕=min ⊗=+     shortest path / minimum cost
        max-plus     ⊕=max ⊗=+     longest / critical path (scheduling)
        bottleneck   ⊕=max ⊗=min   widest path / maximum capacity
        minimax      ⊕=min ⊗=max   minimax path (least worst step)
        reachability ⊕=or  ⊗=and   connectivity / transitive closure
        count/prob   ⊕=+   ⊗=*      number of paths / reliability
     The semiring laws are machine-checked in formal/IDM_Tropical.v. The ⊕-identity (tropical ±∞) is a
     discrete "unreached" sentinel `None`, never a completed infinity.

  B. SCALAR READOUTS — the values read off a finite data series: MIN, MAX, SUM, MEAN, MEDIAN, MODE,
     RANGE, PEAK, peak-to-peak, RMS, variance/σ (population & sample), MAD, energy, power, crest & form
     factor, L1/L2/L∞ norms, argmin/argmax, geometric/harmonic/weighted mean, percentile, moving
     average, prefix sums, running min/max, first/second differences (rate/acceleration).

Exact ℚ is used wherever the answer is rational (sums, means, variance); √ (RMS, σ) is an algebraic
finite operation. Run `python3 tools/aggregate.py` for the self-check.
"""
from fractions import Fraction as Q
import math

# ============================================================ A. SEMIRING PATH ALGEBRAS ============
class Semiring:
    """(⊕, ⊗) with ⊕-identity = None (the discrete 'unreached'/absorbing sentinel) and a finite ⊗-identity."""
    def __init__(self, name, oplus_core, otimes_core, one):
        self.name = name; self._op = oplus_core; self._ot = otimes_core; self.one = one
    def oplus(self, a, b):
        if a is None: return b
        if b is None: return a
        return self._op(a, b)
    def otimes(self, a, b):
        if a is None or b is None: return None          # ⊕-identity is ⊗-absorbing (0·x=0)
        return self._ot(a, b)

MIN_PLUS   = Semiring("min-plus",   min,                    lambda a, b: a + b, 0)      # shortest path
MAX_PLUS   = Semiring("max-plus",   max,                    lambda a, b: a + b, 0)      # critical path
BOTTLENECK = Semiring("bottleneck", max,                    min,                None)   # widest path (one set per-solve)
MINIMAX    = Semiring("minimax",    min,                    max,                None)   # minimax path
REACH      = Semiring("reachability", (lambda a, b: a or b), (lambda a, b: a and b), True)   # connectivity
COUNT      = Semiring("count/prob", (lambda a, b: a + b),   (lambda a, b: a * b), 1)    # #paths / reliability

def mat_mul(A, B, sr):
    """n×p · p×m matrix product over the semiring (⊕-reduce of ⊗-products). Finite."""
    n, p, m = len(A), len(B), len(B[0])
    C = [[None] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            acc = None
            for k in range(p):
                acc = sr.oplus(acc, sr.otimes(A[i][k], B[k][j]))
            C[i][j] = acc
    return C

def walk_count(A):
    """number of walks (= paths in a DAG) between every pair: Σ_{L=1}^{n-1} A^L under sum-product. Finite."""
    n = len(A)
    total = [[A[i][j] for j in range(n)] for i in range(n)]
    P = A
    for _ in range(n - 1):
        P = mat_mul(P, A, COUNT)
        for i in range(n):
            for j in range(n):
                total[i][j] += P[i][j]
    return total

def all_pairs(W, sr):
    """Generalized Floyd–Warshall: all-pairs optimum over semiring `sr`. W is an n×n matrix (list of
    lists) with None where there is no direct edge. Returns the closed n×n matrix (None = unreachable).
    Finite: exactly n³ ⊕/⊗ operations."""
    n = len(W)
    D = [[W[i][j] for j in range(n)] for i in range(n)]
    one = sr.one
    if one is None:                                        # bottleneck/minimax: finite ⊗-identity from the data
        vals = [W[i][j] for i in range(n) for j in range(n) if W[i][j] is not None]
        if sr is BOTTLENECK: one = (max(vals) if vals else 0)     # self-capacity = the largest finite capacity
        else:                 one = (min(vals) if vals else 0)     # minimax self-step = the smallest finite step
    for i in range(n):
        D[i][i] = sr.oplus(D[i][i], one)                  # reflexive ⊗-identity on the diagonal
    for k in range(n):
        for i in range(n):
            for j in range(n):
                D[i][j] = sr.oplus(D[i][j], sr.otimes(D[i][k], D[k][j]))
    return D

# ============================================================ B. SCALAR READOUTS ===================
def _Q(xs): return [Q(x) for x in xs]

def rmin(xs):  return min(xs)
def rmax(xs):  return max(xs)
def rsum(xs):  return sum(_Q(xs), Q(0))
def count(xs): return len(xs)
def mean(xs):  return rsum(xs) / len(xs)                                   # AVG (exact ℚ)
def rrange(xs):        return max(xs) - min(xs)                            # spread
def peak(xs):          return max(abs(x) for x in xs)                      # PEAK = max |x|
def peak_to_peak(xs):  return max(xs) - min(xs)
def argmin(xs):        return min(range(len(xs)), key=lambda i: xs[i])
def argmax(xs):        return max(range(len(xs)), key=lambda i: xs[i])
def energy(xs):        return sum((Q(x) * Q(x) for x in xs), Q(0))         # Σ x²
def power(xs):         return energy(xs) / len(xs)                          # mean square
def rms(xs):           return math.sqrt(float(power(xs)))                  # √ mean square (AC/effective value)
def variance_pop(xs):  m = mean(xs); return sum(((Q(x) - m) ** 2 for x in xs), Q(0)) / len(xs)
def variance_samp(xs): m = mean(xs); return sum(((Q(x) - m) ** 2 for x in xs), Q(0)) / (len(xs) - 1)
def std_pop(xs):       return math.sqrt(float(variance_pop(xs)))
def std_samp(xs):      return math.sqrt(float(variance_samp(xs)))
def mad(xs):           m = mean(xs); return sum((abs(Q(x) - m) for x in xs), Q(0)) / len(xs)   # mean abs deviation
def median(xs):
    s = sorted(_Q(xs)); n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
def mode(xs):
    from collections import Counter
    return Counter(xs).most_common(1)[0][0]
def geometric_mean(xs):  return math.exp(sum(math.log(float(x)) for x in xs) / len(xs))   # positive data
def harmonic_mean(xs):   return len(xs) / float(sum(Q(1) / Q(x) for x in xs))
def weighted_mean(xs, w): return sum((Q(x) * Q(wi) for x, wi in zip(xs, w)), Q(0)) / sum(_Q(w), Q(0))
def crest_factor(xs):    return peak(xs) / rms(xs) if rms(xs) else float("nan")           # peak / RMS
def form_factor(xs):     r = rms(xs); a = sum((abs(Q(x)) for x in xs), Q(0)) / len(xs);   return r / float(a) if a else float("nan")
def norm_L1(xs):   return sum((abs(Q(x)) for x in xs), Q(0))
def norm_L2(xs):   return math.sqrt(float(energy(xs)))
def norm_Linf(xs): return max(abs(x) for x in xs)
def percentile(xs, p):                                                    # p in [0,100], nearest-rank
    s = sorted(xs); k = max(0, min(len(s) - 1, int(math.ceil(p / 100 * len(s))) - 1)); return s[k]

# ---- cumulative / windowed / difference readouts (retained aggregations over the series) ----
def prefix_sum(xs):
    out, acc = [], Q(0)
    for x in xs: acc += Q(x); out.append(acc)
    return out
def running_min(xs):
    out, m = [], None
    for x in xs: m = x if m is None else min(m, x); out.append(m)
    return out
def running_max(xs):
    out, m = [], None
    for x in xs: m = x if m is None else max(m, x); out.append(m)
    return out
def moving_average(xs, k):
    return [sum(_Q(xs[i:i + k]), Q(0)) / k for i in range(len(xs) - k + 1)]
def first_diff(xs):   return [Q(xs[i + 1]) - Q(xs[i]) for i in range(len(xs) - 1)]          # rate (D_ε)
def second_diff(xs):  d = first_diff(xs); return [d[i + 1] - d[i] for i in range(len(d) - 1)]  # curvature/accel

READOUTS = {                       # name -> function, the engineering value dashboard
    "min": rmin, "max": rmax, "sum": rsum, "count": count, "mean(avg)": mean, "median": median,
    "mode": mode, "range": rrange, "peak(|max|)": peak, "peak_to_peak": peak_to_peak,
    "rms": rms, "power(meansq)": power, "energy": energy, "variance_pop": variance_pop,
    "variance_samp": variance_samp, "std_pop": std_pop, "std_samp": std_samp, "mad": mad,
    "crest_factor": crest_factor, "form_factor": form_factor,
    "L1": norm_L1, "L2": norm_L2, "Linf": norm_Linf, "argmin": argmin, "argmax": argmax,
    "geometric_mean": geometric_mean, "harmonic_mean": harmonic_mean,
}

def dashboard(xs):
    return {name: fn(xs) for name, fn in READOUTS.items()}

# ============================================================ self-check ===========================
if __name__ == "__main__":
    import statistics as st
    ok = []
    # --- semiring path algebras on a small weighted digraph ---
    I = None
    W = [[0,   7,   9,   I,   I,  14],
         [7,   0,  10,  15,   I,   I],
         [9,  10,   0,  11,   I,   2],
         [I,  15,  11,   0,   6,   I],
         [I,   I,   I,   6,   0,   9],
         [14,  I,   2,   I,   9,   0]]
    sp = all_pairs(W, MIN_PLUS)
    ok.append(("shortest path 0→4 = 20", sp[0][4] == 20))          # 0-2-5-4 = 9+2+9 = 20
    wide = all_pairs(W, BOTTLENECK)
    ok.append(("widest 0→4 bottleneck = 9", wide[0][4] == 9))
    R = [[(w is not None) for w in row] for row in W]
    reach = all_pairs(R, REACH)
    ok.append(("reachable 0→4", reach[0][4] is True))
    # count paths in a tiny DAG adjacency (number of walks with ⊗=* ⊕=+)
    A = [[0,1,1,0],[0,0,1,1],[0,0,0,1],[0,0,0,0]]
    cnt = walk_count(A)
    ok.append(("#paths 0→3 (0-1-3,0-2-3,0-1-2-3)=3", cnt[0][3] == 3))
    # --- scalar readouts vs stdlib references ---
    xs = [3, -1, 4, 1, -5, 9, 2, -6]
    ok.append(("mean == statistics.mean", mean(xs) == Q(st.mean([Q(x) for x in xs]))))
    ok.append(("median == statistics.median", float(median(xs)) == st.median(xs)))
    ok.append(("variance_pop == pvariance", variance_pop(xs) == Q(st.pvariance([Q(x) for x in xs]))))
    ok.append(("std_samp ≈ stdev", abs(std_samp(xs) - st.stdev(xs)) < 1e-9))
    ok.append(("peak == 9", peak(xs) == 9))
    ok.append(("range == 15", rrange(xs) == 15))
    ok.append(("rms ≈ sqrt(mean sq)", abs(rms(xs) - math.sqrt(sum(x*x for x in xs)/len(xs))) < 1e-9))
    ok.append(("L1 == 31", norm_L1(xs) == 31))
    ok.append(("argmax == 5", argmax(xs) == 5))
    ok.append(("prefix_sum last == sum", prefix_sum(xs)[-1] == rsum(xs)))
    ok.append(("first_diff length", len(first_diff(xs)) == len(xs) - 1))
    ok.append(("moving_average(3) len", len(moving_average(xs, 3)) == len(xs) - 2))
    ok.append(("harmonic ≤ geometric ≤ mean (positives)",
               harmonic_mean([1,2,4,8]) <= geometric_mean([1,2,4,8]) <= float(mean([1,2,4,8]))))
    npass = sum(b for _, b in ok)
    for name, b in ok:
        print(f"  {'ok ' if b else 'FAIL'} {name}")
    print(f"aggregate self-check: {'PASS' if npass == len(ok) else 'FAIL'} ({npass}/{len(ok)})")
    raise SystemExit(0 if npass == len(ok) else 1)
