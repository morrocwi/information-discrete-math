# Benchmark claims — metadata, grounded in committed files only

This document is a structured index of every benchmark actually present in this repository. Each
entry names: the real benchmark script, the real result artifact (or "no committed artifact" if
none is checked in), the real comparison peer (or "none — internal only" if there is no external
library in the comparison), the correctness gate that was actually used, and what the benchmark
does **not** claim.

No number here is asserted beyond what the cited artifact records. Where a run script exists but no
result file is committed, that is stated explicitly rather than inferring a number.

Tier vocabulary follows `idm/kernel/tiers.py` / `THEOREM.md`: `Th_coqc` (machine-checked Coq
theorem), `exact` (exact ℤ/ℚ, no float), `finite_diagnostic` (numeric to a declared tolerance),
`Dr` (design-narrative).

---

## 1. Retained Spectral vs SciPy / NumPy / JAX (tridiagonal 1-D Schrödinger spectrum)

- **Scope**: lowest *k* requested eigenvalues of `H = -1/2 d²/dx² + V(x)` for seven bundled
  potential families (`retained_spectral.examples()`), discovered from raw input
  `(family, parameters, modes, tolerance)` with no supplied window or mesh.
- **Native API**: `retained_spectral.engine.native_eigvals_from_tridiagonal`,
  `retained_spectral.engine.retained_tridiagonal`, `retained_spectral.solve`.
- **Peer**: real, in-repo-executed — `scipy.linalg.eigh_tridiagonal`, `scipy.linalg.eigh` (dense),
  `numpy.linalg.eigvalsh` (dense), `scipy.sparse.linalg.eigsh` (ARPACK), and
  `jax.numpy.linalg.eigvalsh` (dense), all installed and actually run — not simulated numbers.
- **Benchmark file**: `retained_spectral/competition/run.py` (orchestrator),
  `retained_spectral/competition/executor_audit.py` (same-operator kernel-only audit),
  `retained_spectral/competition/scipy_pipeline.py` (independent end-to-end SciPy pipeline),
  `retained_spectral/competition/correctness.py` (three-layer correctness), driven by
  `python3 -m retained_spectral.competition.run`.
- **Result artifact**: `retained_spectral/results/competition_results.json` (committed; keys
  `claim_scope`, `environment`, `executor_audit`, `end_to_end`, `verdicts`, `verdict`, `tier`).
- **Correctness gate**: `retained_spectral/competition/correctness.py` — Layer 1 external
  analytic/published eigenvalue, Layer 2 `mpmath` extended-precision Sturm bisection recomputation
  of the *identical* tridiagonal operator, Layer 3 Sturm sign-count index certificate; all three
  must agree at the problem's own declared tolerance.
- **Speed gate**: `speedup_over_native` 95% bootstrap CI (seeded, `retained_spectral/competition/stats.py`)
  must sit above 1 in every case for a speed `ACCEPT`; a straddling CI is `TIE`, a CI below 1 is
  `HOLD` for that competitor.
- **Recorded verdict (this committed artifact)**: `correctness = ACCEPT`, `speed = ACCEPT`,
  **`fairness = HOLD`**, **overall `verdict = HOLD`**, `tier = finite_diagnostic`. The committed
  `claim_scope` string states: *"finite_diagnostic agreement and wall-clock cost on seven declared
  1-D Schrodinger spectra; the native method is faster than an independent SciPy pipeline
  end-to-end and than SciPy/JAX on an identical operator; no universal quantum-advantage or
  empirical-physics claim is made."* The overall verdict in the checked-in artifact is `HOLD`
  (fairness has not yet reached `ACCEPT`, per its own `verdicts.note` — "Multi-process runs are
  the remaining B3 item"), not a clean `ACCEPT`; do not upgrade this to "accepted" in any summary.
- **EXCLUDED claims**: no claim about non-tridiagonal / dense generic Hermitian matrices as a
  general-purpose eigensolver replacement; no arbitrary sparse or non-Hermitian matrix support; no
  GPU or multi-process/MPI scaling claim (single-thread, pinned BLAS/OMP env, per `run.py`); no
  claim that beating a dense whole-spectrum route generalizes beyond "requested-only O(k·N) Sturm
  vs dense O(N³)" (stated as structural, not physical, in `retained_spectral/README.md` "Honesty
  boundary"); no claim this artifact's overall verdict is `ACCEPT` — it is `HOLD`.

---

## 2. Retained Contraction Protocol (RCP) vs opt_einsum / TensorLy TT-SVD / TT-cross / TTML

- **Scope**: partition + all eleven named-axis first moments of one fixed sparse, coupled,
  non-separable 11-D finite tensor (induced width 2), declared tolerance `1e-12`.
- **Native API**: `tools.retained_contraction_protocol.certify_contraction` /
  `preflight_contraction` / `verdict_report`, via `benchmarks.retained_reverse_compiler.compile_retained_reverse`
  and `benchmarks.coupled_nd_retained_compiler.retained_factor_lineage`.
- **Peer**: real, installed, actually executed — `opt_einsum==3.4.0` (explicit factor-graph input),
  `tensorly==0.9.0` Oseledets TT-SVD (dense tensor input), TensorLy TT-cross (dense API), and
  `ttml==1.0` DMRG TT-cross (black-box callable, sampled).
- **Benchmark file**: `benchmarks/competitor_benchmark.py`, run with
  `--dimension 11 --nodes-per-axis 4 --tt-rank 8 --repeats 7 --tolerance 1e-12`.
- **Result artifact**: `benchmarks/COMPETITOR_RESULTS.md` (committed result table with median wall
  times, slowdown ratios, and max output differences per method; environment stated as
  CPython 3.12.13 / Linux x86-64 / NumPy 2.5.1). No separate machine-readable JSON is committed for
  this specific run — the Markdown table is the only committed artifact.
- **Correctness gate**: declared tolerance `1e-12`; every method's max output difference reported
  against the RCP result (best case `2.776e-16`, worst reported `2.109e-15` — still inside the
  input regime's own reported precision, per the committed table).
- **Result summary (as committed)**: RCP fastest at 0.000673 s median; `opt_einsum` 6.23× slower;
  TensorLy TT-SVD 733.54× slower; TensorLy TT-cross 707.13× slower; TTML DMRG TT-cross 29.76×
  slower — all figures as recorded in `benchmarks/COMPETITOR_RESULTS.md`, not re-derived here.
- **EXCLUDED claims**: TT-SVD/TT-cross solve a strictly more general representation-construction
  problem (approximate the whole tensor); RCP solves only the declared terminal query on an
  already-known sparse coupling graph — the doc's own "Claim boundary" section (not reproduced
  verbatim here) states this is not a claim that RCP dominates tensor-network methods in general;
  no claim about dense/high-treewidth graphs (this instance has induced width 2); no GPU/MPI claim.

---

## 3. RCP ten-topology suite vs opt_einsum + direct enumeration

- **Scope**: 10 fixed graph topologies (chain, cycle, star, binary tree, ladder, 3×3 grid, chordal
  chain, sparse-skip chain, disconnected cycles, complete graph K6), 4 Gauss-Legendre nodes per
  axis, partition + all axis first moments per problem, tolerance `1e-12`.
- **Native API**: same `tools.retained_contraction_protocol` certification path as claim 2, driven
  through `benchmarks/rcp_ten_problem_suite.py`.
- **Peer**: real, installed `opt_einsum` (all 10 problems) plus a second, structurally independent
  witness — full finite enumeration — for the 6 problems small enough to enumerate directly
  (`d ≤ 8`).
- **Benchmark file**: `benchmarks/rcp_ten_problem_suite.py`, run with
  `--nodes-per-axis 4 --repeats 7 --direct-dimension-limit 8`.
- **Result artifact**: `benchmarks/RCP_TEN_PROBLEM_RESULTS.md` (committed per-problem result table:
  work tokens, peak retained elements, RCP vs `opt_einsum` medians, speed ratio, max difference).
  The script itself only prints its JSON report to stdout (`benchmarks/rcp_ten_problem_suite.py:508`)
  — **no machine-readable JSON artifact is committed**; the Markdown table is the only committed
  record of this run.
- **Correctness gate**: preflight `ACCEPT`; planned work tokens == measured work tokens; every
  readout within `1e-12` of `opt_einsum`; full enumeration agreement where `d≤8`; final RCP
  certificate `ACCEPT`. Plus 4 fail-closed negative controls (invalid elimination order, undersized
  work budget, missing witness, deliberately perturbed witness) that must each return
  `BLOCK`/`HOLD`, not `ACCEPT`.
- **Result summary (as committed)**: 10/10 problems `ACCEPT`; largest difference vs `opt_einsum`
  `3.886e-16`; largest difference vs direct enumeration `1.665e-16`; RCP faster than `opt_einsum`
  10/10 (ratios 2.10×–6.40× per the committed table); fail-closed controls 4/4 correct.
- **EXCLUDED claims**: only 10 hand-selected topologies at one fixed width-4 discretization; no
  claim about topologies with induced width beyond what these 10 exercise (K6 is the declared
  "adverse high-width case", not an unbounded-width claim); no GPU/distributed claim.

---

## 4. RCP energy challenge — internal exact-rational stress test (no external peer)

- **Scope**: a finite-horizon (one-tick, six-action) energy/dispatch planning problem solved with
  exact rational arithmetic ("Retained Burden Algebra over exact rational readouts").
- **Native API**: `benchmarks/rcp_energy_challenge.py` (script-level; not a published `idm.*` API).
- **Peer**: **none — internal only.** This is a self-contained exact-arithmetic stress tape, not a
  comparison against any external solver or library. `rcp_energy_results.json` itself states:
  *"no external solver or continuum library produced ours."*
- **Benchmark file**: `benchmarks/rcp_energy_challenge.py`.
- **Result artifact**: `benchmarks/rcp_energy_results.json` (committed) and
  `benchmarks/RCP_ENERGY_RESULTS.md` (committed narrative).
- **Correctness gate**: exact rational equality (`Fraction`/`Q` arithmetic throughout — values are
  reported as exact fractions like `"7/4"`, not floats), preflight `status: ACCEPT` on
  `candidate_bound`/`state_bound`/`work_bound`, and the RCP certificate's own
  `admissible_records`/`candidate_records`/`peak_retained_states` fields.
- **EXCLUDED claims**: the JSON's own `honesty_fence` field states this explicitly — *"finite
  mathematical stress tape; not an empirical facility claim; no external solver or continuum
  library produced ours."* No speed comparison is made because there is no peer; do not present
  this as a "beats X" benchmark.

---

## 5. Retained Readout Pullback self-check — internal independent-implementation cross-check

- **Scope**: a family of sparse pairwise-coupled finite tensor problems (dimension 5–7+ shown),
  checking one upward FTCC fold + one downward relevance unfold (no autodiff, no junction tree)
  against an *independently implemented, in-repo* reference method.
- **Native API**: `benchmarks/compiled_retained_readout_pullback.py`.
- **Peer**: **in-repo independent reference implementation, not an external library** —
  `reference_readouts` in `benchmarks/retained_fold_tree.py`, described as "independent tilted-factor
  contraction + central finite differences." This is a second internally-written method, not a
  third-party package comparison; do not present it as beating an external tool.
- **Benchmark file**: `benchmarks/retained_readout_pullback_benchmark.py`.
- **Result artifact**: `benchmarks/retained_readout_pullback_results.json` (committed; fields
  `benchmark`, `method`, `reference`, `tier: finite_diagnostic`, `tolerance: 1e-09`,
  `worst_abs_difference`, `verdict: ACCEPT`, per-case `agreement_vs_reference`).
- **Correctness gate**: `tolerance = 1e-9`; per the committed artifact, `worst_abs_difference =
  1.8621632014159673e-10`, inside tolerance; `verdict = ACCEPT`.
- **EXCLUDED claims**: no external-library comparison; no timing "beats X" claim (only internal
  `median_seconds`/`minimum_seconds`/`maximum_seconds` self-reported, no competitor runtime in the
  same artifact); no claim beyond the specific sparse pairwise-coupled family exercised.

---

## 6. Direct vs axis-preserving N-D quadrature — internal work-token comparisons (no external peer)

- **Scope A (separable)**: `benchmarks/direct_nd_work_tokens.py` — direct full-tensor-grid
  quadrature (`5^d` samples) vs axis-preserving/retained composition, on the fully separable
  integral `I_d = ∫_{[0,1]^d} exp(-Σx_j) dx = (1-e^{-1})^d`. Result artifact:
  `benchmarks/DIRECT_ND_RESULTS.md` (committed narrative/table; no separate JSON found committed).
- **Scope B (coupled)**: `benchmarks/coupled_nd_retained_compiler.py` — 11-D coupled (non-separable)
  version with 15 pair couplings, comparing against `external_opt_einsum` (real, installed
  `opt_einsum`, per the module's own import). Result artifact: `benchmarks/COUPLED_ND_RESULTS.md`
  (committed).
- **Peer**: Scope A has **no external peer** (it compares two internal quadrature strategies
  against each other). Scope B does use real `opt_einsum` as an external witness (see the module's
  `external_opt_einsum` import), consistent with claim 2's peer.
- **Correctness gate**: both are quadrature-count/work-token comparisons on a declared finite rule
  (5-point or 4-point Gauss–Legendre per axis); Scope B further checks agreement against
  `opt_einsum` (see claim 2's `1e-12` tolerance convention, reused by this module).
- **EXCLUDED claims**: Scope A is a pure engineering work-token count, not a wall-clock speed
  claim against any library; do not describe Scope A as "beats a library."

---

## Summary table

| # | claim name | peer | benchmark file | result artifact | committed? |
|---|---|---|---|---|---|
| 1 | Retained Spectral tridiagonal spectrum | real: SciPy/NumPy/JAX | `retained_spectral/competition/run.py` | `retained_spectral/results/competition_results.json` | yes (overall verdict `HOLD`, not `ACCEPT`) |
| 2 | RCP 11-D coupled tensor | real: opt_einsum/TensorLy/TTML | `benchmarks/competitor_benchmark.py` | `benchmarks/COMPETITOR_RESULTS.md` (Markdown only) | yes |
| 3 | RCP ten-topology suite | real: opt_einsum + direct enum | `benchmarks/rcp_ten_problem_suite.py` | `benchmarks/RCP_TEN_PROBLEM_RESULTS.md` (Markdown only, script does not write JSON) | yes |
| 4 | RCP energy challenge | none — internal only | `benchmarks/rcp_energy_challenge.py` | `benchmarks/rcp_energy_results.json` | yes |
| 5 | Retained readout pullback | internal independent implementation | `benchmarks/retained_readout_pullback_benchmark.py` | `benchmarks/retained_readout_pullback_results.json` | yes |
| 6a | Direct N-D (separable) | none — internal only | `benchmarks/direct_nd_work_tokens.py` | `benchmarks/DIRECT_ND_RESULTS.md` (Markdown only) | yes |
| 6b | Coupled N-D (11-D) | real: opt_einsum | `benchmarks/coupled_nd_retained_compiler.py` | `benchmarks/COUPLED_ND_RESULTS.md` (Markdown only) | yes |

**Dropped / not included as a claim**: `benchmarks/retained_reverse_compiler.py` and
`benchmarks/retained_fold_tree.py` are shared library modules used *by* claims 2, 3, and 5 above
(imported, not standalone benchmarks with their own result artifact) — they are listed as
implementation files in `docs/knowledge_graph.json`, not as separate benchmark claims, so as not to
double-count one run under two names. `assets/competitor_benchmark.png`,
`benchmarks/competitor_showdown*`, `idm/kernel/poly/integer_poly.py`, and
`tests/test_integer_poly.py` were not read or touched, per the founder's untracked-file exclusion.
