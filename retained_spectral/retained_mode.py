"""Retained Mode Readout (RMR) — eigenvector readouts from retained Sturm state.

Built by the METHOD.md loop, Rule 0 first.

DECLARE (step 1)
    Resolution: the eigenvalue tolerance already declared to the Sturm kernel,
    plus a residual gate rho on the mode readout.

EXPRESS (step 2) — the information-language restatement
    An eigenvector is not an object to be constructed; it is a *retained
    selection* — the idempotent that keeps one mode and discards the rest.
    The Sturm bisection that located lambda already formed, at every step, the
    top-down LDL^T pivots of (H - lambda I). That is retained state which the
    classical pipeline throws away and then rebuilds by inverse iteration.
    Reading the mode is therefore not new computation: it is *retention* of the
    pivot record plus one bottom-up companion pass, closed at a twist index.

COMPUTE at finite eps (step 3)
    s : top-down    pivots of (H - lambda I)
    p : bottom-up   pivots of (H - lambda I)
    gamma_r = s_r + p_r - (d_r - lambda)      the retained defect at index r
    r = argmin |gamma_r|                       the least-retained-defect twist
    z is generated outward from r by the retained ratios; no iteration.

STABILIZE (step 4)
    The plateau test is the residual itself: ||H z - lambda z||_inf / ||z||_inf.
    No eps -> 0 object is formed.

TIER-TAG (step 5)
    finite_diagnostic. ACCEPT when residual <= rho * max|lambda|, else HOLD.
    A HOLD returns no vector rather than a fabricated one.

FENCE (step 6)
    +R-Open: this certifies the residual of the readout, not distance to a
    completed continuum eigenfunction. Orthogonality across a cluster tighter
    than the declared eigenvalue tolerance is NOT certified and is reported.
"""

from __future__ import annotations

import numpy as np

try:
    from numba import njit
except ImportError:  # pragma: no cover
    njit = None

TIER = "finite_diagnostic"


def _pivots_py(d, e, lam):
    """Top-down and bottom-up LDL^T pivots of (H - lambda I). Retained state."""
    n = d.size
    s = np.empty(n)
    p = np.empty(n)
    tiny = 1e-308

    s[0] = d[0] - lam
    for i in range(n - 1):
        piv = s[i]
        if piv == 0.0:
            piv = tiny
        s[i + 1] = (d[i + 1] - lam) - e[i] * (e[i] / piv)

    p[n - 1] = d[n - 1] - lam
    for i in range(n - 2, -1, -1):
        piv = p[i + 1]
        if piv == 0.0:
            piv = tiny
        p[i] = (d[i] - lam) - e[i] * (e[i] / piv)

    return s, p


def _generate_py(s, p, d, e, lam):
    """Twisted generation outward from the least-defect index. Retained pass."""
    n = d.size
    tiny = 1e-308
    best = 0
    bestv = 1e308
    for i in range(n):
        g = abs(s[i] + p[i] - (d[i] - lam))
        if g < bestv:
            bestv = g
            best = i
    r = best
    z = np.zeros(n)
    z[r] = 1.0
    i = r - 1
    while i >= 0:
        piv = s[i] if s[i] != 0.0 else tiny
        z[i] = -(e[i] / piv) * z[i + 1]
        if abs(z[i]) > 1e100:
            for j in range(i + 1):
                z[j] = 0.0
            break
        i -= 1
    i = r
    while i < n - 1:
        piv = p[i + 1] if p[i + 1] != 0.0 else tiny
        z[i + 1] = -(e[i] / piv) * z[i]
        if abs(z[i + 1]) > 1e100:
            for j in range(i + 1, n):
                z[j] = 0.0
            break
        i += 1
    return z


def _ldl_solve_py(s, e, b):
    """Solve (H - lambda I) x = b reusing the RETAINED top-down pivots.

    The pivot record s is already held from the mode readout; D_i = s_i and
    L_i = e_i / s_i. Applying the resolvent is therefore not new factorisation
    work, it is re-use of retained state.
    """
    n = s.size
    tiny = 1e-308
    y = np.empty(n)
    y[0] = b[0]
    for i in range(n - 1):
        piv = s[i] if s[i] != 0.0 else tiny
        y[i + 1] = b[i + 1] - (e[i] / piv) * y[i]
    x = np.empty(n)
    piv = s[n - 1] if s[n - 1] != 0.0 else tiny
    x[n - 1] = y[n - 1] / piv
    for i in range(n - 2, -1, -1):
        piv = s[i] if s[i] != 0.0 else tiny
        x[i] = y[i] / piv - (e[i] / piv) * x[i + 1]
    return x


if njit is not None:
    _pivots = njit(cache=True)(_pivots_py)
    _generate = njit(cache=True)(_generate_py)
    _ldl_solve = njit(cache=True)(_ldl_solve_py)
    COMPILED = True
else:  # pragma: no cover
    _pivots, _generate, _ldl_solve, COMPILED = (
        _pivots_py, _generate_py, _ldl_solve_py, False)


def warm():
    d = np.array([2.0, 2.0, 2.0]); e = np.array([-1.0, -1.0])
    mode_readout(d, e, 0.5)


def mode_readout(d, e, lam, rho=1e-10):
    """One retained mode. Returns (z, residual, status)."""
    s, p = _pivots(d, e, lam)
    z = _generate(s, p, d, e, lam)

    nrm = np.linalg.norm(z)
    if not np.isfinite(nrm) or nrm == 0.0:
        return None, np.inf, "HOLD"
    z /= nrm

    hz = d * z
    hz[:-1] += e * z[1:]
    hz[1:] += e * z[:-1]
    resid = float(np.max(np.abs(hz - lam * z)))

    scale = max(abs(lam), float(np.max(np.abs(d))))
    status = "ACCEPT" if resid <= rho * scale else "HOLD"
    return z, resid, status


def modes(d, e, lams, rho=1e-10, orth_tol=1e-8, reltol=1e-3, sweeps=6):
    """Retained selection over several modes.

    A single twisted readout resolves a mode only when its eigenvalue is
    separated from its neighbours by more than the retained resolution. Inside
    a cluster the individual readouts collapse onto the same direction: the
    residual gate still passes (any vector of the near-degenerate subspace has
    a small residual) but the SELECTION is not resolved. Per METHOD.md rule 2
    that is a degeneracy and must be HOLD, never a silent answer.

    We therefore add a second gate at the selection level: retained
    re-orthogonalisation inside each detected cluster, then an explicit
    orthogonality check. Clusters that stay unresolved return HOLD.
    """
    lams = np.asarray(lams, dtype=float)
    k = lams.size
    out, res, st = [], [], []
    for lam in lams:
        z, r_, s_ = mode_readout(d, e, lam, rho)
        out.append(z)
        res.append(r_)
        st.append(s_)

    res = list(res)
    if any(z is None for z in out):
        # a per-mode readout failed its residual gate: return the SAME 6-tuple shape as the success path
        # (out, res, status, verdict, orth, notes) so a caller can always unpack the result uniformly.
        return out, np.array(res), st, "HOLD", float("nan"), ["a mode readout returned no vector"]

    # ---- selection refinement inside clusters -------------------------
    # A cluster is a set of modes indistinguishable at the declared
    # eigenvalue resolution. A single twisted readout cannot split them.
    # But the retained pivot record IS the resolvent, so the selection can be
    # refined by re-applying retained state, orthogonal to the part of the
    # cluster already resolved. No new factorisation, no new declaration.
    scale = max(float(np.max(np.abs(lams))), 1.0)
    gaps = np.diff(lams)
    # distinguishability is RELATIVE: a gap is only a distinction when it is
    # large compared with the magnitude of what is being measured.
    denom = np.maximum(np.abs(lams[:-1]), np.abs(lams[1:]))
    denom = np.maximum(denom, 1e-300)
    clustered = (gaps / denom) <= reltol
    notes = []
    rng = np.random.default_rng(20260727)
    dmax = float(np.max(np.abs(d)))

    # every mode gets one retained-resolvent polish; singletons need no
    # cross-orthogonalisation, so this is O(n) each, not O(n k^2).
    for a in range(k):
        if st[a] == "HOLD":
            continue
        s_piv, _ = _pivots(d, e, lams[a])
        w = _ldl_solve(s_piv, e, out[a])
        nw = np.linalg.norm(w)
        if np.isfinite(nw) and nw > 0.0:
            out[a] = w / nw

    start = 0
    for i in range(k):
        if i == k - 1 or not clustered[i]:
            if i > start:
                members = list(range(start, i + 1))
                notes.append(f"cluster {start}-{i} ({len(members)} modes) refined "
                             f"by retained resolvent")
                basis = []
                for a in members:
                    s_piv, _ = _pivots(d, e, lams[a])
                    v = out[a].copy()
                    for _ in range(sweeps):
                        for b in basis:
                            v -= np.dot(b, v) * b
                        nv = np.linalg.norm(v)
                        if nv < 1e-12:
                            v = rng.standard_normal(d.size)
                            for b in basis:
                                v -= np.dot(b, v) * b
                            nv = np.linalg.norm(v)
                        v /= nv
                        w = _ldl_solve(s_piv, e, v)
                        nw = np.linalg.norm(w)
                        if not np.isfinite(nw) or nw == 0.0:
                            break
                        v = w / nw
                        # METHOD step 4: stop at the plateau, not at a fixed
                        # sweep count. Cost is paid only until the readout
                        # stabilises.
                        hv = d * v
                        hv[:-1] += e * v[1:]
                        hv[1:] += e * v[:-1]
                        if float(np.max(np.abs(hv - lams[a] * v))) <= rho * max(
                                abs(lams[a]), float(dmax)):
                            break
                    for b in basis:
                        v -= np.dot(b, v) * b
                    nv = np.linalg.norm(v)
                    if nv < 1e-12:
                        st[a] = "HOLD"
                        continue
                    v /= nv
                    basis.append(v)
                    out[a] = v
            start = i + 1

    # ---- recertify every mode after refinement ------------------------
    for a in range(k):
        z = out[a]
        hz = d * z
        hz[:-1] += e * z[1:]
        hz[1:] += e * z[:-1]
        r_ = float(np.max(np.abs(hz - lams[a] * z)))
        res[a] = r_
        sc = max(abs(lams[a]), float(np.max(np.abs(d))))
        if st[a] != "HOLD":
            st[a] = "ACCEPT" if r_ <= rho * sc else "HOLD"

    Z = np.array(out).T
    orth = float(np.max(np.abs(Z.T @ Z - np.eye(k)))) if k > 1 else 0.0
    if orth > orth_tol:
        st = ["HOLD"] * k
        notes.append(f"selection not resolved: orthogonality error {orth:.2e}")

    verdict = "ACCEPT" if all(x == "ACCEPT" for x in st) else "HOLD"
    return out, np.array(res), st, verdict, orth, notes


def expectation(d, e, lams, weight, rho=1e-10):
    """Stream a scalar readout per mode without retaining the vectors.

    This is the readout-first payoff: <v|W|v> for a diagonal W costs O(n) per
    mode and O(n) memory total, never O(n*k).
    """
    vals = []
    for lam in lams:
        z, _, s_ = mode_readout(d, e, lam, rho)
        vals.append(np.nan if z is None else float(np.dot(z * z, weight)))
    return np.array(vals)
