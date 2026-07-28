# validation/ — breadth & honesty self-checks

**What this folder does.** Standalone, run-directly validation suites that are broader-but-shallower
than `tests/` (no pytest fixtures, no CI gate by default — each script prints its own scorecard and
exits non-zero on failure). `thousand_problems.py` is the 1000-problem suite (elementary through
graduate); `hundred_continuum_problems.py` is 100 classically-continuum problems solved by the finite-ε
framework; `breadth_problems.py` / `breadth2_problems.py` cover Parts XII–XV (algebra, linear algebra,
complex, combinatorics/graph) and Parts XVI–XIX (measure/functional analysis, category, statistics,
optimization) respectively; `infinity_accuracy.py` is the "no need for the infinite" digit-count
comparison; `paradox_dissolution.py` numerically dissolves three continuum paradoxes
(topology/manifolds/PDE); `discrete_jacobian.py` checks the discrete Jacobian / retained-sensitivity
operator; `negative_controls.py` is the adversarial suite that certified tools must refuse
(`HOLD`) on; `rcp_energy_selfcheck.py` is a dependency-free check of RCP-Energy/1.0.

**The PUBLIC api.** None of these export a stable importable surface — each file's contract is "run it
and read the printed pass/fail scorecard" (`python3 validation/<script>.py`). The one shared helper
pattern (`chk(name, ours, ref, tol=0)` / `expect(name, got, want_status)`) is duplicated per-file, not
a shared library.

**What NOT to import directly.** Don't `import` these modules for their functions from application
code — they are validation entry points, not a reusable API (see `idm/`, `retained_spectral/`,
`tools/` for the corresponding stable library surfaces these scripts validate). Don't add a new
"validation" script whose pass/fail is decided by a continuum library call producing the `ours` value
— the whole point is that `ours` comes only from finite/discrete/rational operations, with the
continuum library appearing solely as `reference`.

**How to test it.** Run each script directly, e.g. `python3 validation/thousand_problems.py`,
`python3 validation/negative_controls.py`. There is no single `pytest` entry point for this folder —
check exit code (`echo $?`) after each run for CI-style gating.

**Limits.** These are breadth/coverage suites at declared numeric tolerances
(`finite_diagnostic`), not machine-checked proofs — that tier lives in `formal/`. A pass here means
"the finite procedure agreed with the reference within the stated tolerance for the cases run," not a
universal correctness guarantee outside those cases; `negative_controls.py` exists specifically
because agreement-only testing cannot catch a tool that always emits a plausible-looking but wrong
number — it must also be shown to say `HOLD` when it should.
