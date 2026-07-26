"""idm.parse — translate a world-language request into a structured problem (the 'translate-first' step).

This is deliberately a RULE-BASED, deterministic translator, not a guesser: it recognizes the shapes of
common requests ("integrate x^2 from 0 to 1", "is 97 prime?", "eigenvalues of [[2,0],[0,3]]") and emits
the exact structured `{"kind": …}` dict that idm.solve expects. When it cannot recognize the request
with confidence it returns HOLD with candidate kinds — it never routes a request to the wrong solver.
The philosophy: the world-language sentence is TRANSLATED into the information language before any math
runs; this module makes that translation explicit and checkable (it echoes the structured form back),
never silent.
"""
import re

_NUM = r"[-+]?\d+(?:\.\d+)?(?:/\d+)?(?:e[-+]?\d+)?"

def _expr(s):
    """normalize a written expression into Python/idm syntax (^→**, ln→log, implicit fixes)."""
    s = s.strip().rstrip(".?").strip()
    s = s.replace("^", "**")
    s = re.sub(r"\bln\b", "log", s)
    s = re.sub(r"\|([^|]+)\|", r"abs(\1)", s)
    return s

def _matrix(s):
    """parse a bracketed matrix like [[2,0],[0,3]] into a list of lists (ints/floats/fractions as str)."""
    try:
        import ast
        m = ast.literal_eval(s.strip())
        if isinstance(m, (list, tuple)) and m and isinstance(m[0], (list, tuple)):
            return [list(r) for r in m]
    except Exception:
        pass
    return None

def _bounds(text):
    """pull integration/summation bounds: 'from A to B', 'between A and B', 'on [A,B]', 'a=..b=..'."""
    m = re.search(r"from\s+(" + _NUM + r"|-?infinity|-?inf)\s+to\s+(" + _NUM + r"|infinity|inf)", text, re.I)
    if not m:
        m = re.search(r"between\s+(" + _NUM + r")\s+and\s+(" + _NUM + r")", text, re.I)
    if not m:
        m = re.search(r"on\s*\[\s*(" + _NUM + r")\s*,\s*(" + _NUM + r")\s*\]", text, re.I)
    if m:
        def cv(x):
            x = x.lower()
            if "inf" in x: return ("-inf" if x.startswith("-") else "inf")
            return x
        return cv(m.group(1)), cv(m.group(2))
    return None

def _var(text, default="x"):
    m = re.search(r"(?:with respect to|w\.?r\.?t\.?|in terms of|d)\s*([a-zA-Z])\b", text)
    if m: return m.group(1)
    return default

def _first_expr_after(text, kw):
    """the math chunk following a keyword, up to a bound/qualifier clause."""
    m = re.search(kw + r"\s+(?:of\s+|the\s+)?(.+?)(?:\s+from\s|\s+between\s|\s+on\s|\s+with respect\s|\s+wrt\s|\s+for\s|\s*$)", text, re.I)
    return _expr(m.group(1)) if m else None


# ---------------- rule table: (name, regex-guard, builder) ----------------
def _b_integral(t):
    if not re.search(r"\b(integral|integrate|∫)\b", t, re.I): return None
    e = _first_expr_after(t, r"(?:integral of|integrate|∫)")
    if not e: return None
    var = _var(t); bnd = _bounds(t)
    if bnd: return {"kind": "integral", "f": e, "a": bnd[0], "b": bnd[1], "var": var}
    return {"kind": "symbolic_integrate", "expr": e, "var": var}

def _b_derivative(t):
    if not re.search(r"\b(derivative|differentiate|d/d[a-z])\b", t, re.I): return None
    e = _first_expr_after(t, r"(?:derivative of|differentiate|d/d[a-z] of|d/d[a-z])")
    if not e: return None
    return {"kind": "symbolic_diff", "expr": e, "var": _var(t)}

def _b_limit(t):
    if not re.search(r"\blimit\b|\blim\b", t, re.I): return None
    e = _first_expr_after(t, r"(?:limit of|lim of|limit|lim)")
    ma = re.search(r"as\s+([a-z])\s*(?:->|→|approaches|goes to)\s*(" + _NUM + r"|infinity|inf|-inf)", t, re.I)
    if not e or not ma: return None
    pt = ma.group(2).lower()
    if "inf" in pt:
        return {"kind": "limit_infinity", "f": e, "var": ma.group(1), "sign": ("-" if pt.startswith("-") else "+")}
    return {"kind": "limit", "f": e, "var": ma.group(1), "point": pt}

def _b_factorize(t):
    m = re.search(r"\b(?:factor(?:ize|ise)?|prime factor(?:ization|s)?)\b.*?(" + _NUM.replace("[-+]?", "") + r")", t, re.I)
    if m: return {"kind": "factorize", "n": int(float(m.group(1)))}
    return None

def _b_prime(t):
    m = re.search(r"\bis\s+(\d+)\s+(?:a\s+)?prime\b", t, re.I) or re.search(r"\bprime\b.*?\b(\d+)\b", t, re.I)
    if m and re.search(r"\bprime\b", t, re.I) and re.search(r"\bis\b|\?", t, re.I):
        return {"kind": "is_prime", "n": int(m.group(1))}
    return None

def _b_gcd_lcm(t):
    m = re.search(r"\b(gcd|lcm|greatest common divisor|least common multiple)\b.*?(\d+)\D+(\d+)", t, re.I)
    if m:
        k = "gcd" if m.group(1).lower() in ("gcd", "greatest common divisor") else "lcm"
        return {"kind": k, "a": int(m.group(2)), "b": int(m.group(3))}
    return None

def _b_eigen(t):
    if not re.search(r"\beigen(value|values)?\b", t, re.I): return None
    mm = re.search(r"(\[\[.*\]\])", t)
    M = _matrix(mm.group(1)) if mm else None
    return {"kind": "eigenvalues", "matrix": M} if M else None

def _b_det(t):
    if not re.search(r"\b(determinant|det)\b", t, re.I): return None
    mm = re.search(r"(\[\[.*\]\])", t); M = _matrix(mm.group(1)) if mm else None
    return {"kind": "matrix_determinant", "matrix": M} if M else None

def _b_inverse(t):
    if not re.search(r"\b(inverse|invert)\b", t, re.I) or "matrix" not in t.lower() and "[[" not in t: return None
    mm = re.search(r"(\[\[.*\]\])", t); M = _matrix(mm.group(1)) if mm else None
    return {"kind": "matrix_inverse", "matrix": M} if M else None

def _b_solve_eq(t):
    if not re.search(r"\bsolve\b", t, re.I): return None
    m = re.search(r"solve\s+(.+?)\s*=\s*(.+?)(?:\s+for\s+([a-z]))?\s*$", t, re.I)
    if m:
        lhs, rhs = _expr(m.group(1)), _expr(m.group(2))
        expr = lhs if rhs.strip() in ("0", "0.0") else f"({lhs})-({rhs})"
        return {"kind": "symbolic_solve", "expr": expr, "var": m.group(3) or "x"}
    return None

def _b_series(t):
    if not re.search(r"\b(sum|series|summation)\b", t, re.I): return None
    e = _first_expr_after(t, r"(?:sum of|series of|summation of|sum|series)")
    if not e: return None
    return {"kind": "series_sum", "a_n": e.replace("x", "n"), "var": "n"}

def _b_taylor(t):
    if not re.search(r"\b(taylor|maclaurin)\b", t, re.I): return None
    e = _first_expr_after(t, r"(?:taylor series of|maclaurin series of|taylor of|taylor|maclaurin)")
    ma = re.search(r"(?:at|around|about)\s+(" + _NUM + r")", t, re.I)
    mo = re.search(r"order\s+(\d+)|to\s+(\d+)\s+terms", t, re.I)
    if not e: return None
    return {"kind": "taylor_series", "f": e, "var": _var(t), "a": (ma.group(1) if ma else "0"),
            "order": int((mo.group(1) or mo.group(2))) if mo else 6}

def _b_hull(t):
    if not re.search(r"\bconvex hull\b", t, re.I): return None
    mm = re.search(r"(\[\[.*\]\]|\[\(.*\)\])", t); pts = _matrix(mm.group(1)) if mm else None
    return {"kind": "convex_hull", "points": pts} if pts else None

def _b_regression(t):
    if not re.search(r"\b(regression|line of best fit|least squares fit)\b", t, re.I): return None
    xs = re.search(r"x\s*=\s*(\[[^\]]*\])", t); ys = re.search(r"y\s*=\s*(\[[^\]]*\])", t)
    if xs and ys:
        import ast
        return {"kind": "regression", "x": ast.literal_eval(xs.group(1)), "y": ast.literal_eval(ys.group(1)),
                "degree": 2 if re.search(r"\bquadratic\b", t, re.I) else 1}
    return None

def _b_ode(t):
    if not re.search(r"\b(ode|differential equation|dy/dx|y'\s*=)\b", t, re.I): return None
    m = re.search(r"(?:dy/dx|y')\s*=\s*(.+?)(?:,|\s+with|\s+y\(|\s*$)", t, re.I)
    y0 = re.search(r"y\(\s*(" + _NUM + r")\s*\)\s*=\s*(" + _NUM + r")", t)
    if m and y0:
        return {"kind": "ode", "f": _expr(m.group(1)), "x0": y0.group(1), "y0": y0.group(2),
                "x1": (_bounds(t)[1] if _bounds(t) else "1")}
    return None

def _b_evaluate(t):
    m = re.search(r"^\s*(?:evaluate|compute|what is|calculate)\s+(.+?)\s*(?:at\s+([a-z])\s*=\s*(" + _NUM + r"))?\s*[.?]?\s*$", t, re.I)
    if m and re.search(r"[-+*/^()\d]", m.group(1)):
        e = _expr(m.group(1))
        if m.group(2):
            return {"kind": "evaluate", "expr": e, "var": m.group(2), "at": m.group(3)}
        if any(c.isalpha() for c in re.sub(r"\b(pi|e|log|sin|cos|tan|exp|sqrt|abs)\b", "", e)):
            return None  # has a free variable but no value → not a pure evaluation
        return {"kind": "evaluate", "expr": e}
    return None

_RULES = [
    ("integral", _b_integral), ("derivative", _b_derivative), ("limit", _b_limit),
    ("taylor", _b_taylor), ("series", _b_series), ("ode", _b_ode),
    ("factorize", _b_factorize), ("is_prime", _b_prime), ("gcd/lcm", _b_gcd_lcm),
    ("eigenvalues", _b_eigen), ("determinant", _b_det), ("matrix_inverse", _b_inverse),
    ("solve", _b_solve_eq), ("convex_hull", _b_hull), ("regression", _b_regression),
    ("evaluate", _b_evaluate),
]

# keyword → candidate kinds, used to suggest when nothing parses cleanly
_HINTS = {
    r"prime|factor": ["is_prime", "factorize", "primality_certificate", "primes"],
    r"integ|∫": ["integral", "symbolic_integrate", "double_integral", "improper_integral"],
    r"deriv|differen": ["symbolic_diff", "derivative", "gradient"],
    r"eigen|matrix|determinant": ["eigenvalues", "matrix_determinant", "matrix_inverse", "matrix_rank"],
    r"prob|distribution|test|regress": ["binomial", "normal", "regression", "t_test", "chi_square_test"],
    r"graph|shortest|flow|path": ["dijkstra", "max_flow", "shortest_path", "spanning_tree_count"],
    r"geometr|polygon|hull|point": ["convex_hull", "polygon_area", "point_in_polygon", "closest_pair"],
    r"rsa|crypto|elliptic|discrete log": ["rsa_keygen", "ec_mul", "discrete_log", "primality_certificate"],
}


def parse(text):
    """translate a world-language request into a structured problem dict for idm.solve, or HOLD.

    Returns the recognized `{"kind": …, …}` (with a `_source` echo of the original text so the
    translation is checkable), or {"status":"HOLD", …, "candidates":[…]} when no rule matches with
    confidence — never a guessed, possibly-wrong routing."""
    if not isinstance(text, str) or not text.strip():
        return {"status": "HOLD", "reason": "empty request"}
    t = " ".join(text.strip().split())
    for name, builder in _RULES:
        try:
            got = builder(t)
        except Exception:
            got = None
        if got and got.get("kind") and all(v is not None for v in got.values()):
            got["_source"] = text
            got["_note"] = "rule-based translation of a world-language request — verify the structured form"
            return got
    # no clean parse → offer honest candidates rather than guess
    cand = []
    for pat, ks in _HINTS.items():
        if re.search(pat, t, re.I):
            cand.extend(ks)
    return {"status": "HOLD", "reason": "could not translate this request into a single structured kind",
            "candidates": sorted(set(cand)) or None,
            "hint": "phrase it like 'integrate x^2 from 0 to 1', 'is 97 prime?', 'eigenvalues of [[2,0],[0,3]]', "
                    "or call idm.solve directly with a structured {'kind': …}."}


def parse_and_solve(text):
    """convenience: translate then solve. Returns the solve result annotated with the translation."""
    from .solve import solve
    p = parse(text)
    if p.get("status") == "HOLD":
        return p
    res = solve({k: v for k, v in p.items() if not k.startswith("_")})
    res["_translated_from"] = text
    res["_structured"] = {k: v for k, v in p.items() if not k.startswith("_")}
    return res
