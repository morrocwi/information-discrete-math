#!/usr/bin/env python3
"""provefull/networks.py — COMPUTING / NETWORKS continuum-frontier problems.

~200 problems from information theory, Markov chains / PageRank, queueing theory, signal processing
(DFT), and discrete combinatorics on graphs/sequences — each one classically leans on a continuum
object (a dominant eigenvector as an n->infinity power-iteration limit, a stationary distribution as
a fixed point, a geometric-series limit for mean queue length, ln/log2/e in entropy and capacity
formulas, roots of unity / continuum Fourier coefficients, Stirling's asymptotic with sqrt(2 pi n),
the Euler-Mascheroni constant in the harmonic number, e^{-x} tails in the birthday/coupon problems).

Every 'ours' value is built ONLY from K.* finite-discrete primitives (K.R arithmetic, K.exp_finite,
K.log_finite, K.sin_finite, K.cos_finite, K.pow_finite, K.richardson, finite sums/products, K.T.ode_rk4,
mp.sqrt/mp.floor as algebraic/integer readouts). 'ref' values use plain mpmath transcendentals
(mp.exp/log/sin/cos/pi/e/euler/...) as the standard textbook comparison — never as 'ours'.
"""
import _kernel as K
import mpmath as mp

R = K.R
LN2 = K.LN2_FINITE
PI = K.PI_FINITE
E = K.E_FINITE


def _log2_finite(x):
    return K.log_finite(x) / LN2


def _weighted_geom_partial(rho, n):
    """sum_{m=0}^{n-1} m*rho^m via iterative multiplication (exact finite integer-power recurrence,
    rho^{m+1}=rho^m*rho -- elementary arithmetic, no exp/log needed for an integer exponent)."""
    n = int(n)
    s = R(0); p = R(1)
    for m in range(n):
        s += m * p
        p *= rho
    return s


def _geom_partial(rho, n):
    """sum_{m=0}^{n-1} rho^m via iterative multiplication."""
    n = int(n)
    s = R(0); p = R(1)
    for m in range(n):
        s += p
        p *= rho
    return s


def _geom_N_for(rho, digits=48):
    """finite cutoff N so that rho^N < 10^-digits (genuine geometric decay is exponential in n, so a
    direct finite partial sum to this N is already exact to the working precision -- no extrapolation
    needed, unlike the 1/n power-law asymptotics elsewhere in this file)."""
    rho = float(rho)
    if rho <= 0:
        return 10
    import math
    N = int(digits * math.log(10) / max(1e-9, -math.log(rho))) + 20
    return max(30, min(N, 20000))


def _mat_vec(A, v):
    n = len(v)
    return [mp.fsum(A[i][j] * v[j] for j in range(n)) for i in range(n)]


def _power_iterate_dominant_eigval(A, n_iter=400):
    """Perron/dominant eigenvalue of a nonnegative matrix A via finite power iteration (Rayleigh
    quotient), n_iter is a FIXED finite integer -> a pure finite-discrete computation, no continuum
    limit primitive invoked (the textbook object is the n->infinity limit of this same recursion)."""
    n = len(A)
    v = [R(1) for _ in range(n)]
    for _ in range(n_iter):
        w = _mat_vec(A, v)
        norm = mp.sqrt(mp.fsum(x * x for x in w))
        v = [x / norm for x in w]
    w = _mat_vec(A, v)
    num = mp.fsum(v[i] * w[i] for i in range(n))
    den = mp.fsum(v[i] * v[i] for i in range(n))
    return num / den, v


def _stationary_dist(P_rows, n_iter=800):
    """Stationary distribution of a row-stochastic Markov chain via finite power iteration on the
    left eigenvector (fixed number of iterations = finite discrete recursion)."""
    n = len(P_rows)
    p = [R(1) / n for _ in range(n)]
    for _ in range(n_iter):
        newp = [mp.fsum(p[i] * P_rows[i][j] for i in range(n)) for j in range(n)]
        s = mp.fsum(newp)
        p = [x / s for x in newp]
    return p


def _pagerank(links, n, d=0.85, n_iter=600):
    """PageRank via the standard finite power-iteration recursion (this recursion, run to a fixed
    finite step count, IS how PageRank is computed in practice; the 'continuum' object is only its
    n_iter->infinity idealization)."""
    r = [R(1) / n for _ in range(n)]
    outdeg = [len(links[i]) for i in range(n)]
    for _ in range(n_iter):
        newr = [R(1 - d) / n for _ in range(n)]
        for i in range(n):
            if outdeg[i] == 0:
                for j in range(n):
                    newr[j] += d * r[i] / n
            else:
                share = d * r[i] / outdeg[i]
                for j in links[i]:
                    newr[j] += share
        r = newr
    return r


def PROBLEMS():
    out = []
    dom = "networks"

    # ---------------------------------------------------------------- 1) Shannon entropy H = -sum p log2 p
    dists = [
        [0.5, 0.5], [0.25, 0.25, 0.25, 0.25], [0.1, 0.9], [0.3, 0.3, 0.4],
        [0.05, 0.15, 0.3, 0.5], [0.2, 0.2, 0.2, 0.2, 0.2], [0.01, 0.99],
        [0.6, 0.1, 0.1, 0.1, 0.1], [0.125]*8, [0.4, 0.6], [0.02, 0.08, 0.9],
        [0.33, 0.33, 0.34], [0.7, 0.3], [0.9, 0.05, 0.05], [1.0/6]*6,
    ]
    for k, p in enumerate(dists):
        p = [R(x) for x in p]
        ours = -mp.fsum(pi * _log2_finite(pi) for pi in p if pi > 0)
        ref = -mp.fsum(mp.mpf(pi) * mp.log(pi, 2) for pi in p if pi > 0)
        out.append(K.P(dom, f"shannon_entropy_{k}", "H = -sum p_i log2 p_i (bits)", ours, ref,
                        "finite sum with K.log_finite/LN2_FINITE"))

    # ---------------------------------------------------------------- 2) binary entropy function h(p)
    for k, pv in enumerate([0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]):
        p = R(pv)
        ours = -(p * _log2_finite(p) + (1 - p) * _log2_finite(1 - p))
        ref = -(mp.mpf(pv) * mp.log(pv, 2) + (1 - mp.mpf(pv)) * mp.log(1 - pv, 2))
        out.append(K.P(dom, f"binary_entropy_{k}", "h(p) = -p log2 p - (1-p) log2(1-p)", ours, ref,
                        "K.log_finite/LN2_FINITE"))

    # ---------------------------------------------------------------- 3) channel capacity log2(1+SNR)
    for k, snr in enumerate([0.5, 1, 2, 4, 7.5, 10, 15.85, 20, 31.6, 50, 63, 100, 158, 200, 1000]):
        ours = _log2_finite(1 + R(snr))
        ref = mp.log(1 + snr, 2)
        out.append(K.P(dom, f"shannon_capacity_{k}", "C = log2(1+SNR) bits/symbol", ours, ref,
                        "K.log_finite/LN2_FINITE on 1+SNR"))

    # ---------------------------------------------------------------- 4) KL divergence
    kl_pairs = [
        ([0.5, 0.5], [0.9, 0.1]), ([0.25]*4, [0.4, 0.3, 0.2, 0.1]),
        ([0.1, 0.9], [0.2, 0.8]), ([0.3, 0.3, 0.4], [0.33, 0.33, 0.34]),
        ([0.6, 0.4], [0.5, 0.5]), ([0.2, 0.3, 0.5], [0.3, 0.3, 0.4]),
        ([0.05, 0.95], [0.5, 0.5]), ([0.4, 0.6], [0.6, 0.4]),
        ([0.15, 0.35, 0.5], [0.2, 0.3, 0.5]), ([0.8, 0.2], [0.7, 0.3]),
        ([0.9, 0.1], [0.99, 0.01]), ([0.1]*10, [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05],),
    ]
    for k, (P_, Q_) in enumerate(kl_pairs):
        P_ = [R(x) for x in P_]; Q_ = [R(x) for x in Q_]
        ours = mp.fsum(pi * _log2_finite(pi / qi) for pi, qi in zip(P_, Q_) if pi > 0)
        ref = mp.fsum(mp.mpf(pi) * mp.log(mp.mpf(pi) / mp.mpf(qi), 2) for pi, qi in zip(P_, Q_) if pi > 0)
        out.append(K.P(dom, f"kl_divergence_{k}", "D_KL(P||Q) = sum p log2(p/q)", ours, ref,
                        "finite sum with K.log_finite/LN2_FINITE"))

    # ---------------------------------------------------------------- 5) M/M/1 mean queue length rho/(1-rho)
    # as the geometric-series limit sum_{n>=0} n rho^n (1-rho) obtained via Richardson on partial sums
    for k, rho in enumerate([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.05, 0.55]):
        rho = R(rho)
        N = _geom_N_for(rho)
        ours = (1 - rho) * _weighted_geom_partial(rho, N)
        ref = mp.mpf(rho) / (1 - mp.mpf(rho))
        out.append(K.P(dom, f"mm1_mean_queue_{k}", "L = rho/(1-rho), M/M/1 mean number in system", ours, ref,
                        "finite partial geometric sum to N with rho^N<eps"))

    # ---------------------------------------------------------------- 6) M/M/1 mean wait via Little's law W=L/lambda
    for k, (rho, lam) in enumerate([(0.3, 2), (0.5, 1), (0.7, 3), (0.8, 5), (0.6, 1.5), (0.4, 4),
                                     (0.9, 0.5), (0.2, 6), (0.85, 2.5), (0.55, 3.5)]):
        rho = R(rho); lam = R(lam)
        N = _geom_N_for(rho)
        L = (1 - rho) * _weighted_geom_partial(rho, N)
        ours = L / lam
        ref = (mp.mpf(rho) / (1 - mp.mpf(rho))) / mp.mpf(lam)
        out.append(K.P(dom, f"littles_law_wait_{k}", "W = L/lambda (Little's law, M/M/1)", ours, ref,
                        "finite geometric partial sum to N with rho^N<eps, then /lambda"))

    # ---------------------------------------------------------------- 7) Erlang-B blocking probability recursion
    def erlang_b(A, m):
        """finite recursion B(0)=1; B(k)=A B(k-1) / (k + A B(k-1)) -- exact finite recurrence."""
        B = R(1)
        for k in range(1, m + 1):
            B = (A * B) / (k + A * B)
        return B
    def erlang_b_ref(A, m):
        # standard closed form via factorial series -- reference route uses mp directly (different route: sum form)
        A = mp.mpf(A)
        num = A**m / mp.factorial(m)
        den = mp.nsum(lambda k: A**k / mp.factorial(k), [0, m])
        return num / den
    for k, (A_, m_) in enumerate([(1, 2), (2, 4), (5, 8), (3, 5), (10, 15), (0.5, 1), (7, 10),
                                   (4, 6), (8, 12), (2.5, 5), (6, 9), (12, 20)]):
        ours = erlang_b(R(A_), m_)
        ref = erlang_b_ref(A_, m_)
        out.append(K.P(dom, f"erlang_b_{k}", "Erlang-B blocking recursion B(m,A)", ours, ref,
                        "finite recurrence B(k)=A*B(k-1)/(k+A*B(k-1))"))

    # ---------------------------------------------------------------- 8) Markov chain stationary distribution
    chains = [
        [[0.9, 0.1], [0.5, 0.5]],
        [[0.7, 0.2, 0.1], [0.1, 0.8, 0.1], [0.2, 0.2, 0.6]],
        [[0.5, 0.5], [0.3, 0.7]],
        [[0.6, 0.3, 0.1], [0.2, 0.6, 0.2], [0.1, 0.3, 0.6]],
        [[0.95, 0.05], [0.1, 0.9]],
        [[0.25, 0.25, 0.25, 0.25], [0.4, 0.3, 0.2, 0.1], [0.1, 0.2, 0.3, 0.4], [0.25, 0.25, 0.25, 0.25]],
    ]
    for k, P_rows in enumerate(chains):
        Pm = [[R(x) for x in row] for row in P_rows]
        ours_vec = _stationary_dist(Pm)
        n = len(Pm)
        Pmp = mp.matrix(P_rows)
        # reference: solve pi P = pi, sum pi =1 via linear algebra (different route: direct linear solve)
        A_ = (Pmp.T - mp.eye(n))
        for j in range(n):
            A_[n - 1, j] = 1
        b_ = mp.matrix([0] * (n - 1) + [1])
        piref = mp.lu_solve(A_, b_)
        for i in range(n):
            out.append(K.P(dom, f"markov_stationary_{k}_{i}", "stationary pi P = pi component",
                            ours_vec[i], piref[i], "finite power iteration on left eigenvector"))

    # ---------------------------------------------------------------- 9) Perron eigenvalue of small nonneg matrices
    mats = [
        [[2, 1], [1, 2]], [[0, 1], [1, 0]], [[3, 1], [1, 3]], [[4, 2], [1, 3]],
        [[2, 0, 1], [1, 3, 0], [0, 1, 2]], [[1, 2], [3, 4]], [[5, 1], [1, 5]],
        [[2, 1, 0], [1, 2, 1], [0, 1, 2]], [[6, 2], [2, 3]], [[1, 1], [1, 1]],
    ]
    for k, M in enumerate(mats):
        Mm = [[R(x) for x in row] for row in M]
        eig, _ = _power_iterate_dominant_eigval(Mm, n_iter=500)
        eigvals = mp.eig(mp.matrix(M), left=False, right=False)
        refr = max(mp.re(z) for z in eigvals)
        out.append(K.P(dom, f"perron_eigval_{k}", "dominant eigenvalue via power iteration", eig, refr,
                        "finite power iteration (n_iter=500) Rayleigh quotient"))

    # ---------------------------------------------------------------- 10) PageRank on small link graphs
    graphs = [
        ({0: [1, 2], 1: [2], 2: [0]}, 3),
        ({0: [1], 1: [2], 2: [0]}, 3),
        ({0: [1, 2, 3], 1: [2], 2: [3], 3: [0]}, 4),
        ({0: [1], 1: [0, 2], 2: [0]}, 3),
        ({0: [1, 2], 1: [0], 2: [0, 1]}, 3),
    ]
    for k, (links, n) in enumerate(graphs):
        r = _pagerank(links, n, n_iter=700)
        # reference via direct linear solve of PageRank fixed point
        d = mp.mpf('0.85')
        outdeg = [len(links.get(i, [])) for i in range(n)]
        Mm = mp.zeros(n, n)
        for i in range(n):
            if outdeg[i] == 0:
                for j in range(n):
                    Mm[i, j] = mp.mpf(1) / n
            else:
                for j in links[i]:
                    Mm[i, j] = mp.mpf(1) / outdeg[i]
        A_ = Mm.T * d - mp.eye(n)
        for j in range(n):
            A_[n - 1, j] = 1
        b_ = mp.matrix([-(1 - d) / n] * (n - 1) + [1])
        rref = mp.lu_solve(A_, b_)
        for i in range(n):
            out.append(K.P(dom, f"pagerank_{k}_{i}", "PageRank fixed point via power iteration",
                            r[i], rref[i], "finite power iteration n_iter=700, d=0.85"))

    # ---------------------------------------------------------------- 11) DFT via roots of unity + Parseval
    seqs = [
        [1, 0, 0, 0], [1, 1, 0, 0], [1, -1, 1, -1], [1, 2, 3, 4],
        [0, 1, 0, -1], [1, 0, -1, 0, 1, 0, -1, 0], [2, 1, 0, 1],
        [1, 2, 1, 2, 1, 2], [3, 1, 4, 1, 5, 9],
    ]
    for k, x in enumerate(seqs):
        N = len(x)
        # ours: DFT coefficients via K.sin_finite/K.cos_finite roots of unity
        Xk = []
        for kk in range(N):
            re = mp.fsum(x[n] * K.cos_finite(-2 * PI * kk * n / N) for n in range(N))
            im = mp.fsum(x[n] * K.sin_finite(-2 * PI * kk * n / N) for n in range(N))
            Xk.append((re, im))
        # Parseval: sum |x_n|^2 = (1/N) sum |X_k|^2
        ours = mp.fsum(re * re + im * im for re, im in Xk) / N
        ref = mp.fsum(mp.mpf(v) ** 2 for v in x)
        out.append(K.P(dom, f"dft_parseval_{k}", "Parseval: sum|x|^2 = (1/N) sum|X_k|^2", ours, ref,
                        "finite DFT via K.sin_finite/K.cos_finite roots of unity"))
        # also check one DFT coefficient against mpmath direct complex exponential sum (different route)
        kk = 1 if N > 1 else 0
        ref_re = mp.fsum(x[n] * mp.cos(-2 * mp.pi * kk * n / N) for n in range(N))
        out.append(K.P(dom, f"dft_coeff_re_{k}", f"Re(X_{kk}) DFT coefficient", Xk[kk][0], ref_re,
                        "K.cos_finite roots of unity sum"))

    # ---------------------------------------------------------------- 12) discrete convolution vs direct product identity check (finite, trivially exact -- skip, not continuum)
    # (convolution itself is finite/exact; skip as not a continuum-frontier item)

    # ---------------------------------------------------------------- 13) sinc interpolation reconstructs samples of a bandlimited signal
    def sinc_finite(x):
        x = R(x)
        if abs(x) < R(1) / 10 ** 12:
            return R(1)
        return K.sin_finite(PI * x) / (PI * x)
    for k, f0 in enumerate([0.05, 0.1, 0.15, 0.2, 0.25, 0.3]):
        # bandlimited test signal: cos(2 pi f0 t), sampled at rate 1; reconstruct at t=0.5+k via sinc sum
        Ns = 3000
        samples = [K.cos_finite(2 * PI * f0 * n) for n in range(-Ns, Ns + 1)]
        t0 = R(3.37)
        ours = mp.fsum(samples[n + Ns] * sinc_finite(t0 - n) for n in range(-Ns, Ns + 1))
        ref = mp.cos(2 * mp.pi * f0 * t0)
        out.append(K.P(dom, f"sinc_interp_{k}", "Whittaker-Shannon sinc reconstruction", ours, ref,
                        "finite sinc sum via K.sin_finite/PI_FINITE"))

    # ---------------------------------------------------------------- 14) harmonic number H_n vs ln n + gamma (quicksort avg comparisons)
    def harmonic(n):
        return mp.fsum(R(1) / k for k in range(1, int(n) + 1))
    for k, n in enumerate([5, 10, 20, 50, 100, 200, 500, 1000, 30, 75, 150, 300, 700, 2, 3]):
        Hn = harmonic(n)
        # quicksort avg comparisons ~ 2n ln n (asymptotic uses ln, computed finitely)
        ours = 2 * (n + 1) * Hn - 4 * n
        # true exact recursion for quicksort avg comparisons: C(n) = 2(n+1)H_n - 4n  (Knuth) -- exact finite recursion
        # reference: independent direct recursion C(0)=0, C(n) = n-1 + (2/n) sum_{k=0}^{n-1} C(k)
        def qs_ref(n):
            C = [mp.mpf(0)] * (n + 1)
            for m in range(1, n + 1):
                C[m] = (m - 1) + (mp.mpf(2) / m) * mp.fsum(C[j] for j in range(m))
            return C[n]
        ref = qs_ref(int(n))
        out.append(K.P(dom, f"quicksort_avg_comparisons_{k}", "C(n)=2(n+1)H_n-4n exact avg comparisons",
                        ours, ref, "finite harmonic sum vs independent finite recursion"))

    # ---------------------------------------------------------------- 15) H_n vs ln(n)+gamma asymptotic (continuum frontier: Euler-Mascheroni + ln)
    # H_n - ln n -> gamma only as O(1/2n); use K.richardson on h=1/n to accelerate to the true limit.
    for k, M0 in enumerate([20, 30, 40, 50, 25, 35, 60, 15]):
        def seq(n):
            return harmonic(int(n)) - K.log_finite(int(n))
        ours = K.richardson(seq, M=M0, K=9)
        ref = mp.euler
        out.append(K.P(dom, f"harmonic_euler_mascheroni_{k}", "H_n - ln n -> gamma (Euler-Mascheroni)",
                        ours, ref, "finite harmonic sum minus K.log_finite(n), K.richardson on h=1/n"))

    # ---------------------------------------------------------------- 16) Catalan numbers exact vs asymptotic 4^n/(n^1.5 sqrt(pi))
    def catalan_exact(n):
        c = R(1)
        for k in range(n):
            c = c * 2 * (2 * k + 1) / (k + 2)
        return c
    # the ratio C_n / (4^n/(n^1.5 sqrt(pi))) -> 1 only as O(1/n); use K.richardson on h=1/n to accelerate.
    for k, M0 in enumerate([10, 15, 20, 8, 12, 18, 25, 6, 9, 14, 22, 30]):
        def ratio_seq(n):
            n = int(n)
            Cn = catalan_exact(n)
            asym = K.pow_finite(4, n) / (K.pow_finite(R(n), R(1.5)) * K.SQRT_PI)
            return Cn / asym
        ours = K.richardson(ratio_seq, M=M0, K=8)
        ref = mp.mpf(1)
        out.append(K.P(dom, f"catalan_asymptotic_ratio_{k}", "C_n / (4^n/(n^1.5 sqrt(pi))) -> 1", ours, ref,
                        "exact finite Catalan recursion / finite asymptotic formula, K.richardson on h=1/n"))

    # ---------------------------------------------------------------- 17) Stirling n! asymptotic n^n e^-n sqrt(2 pi n)
    # ratio -> 1 only as O(1/n) (Stirling series 1+1/12n+...); use K.richardson on h=1/n to accelerate.
    def stirling_ratio(n):
        n = int(n)
        nf = K.factorial_finite(n)
        stirling = K.pow_finite(R(n), R(n)) * K.exp_finite(-R(n)) * mp.sqrt(2 * PI * n)
        return nf / stirling
    for k, M0 in enumerate([8, 12, 16, 20, 6, 10, 14, 18, 22, 26]):
        ours = K.richardson(stirling_ratio, M=M0, K=7)
        ref = mp.mpf(1)
        out.append(K.P(dom, f"stirling_ratio_{k}", "n! / (n^n e^-n sqrt(2 pi n)) -> 1", ours, ref,
                        "exact finite factorial / finite Stirling formula, K.richardson on h=1/n"))

    # ---------------------------------------------------------------- 18) birthday paradox 1 - e^{-n(n-1)/(2N)}
    for k, (n, N) in enumerate([(23, 365), (50, 365), (10, 365), (70, 365), (100, 365), (30, 365),
                                 (5, 100), (20, 1000), (40, 1000), (15, 52), (60, 365), (200, 8000)]):
        exponent = -R(n) * (n - 1) / (2 * N)
        ours = 1 - K.exp_finite(exponent)
        ref = 1 - mp.e ** (mp.mpf(-n) * (n - 1) / (2 * N))
        out.append(K.P(dom, f"birthday_approx_{k}", "P(collision) ~ 1 - e^{-n(n-1)/2N}", ours, ref,
                        "K.exp_finite of exact rational exponent"))

    # ---------------------------------------------------------------- 19) exact birthday probability (product form) vs the
    # same exact quantity via the factorial-ratio identity 1 - N!/((N-n)! N^n) -- a genuinely different finite route
    # (falling-factorial product vs full factorials K.factorial_finite/K.pow_finite), not an approximation.
    def birthday_exact(n, N):
        p = R(1)
        for i in range(n):
            p *= (R(N) - i) / N
        return 1 - p
    for k, (n, N) in enumerate([(23, 365), (10, 365), (30, 365), (50, 365), (5, 30), (15, 100), (40, 200), (8, 40)]):
        ours = birthday_exact(n, N)
        ref = 1 - mp.factorial(N) / (mp.factorial(N - n) * mp.mpf(N) ** n)
        out.append(K.P(dom, f"birthday_exact_vs_factorial_ratio_{k}", "1-prod(1-i/N) = 1-N!/((N-n)!N^n)",
                        ours, ref, "finite falling-factorial product vs mpmath factorial-ratio identity"))

    # ---------------------------------------------------------------- 20) coupon collector n*H_n
    for k, n in enumerate([5, 10, 20, 50, 100, 200, 6, 12, 25, 40]):
        Hn = harmonic(n)
        ours = n * Hn
        # independent reference: direct expectation via geometric-waiting-time recursion sum n/(n-k)
        ref = mp.fsum(mp.mpf(n) / (n - k) for k in range(n))
        out.append(K.P(dom, f"coupon_collector_{k}", "E[T] = n H_n coupon collector", ours, ref,
                        "finite harmonic sum vs independent finite geometric-waiting sum"))

    # ---------------------------------------------------------------- 21) random walk return probability (1D, 2n steps) central binomial / 4^n
    # ratio -> 1 only as O(1/n); use K.richardson on h=1/n to accelerate to the true continuum-frontier limit.
    def central_binom_over_4n(n):
        n = int(n)
        num = K.factorial_finite(2 * n)
        den = (K.factorial_finite(n)) ** 2 * K.pow_finite(4, n)
        return num / den * mp.sqrt(PI * n)
    for k, M0 in enumerate([8, 12, 16, 20, 6, 10, 14, 18, 22, 26]):
        ours = K.richardson(central_binom_over_4n, M=M0, K=7)
        ref = mp.mpf(1)
        out.append(K.P(dom, f"random_walk_return_asym_{k}", "P(S_2n=0)*sqrt(pi n) -> 1", ours, ref,
                        "exact finite central-binomial ratio * finite sqrt(pi n), K.richardson on h=1/n"))

    # ---------------------------------------------------------------- 22) logistic map orbit convergence to fixed point / Lyapunov-like finite readout
    def logistic_fixed_iterate(r, x0, n):
        x = R(x0)
        for _ in range(n):
            x = r * x * (1 - x)
        return x
    for k, r in enumerate([0.5, 1.2, 1.5, 1.8, 2.0, 2.5, 2.9]):
        # for r<3 logistic map has stable fixed point x* = 1 - 1/r (for r>1); check convergence
        # (r=1 is a bifurcation point with only power-law, not exponential, convergence -- excluded)
        x_final = logistic_fixed_iterate(R(r), R(0.3), 400)
        ours = x_final
        ref = 1 - mp.mpf(1) / r if r > 1 else mp.mpf(0)
        out.append(K.P(dom, f"logistic_fixed_point_{k}", "logistic map orbit -> fixed point 1-1/r", ours, ref,
                        "finite iterated map to n=400 steps"))

    # ---------------------------------------------------------------- 23) entropy rate of a Markov source (limit of block entropy / n)
    for k, P_rows in enumerate(chains[:4]):
        Pm = [[R(x) for x in row] for row in P_rows]
        pi = _stationary_dist(Pm)
        n = len(Pm)
        ours = -mp.fsum(pi[i] * Pm[i][j] * _log2_finite(Pm[i][j]) for i in range(n) for j in range(n) if Pm[i][j] > 0)
        Pmp = mp.matrix(P_rows)
        A_ = (Pmp.T - mp.eye(n))
        for j in range(n):
            A_[n - 1, j] = 1
        b_ = mp.matrix([0] * (n - 1) + [1])
        piref = mp.lu_solve(A_, b_)
        ref = -mp.fsum(piref[i] * mp.mpf(P_rows[i][j]) * mp.log(P_rows[i][j], 2)
                        for i in range(n) for j in range(n) if P_rows[i][j] > 0)
        out.append(K.P(dom, f"markov_entropy_rate_{k}", "H(chain) = -sum pi_i P_ij log2 P_ij", ours, ref,
                        "finite power-iteration stationary dist + finite log-sum"))

    # ---------------------------------------------------------------- 24) mutual information I(X;Y) = H(X)+H(Y)-H(X,Y)
    joints = [
        [[0.25, 0.25], [0.25, 0.25]], [[0.4, 0.1], [0.1, 0.4]], [[0.3, 0.2], [0.1, 0.4]],
        [[0.5, 0.0], [0.0, 0.5]], [[0.2, 0.3], [0.3, 0.2]], [[0.45, 0.05], [0.05, 0.45]],
    ]
    for k, J in enumerate(joints):
        Jm = [[R(x) for x in row] for row in J]
        n = len(Jm)
        px = [mp.fsum(Jm[i][j] for j in range(n)) for i in range(n)]
        py = [mp.fsum(Jm[i][j] for i in range(n)) for j in range(n)]
        Hx = -mp.fsum(p * _log2_finite(p) for p in px if p > 0)
        Hy = -mp.fsum(p * _log2_finite(p) for p in py if p > 0)
        Hxy = -mp.fsum(Jm[i][j] * _log2_finite(Jm[i][j]) for i in range(n) for j in range(n) if Jm[i][j] > 0)
        ours = Hx + Hy - Hxy
        pxr = [mp.fsum(mp.mpf(J[i][j]) for j in range(n)) for i in range(n)]
        pyr = [mp.fsum(mp.mpf(J[i][j]) for i in range(n)) for j in range(n)]
        Hxr = -mp.fsum(p * mp.log(p, 2) for p in pxr if p > 0)
        Hyr = -mp.fsum(p * mp.log(p, 2) for p in pyr if p > 0)
        Hxyr = -mp.fsum(mp.mpf(J[i][j]) * mp.log(J[i][j], 2) for i in range(n) for j in range(n) if J[i][j] > 0)
        ref = Hxr + Hyr - Hxyr
        out.append(K.P(dom, f"mutual_information_{k}", "I(X;Y)=H(X)+H(Y)-H(X,Y)", ours, ref,
                        "finite entropy sums via K.log_finite/LN2_FINITE"))

    # ---------------------------------------------------------------- 25) Little's law general (L = lambda W) sanity across (lambda,W) pairs via M/M/1 model
    for k, (rho, mu) in enumerate([(0.3, 4), (0.5, 2), (0.7, 6), (0.2, 10), (0.6, 3), (0.8, 8),
                                    (0.4, 5), (0.9, 1), (0.15, 12), (0.65, 7)]):
        rho = R(rho); mu = R(mu); lam = rho * mu
        N = _geom_N_for(rho)
        L = (1 - rho) * _weighted_geom_partial(rho, N)
        W = L / lam
        ours = lam * W
        ref = mp.mpf(rho) / (1 - mp.mpf(rho))
        out.append(K.P(dom, f"littles_law_identity_{k}", "lambda*W = L (Little's law identity)", ours, ref,
                        "finite geometric partial sum to N, L/lambda, times lambda"))

    # ---------------------------------------------------------------- 26) channel capacity with bandwidth B: C = B log2(1+SNR)
    for k, (B, snr) in enumerate([(1000, 10), (2000, 5), (500, 20), (4000, 2), (10000, 1),
                                   (3000, 15), (1500, 8), (8000, 3), (6000, 12), (200, 50)]):
        ours = R(B) * _log2_finite(1 + R(snr))
        ref = mp.mpf(B) * mp.log(1 + snr, 2)
        out.append(K.P(dom, f"capacity_bandwidth_{k}", "C = B log2(1+SNR)", ours, ref,
                        "K.log_finite/LN2_FINITE scaled by bandwidth"))

    # ---------------------------------------------------------------- 27) M/M/1 utilization power-series identity: sum rho^n = 1/(1-rho)
    for k, rho in enumerate([0.1, 0.25, 0.33, 0.5, 0.6, 0.75, 0.8, 0.9, 0.95, 0.99]):
        rho = R(rho)
        N = _geom_N_for(rho)
        ours = _geom_partial(rho, N)
        ref = 1 / (1 - mp.mpf(rho))
        out.append(K.P(dom, f"geometric_series_limit_{k}", "sum_{n>=0} rho^n = 1/(1-rho)", ours, ref,
                        "finite geometric partial sum to N with rho^N<eps"))

    return out
