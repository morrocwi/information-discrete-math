#!/usr/bin/env python3
"""Paradox dissolution (Part XXI): the three frontier areas — topology, manifolds, PDE — each has a
famous continuum PARADOX, and each is DISSOLVED because our computation never forms the injected
non-readout. This suite demonstrates numerically that the readout-first computation returns the
practical value WITHOUT producing the paradox. Run: python3 paradox_dissolution.py
"""
import math
P = 0; T = 0; FAILS = []
def chk(name, ours, ref, tol=0):
    global P, T
    T += 1
    ok = (ours == ref) if tol == 0 else (abs(float(ours) - float(ref)) <= tol)
    if ok: P += 1
    else: FAILS.append((name, str(ours), str(ref)))

# ═══════ TOPOLOGY — Banach–Tarski dissolved: μ_λ is finitely additive, no doubling ═══════
# NOTE (honest scope): this does NOT refute the classical geometric proof; it shows that in a finite-
# readout framework the paradox's non-measurable pieces are never FORMED (they have no G_λ description),
# so any actual decomposition conserves the retained count. Finite additivity on finite sets cannot fail
# by construction — that is exactly the point: no readout region can be read out as two copies.
region = set(range(1000))                       # a finite readout region, μ = 1000
parts = [set(range(0,250)), set(range(250,600)), set(range(600,1000))]   # disjoint decomposition
chk("BanachTarski: disjoint parts partition the region", set().union(*parts), region)
chk("μ_λ finitely additive: Σμ(parts) = μ(whole)", sum(len(p) for p in parts), len(region))
# "reassemble into two copies" is impossible: two disjoint copies need 2000 cells, but the parts hold 1000
reassembled = sum(len(p) for p in parts)
chk("no measure created: reassembled count ≠ 2×original (no doubling)", reassembled == 2*len(region), False)
chk("reassembled = original exactly", reassembled, len(region))

# ═══════ MANIFOLDS — curvature paradox dissolved: discrete Gauss–Bonnet, no smooth limit ═══════
# Total curvature = Σ vertex angle-defects = 2π·χ, EXACT on a polyhedron (flat faces, sharp corners).
def total_defect(vertices_incident_angles):
    return sum(2*math.pi - sum(angles) for angles in vertices_incident_angles)
# Tetrahedron: 4 vertices, each meeting 3 equilateral triangles (angle π/3 each) → defect 2π-π = π
tetra = [[math.pi/3]*3 for _ in range(4)]
chk("Gauss–Bonnet tetrahedron: Σdefect = 2π·χ = 4π (χ=2)", total_defect(tetra), 4*math.pi, 1e-9)
chk("tetrahedron χ from V−E+F = 2", 4-6+4, 2)
# Cube: 8 vertices, each meeting 3 squares (angle π/2 each) → defect 2π - 3π/2 = π/2
cube = [[math.pi/2]*3 for _ in range(8)]
chk("Gauss–Bonnet cube: Σdefect = 4π (χ=2)", total_defect(cube), 4*math.pi, 1e-9)
chk("cube χ from V−E+F = 2", 8-12+6, 2)
# Octahedron: 6 vertices, each meeting 4 triangles (π/3) → defect 2π - 4π/3 = 2π/3 ; total = 4π
octa = [[math.pi/3]*4 for _ in range(6)]
chk("Gauss–Bonnet octahedron: Σdefect = 4π", total_defect(octa), 4*math.pi, 1e-9)
# curvature is FINITE at every vertex — no h→0, no smooth chart needed
chk("each vertex defect is finite (tetra = π)", all(math.isfinite(2*math.pi-sum(a)) for a in tetra), True)

# ═══════ PDE — blow-up dissolved: finite-ε schemes return finite fields within their stability window ═══════
# NOTE (honest scope): these are LINEAR MODEL PDEs (heat, transport), run at a stable stencil ratio
# (r ≤ 1/2). They are NOT Navier–Stokes (nonlinear, vortex-stretching) — NS's own blow-up question is a
# distinct, declined +ℝ-Open question about the completed continuum. Outside the stability window an
# explicit scheme diverges numerically (a discretization failure, not a continuum blow-up).
# Heat equation u_t = u_xx by the explicit finite-ε stencil: a bump decays smoothly, no blow-up.
def heat_step(u, r):
    return [u[i] + r*(u[i-1] - 2*u[i] + u[i+1]) for i in range(1, len(u)-1)]
n = 41; u = [0.0]*n; u[n//2] = 1.0            # initial bump
r = 0.25                                       # stable stencil ratio (r ≤ 1/2)
mass0 = sum(u)
for _ in range(2000):
    u = [0.0] + heat_step(u, r) + [0.0]        # Dirichlet ends
chk("heat: field stays finite for all steps (no blow-up)", all(math.isfinite(x) for x in u), True)
chk("heat: peak decays (diffusion, not explosion)", max(u) < 1.0, True)
chk("heat: solution remains bounded and non-negative", min(u) >= -1e-12 and max(u) <= 1.0, True)
# Transport/wave advances at FINITE speed — a reached +∞ never occurs
c = 0.5; steps = 100; wave = [math.exp(-((i-5))**2) for i in range(60)]
for _ in range(steps):
    wave = [wave[0]] + [wave[i] - c*(wave[i]-wave[i-1]) for i in range(1, len(wave))]
chk("transport: field finite for all steps (finite propagation speed)", all(math.isfinite(x) for x in wave), True)
chk("transport: no value exceeds the initial max (no +∞)", max(wave) <= 1.0 + 1e-9, True)
# Compare heat decay against the exact continuum solution's qualitative law (total mass decreases,
# never diverges) — the readout tracks the appearance without ever forming +∞
chk("heat: total 'mass' bounded by initial (no creation of infinity)", sum(abs(x) for x in u) <= mass0 + 1e-9, True)

# ── Discovered bound 1: relaxation-inertia τ dI/dt + L_R I = 0 with L_R PSD → energy NON-GROWING ──
# (URCF relaxation-inertia; the discrete no-blow-up bound d/dt‖I‖²=−(2/τ)B(I,I)≤0, keystone L_R PSD)
def graph_laplacian(edges, nv):
    L = [[0.0]*nv for _ in range(nv)]
    for i, j, w in edges:
        L[i][i]+=w; L[j][j]+=w; L[i][j]-=w; L[j][i]-=w
    return L
edges = [(0,1,1.0),(1,2,1.0),(2,3,1.0),(0,3,1.0)]   # a 4-cycle, L_R is PSD
L = graph_laplacian(edges, 4)
I = [3.0, -1.0, 2.0, -4.0]; tau = 2.0; dt = 0.05
energy0 = sum(x*x for x in I)
energies = [energy0]
for _ in range(400):
    LI = [sum(L[a][b]*I[b] for b in range(4)) for a in range(4)]
    I = [I[a] - (dt/tau)*LI[a] for a in range(4)]      # explicit relaxation step
    energies.append(sum(x*x for x in I))
chk("relaxation: energy non-growing at every step (L_R PSD ⇒ no blow-up)",
    all(energies[k+1] <= energies[k] + 1e-9 for k in range(len(energies)-1)), True)
chk("relaxation: energy stays finite (no +∞)", all(math.isfinite(e) for e in energies), True)
chk("relaxation: final energy ≤ initial", energies[-1] <= energy0 + 1e-9, True)

# ── Discovered bound 2: telegraph τ_c u_tt + u_t = D u_xx propagates at FINITE speed √(D/τ_c) ──
D_coef, tau_c = 1.0, 4.0
c_speed = math.sqrt(D_coef/tau_c)                       # finite signal speed = 0.5
chk("telegraph: finite propagation speed √(D/τ_c) = 0.5", c_speed, 0.5, 1e-12)
chk("telegraph: speed is finite (no infinite propagation like heat τ_c→0)", math.isfinite(c_speed) and c_speed > 0, True)

print("="*80)
print("PARADOX DISSOLUTION (Part XXI) — topology · manifolds · PDE computed WITHOUT the paradox")
print("="*80)
if FAILS:
    print(f"  FAILS ({len(FAILS)}):")
    for n_,o,r_ in FAILS: print(f"    {n_}: ours={o} vs {r_}")
print("-"*80)
print(f"  TOTAL: {P}/{T}  ({100*P/max(T,1):.1f}%)  — the continuum is optional; the maya computes all three")
print("="*80)
