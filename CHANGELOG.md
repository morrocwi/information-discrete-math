# Changelog

All notable changes to Information Discrete Mathematics. Tiers are honest: `Th_coqc` = machine-checked
axiom-free (Coq 8.20, `Print Assumptions` = *Closed under the global context*); `finite_diagnostic` =
finite procedure cross-checked numerically; `exact` = exact over ℚ; `Open`/`+ℝ-Open` = declared open,
never dressed as a theorem.

## [Unreleased]

### PyPI packaging made publish-ready (Track B gap 1 — prep)
`pyproject.toml` now carries the metadata a good PyPI listing needs: `readme = "README.md"` (markdown
long description), 13 trove `classifiers` (Production/Stable, Science/Research, Python 3.9–3.13, Maths),
`keywords`, and expanded `[project.urls]` (Repository, Changelog, Issues, Documentation). The build was
verified end-to-end: `python -m build` produces a wheel + sdist; the wheel installs into a clean target
and `import idm` solves (269 kinds, `factorize`/`ai.run`/`describe` all work); the METADATA renders the
long description + classifiers + URLs. The only remaining step is `twine upload`, which needs a founder
PyPI token — the exact steps are in [`docs/PUBLISHING.md`](docs/PUBLISHING.md). `dist/`/`build/` stay
git-ignored. No code change, no count change (269).

### Track C (AI Gateway) Phase C — synthetic tool-use dataset + benchmark harness
Completes Track C (roadmap #52). `idm/ai_bench.py` (exposed as `idm.ai_bench`):
- **`dataset()`** — a fixed, deterministic set of 17 tool-use cases spanning all 11 gateway ops, plus
  free-form-string cases (routed via `idm.parse`) and deliberately-unclassifiable ones, each labelled
  with the expected op and the expected solve status.
- **`score(router)`** — model-agnostic: run any `router` callable (request → an op name, or a
  plan/route dict) over the dataset and report **op-selection accuracy** and **end-to-end execution
  accuracy** with the per-case failures.
- **`benchmark_router()`** — scores the built-in deterministic `idm.ai.route` as the oracle/ceiling
  (**100 % op-selection, 100 % execution**). To benchmark a real 0.5B model, pass a router that calls
  it — no model weights are shipped or needed for the self-test; the harness is proven to discriminate
  (a constant "always factor" router scores < 0.3). No new kind, no count change (269).

### Track C (AI Gateway) Phase B — free-form router + plan/validate/dry-run
Builds on Phase A (roadmap #52, Phase B), additive:
- **`idm.ai.route(request)`** — the domain router / expression classifier. A free-form **string** is
  translated by `idm.parse` (rule-based world-language → problem dict) and its kind mapped back to a
  gateway op; a structured `{"op": …}` or `{"kind": …}` dict is normalized; a kind outside the ~11 ops
  still routes (op=None) — never a capability reduction. Unclassifiable input → `status:"HOLD"`,
  `error_code:"UNCLASSIFIED"` (honest, no NL guessing beyond `idm.parse`).
- **`idm.ai.plan(op, **params)`** and **`idm.ai.run(op, dry_run=True, **params)`** — the plan→validate
  step: return the route + the exact `problem` dict that WOULD be solved, without executing. The
  validate is honest — `idm.schema` now splits **required** (`p["x"]` subscript reads) vs **optional**
  (`p.get("x")`), so `plan` flags only genuinely-missing required fields (`status` ready/needs_params),
  not absent optionals. `idm.schema(kind)` gains `required`/`optional` keys.
Phase C (synthetic dataset + 0.5B benchmark) remains. Tests: `tests/test_ai_gateway.py` +2. No count change (269).

### `all_roots` — second (build-bound) fence gate closes the high-degree residual (#65)
The layer-2 resultant-bits gate caught *isolation-bound* hangs (a high-bit resultant) but missed
*build-bound* ones — a high-DEGREE resultant is slow to build/interpolate even at moderate bits
(e.g. `x⁷−20`: a degree-49 resultant at only 55 bits, under the 64-bit cap, yet >60s). Instrumenting
showed neither Sturm-eval count nor bit-operation count correlates with wall-time here (the cost sits in
different phases — build vs isolation — for different inputs), so a single computed counter can't bound
it either. Instead a **second deterministic gate** on the resultant's **degree·bits**
(`max_resultant_degbits=2400`) now catches the build-bound regime: `x⁷−20` (degree·bits ≈ 2695) → **HOLD
in ~1s** (was >60s), while `x⁷−2` (≈ 2205, ~14s) and every fixture stay under it. Measured margins:
KEEP ≤ 2205 < 2400 < 2695 ≤ BLOCK. Still an honest **heuristic** (not a proven bound — a novel input in
the gaps could slip; `force` / `fence` override) but it now covers **both** cost regimes. Deterministic,
still entirely in `complex_roots.py`, golden unchanged, no count change (269).

### Track C (AI Gateway) Phase A — `idm.ai`: a small deterministic entrance over the full solver
An **entrance**, never a capability reduction (roadmap #52, Phase A): a small model (or a human) can
drive the solver through ~11 high-level ops instead of memorizing 269 kind names.
- **`idm.ai.run(op, **params)`** deterministically routes an op to its registry kind and returns a
  `Result` — `run("factor", n=360360)`, `run("roots", coeffs=[…])`, `run("solve_linear", A=…, b=…)`, etc.
  Ops: `factor · gcd · integrate · integrate_exact · roots · solve_linear · eigenvalues · determinant ·
  ode · limit · shortest_path`.
- **`idm.ai.ops()`** is the central schema — each op with its target kind, parameter fields (from
  `idm.schema`), and honest tier — the small decision space a model reasons over.
- Design principles honored: the **route** is always exposed (`result["route"] = {op, kind}`); **tiers
  are forwarded verbatim** (the gateway does no math, no silent exact→numeric downgrade); failures are
  **structured** (`error_code` ∈ `UNKNOWN_OP` (+`did_you_mean`) / `MISSING_PARAM` / `SOLVER_HOLD`);
  extra kwargs pass straight through; and the full 269-kind `idm.solve` registry is the documented
  **escalation path**. Phases B (free-form router) and C (0.5B benchmark) are declared later increments
  needing founder scope. Tests: `tests/test_ai_gateway.py` (5). No new kind, no count change (269).

### Track B (developer experience) — `Result` object + typed convenience wrappers
Two of the five DX gaps (roadmap #51, gaps 3 & 4), pure additions, no behaviour change:
- **`Result`** (`idm/results.py`) — `idm.solve()` now returns a `Result` instead of a bare dict.
  `Result` **subclasses `dict`**, so every existing pattern is unchanged (`r["status"]`,
  `json.dumps(r)`, `isinstance(r, dict)`, dict-equality, the REST server, and the golden snapshots all
  behave identically — verified: `json.dumps(Result) == json.dumps(dict)`, full golden suite passes). It
  adds typed accessors on top: `.kind .status .value .bound .tier .reason .method .coq_theorem`,
  `.is_hold`, `.is_open`, `.is_ok`, `.raise_for_hold()` (raises `idm.SolveHold` with the solver's own
  reason, and returns `self` on success so it chains), and `.to_dict()`. The predicates cover the full
  status space the solver actually emits: `is_ok` is defined by the presence of a `value` (so it
  correctly includes a definitive `REFUTED` counterexample and excludes the value-less open-tail
  `+R_OPEN`), `is_open` flags the `+R_OPEN` open-tail readout, `is_hold` the no-readout HOLD.
- **Typed convenience** (`idm/convenience.py`) — one-call wrappers so a programmer need not hand-assemble
  the problem dict: `idm.factorize(n)`, `idm.gcd(a, b)`, `idm.solve_integral(f, a, b, eps=…)`,
  `idm.integrate_rational(num, den)`, `idm.solve_matrix(A, b)`, `idm.eigenvalues(matrix)`,
  `idm.solve_roots(coeffs)`, `idm.solve_ode(coeffs)`. Each returns a `Result`; each dispatches through
  the same `solve` CI uses — no new math, no new kind.

PyPI publish (gap 1) is a founder call. No count change (269).

### Track B (developer experience) — schema discovery + Quick Start
The other two pure-DX gaps (roadmap #51, gaps 2 & 5):
- **`idm.describe(kind)` / `idm.schema(kind)` / `idm.example(kind)`** (`idm/discovery.py`) — the same
  introspection the `python -m idm` CLI does, now returning STRUCTURED data in Python: `describe` gives
  tier + handler signature + doc + a verify hint; `schema` gives the (heuristically-derived, honestly
  labelled) parameter names the handler reads plus a real on-file example; `example` returns a real
  `{"kind": …}` problem dict found in `tests/`. Unknown kind → `KeyError`. The CLI now imports these
  helpers, so CLI and Python API are one source of truth (no duplicated logic).
- **Quick Start** — [`docs/QUICKSTART.md`](docs/QUICKSTART.md): `idm` in 10 minutes, copy-runnable, every
  shown output produced by running it; linked from the README. This closes Track B's internal DX gaps
  (2, 3, 4, 5); only gap 1 (PyPI publish) remains, a founder call. No count change (269).

### `all_roots` — layer-2 resultant-bits fence (removes the worst multi-minute hangs; heuristic, not a tight bound)
A quartic with small *input* coefficients but an expensive degree-16 resultant (e.g.
`[9999,-4242,1313,-77,1]`, well-separated large-magnitude roots) passed the layer-1 input pre-check yet
ran for **>90s**. Profiling pinned the cost to Sturm-**isolating** the built resultant (which itself
builds in ~0.03s). A second deterministic layer now measures the built resultant's coefficient bit-size
— after the cheap build, before the expensive isolation — and HOLDs above `max_resultant_bits=64`, so
`[9999,…]` (73-bit resultant) HOLDs in ~0.06s while every fixture (≤ 39) and fast mid-range inputs (a
~58-bit quartic resolves in ~8s) still resolve. **Honest scope (not overclaimed):** isolation runtime is
genuinely *not* a monotone function of resultant bit-size (a degree-6 resultant at 57 bits isolates in
~2s while a degree-49 one at 55 bits can take over a minute), so this cap is a **heuristic size proxy**
that removes the worst hangs but is neither an upper nor a lower runtime bound — it can still let a slow
large-degree/low-bit input through (recover nothing needed) or, rarely, HOLD a fast input above the cap
(recover with `force`). A *tight* deterministic bound needs a computed work budget counting the actual
Sturm sign-evaluations — still open (#65). Deterministic (function of the resultants only, no
wall-clock), entirely within `complex_roots.py` (no `univariate.py` change), golden unchanged,
`"force": true` / `fence=None` bypass. No new kind, no count change (269).

### Documented a third machine-checked arrival at the same indistinguishability kernel
`docs/FORMAL_COMPANIONS.md` now records that `readout_genesis`'s `InfoTrueRecordUnreadable`
(`Th_coqc`, axiom-free — verified locally: 3 lemmas, all *Closed under the global context*;
`no_decoder_recovers_state`: no decoder recovers two distinct states a readout maps to one record) is
the abstract twin of the companion's zero-fibre indistinguishability equivalence (`indist` refl/sym/trans
+ `keystone_zero_iff_component`) — `O := Φ ↦ [Φ]_indist` makes the two compose directly. **Tier-honest
fence:** the shared core is the *generic* equivalence-kernel of any non-injective map (the abstract
lemma is a one-line consequence of non-injectivity), so the multiple arrivals are program coherence, not
independent deep evidence — the value is that a foundation's central move is elementary and universal.
Corrects a provenance mix-up: `minimal_three_values` / `discrete_floor` live in THIS repo
(`formal/IDM_ReadoutMinimality.v`, `formal/IDM_Genesis.v`), not `readout_genesis`. Docs-only; no code,
no new kind, no count change (269).

### `all_roots` — deterministic performance fence (HOLD, never hang, on large-coefficient high-degree inputs)
`all_roots` could run for **minutes** on a high-degree or large-coefficient square-free factor (its
degree-`n²` resultants + Sturm isolation). Profiling found **two independent cliffs** — a degree cliff
(a degree-7 factor resolves in ~seconds, a degree-8 one in minutes even for tiny coefficients, because
its resultant is degree 64) and a coefficient-bits cliff (a degree-4 factor with ~13-bit coefficients
already runs for tens of seconds). No single smooth proxy separates both, so a **deterministic fence**
(pure pre-check on `(degree, coefficient bit-length)` — O(1), **no wall-clock**, so golden/tests stay
reproducible) caps the **degree** directly (`max_factor_degree=7`) and the **`n²·bits` interaction**
(`max_mix=350`), raising `ComplexRootsHOLD` with an actionable reason **before** the expensive work —
HOLD, never hang. There is deliberately **no standalone bit-length cap**: coefficient size costs only
*through* the degree-`n²` resultant, so a low-degree large-coefficient factor (e.g. a degree-2 with
20-bit coefficients, ~0.03s) is fast and is **not** fenced — only `n²·bits` gates the coefficient axis.
Honest limit (disclosed, not overclaimed): this static pre-check catches the two named cliffs but does
not fully bound runtime — a mid-degree factor with an expensive degree-`n²` resultant (e.g. a quartic
with large-magnitude well-separated roots) can still run long inside the caps; a *computed* work budget
threaded through the resultant/Sturm path is a declared follow-up. Every capability that currently returns in ≲15s is preserved
(verified: all existing fixtures + `x⁷−2` still resolve; golden unchanged). The `all_roots` kind takes
`"force": true` (and `all_roots(..., fence=None)` / a widened `fence` dict) to bypass or loosen the
fence and grind an input out. No new kind, no count change (269).

### Wired the published formal companion `zero-readout-certifies` into the ecosystem
Added [`docs/FORMAL_COMPANIONS.md`](docs/FORMAL_COMPANIONS.md) — the single map of the machine-checked
sibling repos this repo cites, and, for `zero-readout-certifies` (Coq 8.20 / Rocq 9.2, 38 audited results,
all *Closed under the global context*, DOI [`10.5281/zenodo.21665100`](https://doi.org/10.5281/zenodo.21665100)),
the exact code-to-proof mapping. That companion machine-checks two extensions of this repo's keystone
(`formal/IDM_Keystone.v`): (1) the keystone operator's **zero fibre** — `I(Φ)=0 ⟺ Φ constant on every
connected component` (positive weights) — and (2) the typed **reader-state** separation that is the
soundness floor under this repo's **HOLD discipline** (a resolved `0` is a provably distinct object from
an unresolved HOLD; a HOLD is fail-closed). Cross-referenced from `THEOREM.md §IV`, `INDEX.md` row V,
`formal/README.md`, `README.md`, and `docs/knowledge_graph.json`. Cite, don't copy: the companion is a
frozen, separately-published artifact — no `.v` files are duplicated here. Verified locally
(`make verify` → *verified 38 audited results with no additional global assumptions*). No new kind, no
count change (269). Horizontal-knowledge: a witness we cite, not an external authority.

### `all_roots` — root multiplicity (repeated-root polynomials no longer HOLD)
`all_roots` previously HELD on any polynomial with a repeated root (`(x−1)³`). It now finds the DISTINCT
roots of each **square-free factor** and tags them with that factor's multiplicity, so it returns every
root (real + complex) with its exact **multiplicity** and certifies completeness by `Σ multiplicity ==
degree`. E.g. `(x−1)³` → root 1 (multiplicity 3); `(x²+1)²` → `±i` each multiplicity 2; `(x²+1)(x−1)²` →
`±i` (m1) + `1` (m2). Each root gains a `multiplicity` field and the result a `num_distinct`; `num_real`/
`num_complex` are now counted with multiplicity (so they still sum to the degree). Bonus: each square-free
factor is lower-degree, so this is also faster than isolating the whole polynomial. No new kind, no count
change (269).


### WP8 (Increment 2) — `integrate_rational` now handles repeated irreducible quadratics
The rational-function integrator previously HELD on a denominator with a repeated irreducible quadratic
(e.g. `1/(x²+1)²`). It now integrates them via the **reduction formula**
`∫du/(u²+w²)^n = u/(2w²(n−1)(u²+w²)^{n−1}) + (2n−3)/(2w²(n−1))·∫du/(u²+w²)^{n−1}` (completing the square,
`w²=q−p²/4`): `∫1/(x²+1)² = ½·x/(x²+1) + ½·arctan x`, `∫x/(x²+1)² = −1/(2(x²+1))`, and mixed cases like
`1/((x−1)(x²+1)²)` all verify by differentiating back. So `integrate_rational` now covers **any rational
function whose denominator factors into linear and irreducible-quadratic factors, to any multiplicity** —
only a degree-≥3 irreducible denominator still HOLDs (algebraic-function / Risch, a later increment). No new
kind, no count change (269); the `integrate_rational` fixture is degree-2 so the golden snapshot is
byte-identical.


### WP8 (Increment 1) — exact rational-function integration
New kind **`integrate_rational`** (`exact`, → **269** kinds): the exact symbolic integral of a rational
function `P(x)/Q(x)` over ℚ, where the elementary integrator only handled polynomials + a few linear-argument
patterns. Method (all exact ℚ): polynomial part by division; factor `Q` over ℚ into irreducibles; partial
fractions by **undetermined coefficients** (an exact ℚ linear solve, since `apart` only splits square-free
blocks); integrate each term → `c·ln(x−a)`, `−c/((k−1)(x−a)^{k−1})`, and `(b/2)·ln(x²+px+q) +
K·arctan((x+p/2)/√(q−p²/4))`. E.g. `∫1/(x²+1)=arctan x`, `∫1/(x²−1)=½ln|x−1|−½ln|x+1|`, `∫x²/(x²+1)=x−arctan x`,
`∫1/(x−1)²=−1/(x−1)`. Verified by differentiating the result back. Scope: linear factors any multiplicity,
irreducible quadratics multiplicity 1; a degree-≥3 irreducible or a repeated quadratic HOLDs (Hermite/Risch
are later increments). `idm/kernel/poly/rational_integration.py` + test.


### Complex-root isolation — `all_roots`: every root, real AND complex, as exact enclosures (→268)
Completes the "degree-n polynomial → all n roots" story (the complex half of WP3/WP6/WP11/WP13). New kind
**`all_roots`** (`exact`): every root is an **exact rational-rectangle enclosure** `[re]×[im]` isolating one
root, with the real and imaginary parts each an exact real algebraic number (`AlgReal`) — **no
Durand–Kerner**. Method (all over ℚ): split `p(x+iy) = P + iQ`; the real/imaginary parts are the real roots
of `Res_y(P,Q)` / `Res_x(P,Q)` (recovered exactly by evaluation + Lagrange interpolation of the univariate
resultant), isolated as `AlgReal`; a candidate pair `(a,b)` is a root iff `P(a,b)=Q(a,b)=0`, decided by
exact rational **interval arithmetic** (sidesteps the algebraic-product blow-up). The resultants' real
roots are isolated by **Sturm on their square-free part** (no factoring — the resultants have degree n²),
so it handles **distinct-root (square-free) ℚ-polynomials at any degree**; the result is certified complete
(isolated count == degree, complex in conjugate pairs) or HOLDs. A repeated-root input fails closed (an
irrational part carries a defining polynomial, not the minimal one; repeated-root multiplicity + exact
complex arithmetic are declared later increments). E.g. `x²+1`→
`±i`; `x³−2`→ `∛2` + a complex pair; `x⁴+1`→ the four `±√2/2 ± i√2/2`; `x⁴−1`→ `±1, ±i`. Exact complex
*arithmetic* on these roots is a later increment. `idm/kernel/poly/complex_roots.py` + test.


### WP11 (Increment 1) — linear ODEs resolve real algebraic characteristic roots at any degree
`linear_ode` previously **HELD** on an irreducible degree-≥3 characteristic factor ("roots not in
radicals"). It now resolves that factor's **real** roots exactly as algebraic numbers (WP2/WP3 `AlgReal`):
each real root ρ contributes the basis `e^{ρx}, x e^{ρx}, …` with ρ described by its exact minimal
polynomial + isolating interval. So `y‴ − 3y′ + y = 0` (char `r³−3r+1`, three real irrational roots, casus
irreducibilis) is now **fully solved** — a solution space that was entirely out of reach before. When a
degree-≥3 factor also has complex roots (e.g. char `r³−2`: real `∛2` + a complex pair), the real part is
resolved exactly and only the complex conjugate roots are left `partial` (complex-algebraic basis is a
declared later WP11 increment). Degree-1/2 factors are unchanged (golden snapshot byte-identical).


### WP13 (Increment 1) — exact eigenvalues as algebraic objects
New kind **`exact_eigenvalues`** (`exact`, → **267** kinds): the real eigenvalues of a rational matrix as
**exact algebraic objects with multiplicity** — no Durand–Kerner. The characteristic polynomial is exact
(Faddeev–LeVerrier over ℚ, existing `eigen.characteristic_polynomial`); its real roots are isolated as
`AlgReal` (WP2/WP3). Reports `num_complex` and `completeness` (`complete` iff all eigenvalues real, else
`real_complete`). E.g. `[[2,1],[1,2]]` → 1, 3 exact; `[[0,1],[1,1]]` → the golden pair `(1±√5)/2` (min-poly
`x²−x−1`); a rotation `[[0,-1],[1,0]]` → 0 real, 2 complex; `diag(2,2,3)` → eigenvalue 2 (mult 2), 3.
Hard char-poly factorization fails closed (HOLD), never hangs. The existing numeric `eigenvalues` kind is
unchanged. Exact complex eigenvalues are a later increment.
### WP6 (Increment 1) — `symbolic_solve` returns the complete exact real solution set
For a univariate ℚ-polynomial equation, `symbolic_solve` (via `idm.kernel.cas.solve`) previously returned
**only rational roots** at degree ≥3 and told you to "use poly_roots" — silently **losing every irrational
real root**. It now returns the **complete exact real solution set** through WP2/WP3's `AlgReal`: each real
root as an exact algebraic object (minimal polynomial + isolating interval) with its multiplicity, plus an
honest `num_complex` and `completeness` (`complete` iff all roots real, else `real_complete`). E.g.
`x³−2` now returns `∛2` exactly (min-poly `x³−2`) with 2 complex; `(x−1)(x−2)(x−3)` returns 1, 2, 3 complete.
Degrees 1–2 keep their exact radical forms; a hard high-degree factorization fails closed (`partial` + note),
never hangs. No lost roots. (Existing behavior for degree ≤2 is byte-identical — golden snapshot unchanged.)


### WP3 (Increment 1) — exact real root objects, no Durand–Kerner
Builds on WP2's `AlgReal`. New kind **`all_real_roots`** (`exact`, → **266** kinds): given a ℚ-polynomial,
it returns **every real root as an exact algebraic object with its multiplicity** (irreducible
factorization over ℚ + Sturm isolation), sorted, verified by substitute-back — **no reduction to
Durand–Kerner floats**. It also reports `num_complex = deg − Σ(real multiplicities)` and a `completeness`
of `complete` (all roots real) or `real_complete` (all real roots found exactly; the remaining complex
conjugate pairs are a declared later WP3 increment). `AlgReal.real_roots_with_multiplicity` exposes the
same at the kernel level. This meets the WP3 real-part closure criterion: a degree-n polynomial yields all
its real roots with multiplicity, exactly. Registry 265 → 266, counts synced across all docs + gates.


### WP2 — exact real algebraic-number arithmetic (the #1 CAS gap, now open)
The `AlgebraicNumber` type was a data-shell with no arithmetic. **`idm/kernel/poly/algebraic.py`** makes a
root of a ℚ-polynomial a genuinely computable exact object — `AlgReal(min_poly, isolating_interval)`:
- construct from a ℚ-polynomial + real-root index (Sturm isolation); `+ − × ÷`, integer powers; exact
  ordering / equality / sign — **all exact over ℚ, never a float**. The minimal polynomial of `α∘β` comes
  from a power-basis dependency in ℚ(α,β) (linear algebra over ℚ), then the correct root is re-isolated by
  Sturm bisection. Division by zero and out-of-range roots **HOLD**, never guess.
- **WP2 closure criterion met:** every result **substitutes back** to satisfy its own minimal polynomial
  exactly (e.g. `(2^{1/3})³ = 2`, `√2+√3` → `x⁴−10x²+1`, `√2·√3` → `x²−6`, `1/√2` → `x²−½`). Verified in
  `tests/test_algebraic.py`, including a **differential cross-check against SymPy's `minimal_polynomial`**
  (comparator only).
- New solver kinds (**265** total): `real_root` (k-th exact real root of a ℚ-polynomial) and
  `algebraic_arith` (exact `add/sub/mul/div` of two algebraic reals) — both `exact`, returning the
  minimal polynomial + isolating interval + substitute-back certificate.
- This is the root of Track A that unblocks WP3 (`RootOf`), WP6 (complete univariate solving), WP11
  (degree-≥3 ODE roots), WP13 (exact eigenvalues). *Increment 1 is **real** algebraic numbers; complex,
  number fields ℚ(α), towers, and ℚ(x) are declared later WP2 increments.*
- Registry count 263 → **265**; all kind-count references synced across README / SOLVER.md / API.md /
  capabilities.json / the manifest gate (the founder's "one continuous system" — a stale 259 in a few
  docs was corrected in the same pass).

### The continuum as a first-class ℚ PRIMITIVE — `idm.continuum.Continuum`
Founder question (2026-07-29): *can we build a ℚ-primitive function that behaves like the ℝ-rung
continuum?* Yes — the operational form of "the continuum is a readout of the discrete" (Part XX /
machine-checked FTCC bridge). A `Continuum` is a resolution-indexed **exact-ℚ** readout `g : N → ℚ`,
never an ℝ object:
- `.at(N)` — the exact ℚ readout at declared resolution N (the primitive operation).
- `.readout(ε)` — tier-honest: `CERTIFIED` **only** on a PROVEN tail bound (`geometric`'s exact
  rᴺ⁺¹/(1−r), or a bound propagated through `+`/`−` by the triangle law); a bare observed plateau is
  `finite_diagnostic` (measured, not proven beyond N — a flat-then-diverge sequence lands here, never
  falsely CERTIFIED); `HOLD` where no plateau exists. It never emits a completed limit.
- a **ℚ-algebra** closed and exact pointwise (`+ − ×`, scalar, `compose`): `(a+b).at(N) == a.at(N)+b.at(N)`,
  so continuum-readouts are a commutative ℚ-algebra you compute with directly, ℝ never a primitive.
- **Formal core → 194** (from 189): **`IDM_Continuum.v`** machine-checks the algebra's soundness
  axiom-free over ℚ — pointwise homomorphism (`radd_at`/`rmul_at`), commutativity, a constant's zero gap,
  and the key **`gap_subadditive`** (|Δ(g+h)| ≤ |Δg|+|Δh|, so summing two plateauing continua still
  plateaus — the algebra can't silently break `.readout`'s honesty).
- `idm/continuum.py` + `tests/test_continuum.py` (11 tests) + discovery pointer in `idm/README.md`.
- **Anti-ℝ-slide guard** `tests/test_continuum_no_R_slide.py` — enforces (in CI, not just intent) that no
  doc/code surface positively claims ℝ was constructed / is a primitive / that the completed limit is
  emitted as a value. Negation-aware, so the honest fenced phrasings pass ("ℝ is never a primitive", "the
  completed real stays +ℝ-Open"); it also pins the module's fence markers and asserts every non-HOLD
  readout keeps the `+ℝ-Open` fence and returns only exact ℚ. Closes the "language drift" vigilance point.

### The ℚ-computability law — the +ℝ-Open Hilbert frontier now splits its two truths
Founder principle (2026-07-29): *if an ℝ-rung quantity is actually COMPUTED, it is computed on ℚ — so
it must carry a ℚ tier, not a blanket `+ℝ-Open`.* Audit of the 5 frontier kinds found 4 of them do
compute an exact ℚ readout (partial energy `Σ|xₖ|²`, the Cauchy tail `x_N`, the finite ONB) that was
buried under one uniform `+ℝ-Open` tag — an under-claim. Fixed with a **two-tier readout** (the
continuum-maya split, Part XX), without weakening the anti-overclaim fence:
- `idm/hilbert_open.py` now returns `computed_core` (the exact ℚ quantity, with its OWN honest tier:
  `Th_coqc` for the ℓ²/L² partial energy, `exact` for the Cauchy/ONB readouts) **and** `open_tail` (the
  completed limit / whole-space object, staying `+ℝ-Open`). The fence is unchanged: still
  `status:+R_OPEN`, still no top-level `value`, kind-level tier never `Th_coqc`. `infinite_spectral`
  honestly reports `computed_core: None` — it is the one kind that computes nothing on ℚ.
- **Formal core → 189** (from 184): **`IDM_HilbertReadout.v`** machine-checks the ℚ core the
  `Th_coqc` claim rests on — the unweighted `partial_energy` (`nonneg` · exact-`app`-additive ·
  `monotone` in N) and the **weighted** quadrature `weighted_energy` (`nonneg` under measure weights
  wᵢ≥0 · exact-`app`-additive), all axiom-free over ℚ. This *is* "computable on ℚ" made machine-checked.
- **Honest L² tier (reviewer-caught).** `L2_readout` computes a *weighted* quadrature `Σ wᵢ|f(xᵢ)|²`; its
  `computed_core` is `Th_coqc` **only when the weights form a measure (wᵢ ≥ 0)** — the hypothesis of
  `weighted_energy_nonneg`. With a signed weight (not a measure, value can go negative) it honestly drops
  to `exact` and cites no witness, instead of claiming a nonneg witness whose premise fails.
- Guard test `tests/test_hilbert.py::test_two_tier_readout_gives_the_q_core_its_honest_tier` — every
  computing kind's `computed_core` carries an `exact`/`Th_coqc` tier, any `Th_coqc` cites a real in-tree
  witness, and `open_tail` stays `+ℝ-Open`. Golden snapshot regenerated (additive; 5 kinds).

## [1.4.1]

Quality + integrity release: acts on a world-class multi-discipline review, pays down architectural
debt, and adds the algebraic atom of the inertia boundary-readout — all backward-compatible.

### Formal core → 184 machine-checked axiom-free theorems (from 177)
- **`IDM_Schur.v`** — the exact Schur/boundary congruence over ℚ (`A = Mᵀ·diag(a, c−b²/a)·M` for a 2×2
  block, the `b²/a` cancellation), the algebraic atom of Haynsworth inertia-additivity — machine-checks,
  in this framework's own semantics, that eliminating a boundary node produces exactly the Schur
  complement. Fenced: Sylvester's sign-count invariance stays `+ℝ-Open`.

### P5 (inertia lower bound) — recast in the information language
- `docs/P46_P5_lower_bound_analysis.md` rewritten **purely readout-first** (removing a borrowed
  classical-complexity frame): P5 = "does a BOUNDARY readout require producing the VOLUME?"; the READOUT
  rule predicts against `Ω(fill*)`; info-P5 is a boundary-retention (Declaration-Bound-on-the-separator)
  question, still `+ℝ-Open`. No conjecture formalized.

### World-class review — acted on
- Fixed 4 verified defects: package `__version__` drift (was 1.3.0), stale "127 theorems" docs
  (→ live count), CLI `describe`/`list` now report the **honest runtime tier** (mirroring solve()'s
  downgrade), and `retained_spectral/README` now points to the discovery layer ("do not infer scope").
- New **CI drift gates**: version single-sourced (idm == pyproject == manifest) and documented theorem
  counts (README / formal-README / **SKILL.md**) gated against `formal/verify.sh`.

### Debt paid down
- `idm/solve.py` split from a 924-line monolith into `idm/_solve_core.py` + **30 per-domain modules** +
  a 44-line dispatch facade — verified **byte-identical** for all 263 kinds (golden snapshot).

## [1.4.0]

### Discovery layer — the repository now describes itself (humans + AI)
- **`capabilities.json`** — a machine-readable manifest **generated** from the live `idm.solve` registry
  by `tools/gen_capabilities.py` (all 263 problem kinds classified into 11 domains, none dropped/duplicated).
- **CI gate** `tests/test_capabilities_manifest.py` — fails if `total_problem_kinds != len(idm.kinds())`,
  if any kind is unclassified, or if the manifest is not byte-identical to a fresh regeneration. Adding or
  removing an API without regenerating now breaks CI.
- **CLI discovery** — `python -m idm list | kinds | describe <kind> | example <kind>` (new `idm` console
  script), grounded in the registry; `example` returns a real test fixture or honestly reports none.
- **AI-first docs** — `AI_START_HERE.md` ("do not infer capability from a single module" + a discovery
  order), `llms.txt`, `API_INDEX.md`, a README capability-map + 5-level-platform, and per-folder READMEs.
- **Reproducibility** — `Makefile` (`install`/`discover`/`test`/`prove`/`formal`/`benchmark`/`verify-all`),
  a build-verified core `Dockerfile`, `docker/{spectral,hpc,formal}` profiles + `docker-compose.yml`
  (the PETSc/SLEPc HPC image is authored, honestly marked not-build-verified).
- **Benchmark honesty** — `docs/BENCHMARK_CLAIMS.md` (each claim: scope · native API · peer · run file ·
  committed result artifact · correctness gate · **excluded** claims) and `docs/knowledge_graph.json`
  (claim → API → implementation → tests → benchmark → theory).

### Formal core — grew from 107 to 177 machine-checked, axiom-free theorems
- **`IDM_ReadoutMinimality.v`** — the minimal value-set of a signed readout (Theorem 1: ≥3 values forced,
  the third a neutral) and the four-valued algebra `{+,−,0,⊥}` with `0` (determinate) distinct from `⊥`
  (unresolved) on both the involution and the information-order axes.
- **`IDM_ResolvedCount.v`** — the resolved (four-valued) inertia readout: `⊥` arises **only** from a
  positive declared resolution (a fact about the instrument), `0` **only** at exact resolution on a true
  balance (a fact about the object). Shipped API `retained_spectral/inertia.py: resolved_count_below`
  closes the silent-failure gap (a floored pivot is now reported `⊥`, not folded into `n₀`).
- **`IDM_EquivariantReadout.v`** — the necessary condition behind P1 (general-group minimal readout):
  `Stab_X(x) ⊆ Stab_V(r x)`, equality under faithfulness. The cardinality formula stays **Conjecture P1**.
- **`IDM_Apriori.v`** — the Richardson **a-priori** stability certificate: an order-`p` method has
  contraction ratio `ρ = 2⁻ᵖ` known up front (feeds `refine_stable`), no gap monitoring.
- **`IDM_SetsFunctions.v`** (Th 10.2) and **`IDM_FirstOrder.v`** (finite first-order `⊨_λ` decidable) —
  the v-proofs edition: two `Th_coqc`-eligible sketches converted to real witnesses.
- **`IDM_ApproxCount.v`** — an honest `Ω(log(n/r))` lower bound for approximate deferred counting;
  **P7 (`Θ(n/r)`) and P8 (randomized) stay Open**, not formalized.

### Certified computation
- **Multi-dimensional quadrature** — `idm.certified.integral_nd` (tensor-trapezoid, reuses the
  dimension-agnostic `refine_stable` theorem); certifies with bound `0` when the readout is exact.
- **Richardson a-priori** — `idm.certified.richardson_apriori_{ratio,bound,certified}`.

### Documentation / honesty
- New textbook §10.14 "named-Open-problems frontier" (Hauptvermutung, strong LLN, topos completeness,
  exact π/φ) — each stated, predicted, fenced; no closure claimed.
- Corrected a pre-existing overclaim: a §10.7 "machine-checked witness `formal/InfoCausalPartialOrder_attempt.v`"
  citing a file not in-tree — downgraded to `Th_coqc`-eligible with an honesty note.
- §10.9 renumbered to §10.13 (consistency).

## [1.3.0]
- Genuinely installable self-contained wheel (`pip install .` works from outside the source tree);
  P2 CAS-grade kernel ops (matrix_solve, rational_limit, linear_ode, groebner_basis); the Five Core
  Theorems written into `THEOREM.md` at referee grade with local self-proving witnesses.
