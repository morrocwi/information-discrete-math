# The Hilbert-space `+ℝ` frontier — completeness & infinite dimension (honest, code-enforced)

**Tier:** `+ℝ-Open` throughout. **Realization:** `idm/hilbert_open.py`. **Fence:** enforced in code, not prose.

The finite-dimensional Hilbert-space core (`idm/hilbert.py`, textbook Part "Hilbert-space mathematical
core", Coq `formal/IDM_Hilbert.v`) is exact / `finite_diagnostic`. The step from there to a *Hilbert*
space proper — **completeness** (every Cauchy sequence converges) and **infinite dimension** — crosses
the two non-readouts this repository's foundation guards: `I1` (ℝ-completeness) and actual infinity. So
they are never computed. They are named `+ℝ-Open` targets, each returned only as a **finite ℚ-approximant
plus a certified tail/contraction bound**.

## The frontier table

| construction | fence | `idm.hilbert_open` returns (a finite readout, never the limit) |
|---|---|---|
| Cauchy sequence → limit in `H` | `+ℝ` (`I1`) | `completeness_readout`: the rational tail `x_N` up to index `N` + the observed tail spacing — never "the limit" |
| `ℓ²` (square-summable sequences) | `+ℝ-Open` | `l2_readout`: the first `N` coordinates + the exact partial energy `Σ_{k≤N}|xₖ|²`; the total norm needs the tail (a limit) |
| `L²(X,μ)` | `+ℝ-Open` | `L2_readout`: a finite quadrature `Σ wᵢ|f(xᵢ)|²` on a declared mesh; the completed space / exact integral is open |
| infinite orthonormal basis | `+ℝ-Open` | `infinite_orthonormal_basis_readout`: `orthonormal_basis` on the first `N` vectors only, with an explicit non-claim of completeness of the span |
| infinite-dim spectral theorem / unbounded operators | `+ℝ-Open` | `infinite_spectral_readout`: **not computed at all** — returns the named target, pointing at the finite-`n` `spectral_decomposition` as what actually exists |

## The fence is code, not prose

1. **One-directional import.** `idm/hilbert.py` **never imports** `idm/hilbert_open.py`. A test
   (`tests/test_hilbert.py::test_plus_r_fence_enforced_in_code`, an AST scan) fails CI if it ever does —
   so no infinite-dim object can leak into the exact core.
2. **No certified envelope.** Every `hilbert_open` function returns
   `{"status": "+R_OPEN", "tier": "+ℝ-Open", "target": …, "approximant": …, "N": …, "note": …}` — with
   **no `"value"` field** of the shape `solve.py`'s `_ok()`/`CERTIFIED` path produces. A caller cannot
   mistake it for a certified answer (`tests/test_hilbert.py::test_plus_r_open_never_certified`).
3. **Wired only through the open path.** `solve.py` registers these kinds so they emit `+R_OPEN`, never
   an `@kind(…, "exact")` or `@kind(…, "Th_coqc")` entry.

## Permanent, not "to be closed later"

Nothing infinite-dimensional is ever tagged `Th_coqc`. The finite Hermitian `2×2` spectral facts in
`formal/IDM_Hilbert.v` are `Th_coqc` precisely because they are fixed, finite, checked *instances*. A
general-`n` — let alone infinite-dim — spectral theorem is recorded here as **permanently `+ℝ-Open`**,
not a future `Th_coqc` target: closing it *is* forming the completed continuum as a primitive, which the
foundation forbids. The honesty is the point — the frontier stays named and open.
