# analysis (extended)
from idm._solve_core import *  # noqa: F401,F403

@kind("gradient")
def _grad(p):
    names = p["vars"]; pt = [_val(v) for v in p["point"]]
    f = lambda **kw: F.evaluate(str(p["f"]), **kw)
    return _ok("gradient", AN.gradient(f, pt, names), "finite central differences per variable")
@kind("convolution", "Th_coqc")
def _conv(p): return _ok("convolution", AN.convolution(p["a"], p["b"]), "discrete Σ a[i]b[k−i]")
@kind("arc_length")
def _al(p): return _ok("arc_length", AN.arc_length(_fn(p["f"]), _val(p["a"]), _val(p["b"])), "∫√(1+f'²) finite quadrature")
@kind("fixed_point")
def _fp(p): return _ok("fixed_point", AN.fixed_point(_fn(p["g"]), _val(p["x0"])), "finite iteration x=g(x)")
@kind("summation", "Th_coqc")
def _sm(p):
    terms = [F.evaluate(str(p["term"]), n=n) for n in range(int(p["a"]), int(p["b"]) + 1)]
    tot = terms[0]
    for t in terms[1:]: tot = tot + t
    return _ok("summation", tot, "finite Σ")
