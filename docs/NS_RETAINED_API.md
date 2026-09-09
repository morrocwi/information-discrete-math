# Navier-Stokes Retained Solver API

## Public kind

```text
ns_retained_rk4
```

The handler is registered in the ordinary `idm.solve()` registry and is therefore available through the existing REST endpoint:

```text
POST /solve
```

Start the server with:

```bash
python3 -m idm.server
```

Then submit, for example:

```json
{
  "kind": "ns_retained_rk4",
  "K": 2,
  "nu": 0.005,
  "dt": 0.0025,
  "horizon": 1,
  "target_mode": [1, 0, 0],
  "verify": true
}
```

Equivalent Python:

```python
import idm

r = idm.solve({
    "kind": "ns_retained_rk4",
    "K": 2,
    "nu": 0.005,
    "dt": 0.0025,
    "horizon": 1,
    "target_mode": [1, 0, 0],
    "verify": True,
})
```

## Returned fields

The result contains:

- `value`: the three complex velocity components of the requested terminal Fourier mode;
- `target_mode`;
- `mode_count`;
- `ordered_triads`;
- `rk4_stage_ledger`;
- `retained_triad_work`;
- `full_triad_work`;
- `structural_work_reduction`;
- `verification` when `verify=true`;
- `backend = portable_direct_retained`;
- `tier = finite_diagnostic`.

## Mathematical scope

For a fixed finite Fourier cube, one RK4 step is pulled back from its terminal readout through the exact ordered-triad dependencies

\[
p+q=k.
\]

If `D(S)` denotes `S` plus every `p,q` required by an output `k in S`, the stage sets are

\[
K_4=T,\qquad K_3=D(K_4),\qquad K_2=D(K_3),\qquad K_1=D(K_2),\qquad S_{in}=D(K_1).
\]

The portable solver evaluates only these required stage modes. With `verify=true` it also runs the same finite full RK4 recurrence and requires terminal agreement within `1e-12`; otherwise the handler returns `HOLD`.

This is task-exact relative to the same fixed finite Fourier-Galerkin RK4 recurrence. It is not an exact-in-time continuum Navier-Stokes solver and it makes no regularity or singularity claim.

## Portable resource guard

The core IDM package deliberately remains standard-library-only for this solver. The portable API currently admits:

```text
1 <= K <= 3
1 <= horizon <= 3
```

Requests beyond that boundary return `HOLD`. The NumPy/FFT hybrid performance benchmark remains in the separate `readout-problem-navier-stokes` reproduction repository; its timing claims are not silently transferred to this portable API backend.

## Registry consistency

The live `idm.solve()` registry is the source of truth for solver kinds. `tools/sync_solver_surface.py` synchronizes registry-derived fixtures, documented total-kind counts, `capabilities.json`, the package version facade, and the migration golden snapshot. `.github/workflows/sync-solver-surface.yml` runs that synchronization when solver registrations change, preventing a newly registered kind from remaining outside the repository-wide adversarial and migration gates.
