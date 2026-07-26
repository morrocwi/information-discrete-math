"""idm.optimize — continuous optimization as finite iterations.

Gradient descent with a finite backtracking line search, Newton's method for minimization and for
nonlinear systems (finite-difference gradient / Hessian / Jacobian, the linear step solved by mpmath's
LU), exact-ℚ linear least squares (normal equations), and equality-constrained minimization by Newton on
the KKT system (Lagrange multipliers). Every result is a finite readout at a declared tolerance; no
completed limit is formed.
"""
from fractions import Fraction as Q
import mpmath as mp
mp.mp.dps = 30
R = mp.mpf


def _grad(f, x, h=R("1e-10")):
    n = len(x); g = []
    for i in range(n):
        xp = list(x); xm = list(x); xp[i] += h; xm[i] -= h
        g.append((f(xp) - f(xm)) / (2 * h))
    return g

def _hess(f, x, h=R("1e-5")):
    n = len(x); H = [[R(0)] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            xpp = list(x); xpm = list(x); xmp = list(x); xmm = list(x)
            xpp[i] += h; xpp[j] += h; xpm[i] += h; xpm[j] -= h
            xmp[i] -= h; xmp[j] += h; xmm[i] -= h; xmm[j] -= h
            H[i][j] = (f(xpp) - f(xpm) - f(xmp) + f(xmm)) / (4 * h * h)
    return H

def _solve(A, b):
    return list(mp.lu_solve(mp.matrix(A), mp.matrix(b)))


def gradient_descent(f, x0, lr=R("0.1"), iters=5000, tol=R("1e-12")):
    """minimize f: ℝⁿ→ℝ from x0 by steepest descent with backtracking line search."""
    x = [R(v) for v in x0]
    for _ in range(iters):
        g = _grad(f, x); gn = mp.sqrt(mp.fsum(gi * gi for gi in g))
        if gn < tol: break
        step = lr; fx = f(x)                              # backtracking (Armijo)
        for _ in range(60):
            xn = [x[i] - step * g[i] for i in range(len(x))]
            if f(xn) < fx - R("1e-4") * step * gn * gn: break
            step /= 2
        x = [x[i] - step * g[i] for i in range(len(x))]
    return {"argmin": x, "min": f(x)}

def newton_min(f, x0, iters=100, tol=R("1e-14")):
    """minimize f by Newton's method: x ← x − H⁻¹∇f (finite gradient & Hessian)."""
    x = [R(v) for v in x0]
    for _ in range(iters):
        g = _grad(f, x)
        if mp.sqrt(mp.fsum(gi * gi for gi in g)) < tol: break
        d = _solve(_hess(f, x), [-gi for gi in g])
        x = [x[i] + d[i] for i in range(len(x))]
    return {"argmin": x, "min": f(x)}

def newton_system(Fs, x0, iters=100, tol=R("1e-14"), h=R("1e-9")):
    """solve F(x)=0 (a vector of functions Fs) by Newton with a finite-difference Jacobian."""
    x = [R(v) for v in x0]; n = len(x)
    for _ in range(iters):
        Fx = [g(x) for g in Fs]
        if mp.sqrt(mp.fsum(v * v for v in Fx)) < tol: break
        J = [[R(0)] * n for _ in range(n)]
        for j in range(n):
            xp = list(x); xm = list(x); xp[j] += h; xm[j] -= h
            for i in range(n): J[i][j] = (Fs[i](xp) - Fs[i](xm)) / (2 * h)
        d = _solve(J, [-v for v in Fx])
        x = [x[i] + d[i] for i in range(n)]
    return {"root": x, "residual": mp.sqrt(mp.fsum(g(x) ** 2 for g in Fs))}

def least_squares(A, b):
    """exact-ℚ linear least squares: solve the normal equations (AᵀA)x = Aᵀb."""
    from .exact import transpose, mat_mul, solve_linear
    At = transpose(A); AtA = mat_mul(At, A)
    Atb = [sum(Q(At[i][k]) * Q(b[k]) for k in range(len(b))) for i in range(len(At))]
    x = solve_linear(AtA, Atb)
    res = [sum(Q(A[r][c]) * x[c] for c in range(len(x))) - Q(b[r]) for r in range(len(A))]
    return {"x": x, "residual_sq": sum(rr * rr for rr in res)}

def lagrange_min(f, gs, x0, lam0=None, iters=100, tol=R("1e-13")):
    """minimize f subject to equality constraints g_i(x)=0, by Newton on the KKT system
    ∇f − Σλ_i∇g_i = 0, g_i = 0 (a finite-difference stationarity solve)."""
    n = len(x0); m = len(gs); lam0 = lam0 or [R(0)] * m
    def L_grad(z):                                        # z = [x…, λ…]; returns [∂L/∂x…, g…]
        x = z[:n]; lam = z[n:]
        gx = _grad(f, x)
        for i, g in enumerate(gs):
            gg = _grad(g, x)
            for k in range(n): gx[k] -= lam[i] * gg[k]
        return gx + [g(x) for g in gs]
    Fs = [(lambda z, _i=i: L_grad(z)[_i]) for i in range(n + m)]
    sol = newton_system(Fs, list(x0) + list(lam0), iters, tol)
    z = sol["root"]
    return {"argmin": z[:n], "multipliers": z[n:], "min": f(z[:n])}
