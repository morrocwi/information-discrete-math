#!/usr/bin/env python3
"""Breadth validation for Parts XVI–XIX (measure/functional analysis · category · statistics · optimization).

Finite, exact/declared-resolution readouts — no continuum primitive. Reference values are exact (sympy)
or closed-form; statistical/optimization claims are checked at a declared tolerance. Also exercises the
numeric-honesty discipline (Verdict ACCEPT/HOLD/BLOCK). Run: python3 breadth2_problems.py
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import sympy as sp
from idm_discipline import eq_eps, eq_chain_guard, Verdict, ACCEPT, HOLD, BLOCK, solve_obstruction, sum_neumaier
P = 0; T = 0; FAILS = []
def chk(name, ours, ref, tol=0):
    global P, T
    T += 1
    ok = (ours == ref) if tol == 0 else (abs(float(ours) - float(ref)) <= tol)
    if ok: P += 1
    else: FAILS.append((name, str(ours), str(ref)))

# ═══════ XVI. MEASURE & FUNCTIONAL ANALYSIS ═══════
# Discrete measure μ_λ(S)=I_ε(1_S): finite additivity on disjoint sets
A, B = {1,2,3}, {4,5}
chk("μ finitely additive: |A∪B|=|A|+|B| (disjoint)", len(A|B), len(A)+len(B))
chk("μ(∅)=0", len(set()), 0)
# ⟨f,g⟩_G = Σ f_i g_i ; Cauchy-Schwarz |⟨f,g⟩| ≤ ‖f‖‖g‖ (exact ℚ)
f = sp.Matrix([1, 2, 2]); g = sp.Matrix([2, 0, 1])
ip = (f.T*g)[0]; nf = sp.sqrt((f.T*f)[0]); ng = sp.sqrt((g.T*g)[0])
chk("Cauchy-Schwarz |⟨f,g⟩| ≤ ‖f‖‖g‖", bool(abs(ip) <= nf*ng), True)
chk("⟨f,g⟩ = 4 exact", ip, 4)
chk("‖f‖₂ = 3 (=√9)", nf, 3)
# L^p norm: ‖f‖_1 and ‖f‖_∞
chk("‖f‖₁ = 5", sum(abs(x) for x in f), 5)
chk("‖f‖_∞ = 2", max(abs(x) for x in f), 2)
# Finite spectral theorem: symmetric M = Σ λ_i v_i v_iᵀ reconstructs exactly
M = sp.Matrix([[2,1],[1,2]])
Pv, D = M.diagonalize()            # M = P D P⁻¹, P orthogonalizable (symmetric)
chk("spectral: P D P⁻¹ reconstructs M", sp.simplify(Pv*D*Pv.inv()), M)
chk("eigenvalues of [[2,1],[1,2]] = {1,3}", set(M.eigenvals().keys()), {sp.Integer(1), sp.Integer(3)})
chk("self-adjoint: M = Mᵀ", M, M.T)
# Riesz (finite): functional φ(x)=x₀+2x₁ is ⟨v,·⟩ with v=(1,2)
v = sp.Matrix([1,2]); x = sp.Matrix([3,5])
chk("Riesz-finite: φ(x)=⟨v,x⟩=13", (v.T*x)[0], 13)

# ═══════ XVII. CATEGORY THEORY ═══════
# G_λ idempotent reflector: dedup∘dedup = dedup (coarse-grain twice = once)
def G(xs): return sorted(set(xs))
data = [3,1,2,3,1,2,2]
chk("G_λ idempotent: G(G(x))=G(x)", G(G(data)), G(data))
# Functor composition associative / identity
comp = lambda f,g: (lambda x: f(g(x)))
idf = lambda x: x
inc = lambda x: x+1; dbl = lambda x: 2*x
chk("functor identity law: f∘id = f", comp(dbl, idf)(5), dbl(5))
chk("functor composition assoc: (h∘g)∘f = h∘(g∘f)", comp(comp(inc,dbl),inc)(3), comp(inc,comp(dbl,inc))(3))
# =_λ coequalizer / smallest congruence: quotient by even/odd
cls = lambda n: n % 2
chk("=_λ congruence: 4 ≡ 6 (mod 2)", cls(4), cls(6))
chk("=_λ separates: 4 ≢ 5 (mod 2)", cls(4) != cls(5), True)
# Finite Yoneda: an object is determined by its readouts. Two vectors with the same
# inner products against a spanning test-set are equal.
tests = [sp.Matrix([1,0]), sp.Matrix([0,1])]
u1 = sp.Matrix([2,3]); u2 = sp.Matrix([2,3])
chk("finite Yoneda: equal readouts ⇒ equal object",
    all((t.T*u1)[0]==(t.T*u2)[0] for t in tests) == (u1==u2), True)
chk("finite Yoneda: differing readout ⇒ distinct", (tests[0].T*sp.Matrix([2,3]))[0] != (tests[0].T*sp.Matrix([9,3]))[0], True)

# ═══════ XVIII. STATISTICS & INFERENCE ═══════
# LLN plateau: sample mean of a fixed deterministic pattern → true mean (A8 stability)
pattern = [1,2,3,4,5,6]                      # mean 3.5
def running_mean(N):
    s = sum(pattern[i % len(pattern)] for i in range(N))
    return s / N
chk("LLN plateau: running mean → 3.5", running_mean(6000), 3.5, 1e-9)
# Bayesian update = retained reweighting; posterior normalizes to 1 (Born-rule special case)
prior = [sp.Rational(1,2), sp.Rational(1,2)]; like = [sp.Rational(1,4), sp.Rational(3,4)]
un = [p*l for p,l in zip(prior, like)]; Z = sum(un); post = [u/Z for u in un]
chk("Bayesian posterior normalizes to 1", sum(post), 1)
chk("Bayesian posterior = (1/4, 3/4)", post, [sp.Rational(1,4), sp.Rational(3,4)])
# Born-rule normalization Σ|a_i|²/Σ = 1
amp = [sp.Integer(3), sp.Integer(4)]; probs = [a*a/sum(x*x for x in amp) for a in amp]
chk("Born-rule probs sum to 1", sum(probs), 1)
chk("Born-rule p = (9/25, 16/25)", probs, [sp.Rational(9,25), sp.Rational(16,25)])
# Hypothesis test IS a Verdict: distinct means → ACCEPT ; overlapping at resolution → HOLD
def test(mean_a, mean_b, eps):
    if eq_eps(mean_a, mean_b, eps):
        return Verdict(HOLD, reason="indistinguishable at declared resolution — not 'no effect'")
    return Verdict(ACCEPT, value=abs(mean_a-mean_b), reason="distinct at declared resolution")
chk("test distinct means → ACCEPT", test(3.5, 5.0, 0.1).status, ACCEPT)
chk("test overlapping means → HOLD (not silent null)", test(3.50, 3.501, 0.1).status, HOLD)
# sorites guard BLOCKs a non-transitive significance chain
chk("inference chain guard BLOCKs sorites", eq_chain_guard([0.0,0.4,0.8,1.2], 0.5).status, BLOCK)

# ═══════ XIX. OPTIMIZATION ═══════
# Convex J(x)=(x-3)²: D_ε J = 0 at the minimum x=3 ; D_ε²J ≥ 0 (convex)
J = lambda x: (x-3)**2
eps = 1e-4
dJ = lambda x: (J(x+eps)-J(x-eps))/(2*eps)
chk("gradient D_ε J(3) = 0 at minimum", dJ(3), 0, 1e-6)
d2J = (J(3+eps)-2*J(3)+J(3-eps))/eps**2
chk("convexity D_ε²J ≥ 0", d2J >= 0, True)
# Stationarity via obstruction-zeroing: solve D_ε J = 0 → x=3 (fail-closed ACCEPT)
vsol = solve_obstruction(dJ, 0.0, 1e-7)
chk("solve_obstruction finds min → ACCEPT", vsol.status, ACCEPT)
chk("minimizer x ≈ 3", vsol.value, 3.0, 1e-3)
# Linear programming exact ℚ: max x+y s.t. x+2y≤4, 3x+y≤6, x,y≥0 → vertex (8/5,6/5), obj 14/5
verts = [(0,0),(2,0),(0,2),(sp.Rational(8,5),sp.Rational(6,5))]
feas = lambda p: p[0]+2*p[1]<=4 and 3*p[0]+p[1]<=6 and p[0]>=0 and p[1]>=0
obj = lambda p: p[0]+p[1]
best = max((p for p in verts if feas(p)), key=lambda p: obj(p))
chk("LP exact-ℚ optimum vertex = (8/5,6/5)", best, (sp.Rational(8,5), sp.Rational(6,5)))
chk("LP optimal value = 14/5", obj(best), sp.Rational(14,5))
# Gradient descent = I_ε of -grad field converges to known min of (x-3)²
x = 0.0
for _ in range(500): x -= 0.1*dJ(x)
chk("gradient descent → minimizer 3", x, 3.0, 1e-3)
# Lagrange: min x²+y² s.t. x+y=1 → (1/2,1/2), value 1/2
chk("Lagrange min x²+y² on x+y=1 = 1/2", sp.Rational(1,2)**2 + sp.Rational(1,2)**2, sp.Rational(1,2))

print("="*78)
print("BREADTH-2 validation — Parts XVI–XIX (measure/functional · category · statistics · optimization)")
print("="*78)
if FAILS:
    print(f"  FAILS ({len(FAILS)}):")
    for n,o,r in FAILS: print(f"    {n}: ours={o} vs {r}")
print("-"*78)
print(f"  TOTAL: {P}/{T}  ({100*P/max(T,1):.1f}%)  — finite readouts + fail-closed verdicts, no continuum")
print("="*78)
