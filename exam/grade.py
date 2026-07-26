#!/usr/bin/env python3
"""grade — robust automated answer grading (RAM-free, no agents). Handles int/frac/expr/text/tuple/degrees."""
import re
def _clean(a):
    a=str(a).strip()
    # unwrap \boxed, \text, \mathrm (keep inner content)
    for _ in range(3):
        a=re.sub(r"\\(?:boxed|text|mathrm|textbf|mathbf|operatorname)\{([^{}]*)\}", r"\1", a)
    a=re.sub(r"\\left|\\right|\\!|\\,|\;|\\ |\\displaystyle|\$|\\%|percent|\^\\?\{?\\circ\}?|degrees?|\\circ", "", a)
    a=a.replace("\\dfrac","\\frac").replace("\\tfrac","\\frac")
    for _ in range(4):
        a=re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", a)
    a=a.replace("\\pi","pi").replace("\\cdot","*").replace("\\times","*").replace("\\sqrt","sqrt")
    a=re.sub(r"\\[a-zA-Z]+","",a)              # drop remaining latex commands
    a=a.replace("^","**").replace("{","(").replace("}",")")
    a=a.replace(" ","").replace(",","").replace("$","").strip().strip(".").strip()
    return a
def _tuple(a):
    m=re.match(r"^\(?(.+)\)?$",a)
    inner=a.strip("()")
    return [x for x in re.split(r"[;,]|\)\(", inner) if x]
def grade(solver, benchmark):
    s,b=_clean(solver),_clean(benchmark)
    if s==b: return True
    # text answer (letters only) — compare alphanumeric lowercase
    sa=re.sub(r"[^a-z0-9]","",s.lower()); ba=re.sub(r"[^a-z0-9]","",b.lower())
    if ba and sa==ba: return True
    if ba and len(ba)>3 and (ba in sa or sa in ba): return True   # containment for text
    # sympy equivalence
    try:
        import sympy as sp
        if sp.simplify(sp.sympify(s.replace("pi","pi"))-sp.sympify(b))==0: return True
    except Exception: pass
    # numeric
    try:
        return abs(float(s)-float(b))<1e-6
    except Exception: pass
    return False
if __name__=="__main__":
    T=[("42","42"),("\\frac{1}{2}","0.5"),("\\boxed{7}","7"),("2/4","1/2"),
       ("Evelyn","\\text{Evelyn}"),("90","90^\\circ"),("(3, \\pi/2)","\\left( 3, \\frac{\\pi}{2} \\right)"),
       ("f(n)=cn","f(n) = cn")]
    for s,b in T: assert grade(s,b),(s,b)
    assert not grade("(p!)^2","2(p!)^2") and not grade("62","28")
    print("grade self-check OK — int/frac/boxed/text/degrees/tuple/expr; rejects wrong")
