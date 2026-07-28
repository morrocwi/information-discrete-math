# tools/ — the vendored operator toolkit

**What this folder does.** The tested home of the finite-readout operators that `idm/` re-exports (see
`tools/__init__.py`: "Vendored: audited helper modules imported (also) by bare name via
`idm/_bridge.py`"). `idm_tools.py` holds the operators proven in `validation/` (1000-problem +
100-continuum suites) — the *nouns*; `idm_discipline.py` is the numeric-honesty layer sitting on top
of the classical float/exact substrate; `certified_readout.py` is the Certified Finite-Readout
contract (`Readout(value, bound, status)`, re-exported as `idm.certified`); `aggregate.py` is the
retained-information / `I_ε` aggregation toolkit (MIN/MAX/AVG/MEDIAN/PEAK/RMS/variance/σ, min-plus /
max-plus / bottleneck semirings for shortest/critical/widest paths, machine-checked in
`formal/IDM_Tropical.v`); `eng_readouts.py` adds domain-spanning finite readouts (DFT/spectrum, THD,
dB, correlation, exact-ℚ least-squares regression, Cp/Cpk, response overshoot/rise/settling, Shannon
entropy, safety factor); `retained_contraction_protocol.py` is the RCP fail-closed contraction
contract; `retained_energy_protocol.py` is RCP-Energy; `retained_burden_algebra.py` is the exact
finite algebra for retaining least-burden readable history; `framework_compliance.py` detects
"cosmetic relabeling" (a solution that wraps a standard proof in framework vocabulary without doing
framework-native work).

**The PUBLIC api.** Most callers should go through `idm.certified` / `idm.readouts` / `idm.rcp` rather
than `tools/` directly — those are the documented facade. Direct users of `tools/` itself: import the
specific module (`from tools import certified_readout`, `from tools import aggregate`, `from tools
import eng_readouts`, `from tools.retained_contraction_protocol import ...`); each module's own
docstring is its contract (read the file header before use — every one of these opens with a
tier/scope statement).

**What NOT to import directly.** Don't import `tools/` modules that duplicate an `idm/` facade (e.g.
`certified_readout`) from application code that already has `idm` installed — use `idm.certified` so
the tier-tagging and registry wiring stay in one place. Any name prefixed `_` inside these modules is
internal.

**How to test it.** `pytest -q` exercises `tools/` transitively through `idm/` and `retained_spectral/`
imports; there is no `tests/test_tools_*.py` naming convention to grep for specifically — search
`tests/` for the module name you're changing (e.g. `grep -rl retained_contraction_protocol tests/`)
before editing.

**Limits.** These modules are vendored/audited helpers, not a second independent implementation —
changing one changes what `idm.certified`, `idm.readouts`, `idm.rcp`, and `retained_spectral`
(via `idm._bridge`) all see. `framework_compliance.py` is a detector for one caught failure mode
(cosmetic relabeling, found 2026-07-26 in a 10-problem exam) — passing it is evidence against that
specific defect, not a general correctness certificate.
