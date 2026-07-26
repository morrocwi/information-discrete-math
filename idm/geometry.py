"""idm.geometry — computational geometry on EXACT rational predicates.

Geometry is where floating point silently lies: a point is "almost" on a line, a hull edge "almost"
collinear, and the wrong branch is taken. Here every predicate — orientation, in-circle, intersection —
is an EXACT sign of a rational determinant, so the combinatorial answer (which side, is it inside, do
they cross) is decided, never estimated. Coordinates are taken as rationals; a point of "zero size" is
never needed — a point is just a pair of readouts.
"""
from fractions import Fraction as Q


def _P(p): return (Q(str(p[0])), Q(str(p[1])))

def orient(a, b, c):
    """exact orientation of the ordered triple: +1 counter-clockwise, −1 clockwise, 0 collinear.
    Sign of the 2×2 determinant — an exact combinatorial decision, no tolerance."""
    a, b, c = _P(a), _P(b), _P(c)
    d = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return {"orientation": (d > 0) - (d < 0), "det": d}

def convex_hull(points):
    """exact convex hull (Andrew's monotone chain) using rational orientation — no float, no epsilon."""
    pts = sorted(set(_P(p) for p in points))
    if len(pts) <= 1: return {"hull": [list(p) for p in pts], "vertices": len(pts)}
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0: lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0: upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    return {"hull": [[str(x), str(y)] for x, y in hull], "vertices": len(hull)}

def polygon_area(points):
    """exact area of a simple polygon by the shoelace formula — a rational, no rounding."""
    pts = [_P(p) for p in points]; n = len(pts)
    s = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    return {"area": abs(s) / 2, "signed_area": s / 2}

def point_in_polygon(point, polygon):
    """exact point-in-polygon by ray crossing with rational orientation (boundary detected exactly)."""
    p = _P(point); poly = [_P(v) for v in polygon]; n = len(poly)
    inside = False
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        # exact on-boundary test
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if cr == 0 and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]):
            return {"inside": True, "on_boundary": True}
        if (a[1] > p[1]) != (b[1] > p[1]):
            xint = a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if p[0] < xint: inside = not inside
    return {"inside": inside, "on_boundary": False}

def segments_intersect(p1, p2, p3, p4):
    """exact test whether segments p1p2 and p3p4 intersect (proper or at an endpoint), rational signs."""
    def o(a, b, c):
        a, b, c = _P(a), _P(b), _P(c)
        d = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]); return (d > 0) - (d < 0)
    def on(a, b, c):
        a, b, c = _P(a), _P(b), _P(c)
        return min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])
    o1, o2, o3, o4 = o(p1, p2, p3), o(p1, p2, p4), o(p3, p4, p1), o(p3, p4, p2)
    hit = (o1 != o2 and o3 != o4) or (o1 == 0 and on(p1, p2, p3)) or (o2 == 0 and on(p1, p2, p4)) \
        or (o3 == 0 and on(p3, p4, p1)) or (o4 == 0 and on(p3, p4, p2))
    return {"intersect": bool(hit)}

def closest_pair(points):
    """closest pair of points by EXACT squared rational distance (no sqrt needed to compare)."""
    pts = [_P(p) for p in points]; n = len(pts)
    best = None; pair = None
    for i in range(n):
        for j in range(i + 1, n):
            d2 = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
            if best is None or d2 < best: best = d2; pair = (i, j)
    return {"pair_indices": list(pair) if pair else None, "distance_squared": best,
            "points": [[str(pts[pair[0]][0]), str(pts[pair[0]][1])], [str(pts[pair[1]][0]), str(pts[pair[1]][1])]] if pair else None}

def in_circle(a, b, c, d):
    """exact in-circle predicate (Delaunay test): is d inside the circle through a,b,c? sign of a 3×3 det.
    +1 inside, −1 outside, 0 cocircular — the exact test Delaunay triangulation is built on."""
    a, b, c, d = _P(a), _P(b), _P(c), _P(d)
    def row(p): return (p[0] - d[0], p[1] - d[1], (p[0] - d[0]) ** 2 + (p[1] - d[1]) ** 2)
    ax, ay, az = row(a); bx, by, bz = row(b); cx, cy, cz = row(c)
    det = ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)
    return {"in_circle": (det > 0) - (det < 0), "det": det}
