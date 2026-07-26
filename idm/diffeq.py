"""idm.diffeq — differential equations as finite-difference readouts.

ODEs by finite Runge–Kutta, PDEs by finite-difference stencils (Crank–Nicolson heat, leapfrog wave,
Gauss–Seidel Poisson), boundary-value problems by a finite-difference linear system, and Sturm–Liouville
eigenvalues by Sturm-sequence bisection on the tridiagonal matrix. No completed continuum: a solution is
the value read off a finite grid at a declared resolution, refinable and (where relevant) stability-checked.
"""
import mpmath as mp
mp.mp.dps = 30
R = mp.mpf


# ---------------------------------------------------------------- tridiagonal solve (Thomas) ----
def thomas(a, b, c, d):
    """solve a tridiagonal system (sub-diagonal a, diagonal b, super-diagonal c, rhs d). Finite, O(n)."""
    n = len(d); cp = [R(0)] * n; dp = [R(0)] * n
    cp[0] = c[0] / b[0]; dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < n - 1 else R(0)
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = [R(0)] * n; x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


# ---------------------------------------------------------------- ODE systems (RK4) ----
def ode_system(fs, x0, y0, xT, N=2000):
    """solve y′ = f(x, y) for a vector y by classical RK4; returns y(xT). fs = [f_0, …], each f_i(x, *y)."""
    x = R(x0); y = [R(v) for v in y0]; h = (R(xT) - x) / N; m = len(fs)
    def F(xx, yy): return [f(xx, *yy) for f in fs]
    for _ in range(N):
        k1 = F(x, y)
        k2 = F(x + h / 2, [y[i] + h / 2 * k1[i] for i in range(m)])
        k3 = F(x + h / 2, [y[i] + h / 2 * k2[i] for i in range(m)])
        k4 = F(x + h, [y[i] + h * k3[i] for i in range(m)])
        y = [y[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(m)]
        x += h
    return y


# ---------------------------------------------------------------- heat (Crank–Nicolson) ----
def pde_heat(alpha, L, T, init, bc=(0, 0), Nx=80, Nt=400):
    """u_t = α u_xx on [0,L], Dirichlet u(0)=bc0, u(L)=bc1, u(x,0)=init(x). Crank–Nicolson (2nd order,
    unconditionally stable). Returns the profile [u(x_i, T)]."""
    alpha, L, T = R(alpha), R(L), R(T); dx = L / Nx; dt = T / Nt
    r = alpha * dt / dx ** 2
    x = [i * dx for i in range(Nx + 1)]
    u = [R(bc[0])] + [R(init(x[i])) for i in range(1, Nx)] + [R(bc[1])]
    n = Nx - 1                                            # interior unknowns
    a = [-r / 2] * n; b = [1 + r] * n; c = [-r / 2] * n
    for _ in range(Nt):
        d = []
        for i in range(1, Nx):
            d.append(u[i] + r / 2 * (u[i - 1] - 2 * u[i] + u[i + 1]))
        d[0] += r / 2 * u[0]; d[-1] += r / 2 * u[Nx]     # boundary contributions
        interior = thomas(a, b, c, d)
        u = [R(bc[0])] + interior + [R(bc[1])]
    return u


# ---------------------------------------------------------------- wave (explicit leapfrog) ----
def pde_wave(c_speed, L, T, init, init_vel=None, bc=(0, 0), Nx=100, Nt=None):
    """u_tt = c² u_xx on [0,L], Dirichlet BC, u(x,0)=init, u_t(x,0)=init_vel. Explicit leapfrog with a
    CFL-stable step. Returns [u(x_i, T)]."""
    c_speed, L, T = R(c_speed), R(L), R(T); dx = L / Nx
    dt = R("0.9") * dx / c_speed if Nt is None else T / Nt
    Nt = int(mp.floor(T / dt)); dt = T / Nt
    lam = (c_speed * dt / dx) ** 2
    x = [i * dx for i in range(Nx + 1)]
    u_prev = [R(bc[0])] + [R(init(x[i])) for i in range(1, Nx)] + [R(bc[1])]
    v = (lambda xx: R(0)) if init_vel is None else init_vel
    u = list(u_prev)                                     # first step (Taylor with initial velocity)
    for i in range(1, Nx):
        u[i] = u_prev[i] + dt * R(v(x[i])) + lam / 2 * (u_prev[i - 1] - 2 * u_prev[i] + u_prev[i + 1])
    for _ in range(Nt - 1):
        u_next = [R(bc[0])] + [R(0)] * (Nx - 1) + [R(bc[1])]
        for i in range(1, Nx):
            u_next[i] = 2 * u[i] - u_prev[i] + lam * (u[i - 1] - 2 * u[i] + u[i + 1])
        u_prev, u = u, u_next
    return u


# ---------------------------------------------------------------- Poisson 2-D (Gauss–Seidel) ----
def pde_poisson(f, box, bc=0, Nx=40, Ny=40, tol=R("1e-10"), it=20000):
    """Δu = f on [x0,x1]×[y0,y1], Dirichlet u = bc on the boundary. Gauss–Seidel to a residual tolerance.
    Returns the interior grid; bc may be a constant or a function bc(x,y)."""
    x0, x1, y0, y1 = [R(v) for v in box]; dx = (x1 - x0) / Nx; dy = (y1 - y0) / Ny
    X = [x0 + i * dx for i in range(Nx + 1)]; Y = [y0 + j * dy for j in range(Ny + 1)]
    bcf = bc if callable(bc) else (lambda a, b: R(bc))
    u = [[R(bcf(X[i], Y[j])) if i in (0, Nx) or j in (0, Ny) else R(0) for j in range(Ny + 1)] for i in range(Nx + 1)]
    dx2, dy2 = dx * dx, dy * dy; denom = 2 * (dx2 + dy2)
    for _ in range(it):
        err = R(0)
        for i in range(1, Nx):
            for j in range(1, Ny):
                new = (dy2 * (u[i - 1][j] + u[i + 1][j]) + dx2 * (u[i][j - 1] + u[i][j + 1])
                       - dx2 * dy2 * R(f(X[i], Y[j]))) / denom
                err = max(err, abs(new - u[i][j])); u[i][j] = new
        if err < tol:
            break
    return u


# ---------------------------------------------------------------- boundary-value problem ----
def ode_bvp(q, r, a, b, alpha, beta, N=400):
    """linear BVP  u'' = q(x)·u + r(x),  u(a)=alpha, u(b)=beta, by second-order finite differences
    (a tridiagonal solve). Returns [(x_i, u_i)]."""
    a, b = R(a), R(b); h = (b - a) / N; x = [a + i * h for i in range(N + 1)]
    n = N - 1
    sub = [R(1)] * n; diag = [R(0)] * n; sup = [R(1)] * n; d = [R(0)] * n
    for k in range(n):
        xi = x[k + 1]
        diag[k] = -2 - h * h * R(q(xi)); d[k] = h * h * R(r(xi))
    d[0] -= R(alpha); d[-1] -= R(beta)
    u_int = thomas(sub, diag, sup, d)
    u = [R(alpha)] + u_int + [R(beta)]
    return [(x[i], u[i]) for i in range(N + 1)]


# ---------------------------------------------------------------- Sturm–Liouville eigenvalues ----
def _sturm_count(diag, off, lam):
    """number of eigenvalues of the symmetric tridiagonal (diag, off) below lam — Sturm sequence."""
    n = len(diag); d = diag[0] - lam; count = 1 if d < 0 else 0
    for i in range(1, n):
        if d == 0: d = R("1e-30")
        d = (diag[i] - lam) - off[i - 1] ** 2 / d
        if d < 0: count += 1
    return count

def sturm_liouville(potential, L, n_eigs=5, N=200):
    """eigenvalues of  −u'' + V(x)·u = λ u  on [0,L] with u(0)=u(L)=0, by a finite-difference symmetric
    tridiagonal matrix whose eigenvalues are found by Sturm-sequence bisection (finite, decidable)."""
    L = R(L); h = L / N; x = [i * h for i in range(N + 1)]
    m = N - 1
    diag = [2 / h ** 2 + R(potential(x[i + 1])) for i in range(m)]
    off = [-1 / h ** 2] * (m - 1)
    lo, hi = min(diag) - 4 / h ** 2, max(diag) + 4 / h ** 2       # Gershgorin bounds
    eigs = []
    for k in range(1, n_eigs + 1):
        a, b = lo, hi
        for _ in range(200):
            mid = (a + b) / 2
            if _sturm_count(diag, off, mid) >= k: b = mid
            else: a = mid
        eigs.append((a + b) / 2)
    return eigs
