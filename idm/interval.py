"""idm.interval — rigorous certification by interval arithmetic.

This is the layer that turns "computes the right number" into "computes it WITH A GUARANTEE." Every value
here is a rigorous ENCLOSURE [lo, hi] proven to contain the true answer — obtained by validated interval
arithmetic (mpmath's directed-rounding interval context is the finite arithmetic engine). From it:
verified ranges of a function over a box, root enclosures proven by the intermediate-value theorem,
rigorous lower bounds on a minimum by interval branch-and-bound, and Gershgorin discs that provably
contain every eigenvalue. Where a bound cannot be certified, the routine returns HOLD.
"""
import mpmath as mp
mp.mp.dps = 30
_IV = mp.iv
_IV.dps = 30

_NS = {"exp": _IV.exp, "sin": _IV.sin, "cos": _IV.cos, "log": _IV.log, "ln": _IV.log,
       "sqrt": _IV.sqrt, "tan": lambda z: _IV.sin(z) / _IV.cos(z), "pi": _IV.pi, "e": _IV.e, "abs": abs}

def _num(v): return _IV.mpf([v, v]) if not isinstance(v, type(_IV.mpf(0))) else v
def _ival(a, b): return _IV.mpf([mp.mpf(str(a)), mp.mpf(str(b))])

def ieval(expr, env):
    """rigorous interval value of an expression, with each variable an interval env[name]=(lo,hi)."""
    ns = dict(_NS)
    for k, (lo, hi) in env.items(): ns[k] = _ival(lo, hi)
    return eval(compile(str(expr), "<iv>", "eval"), {"__builtins__": {}}, ns)

def _lohi(iv): return (mp.mpf(iv.a), mp.mpf(iv.b))


def enclose(expr, box):
    """a guaranteed enclosure [lo,hi] of `expr` over the box {var:(lo,hi)} — single-shot interval eval."""
    lo, hi = _lohi(ieval(expr, box))
    return {"lo": lo, "hi": hi, "width": hi - lo, "certified": True}


def verified_range(expr, var, a, b, depth=16):
    """rigorous [min,max] enclosure of a 1-var expression over [a,b], tightened by interval subdivision."""
    a, b = mp.mpf(str(a)), mp.mpf(str(b))
    lo = mp.inf; hi = -mp.inf; stack = [(a, b, 0)]
    while stack:
        x0, x1, d = stack.pop()
        iv = ieval(expr, {var: (x0, x1)}); ilo, ihi = _lohi(iv)
        if d >= depth or (x1 - x0) < mp.mpf(10) ** -12:
            lo = min(lo, ilo); hi = max(hi, ihi)
        else:
            m = (x0 + x1) / 2; stack.append((x0, m, d + 1)); stack.append((m, x1, d + 1))
    return {"min": lo, "max": hi, "certified": True, "method": "interval subdivision (rigorous)"}


def certified_root(expr, var, a, b, tol=mp.mpf(10) ** -25, it=400):
    """a VERIFIED root enclosure: if f is proven to change sign across [a,b] (rigorous interval values at
    the ends), bisect to a guaranteed interval containing a root (intermediate-value theorem). Else HOLD."""
    a, b = mp.mpf(str(a)), mp.mpf(str(b))
    fa = ieval(expr, {var: (a, a)}); fb = ieval(expr, {var: (b, b)})
    alo, ahi = _lohi(fa); blo, bhi = _lohi(fb)
    if not ((ahi < 0 and blo > 0) or (alo > 0 and bhi < 0)):
        return {"status": "HOLD", "reason": "no rigorously verified sign change on [a,b] — root not certified"}
    neg_left = ahi < 0
    for _ in range(it):
        m = (a + b) / 2; fm = ieval(expr, {var: (m, m)}); mlo, mhi = _lohi(fm)
        if b - a < tol: break
        if mlo <= 0 <= mhi: break                        # can't decide sign at m; enclosure already tight enough
        m_neg = mhi < 0
        if m_neg == neg_left: a = m
        else: b = m
    return {"status": "ok", "root_lo": a, "root_hi": b, "width": b - a, "certified": True,
            "method": "interval bisection (intermediate-value theorem)"}


def certified_min(expr, var, a, b, tol=mp.mpf(10) ** -10, max_boxes=200000):
    """a rigorous bracket [lower, upper] for the global minimum of a 1-var expression over [a,b] by
    interval branch-and-bound: `lower` is a proven lower bound, `upper` an achieved value."""
    a, b = mp.mpf(str(a)), mp.mpf(str(b))
    import heapq
    def val(x0, x1):
        iv = ieval(expr, {var: (x0, x1)}); return _lohi(iv)
    ilo, ihi = val(a, b); heap = [(ilo, a, b)]; best_upper = ihi; boxes = 0
    while heap and boxes < max_boxes:
        lb, x0, x1 = heapq.heappop(heap); boxes += 1
        if lb > best_upper: continue                     # prune
        if x1 - x0 < tol: return {"min_lower": lb, "min_upper": best_upper, "argmin_near": (x0 + x1) / 2, "certified": True}
        m = (x0 + x1) / 2
        for c0, c1 in ((x0, m), (m, x1)):
            clo, chi = val(c0, c1); best_upper = min(best_upper, chi)
            if clo <= best_upper: heapq.heappush(heap, (clo, c0, c1))
    lb = heap[0][0] if heap else best_upper
    return {"min_lower": lb, "min_upper": best_upper, "certified": True, "method": "interval branch-and-bound"}


def gershgorin(matrix):
    """Gershgorin discs — every eigenvalue of the matrix lies in ∪ discs(center=aᵢᵢ, radius=Σ_{j≠i}|aᵢⱼ|).
    Returns the discs and a rigorous bounding interval for the (real part of the) spectrum."""
    n = len(matrix); discs = []; lo = mp.inf; hi = -mp.inf
    for i in range(n):
        c = mp.mpf(str(matrix[i][i])); r = mp.fsum(abs(mp.mpf(str(matrix[i][j]))) for j in range(n) if j != i)
        discs.append({"center": c, "radius": r}); lo = min(lo, c - r); hi = max(hi, c + r)
    return {"discs": discs, "spectrum_bound": {"lo": lo, "hi": hi}, "certified": True}
