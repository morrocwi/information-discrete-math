# IDM Codebase Map — Current Symbolic/Computational Core (2026-07-27, branch `main`)

## 1. Expression representation today

**Two entirely separate, non-interoperating representations coexist:**

**(a) `idm/symbolic.py` — a real symbolic AST** (the only true tree in the repo):
```
idm/symbolic.py:8-15
    Fraction                      — a rational constant
    ('var', name)                 — a symbol
    ('add', [t, …])               — n-ary sum
    ('mul', [f, …])               — n-ary product
    ('pow', base, exp)            — power
    ('func', name, arg)           — sin/cos/tan/exp/log/sqrt
```
Built by `parse()` (`idm/symbolic.py:23-44`) from Python's `ast` module parsing a string via `ast.parse(s, mode="eval")`. Every constant becomes an exact `Fraction` (`idm/symbolic.py:28`), so the tree is finite-discrete-rational by construction — no float ever enters a symbolic node. Consumers: `diff`, `simplify`, `expand`, `evaluate`, `integrate` (indefinite), `poly_coeffs`, `solve` (algebraic, not the dispatcher), `taylor` — all in this one file (`idm/symbolic.py:71-307`).

**(b) Everything else in the solver — strings evaluated through a locked numeric namespace, never parsed to a tree.** `idm/functions.py:57-69` (`math_namespace()`/`evaluate()`) does `eval(compile(expr, ...), {"__builtins__": {}}, ns)` against a fixed dict of finite-readout functions (`exp/log/sin/cos/erf/gamma/sqrt/pi/e/abs/pow`). `idm/interval.py:21-25` (`ieval`) does the same trick but with `mp.iv` interval objects standing in for the finite ops. `idm/solve.py:55-59, 482-485` wrap these as `_fn`/`_fn2`/`_cfn`/`_fnv` closures. **There is no shared AST between the "exact CAS" (symbolic.py) and the numeric solver (functions.py/integrate.py/interval.py) — a `str` expression is the only thing that crosses that boundary**, and each side re-`eval`s it independently with its own namespace/semantics.

## 2. How `solve(problem)` dispatches — the registry mechanism

Single flat dict `_REG: dict[str, (fn, tier)]` (`idm/solve.py:27`), populated by decorator `@kind(name, tier="finite_diagnostic")` (`idm/solve.py:28-30`) applied ~258 times across the file (confirmed live: `len(idm.kinds())==258`). Each handler is a bare `def handler(p: dict) -> dict`; there is no shared base class, protocol, or type contract beyond "takes the problem dict, returns a dict with `kind`/`status`/`value`". Helper factories generate families of near-identical handlers, e.g. `_make_path` for the 6 tropical-semiring path kinds (`idm/solve.py:213-223`), `_spec` for ~26 special functions (`idm/solve.py:457-461`), `_hb`/`_hbo` for the ~26 Hilbert-space kinds (`idm/solve.py:729-778`).

Dispatch entry point `solve()` (`idm/solve.py:802-823`):
```python
if k not in _REG: return HOLD "unknown problem kind"
fn, tier = _REG[k]
try: res = fn(problem)
except KeyError as ex: HOLD "missing required field"
except Exception as ex: HOLD f"{type(ex).__name__}: {ex}"
res.setdefault("tier", tier)
if res["tier"] == "Th_coqc" and k not in _COQ_BACKED: res["tier"] = "exact"   # tier-honesty downgrade
```
So: (1) unknown kind → HOLD, never crash; (2) any exception inside a handler → HOLD, never crash; (3) a tier-honesty pass at the very end strips `Th_coqc` down to `exact` unless the kind has a named Coq theorem in `_COQ_BACKED` (`idm/solve.py:790-800`, currently 9 entries — geometry orientation, tropical semiring laws, Kirchhoff, geometric series). This is a **post-hoc string-keyed downgrade**, not something the handler itself enforces.

Value normalization is centralized in `_norm()` (`idm/solve.py:34-51`): `Fraction`→`{"exact":.., "float":..}`, `mp.mpf`→`{"digits":.., "float":..}`, everything else passes through or `str()`s. Two handler-return idioms: `_ok(kind, value, method, **extra)` for plain success, `_readout(kind, r, method)` for wrapping a `certified.Readout` (adds `bound`/`reason`).

## 3. Number types in play

| Type | Where used | Notes |
|---|---|---|
| `fractions.Fraction` (aliased `Q`) | `symbolic.py` tree constants; all of `exact.py` (number theory, exact linear algebra, polynomials); `stats.py`/`geometry.py` per solve.py comments | Exact, finite, no float ever produced |
| `mpmath.mpf` (arbitrary-precision decimal, `mp.mp.dps` set per-module: `series.py` dps=40, `integrate.py` dps=40, `interval.py` dps=30) | `functions.py` finite-kernel results; `integrate.py` DE quadrature; `series.py` Richardson/Taylor/Fourier | Finite-precision decimal, tolerance-bounded, tagged `finite_diagnostic` in solve.py unless wrapped in a `certified.Readout` |
| `mpmath.iv` interval type (directed-rounding enclosure `[lo,hi]`) | `interval.py` exclusively | Rigorous enclosures; the only place uncertainty is a first-class type rather than a bare number |
| Python `int`/`float` | scattered (e.g. `von_mangoldt` returns a raw Python `float` from `math.log`, `exact.py:418-421` — an explicit exception the module docstring doesn't call out) | — |
| `complex` / `mpmath.mpc` | `transforms.py` (FFT, Laplace, contour integrals), `integrate.py:residue_sum` | — |

`certified.Readout(value, bound, status, reason)` (`idm/certified.py:9-16`, re-exported from `tools/certified_readout.py` via `_bridge.py`) is the one place a value+error-bound+verdict is bundled as a single object before it reaches `solve.py`.

## 4. Assumption/domain system — confirmed absent

Grep across `symbolic.py`, `solve.py`, `interval.py` for `domain|assumption|Piecewise|branch` turns up **zero** matches for any assumption/domain/piecewise machinery (`idm/solve.py:232` "outside this readout's domain" is just an error-message string, not a domain object). Concretely:

- `symbolic.simplify()`'s `pow` case (`idm/symbolic.py:111-118`) does `("pow", b, ex)` → `simplify(("pow", b[1], b[2]*ex))` for nested powers **unconditionally** — this is the `(x^a)^b → x^(ab)` identity applied with no domain check at all (currently: since only integer/half-integer literal exponents ever appear via the`func:"sqrt"`desugaring and no `x**Q(1,2)` folding into `sqrt` back happens automatically, the live blast radius is small, but the code path itself has no gate).
- `symbolic.integrate()`/`_int_term` (`idm/symbolic.py:222-249`) picks antiderivatives (`log(v)` for `v**-1`, `exp/sin/cos` primitives) purely by pattern match, with no domain restriction attached to the returned expression (no branch cut, no `abs`, no `Piecewise`) — anything not matched raises `_Hold`, which is the *only* domain-safety mechanism present, and it's coarse (whole-term HOLD, not a partial/conditional result).
- `interval.py`'s rigorous bracketing (`enclose`/`verified_range`/`certified_root`/`certified_min`, `idm/interval.py:30-100`) is the closest thing to domain-safe reasoning in the repo, but it works by *numeric enclosure*, not by *symbolic* domain gating — it never touches `symbolic.py`'s tree, and `certified_root` explicitly checks for an unbounded enclosure to reject poles masquerading as sign changes (`idm/interval.py:66-78`), which is a bespoke one-off guard, not a general domain framework.
- `sqrt(x**2) → abs(x)`, `log(a*b) → log(a)+log(b)`, `(x**a)**b` splitting under assumptions: **none of these identities are implemented at all** in `symbolic.py` currently (no `log`/`sqrt` algebraic-identity rewriting exists in `simplify`/`expand` beyond the trivial `exp(0)→1`, `log(1)→0`, `sin(0)→0`, `cos(0)→1` special-casing at `idm/symbolic.py:104-110`). This is good news for the redesign — there is no unsafe identity to rip out, only a green field to gate correctly from the start.

**Conclusion: there is no assumption/domain kernel anywhere in the current codebase.** The gating that exists is ad hoc and per-module (HOLD-on-no-pattern-match in `symbolic.integrate`; enclosure-unboundedness check in `interval.certified_root`; the tier-honesty downgrade in `solve.py`), not a shared mechanism a new identity-rewrite could plug into.

## 5. Symbolic vs numeric module classification

| Module | Kind | Basis |
|---|---|---|
| `symbolic.py` | **Symbolic** (exact CAS) | Own AST, exact `Fraction` arithmetic, string↔tree parse/print |
| `exact.py` | **Symbolic-adjacent / exact-numeric** | No tree; operates on `Fraction`/`int`/coefficient-lists — the exact arithmetic substrate `symbolic.py` and `solve.py` both call into |
| `algebra.py` | **Numeric (exact-semiring)** | Thin re-export of `tools/aggregate.py`'s tropical-semiring Floyd–Warshall; operates on numeric matrices, no expression tree |
| `functions.py` | **Numeric** | Finite-kernel evaluation (`_kernel`), `eval()`-based string evaluator, no AST |
| `integrate.py` | **Numeric** | DE quadrature (tanh-sinh/exp-sinh/sinh-sinh) over `mp.mpf`, wraps `functions.py` callables |
| `series.py` | **Numeric** | Cauchy-FFT/finite-difference Taylor/Laurent/Fourier over `mp.mpf`/`mp.mpc`, calls `functions.py` |
| `interval.py` | **Numeric, rigorous** | `mp.iv` enclosures, its own tiny `eval()`-based interpreter (`ieval`), independent of `symbolic.py` |
| `certified.py` | **Contract layer** | Not symbolic or numeric per se — the `Readout` verdict wrapper both integrate.py and analysis.py populate |
| `solve.py` | **Dispatcher / registry** | Orchestrates all of the above; itself contains no math, only routing + normalization + tier bookkeeping |
| `parse.py` | **World-language translator** | Regex rule table → structured `{"kind": ...}` dict; feeds `solve()`, does not touch `symbolic.py`'s tree either |

## 6. Concrete seams for a new shared kernel

1. **`symbolic.parse()`/`tostr()`** (`idm/symbolic.py:23-24, 51-67`) is the only string↔tree boundary that exists — a new kernel object (with assumptions/domain tags) would replace this tree as the target of `parse`, and every symbolic solve-kind (`symbolic_diff`, `simplify`, `expand`, `symbolic_integrate`, `symbolic_solve`, `symbolic_series` — `idm/solve.py:532-552`) would need its call into `SYM.*` re-pointed at the new kernel's equivalent function.

2. **`functions.evaluate()`/`math_namespace()`** (`idm/functions.py:57-69`) is the seam where numeric string-eval happens; a shared kernel that can *both* be symbolically manipulated *and* numerically evaluated (finite readout) would let `solve.py`'s `_fn`/`_fn2`/`_seq` wrappers (`idm/solve.py:55-61`) call `kernel.evaluate(env)` instead of re-parsing the string through `eval()` — this is the seam that currently duplicates domain-unaware evaluation logic three times (`functions.py`, `interval.py:_NS`/`ieval`, `solve.py:_CNS`/`_cfn`).

3. **`solve.py`'s `_REG` decorator + tier system** (`idm/solve.py:27-30, 785-823`) is already the uniform place every kind's result tier is decided; a shared kernel's own certificate/status (e.g. `HOLD` for a domain-unsafe rewrite, or a `Piecewise` result) could be threaded through `_ok`/`_readout` without changing the registry mechanism itself — only handler bodies for `symbolic_*` kinds need to change what they call.

4. **`certified.Readout`** (`idm/certified.py:9-16`) is the existing verdict/bound contract (`CERTIFIED`/`HOLD` + bound) that a domain-aware symbolic rewrite should reuse rather than invent a third status vocabulary — `interval.py` already returns ad hoc `{"status": "HOLD", "reason": ...}` dicts instead of a `Readout`, so there are actually two parallel "give up honestly" idioms in the repo today (`Readout` object vs. raw dict with `status`/`reason` keys) that a shared kernel should probably unify.

5. **`_COQ_BACKED`** (`idm/solve.py:790-800`) is the seam for wiring new proof-governed identities: if a new kernel's `sqrt(x**2)→abs(x)`-under-assumption rewrite gets a Coq theorem in `formal/`, its kind name gets added here to earn `Th_coqc`; anything else defaults to `exact` per the existing tier-honesty pass — no change to that pass is needed, just new entries.

6. **`_bridge.py`** (`idm/_bridge.py`) is the path-wiring seam if a new kernel module lives outside `idm/` proper (e.g. in `tools/` or a new `formal/`-linked package) — same pattern as `certified.py`/`algebra.py`'s thin re-exports.

**Net assessment for the redesign**: the exact symbolic tree (`symbolic.py`) is small (~300 lines), self-contained, and already finite-rational by construction — the natural place to *become* the shared kernel rather than be replaced. Its two live domain gaps to close first are (a) the unconditional `(b^a)^c → b^(ac)` power-collapse in `simplify()` (`idm/symbolic.py:117`) and (b) the complete absence of `log`/`sqrt` product/power-splitting identities (currently unimplemented, so nothing to fix, but also nothing gating them if someone adds them later without assumptions). The numeric side (`functions.py`, `integrate.py`, `interval.py`) has no tree at all today and would need a `kernel.to_callable(env)`-style bridge to consume the new kernel's expressions instead of re-`eval`-ing strings.