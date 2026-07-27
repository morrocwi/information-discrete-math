"""idm.symbolic — a small EXACT symbolic engine (our own, not SymPy).

An expression is a finite tree; every transformation on it is a finite, exact rewrite. This is the
readout-first stance applied to algebra: a symbolic result is a finite readout of a finite tree, and no
continuum is needed to manipulate it. SymPy appears only as a reference comparator in the tests, never
producing `ours`.

Node representation (all finite):
    Fraction                      — a rational constant
    ('var', name)                 — a symbol
    ('add', [t, …])               — n-ary sum
    ('mul', [f, …])               — n-ary product
    ('pow', base, exp)            — power
    ('func', name, arg)           — sin/cos/tan/exp/log/sqrt
"""
import ast
from fractions import Fraction as Q

FUNCS = {"sin", "cos", "tan", "exp", "log", "ln", "sqrt"}


# ---------------------------------------------------------------- parse (string → tree) ----
def parse(s):
    return _from_ast(ast.parse(str(s), mode="eval").body)

def _from_ast(node):
    if isinstance(node, ast.Expression): return _from_ast(node.body)
    if isinstance(node, ast.Constant): return Q(node.value)
    if isinstance(node, ast.Name): return ("var", node.id)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return _mul([Q(-1), _from_ast(node.operand)])
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
        return _from_ast(node.operand)
    if isinstance(node, ast.BinOp):
        a, b = _from_ast(node.left), _from_ast(node.right)
        if isinstance(node.op, ast.Add): return _add([a, b])
        if isinstance(node.op, ast.Sub): return _add([a, _mul([Q(-1), b])])
        if isinstance(node.op, ast.Mult): return _mul([a, b])
        if isinstance(node.op, ast.Div): return _mul([a, ("pow", b, Q(-1))])
        if isinstance(node.op, ast.Pow): return ("pow", a, b)
    if isinstance(node, ast.Call):
        name = node.func.id
        if name in FUNCS: return ("func", "log" if name == "ln" else name, _from_ast(node.args[0]))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")

def _add(ts): return ("add", ts)
def _mul(fs): return ("mul", fs)


# ---------------------------------------------------------------- pretty-print (tree → string) ----
def tostr(e):
    if isinstance(e, Q):
        return str(e.numerator) if e.denominator == 1 else f"{e.numerator}/{e.denominator}"
    h = e[0]
    if h == "var": return e[1]
    if h == "add":
        parts = [tostr(t) for t in e[1]]
        return "(" + " + ".join(parts).replace("+ -", "- ") + ")"
    if h == "mul":
        return "*".join(_wrap(f) for f in e[1])
    if h == "pow":
        return f"{_wrap(e[1])}**{_wrap(e[2])}"
    if h == "func":
        return f"{e[1]}({tostr(e[2])})"
def _wrap(e):
    s = tostr(e)
    return f"({s})" if (isinstance(e, tuple) and e[0] in ("add", "mul")) or (isinstance(e, Q) and e < 0) else s


# ---------------------------------------------------------------- differentiate ----
def diff(e, v):
    if isinstance(e, Q): return Q(0)
    h = e[0]
    if h == "var": return Q(1) if e[1] == v else Q(0)
    if h == "add": return _add([diff(t, v) for t in e[1]])
    if h == "mul":
        fs = e[1]; terms = []
        for i in range(len(fs)):
            terms.append(_mul([diff(fs[i], v)] + [fs[j] for j in range(len(fs)) if j != i]))
        return _add(terms)
    if h == "pow":
        b, ex = e[1], e[2]
        if isinstance(ex, Q):                                   # power rule
            return _mul([ex, ("pow", b, ex - 1), diff(b, v)])
        # general: b^e (e' ln b + e b'/b)
        return _mul([e, _add([_mul([diff(ex, v), ("func", "log", b)]),
                              _mul([ex, diff(b, v), ("pow", b, Q(-1))])])])
    if h == "func":
        name, arg = e[1], e[2]; da = diff(arg, v)
        d = {"sin": ("func", "cos", arg),
             "cos": _mul([Q(-1), ("func", "sin", arg)]),
             "exp": ("func", "exp", arg),
             "log": ("pow", arg, Q(-1)),
             "sqrt": _mul([Q(1, 2), ("pow", arg, Q(-1, 2))]),
             "tan": ("pow", ("func", "cos", arg), Q(-2))}[name]
        return _mul([d, da])


# ---------------------------------------------------------------- simplify ----
def simplify(e, assumptions=None):
    # assumptions (a kernel AssumptionSet) is OPTIONAL and defaults to None → behavior is byte-identical
    # to before. When supplied, the nested-power collapse (bᵃ)ᶜ→b^(ac) is domain-GATED instead of
    # unconditional (the idm/symbolic.py:117 fix), via idm.kernel.engine.pow_pow_collapse_safe.
    if isinstance(e, Q): return e
    h = e[0]
    if h == "var": return e
    if h == "func":
        a = simplify(e[2], assumptions)
        if e[1] == "exp" and a == Q(0): return Q(1)
        if e[1] in ("log",) and a == Q(1): return Q(0)
        if e[1] == "sin" and a == Q(0): return Q(0)
        if e[1] == "cos" and a == Q(0): return Q(1)
        return ("func", e[1], a)
    if h == "pow":
        b = simplify(e[1], assumptions); ex = simplify(e[2], assumptions)
        if isinstance(ex, Q) and ex == 0: return Q(1)
        if isinstance(ex, Q) and ex == 1: return b
        if isinstance(b, Q) and isinstance(ex, Q) and ex.denominator == 1 and ex >= 0: return b ** int(ex)
        if isinstance(b, Q) and b == 1: return Q(1)
        if isinstance(b, tuple) and b[0] == "pow":
            if assumptions is None:
                return simplify(("pow", b[1], _mulq(b[2], ex)))
            from .kernel import engine as _eng
            if _eng.pow_pow_collapse_safe(b[1], ex, assumptions):
                return simplify(("pow", b[1], _mulq(b[2], ex)), assumptions)
            return ("pow", b, ex)
        return ("pow", b, ex)
    if h == "add":
        flat = []
        for t in e[1]:
            t = simplify(t, assumptions)
            if isinstance(t, tuple) and t[0] == "add": flat += t[1]
            else: flat.append(t)
        num = sum((t for t in flat if isinstance(t, Q)), Q(0))
        rest = [t for t in flat if not isinstance(t, Q)]
        # collect like terms by their symbolic key
        coll = {}
        for t in rest:
            c, base = _split_coeff(t); k = _key(base)
            coll[k] = (coll.get(k, (Q(0), base))[0] + c, base)
        out = []
        for c, base in coll.values():
            if c == 0: continue
            out.append(base if c == 1 else _mul([c, base]))
        if num != 0: out = [num] + out
        out = [o for o in out if o != Q(0)]
        if not out: return Q(0)
        return out[0] if len(out) == 1 else ("add", out)
    if h == "mul":
        flat = []
        for f in e[1]:
            f = simplify(f, assumptions)
            if isinstance(f, tuple) and f[0] == "mul": flat += f[1]
            else: flat.append(f)
        num = Q(1)
        for f in flat:
            if isinstance(f, Q): num *= f
        if num == 0: return Q(0)
        rest = [f for f in flat if not isinstance(f, Q)]
        # combine powers of identical bases
        powmap = {}
        for f in rest:
            b, ex = (f[1], f[2]) if isinstance(f, tuple) and f[0] == "pow" else (f, Q(1))
            k = _key(b); powmap[k] = (powmap.get(k, (b, Q(0)))[0], powmap.get(k, (b, Q(0)))[1] + (ex if isinstance(ex, Q) else None))
        out = []
        ok = True
        for b, ex in powmap.values():
            if ex is None: ok = False; break
            if ex == 0: continue
            out.append(b if ex == 1 else ("pow", b, ex))
        if not ok: out = rest
        factors = ([] if num == 1 else [num]) + out
        if not factors: return Q(1)
        return factors[0] if len(factors) == 1 else ("mul", factors)

def _mulq(a, b): return a * b if isinstance(a, Q) and isinstance(b, Q) else ("mul", [a, b])
def _split_coeff(t):
    if isinstance(t, tuple) and t[0] == "mul":
        nums = [f for f in t[1] if isinstance(f, Q)]; rest = [f for f in t[1] if not isinstance(f, Q)]
        c = Q(1)
        for n in nums: c *= n
        base = rest[0] if len(rest) == 1 else ("mul", rest) if rest else Q(1)
        return c, base
    return Q(1), t
def _key(e): return tostr(e)


# ---------------------------------------------------------------- expand ----
def expand(e):
    e = _expand(e)
    return simplify(e)
def _expand(e):
    if isinstance(e, Q) or e[0] == "var": return e
    if e[0] == "func": return ("func", e[1], _expand(e[2]))
    if e[0] == "add": return ("add", [_expand(t) for t in e[1]])
    if e[0] == "pow":
        b = _expand(e[1]); ex = e[2]
        if isinstance(ex, Q) and ex.denominator == 1 and 1 <= ex <= 12 and isinstance(b, tuple) and b[0] == "add":
            res = b
            for _ in range(int(ex) - 1): res = _distribute(res, b)
            return res
        return ("pow", b, ex)
    if e[0] == "mul":
        fs = [_expand(f) for f in e[1]]; res = fs[0]
        for f in fs[1:]: res = _distribute(res, f)
        return res
def _distribute(a, b):
    at = a[1] if isinstance(a, tuple) and a[0] == "add" else [a]
    bt = b[1] if isinstance(b, tuple) and b[0] == "add" else [b]
    return ("add", [("mul", [x, y]) for x in at for y in bt])


# ---------------------------------------------------------------- evaluate (numeric check) ----
def evaluate(e, env):
    import mpmath as mp
    if isinstance(e, Q): return mp.mpf(e.numerator) / e.denominator
    h = e[0]
    if h == "var": return mp.mpf(str(env[e[1]]))
    if h == "add": return sum((evaluate(t, env) for t in e[1]), mp.mpf(0))
    if h == "mul":
        r = mp.mpf(1)
        for f in e[1]: r *= evaluate(f, env)
        return r
    if h == "pow": return evaluate(e[1], env) ** evaluate(e[2], env)
    if h == "func":
        a = evaluate(e[2], env)
        return {"sin": mp.sin, "cos": mp.cos, "tan": mp.tan, "exp": mp.exp, "log": mp.log, "sqrt": mp.sqrt}[e[1]](a)


# ---------------------------------------------------------------- integrate (indefinite) ----
def integrate(e, v):
    """indefinite ∫ e dv for polynomials and elementary patterns with a linear argument; HOLD otherwise."""
    e = expand(e)
    if isinstance(e, tuple) and e[0] == "add":
        return simplify(("add", [integrate(t, v) for t in e[1]]))
    return _int_term(e, v)
def _int_term(e, v):
    if isinstance(e, Q): return _mul([e, ("var", v)])
    if e[0] == "var": return ("mul", [Q(1, 2), ("pow", ("var", v), Q(2))]) if e[1] == v else _mul([e, ("var", v)])
    c, base = _split_coeff(e)
    if c != 1: return _mul([c, _int_term(base, v)])
    if e[0] == "pow" and e[1] == ("var", v) and isinstance(e[2], Q):
        n = e[2]
        return ("func", "log", ("var", v)) if n == -1 else ("mul", [Q(1, int(n) + 1) if n.denominator == 1 else 1 / (n + 1), ("pow", ("var", v), n + 1)])
    if e[0] == "func":
        a = e[2]; sc = _lin_coeff(a, v)
        if sc is not None:
            prim = {"exp": ("func", "exp", a), "sin": _mul([Q(-1), ("func", "cos", a)]),
                    "cos": ("func", "sin", a)}.get(e[1])
            if prim is not None: return _mul([Q(1, 1) if sc == 1 else 1 / sc, prim]) if isinstance(sc, Q) else prim
    raise _Hold(f"no elementary antiderivative for {tostr(e)}")
def _lin_coeff(a, v):
    """if a = k·v (+ const), return k (rational); else None (only pure k·v handled for the 1/scale factor)."""
    if a == ("var", v): return Q(1)
    if isinstance(a, tuple) and a[0] == "mul":
        c, base = _split_coeff(a)
        if base == ("var", v): return c
    return None
class _Hold(Exception): pass


# ---------------------------------------------------------------- polynomial coeffs & solve ----
def poly_coeffs(e, v):
    """coefficients {power: Fraction} if e is a polynomial in v, else None."""
    e = expand(e); coeffs = {}
    terms = e[1] if isinstance(e, tuple) and e[0] == "add" else [e]
    for t in terms:
        c, base = _split_coeff(t)
        if base == Q(1) or isinstance(base, Q):
            coeffs[0] = coeffs.get(0, Q(0)) + c * (base if isinstance(base, Q) else Q(1)); continue
        if base == ("var", v):
            coeffs[1] = coeffs.get(1, Q(0)) + c; continue
        if isinstance(base, tuple) and base[0] == "pow" and base[1] == ("var", v) and isinstance(base[2], Q) and base[2].denominator == 1:
            p = int(base[2]); coeffs[p] = coeffs.get(p, Q(0)) + c; continue
        return None
    return coeffs

def solve(e, v):
    """solve e = 0 for v. Exact for linear & quadratic (radicals); rational/numeric roots for higher
    polynomials; HOLD for non-polynomial."""
    c = poly_coeffs(e, v)
    if c is None:
        return {"status": "HOLD", "reason": "non-polynomial equation — symbolic solve not available"}
    deg = max(c) if c else 0
    a = lambda k: c.get(k, Q(0))
    if deg == 1:
        return {"solutions": [tostr(simplify(_mul([-a(0), ("pow", a(1), Q(-1))])))]}
    if deg == 2:
        A, B, C = a(2), a(1), a(0); disc = B * B - 4 * A * C
        return {"solutions": [f"(-({B}) + sqrt({disc}))/(2*({A}))", f"(-({B}) - sqrt({disc}))/(2*({A}))"],
                "discriminant": tostr(disc)}
    from .exact import rational_roots
    coeffs = [a(k) for k in range(deg + 1)]
    rr = rational_roots(coeffs)
    return {"rational_solutions": [tostr(r) for r in rr], "degree": deg,
            "note": "higher-degree: rational roots exact; use kind 'poly_roots' for all complex roots"}


# ---------------------------------------------------------------- symbolic Taylor series ----
def taylor(e, v, x0, n):
    """exact symbolic Taylor coefficients c_0..c_n = f^(k)(x0)/k! by repeated symbolic differentiation."""
    from .exact import factorial
    cur = simplify(e); out = []
    for k in range(n + 1):
        val = simplify(_subst(cur, v, Q(x0) if not isinstance(x0, tuple) else x0))
        out.append(simplify(_mul([Q(1, factorial(k)), val])))
        cur = simplify(diff(cur, v))
    return out
def _subst(e, v, val):
    if isinstance(e, Q): return e
    if e[0] == "var": return val if e[1] == v else e
    if e[0] == "add": return ("add", [_subst(t, v, val) for t in e[1]])
    if e[0] == "mul": return ("mul", [_subst(f, v, val) for f in e[1]])
    if e[0] == "pow": return ("pow", _subst(e[1], v, val), _subst(e[2], v, val))
    if e[0] == "func": return ("func", e[1], _subst(e[2], v, val))
