The merged architecture document is complete. File: `/tmp/user/1000/claude-1000/-home-yaoharee-lt-ANSE-ASIA/8b2f7d4f-a9d2-454d-bf0c-68f2c732d997/scratchpad/IDM_SYMBOLIC_KERNEL_V2_MERGED.md`

Full content below, verbatim, as the deliverable.

---

# IDM Symbolic Kernel v2 — Merged Architecture (Phase 1)

**Chief-architect merge of six pillar specs** (P1.1 expression kernel, P1.2 assumption/domain
engine, P1.3 pattern matcher/rewrite engine, P1.4 polynomial/algebra domain tower, P1.5 conditional
solution objects, P1.6 exact/certified numeric tower) into one coherent Phase‑1 design for
`information-discrete-math`. Design only — no implementation beyond the Phase‑1 v0 skeleton in §6.
Grounded in the actual repo (`idm/symbolic.py`, `idm/solve.py`, `idm/exact.py`, `idm/interval.py`,
`idm/certified.py`, `idm/functions.py`, `idm/crypto.py`, `idm/analysis.py`, `idm/_bridge.py`) as read
directly by all six pillar authors, and in
`textbook/INFORMATION_DISCRETE_MATHEMATICS.md` / the `information-discrete-math` skill's
contaminated‑concept table (I1–I4 injected infinities, Z1–Z4 injected zeros).

Where the six pillars disagree, this document picks one answer and states why — see the
**Reconciliation Ledger** in §3. Nothing below claims parity with a general CAS ("equals
Mathematica"); IDM's edge is certificate‑first / ACCEPT‑HOLD / explicit tier / resource ledger /
exact→certified / no silent guessing, and every claim in this document is scoped to Phase 1 only.

---

## 1. Overview — the one‑kernel thesis

`idm/solve.py` today dispatches **258** `@kind`-decorated handlers through one clean registry
(`_REG`, `_ok`/`_norm`, a tier‑honesty pass that downgrades unbacked `Th_coqc` claims to `exact`,
`_COQ_BACKED`). What is *not* shared is everything **underneath** the registry: six independent
number/expression substrates exist today — `symbolic.py`'s tuple/`Fraction` tree, `exact.py`'s
bare‑`Fraction` arithmetic, `interval.py`'s `mp.iv` enclosures, `functions.py`'s locked‑namespace
numeric evaluator, `crypto.py`'s bare‑`int` modular arithmetic, and `analysis.py`'s iterative numeric
root/eigen code — each duplicating parsing, evaluation, and (worst) domain‑safety logic in its own
way. Six of the ~258 kinds (`symbolic_diff/simplify/expand/integrate/solve/series`) already share
one AST; the other ~252 do not, and none of the six today gate a domain‑unsafe identity
(`(x^a)^b → x^(ab)`, `sqrt(x²)→|x|`, `log(ab)→log a+log b`) on an assumption.

**The thesis of this v2 design is not "add a 259th kind that does more."** It is: collapse the
substrate underneath all 258 kinds onto **one shared kernel** — one expression tree, one assumption/
domain engine, one rewrite engine, one exact‑number tower with certified‑enclosure escalation, one
solution‑object contract, one polynomial/algebra tower — so that a kind handler's *body* becomes a
thin call into that kernel instead of hand‑rolled tree‑walking code, and so that domain‑unsafe
rewrites become **structurally impossible to add ungated** rather than merely "not yet added."

This is tier‑honest by construction, not by discipline alone:

- Every kernel object is a **finite, discrete, rational readout** — a `Fraction`-rooted tree, an
  exact integer/rational/algebraic value, or a directed‑rounding enclosure with an explicit
  precision tag. The continuum (ℝ‑completeness/I1, `h→0`/I2, `Re→∞`/I3, actual `+∞`/I4, the
  zero‑extent point/Z1) is never silently constructed: `Undefined`/`Infinity`/`ComplexInfinity` are
  explicit tagged leaves (`is_nonreadout=True`), a `Limit` node never auto‑evaluates, and
  `RealBall`/`ComplexBall` self‑disclose as finite‑precision (`name="R~40dps"`) rather than
  pretending to be "the reals."
- Every kernel result carries the same two independent axes the registry already uses:
  **status** ∈ `{ok, CERTIFIED, HOLD}` (reusing `idm.certified`'s `CERTIFIED`/`HOLD` string
  constants verbatim, plus `solve.py`'s existing `"ok"`), and **tier** ∈
  `{Th_coqc, exact, finite_diagnostic, +ℝ‑Open, Dr}`. No sixth pillar‑local status vocabulary
  survives the merge (see Reconciliation Ledger, item R5).
- **Phase 1 adds zero new kinds and zero new `_COQ_BACKED` entries.** The registry mechanism
  (`_REG`, `@kind`, `_norm`, `_ok`, `_readout`, the tier‑honesty pass) is untouched; only the
  *bodies* of the six existing `symbolic_*` handlers are re‑pointed from `SYM.*` calls to
  `kernel.*` calls, in the last step of Phase 1 (§5, §7).

---

## 2. Module layout

All six pillars proposed a different home for their piece (`idm/kernel/`, flat `idm/assumptions.py`,
flat `idm/kernel_solutions.py`, flat `idm/types.py`, `idm/poly/`). Scattering the "one shared kernel"
across five sibling top‑level modules undercuts the thesis, so this design puts **everything under
one new, additive, non‑breaking package**: `idm/kernel/`. Nothing existing is deleted, moved, or
edited except the six named `symbolic.py` call‑sites re‑pointed in the final Phase‑1 step.

```
idm/
├── symbolic.py        UNCHANGED — the legacy Fraction/tuple tree (Const|Var|Add|Mul|Pow|Func).
│                        Stays importable, deprecated‑not‑deleted, same posture as algebra.py.
│                        This is what the 6 symbolic_* kinds speak on the wire in Phase 1.
├── exact.py            UNCHANGED — leaf dependency: Fraction/int arithmetic, poly_*, matrix_*,
│                        rational_roots, tonelli_shanks, is_prime, mod_inverse, …
├── interval.py          UNCHANGED — leaf dependency: mp.iv enclosures, verified_range,
│                        certified_root, certified_min, gershgorin.
├── certified.py          UNCHANGED — leaf dependency: Readout, CERTIFIED, HOLD (reused verbatim
│                        as the kernel's own status vocabulary — not reimplemented, see §3 R5).
├── functions.py          UNCHANGED — leaf dependency: finite numeric primitives (exp/log/sin/…)
│                        that kernel.eval routes Func‑nodes through, closing symbolic.py:216‑218's
│                        bypass of the finite‑kernel discipline.
├── crypto.py, analysis.py   UNCHANGED — leaf dependencies for GF(p) ops / Durand–Kerker.
├── solve.py             UNCHANGED registry mechanism (_REG, @kind, _norm, _ok, _COQ_BACKED,
│                        tier‑honesty pass). ONLY the 6 symbolic_* handler BODIES are re‑pointed
│                        (last Phase‑1 step, §5/§7 item 21) to call kernel.* instead of SYM.*.
├── __init__.py           add `kernel` to the existing submodule re‑export list (same pattern
│                        every other idm/*.py already uses).
├── _bridge.py            UNCHANGED — kernel/ is a plain idm/-local package like symbolic.py, not a
│                        tools/-bridge import, so no new path wiring is needed.
└── kernel/               ★ NEW package — the one shared substrate. Nothing here is imported
    │                      by anything outside idm/kernel/ and the 6 re‑pointed handlers in Phase 1.
    ├── __init__.py        Public re‑export surface: `from idm import kernel as K`. §3.
    ├── tiers.py            Tier enum (5 values, FIXED to include Dr — see R2) + status
    │                      constants (CERTIFIED/HOLD reused from certified.py, plus "ok").
    ├── nodes.py             Expr dataclass hierarchy — the NEW kernel tree (P1.1 §a.1),
    │                      additive, not yet the wire format any kind speaks (§3 R1).
    ├── hashcons.py           structural hashing + request‑scoped interning (P1.1 §c.1).
    ├── numbers.py             the exact/certified number tower: ExactInteger, ExactRational,
    │                      AlgebraicNumber (ball‑based), ComplexExact, RealBall, ComplexBall,
    │                      coerce_up/coerce_down (P1.6 tower, canonical — see R6).
    ├── legacy.py               from_legacy / to_legacy: idm.symbolic tuple‑tree ⟷ kernel.nodes
    │                      Expr adapters (P1.1 §b, migration‑only).
    ├── assumptions.py           PredKind / Interval / Predicate / SymbolDomain / AssumptionSet /
    │                      closure / query / entails / safe_rewrite / resolve — the ONE
    │                      assumption/domain engine (P1.2, canonical — see R3).
    ├── engine.py                Pattern / Wildcard / Rule / RuleSet / Strategy / match /
    │                      rewrite / search_paths / apply_rule / Guard — the ONE rewrite
    │                      engine (P1.3, canonical — see R4), Guards call assumptions.py.
    ├── rewrite.py                 public spine: simplify / expand / diff / subst / integrate /
    │                      taylor / poly_coeffs / rewrite_safe — thin orchestration wired onto
    │                      engine.py's RuleSets (P1.1's public names, P1.3's bodies).
    ├── eval.py                     evaluate_exact / evaluate_certified / to_callable /
    │                      to_interval_callable (P1.1 signatures, P1.6 bodies — see R7).
    ├── solution.py                  Condition / Solution / ExceptionalCase / SolutionSet /
    │                      solve / solve_system / solve_inequality / solve_boolean /
    │                      solve_diophantine / solve_recurrence / verify (P1.5).
    └── poly/                        the polynomial/algebra domain tower (P1.4), orthogonal to
        ├── coeffring.py               the expression tree — renamed Domain→CoeffRing (R8):
        ├── univariate.py               QRing / ZRing / GFRing(p) / AlgebraicRing / RBallRing /
        ├── multivariate.py             CBallRing protocol implementations.
        ├── algebraic.py
        └── finite_field.py
```

**Naming fix carried from P1.1's original layout:** P1.1 named the tree module `expr.py` in its own
prose but `nodes.py` in its file listing; this document standardizes on `nodes.py` (matches the
dataclass‑hierarchy content described) and keeps `expr.py` out of the tree to avoid a dangling name.

---

## 3. Interface contracts

### 3.0 Reconciliation Ledger (conflicts named and resolved)

| # | Conflict | Pillars involved | Resolution | Why |
|---|---|---|---|---|
| **R1** | **Tree replacement vs. tree preservation.** P1.1 designs a brand‑new immutable dataclass `Expr` tree meant to *become* the shared substrate. P1.2, P1.3, P1.5, P1.6 all independently designed their layer to sit **on top of `idm/symbolic.py`'s existing `Union[Fraction, tuple]` tree**, explicitly refusing to touch it ("Expr = Union[Q, tuple] — the existing tree, UNCHANGED wire format", P1.3 §a; "not redefined, reused as‑is", P1.5 §a; "node: tuple \| Q — the existing idm.symbolic tree, unchanged shape", P1.6 §a). | P1.1 vs. {P1.2, P1.3, P1.5, P1.6} | **Phase 1 ships `kernel/nodes.py` as pure additive infrastructure** (it exists, is tested, is the *target* for Phase 2). But **the 6 `symbolic_*` kinds keep speaking `idm/symbolic.py`'s legacy tuple tree as their wire format through all of Phase 1.** `kernel/assumptions.py`, `kernel/engine.py`, and `kernel/solution.py` are all typed against the **legacy tree** (`Expr = Union[Fraction, tuple]`) per the 4‑pillar majority, using `kernel/legacy.py`'s `from_legacy`/`to_legacy` only when a bridge to the new tree is needed (e.g. `kernel/numbers.py`'s typed `Const.value`). Migrating the 6 kinds *onto* `nodes.py` itself is explicitly Phase‑2, named as such in §5/§7. | 4 of 5 tree‑touching pillars converged independently on "don't replace the tree in Phase 1" — that is strong, independent signal for a low‑risk Phase‑1 posture. Building `nodes.py` anyway (rather than dropping it) preserves the richer vocabulary (`Relation`, `Piecewise`, `Derivative`/`Integral`/`Sum`/`Limit` as first‑class nodes) that Phase 2 genuinely needs and that no other pillar supplies. |
| **R2** | **`Tier` enum missing a value.** P1.1's `Tier(str, Enum)` has only 4 members (`TH_COQC, EXACT, FINITE_DIAGNOSTIC, R_OPEN`) — **`Dr` is absent**, contradicting `solve.py`'s own 4‑tier‑plus‑Dr convention that every other pillar (P1.2, P1.3, P1.5, P1.6) correctly uses. | P1.1 alone (defect) | `kernel/tiers.py`'s `Tier` is fixed to 5 members: `TH_COQC="Th_coqc"`, `EXACT="exact"`, `FINITE_DIAGNOSTIC="finite_diagnostic"`, `R_OPEN="+R-Open"`, `DR="Dr"` — a `str, Enum` so `Tier.EXACT == "exact"` holds for direct comparison against `solve.py`'s existing plain‑string tier field. | Matches `solve.py`'s actual tier vocabulary (P1.2 §e, P1.3 §e, P1.5 §a, P1.6 header all cite the same 5‑value set); an enum missing a real tier is a silent under‑expressiveness bug, not a design choice. |
| **R3** | **Four parallel assumption/domain representations.** (i) P1.1's node‑level `Assumptions` (6 tri‑state bools) + `Domain` (conjunction of `Relation`s, `.entails()`); (ii) P1.2's full `idm/assumptions.py` pillar — `PredKind` (20‑kind closed vocabulary), `Interval`, `Predicate`, `SymbolDomain`, `AssumptionSet`, `closure()`/`query()`/`entails()`/`safe_rewrite()`/`resolve()`; (iii) P1.3's rewrite‑engine‑local `Assumptions` (flat `frozenset` of `(var,prop)` facts) + `Guard`/`domain_gate()`; (iv) P1.6's `DomainTag` (5‑predicate closed set: positive/nonzero/real/integer/unrestricted). | P1.1, P1.2, P1.3, P1.6 | **P1.2's engine is canonical**, relocated to `idm/kernel/assumptions.py`. It is the only one of the four that is a complete, monotone, capped, terminating closure system with its own risk analysis (P1.2 §f) and negative‑case test discipline. P1.1's node‑level `Assumptions`/`Domain` becomes a *thin per‑node cache* of `assumptions.query()` results, not a second inference engine. P1.3's `Assumptions`/`Guard`/`domain_gate(prop, on=var)` becomes a **factory that calls `assumptions.entails()`** — `Guard.check()`'s body is `return SAFE if ASM.entails(a, cond, var) else UNKNOWN` (fail‑closed default preserved). P1.6's `DomainTag` becomes a **convenience constructor** for a single `assumptions.Predicate` (e.g. `DomainTag(var, "positive")` ⇒ `ASM.predicate("positive", var)`) — its worked `(x^a)^b` HOLD example (P1.6 §e#5) becomes the canonical illustration of the *one* gate mechanism, not a fourth mechanism. | Four independently‑built predicate systems is exactly the "third parallel give‑up idiom" failure mode P1.2 §f.3 and P1.5 §f.3 both warn about, just for assumptions instead of verdicts. P1.2's version is the only one with a stated termination proof (monotone rules, bounded vocabulary, `O(\|PredKind\|×\|RULES\|)`), exact‑ℚ interval containment (never a numeric tolerance), and an explicit fail‑closed `UNKNOWN→HOLD` discipline — the strongest foundation to build the other three on top of. |
| **R4** | **Rewrite‑gating function named three different ways with three different signatures.** P1.1: `rewrite_safe(e, rule_name) -> Expr \| Piecewise`. P1.2: `safe_rewrite(rule_name, expr, symbol, a) -> Optional[ConditionedValue]`. P1.3: `apply_rule(rule, e, assumptions) -> Optional[Tuple[Expr,TraceStep]]` plus a full `Rule`/`RuleSet`/`Strategy`/`rewrite()`/`search_paths()` engine around it. | P1.1, P1.2, P1.3 | **P1.3's `Rule`/`RuleSet`/`engine.rewrite()`/`engine.apply_rule()`/`engine.search_paths()` is the canonical rewrite engine** (most complete: cost model, loop guard, trace, bottom‑up/top‑down/fixpoint/search strategies). `kernel/rewrite.py`'s public `rewrite_safe(e, rule_name, assumptions=...)` (the name kept from P1.1, since it is the more legible public‑API name) is a **one‑line wrapper**: `return engine.apply_rule(engine.get_ruleset("core").rules[rule_name], e, assumptions)`, and its `Guard` is built via R3's `domain_gate()`. P1.2's `safe_rewrite`/`ConditionedValue`/`Branch`/`resolve()` machinery is kept, but reclassified as **internal plumbing inside `assumptions.py` only** — it is how `assumptions.py` decides entailment for a *predicate*, not a second rewrite‑application path; nothing outside `assumptions.py` calls `ConditionedValue` directly. | One engine, one public gate function name. P1.3's design is the only one with a stated complexity analysis, loop‑detection, and a cost‑based multi‑path search (`search_paths`) — needed for anything beyond single‑rule application (e.g. picking the cheapest of factor/expand/cancel). |
| **R5** | **Result‑wrapper proliferation.** P1.2's `DomainVerdict`/`ConditionedValue`/`Branch` (assumption‑layer), P1.3's `RewriteResult` (rewrite‑layer, has `.trace`), P1.5's `SolutionSet`/`Solution`/`Verdict` enum (solve‑layer, has `.solutions`/`.exceptional`), P1.6's `Certificate` (numeric‑layer, has `.bound`). P1.5 §f.3 itself names the risk of this becoming a "third give‑up idiom" alongside `certified.Readout` and ad‑hoc `{"status":"HOLD",...}` dicts. | P1.2, P1.3, P1.5, P1.6 | **Not collapsed into one god‑object** — a rewrite result legitimately needs a `.trace`, a solve result legitimately needs `.solutions`/`.exceptional`, a numeric result legitimately needs `.bound`; forcing one shape would lose real information. Instead: **all four share the same two‑axis vocabulary from `kernel/tiers.py`** — `status` is always one of `certified.CERTIFIED` / `certified.HOLD` / the literal string `"ok"` (never a new word, never a new enum with different members); `tier` is always a `kernel.tiers.Tier` value (R2). Each result type additionally implements `.to_dict()`, producing exactly the shape `solve.py`'s existing `_ok()`/`_readout()` helpers already produce (`{"status":..., "tier":..., "value":..., "method":..., ...}`) — this is the ONE convergence point, not the object shape. `RewriteResult`, `SolutionSet`, `Certificate`, and `ConditionedValue`'s internal `resolve()` output are four *views*, one *vocabulary*. | This is what P1.5 §f.3 and P1.6 §e explicitly ask for ("Certificate.status/Certificate.tier are two independent axes, matching the existing repo convention... does not collapse them into one, and does not introduce a fourth status string") — generalizing their own stated fix from 2 pillars to all 4. |
| **R6** | **Three incompatible `AlgebraicNumber` definitions.** P1.1: `min_poly: tuple[Q,...]` + `lo,hi: Q` (exact rational isolating interval only — real roots, degree ≤ 2). P1.4: `AlgebraicNumberField` = `Q[x]/(min_poly)` as a **ring/field object** (not a single number), general base + degree. P1.6: `min_poly` + `interval: RealBall \| ComplexBall` + `index: int` (ball‑based, handles complex roots, has an explicit re‑isolation‑after‑precision‑escalation contract). Also: P1.1's plain `numbers.py` aliases `ZZ=int, QQ=Fraction` with **no wrapper** ("wrapping buys nothing"); P1.6 wraps everything (`ExactInteger`, `ExactRational`) in frozen dataclasses. | P1.1, P1.4, P1.6 | **P1.6's ball‑based `AlgebraicNumber` (with `index` and the re‑isolation contract) is canonical** — it is the only one of the three that handles complex roots and states what happens when two roots' balls overlap after escalation (P1.6 §f risk 2: HOLD, never guess an index). P1.1's simpler `(lo,hi): Q` real‑only representation is retained as the **degenerate case**: when `interval` happens to be an exact‑rational‑endpoint `RealBall` (the quadratic‑radical construction path both P1.1 and P1.4 name), it is still a `RealBall`, just one with `lo==hi` after simplification is not required — no separate type. P1.4's `AlgebraicNumberField` is **kept as a distinct, composing type** — it is a ring, not a number — and its `min_poly` is literally the same tuple an `AlgebraicNumber.min_poly` would carry, so `make_algebraic_field(root.min_poly)` constructs the field `root` generates. On the wrapper question: **P1.6's wrapped `ExactInteger`/`ExactRational` win** — see reasoning column. | Ball‑based is strictly more general (subsumes the exact‑rational‑endpoint case) and is the only one with a stated failure‑mode contract for the hardest real bug in this whole area (root disambiguation after precision escalation). On wrapping: Python's native `Fraction.__add__` silently promotes to `float` when the other operand is a `float` (`Fraction(1,3) + 0.5 == float`) — P1.1's "no wrapper" stance leaves exactly the silent‑float‑contamination door open that the mandate ("never silently turns exact into float") exists to close; P1.6's typed wrapper with `coerce_up`/`coerce_down` as the *only* rung‑crossing functions removes that door structurally. |
| **R7** | **Numeric‑bridge naming overlap, not a real conflict.** P1.1 names `evaluate`/`to_callable`/`to_interval_callable` as the target public signatures; P1.6 independently designs `evaluate_exact`/`evaluate_certified`/`to_callable` with concrete bodies (route every `Func` node through `idm.functions`'s finite primitives; split exact‑vs‑enclosure by whether every leaf is rational). | P1.1, P1.6 (converge, don't conflict) | `kernel/eval.py` keeps **P1.1's public names** (`evaluate`, `to_callable`, `to_interval_callable`) as thin dispatchers that route to **P1.6's split bodies** (`evaluate_exact` / `evaluate_certified` internally) based on whether the expression is leaf‑rational. `evaluate(e, env)` tries `evaluate_exact` first, falls back to `evaluate_certified` on the first non‑rational leaf, and never returns a bare `mp.mpf` — closing `symbolic.py:205‑218`'s existing silent‑float‑drop gap (both pillars name this exact line). | No decision needed — same design from two angles; recorded here only so the merge doesn't look like it missed the overlap. |
| **R8** | **`Domain` used for four different things.** P1.1: a finite conjunction of `Relation` constraints (assumption‑layer). P1.4: a `Protocol` for a coefficient ring/field (`QDomain`/`ZDomain`/`GFDomain`/`RDomain`/`CDomain`/`AlgebraicNumberField`). P1.5: an `Enum{C,R,Q_,Z}` — the ambient number system a `solve()` call is posed over. P1.6: an `Enum{Z,Q,ALGEBRAIC,REAL_BALL,COMPLEX_BALL}` tagging what a `Polynomial`/`Matrix`'s coefficients are drawn from (semantically the same idea as P1.4's protocol, expressed as a weaker enum). | P1.1, P1.4, P1.5, P1.6 | **Renamed to disambiguate, no type literally called `Domain` survives the merge:** (a) P1.1's assumption‑layer concept is absorbed into R3's `AssumptionSet`/`SymbolDomain` — the name `Domain` is dropped here entirely. (b) P1.4's ring/field protocol is renamed **`CoeffRing`**, living in `kernel/poly/coeffring.py`; P1.6's `Polynomial`/`Matrix` coefficient tag adopts `CoeffRing` directly instead of keeping its own weaker enum (P1.4's is strictly more general — it has `GFRing(p)` and `AlgebraicRing`, P1.6's enum does not). (c) P1.5's ambient‑number‑system enum is renamed **`AmbientDomain`**, scoped locally to `kernel/solution.py` since nothing else needs it. | Four unrelated concepts sharing one name is a real readability/maintenance hazard in a package whose entire thesis is "one shared kernel" — silently colliding names would undercut the merge's own goal. |
| **R9** | **Exception‑raising vs. return‑value API style.** P1.1's public spine (`simplify`/`expand`/`diff`/`integrate`/`solve_poly`) **raises** `HoldError`/`DomainUnsafeRewrite`/`ResourceBudgetExceeded` on refusal, relying on `solve.py`'s outer `except Exception` (`solve.py:806‑818`) to convert to HOLD. P1.4's `DomainMismatch`/`NotAField`/`NotYetImplemented` are `ValueError`/`NotImplementedError` subclasses, same reliance. P1.5 and P1.6 **never raise** for expected‑refusal cases — every public function wraps its body in `try/except` internally and **returns** a `SolutionSet`/`Certificate` with `status=HOLD`, explicitly so the function is "safe to call directly, not only through `_REG`" (P1.5 §e). | P1.1, P1.4 (raise) vs. P1.5, P1.6 (return) | **Return‑based wins as the public contract.** Every `kernel.*` public function returns a tier/status‑bearing result object (§R5) and **never raises** for an expected domain‑refusal, HOLD, or unsupported‑pattern case — only for genuine caller programming errors (malformed input, incompatible types passed to `CoeffRing` ops). `HoldError`/`DomainUnsafeRewrite`/`ResourceBudgetExceeded` are **demoted to control‑flow‑internal exceptions**: raised and caught *within* a single `kernel.*` function's own body, never propagated across the `idm.kernel` public boundary. | Return‑based composes correctly when one kernel function calls another (a `Certificate`‑returning `numbers.coerce_up` calling an exception‑raising `rewrite.simplify` internally would need its own try/except at every call site — return‑based avoids that entirely) and matches 2 of 3 overlapping design intents (P1.5, P1.6) plus is what makes functions "safe to call directly" as P1.5 states its own reason. `solve.py`'s outer `except Exception` is *still* a valid backstop for genuine bugs, but is no longer the mechanism by which an ordinary HOLD is produced. |

### 3.1 The stable spine — signatures every pillar and every kind handler may call

```python
# idm/kernel/__init__.py — the ONE import surface: `from idm import kernel as K`

# ---- tiers / status (kernel.tiers, re-exported) ----
Tier = K.tiers.Tier                       # Th_coqc | exact | finite_diagnostic | +R-Open | Dr  (R2)
CERTIFIED, HOLD, OK = "CERTIFIED", "HOLD", "ok"   # == idm.certified.CERTIFIED/HOLD + "ok" verbatim (R5)

# ---- legacy tree bridge (migration-only; nodes.py Expr <-> idm.symbolic tuple tree) ----
def from_legacy(tuple_tree) -> "nodes.Expr": ...
def to_legacy(e: "nodes.Expr"): ...             # raises on nodes with no legacy equivalent (Piecewise,
                                                  # Relation, Matrix, ...) — Phase 1 legacy tree has none
                                                  # of these, so this is a no-op boundary in Phase 1

# ---- exact/certified number tower (kernel.numbers) — R6, R9 ----
def coerce_up(x, target_rung: type, *, prec_dps: int = 30) -> "Certificate": ...   # never raises
def coerce_down(x, target_rung: type) -> "Certificate": ...                          # HOLD if inexact

# ---- assumption/domain engine (kernel.assumptions) — canonical, R3 ----
def parse_assumptions(spec) -> "AssumptionSet": ...
def closure(a: "AssumptionSet") -> "AssumptionSet": ...       # raises DomainContradiction (caller error)
def query(a: "AssumptionSet", symbol: str, pred: "Predicate") -> "DomainVerdict": ...
def entails(a: "AssumptionSet", condition, symbol: str) -> bool: ...

# ---- rewrite engine (kernel.engine + kernel.rewrite) — canonical, R4, operates on the LEGACY
#      tree in Phase 1 (R1): Expr = Union[Fraction, tuple] ----
def simplify(e, assumptions: "AssumptionSet" = EMPTY) -> "RewriteResult": ...      # R9: returns, never raises
def expand(e, *, max_terms: int = 10_000, assumptions=EMPTY) -> "RewriteResult": ...
def diff(e, var: str, order: int = 1) -> "RewriteResult": ...
def integrate(e, var: str, lower=None, upper=None, assumptions=EMPTY) -> "RewriteResult": ...
def taylor(e, var: str, x0, n: int) -> "RewriteResult": ...
def poly_coeffs(e, var: str) -> "RewriteResult": ...
def rewrite_safe(e, rule_name: str, assumptions: "AssumptionSet" = EMPTY) -> "RewriteResult": ...  # R4

# ---- numeric bridge (kernel.eval) — R7 ----
def evaluate(e, env: dict) -> "Certificate": ...           # tries evaluate_exact, falls back certified
def to_callable(e, vars: tuple) -> "Callable": ...
def to_interval_callable(e, vars: tuple) -> "Callable": ...

# ---- solution objects (kernel.solution) — canonical, R5, R8 ----
def solve(equation, var: str, *, domain: "AmbientDomain" = AmbientDomain.C,
          assume: "AssumptionSet" = EMPTY) -> "SolutionSet": ...
def solve_system(equations, variables, *, domain=AmbientDomain.C) -> "SolutionSet": ...
def solve_inequality(expr, var, op, *, domain=AmbientDomain.R) -> "SolutionSet": ...
def solve_diophantine(equation, variables, *, form="linear") -> "SolutionSet": ...
def solve_recurrence(coeffs, initial, *, var="n") -> "SolutionSet": ...
def verify(sset: "SolutionSet", equation, *, var: str = None) -> "SolutionSet": ...
def to_dict(sset) -> dict: ...                              # THE seam solve.py handlers call (R5)

# ---- polynomial / algebra tower (kernel.poly) — R8, orthogonal ----
# idm.kernel.poly.{coeffring,univariate,multivariate,algebraic,finite_field} — see §2 tree; Layer-1
# adapters (exact.py's poly_add/poly_mul/... signatures unchanged) live in exact.py itself as
# one-line wrappers, per P1.4 §b.
```

**Contract with `solve.py` (unchanged mechanism, all six pillars agree):** every `kernel.*` public
function returns a status/tier‑bearing result (R5, R9) with a `.to_dict()` that matches `_ok()`'s
existing shape. `solve.py:806‑818`'s outer `except Exception` remains a correctness backstop for
genuine bugs, but is no longer how an ordinary HOLD is produced (R9) — handlers call `.to_dict()`
directly.

---

## 4. Readout‑tier mapping

Every kernel call is one hop in a fixed pipeline: **parse → assumption‑gate → rewrite/solve/eval →
serialize**. Tier and status are threaded through every hop, never inferred after the fact.

```
 raw problem dict                         idm.solve.py kind handler
      │  p["expr"], p.get("assume", [])
      ▼
 kernel.legacy / idm.symbolic.parse ──────► legacy tuple tree (Fraction-rooted, tier=exact
      │                                      by construction — Const wraps Fraction, never float)
      ▼
 kernel.assumptions.parse_assumptions ────► AssumptionSet (caller-declared facts)
      │  + kernel.assumptions.closure()       raises DomainContradiction on caller error (fail LOUD,
      │                                       not silently — this is a caller bug, not uncertainty)
      ▼
 kernel.engine / kernel.rewrite ──────────► for each domain-sensitive identity:
      │                                       kernel.assumptions.query() → TRUE / FALSE / UNKNOWN
      │                                         TRUE    → rewrite fires, tier stays "exact"
      │                                         FALSE   → rewrite refused, HOLD status, tier "exact"
      │                                                    (we KNOW it's unsafe — that's still exact
      │                                                    knowledge, not diagnostic uncertainty)
      │                                         UNKNOWN → rewrite refused, HOLD status, tier "exact"
      │                                                    reason="cannot determine <predicate> for
      │                                                    <symbol> under the given assumptions"
      ▼
 kernel.eval (evaluate_exact / evaluate_certified) or kernel.solution.solve
      │   all-leaf-rational?  ── yes ──► ExactRational/ExactInteger/AlgebraicNumber(exact rung)
      │                                    status="ok", tier="exact"
      │   any leaf needs enclosure? ──► RealBall/ComplexBall via kernel.numbers.coerce_up
      │                                    status="ok" or "CERTIFIED" (if backed by interval.py's
      │                                    proven bisection/subdivision), tier="finite_diagnostic"
      │                                    (or "Th_coqc" ONLY if the specific enclosure algorithm has
      │                                    a formal/ theorem AND is in _COQ_BACKED — none do in
      │                                    Phase 1, see §5)
      │   precision ceiling hit? ──────► status="HOLD", tier="finite_diagnostic",
      │                                    reason="precision ceiling reached without convergence"
      │   Limit / unbounded Sum node? ─► NEVER auto-evaluated (I2/I3 guard). status="HOLD" unless a
      │                                    certified.richardson/geom_series bridge closes it exactly
      │                                    as today's geometric_series kind already does (Th_coqc-
      │                                    eligible ONLY through that named, existing bridge)
      ▼
 .to_dict()  ──────────────────────────────► {"status": ok|CERTIFIED|HOLD, "tier": ..., "value": ...,
                                                "method": ..., "reason": ... (on HOLD)}
      ▼
 idm.solve.py's _ok()/_readout() shape, unchanged ─► existing tier-honesty pass (solve.py:816-822)
                                                        still has final say: any tier="Th_coqc" not
                                                        backed by _COQ_BACKED is downgraded to "exact"
                                                        — Phase 1 adds ZERO new _COQ_BACKED entries.
```

**Non‑readouts refused at named points, matching the skill's I1–I4/Z1–Z4 table:**

| Non‑readout | Where the kernel refuses it |
|---|---|
| I1 (ℝ‑completeness) | `AlgebraicNumber`/exact `ExactRational` only; an irrational value stays a finite tree (`Func("sqrt", Const(2))`) or a tagged ball with an explicit precision — never "the real number √2." |
| I2 (`h→0`) | `Limit` nodes never auto‑evaluate; `escalate_precision` doubles `mp.dps` a *bounded* number of times toward a caller‑supplied target width, never an unbounded `h→0` loop. |
| I3 (`Re→∞`/unbounded search) | `LoopGuardConfig` (`max_steps`/`max_passes`/`seen_cap`) is a hard, non‑optional argument on every `rewrite()`/`search_paths()` call (R4); `GBBudget` is likewise mandatory on the (Phase‑2‑bodied) Gröbner interface (R8/poly tower). |
| I4 (actual `+∞`) | `Infinity(sign)`/`ComplexInfinity()` are explicit tagged leaves (`is_nonreadout=True`), never a bare `float('inf')`; `Interval(lo=None, hi=None)` means "no bound asserted," never a numeric `+∞` sentinel compared against. |
| Z1 (the point) | Out of this kernel's scope (geometry pillar) — noted for interface consistency only. |

---

## 5. 258‑kind migration order

**Hard invariant for all of Phase 1: zero new kinds are registered, zero new `_COQ_BACKED` entries
are added, and the `@kind`/`_REG`/`_norm`/`_ok`/tier‑honesty‑pass mechanism in `idm/solve.py` is not
edited.** Migration only ever re‑points a handler *body*; the registry keeps working throughout
because every intermediate state still returns the exact `_ok()`‑shaped dict `solve()`'s dispatcher
already expects — this is enforced by requiring every `kernel.*` result's `.to_dict()` to match that
shape (§3 R5) from the very first commit, not as a late integration step.

**Scope: only the 6 `symbolic_*` kinds move in Phase 1** (`symbolic_diff`, `symbolic_simplify`,
`symbolic_expand`, `symbolic_integrate`, `symbolic_solve`, `symbolic_series`, at `idm/solve.py:532‑552`)
— every one of the six pillars independently converged on this exact scope boundary (P1.2 §d: "zero
of the other 252 non‑symbolic_* kinds are touched"; P1.3 §g: "proves the pattern on the 6 symbolic_*
CAS kinds only"; P1.4's poly work stays inside `exact.py`'s existing call sites; P1.5 §d: only the
symbolic/linear‑algebra/diophantine kinds already backed by an AST; P1.6 §d: only `symbolic.evaluate`
changes behavior, confirmed zero‑blast‑radius by grep). This is not six independent guesses — it is
the one part of the design every pillar agreed on without coordination, so it is treated as settled.

**Order (why this order — each wave only depends on waves already built):**

1. **`kernel/tiers.py`, `kernel/hashcons.py`, `kernel/nodes.py`, `kernel/numbers.py`** — zero
   dependencies on anything else in `kernel/`; these are pure new types. Moves first because every
   other module's signatures reference `Tier`/`Number`/`Expr`.
2. **`kernel/legacy.py`** (`from_legacy`/`to_legacy`) — depends only on (1) and the *existing*
   `idm/symbolic.py`. Moves second so every later module can be tested by round‑tripping real
   `symbolic.py` fixtures, catching representation gaps immediately rather than at integration time.
3. **`kernel/assumptions.py`** (R3 canonical engine) — depends only on (1); does not depend on the
   rewrite engine or the legacy bridge. Moves third because both the rewrite engine (4) and the
   solution objects (6) need a working `query()`/`entails()` before they can gate anything.
4. **`kernel/engine.py` + `kernel/rewrite.py`** (R4) — depends on (1) and (3) for `Guard`. The
   *first* domain‑gated identity shipped is `(x^a)^b → x^(ab)` (P1.1's `symbolic.py:117`
   unconditional‑collapse gap, independently flagged by P1.2, P1.3, and P1.6 as the concrete,
   already‑live bug this whole pillar exists to close) — moves first among rules because it is the
   named ground‑map defect, not a green‑field addition.
5. **`kernel/eval.py`** (R7) — depends on (1) and `idm/functions.py` (existing leaf dependency).
   Independent of (4); can be built in parallel with wave 4 by a different implementer.
6. **`kernel/solution.py`** (P1.5) — depends on (1), (3), (4)'s `simplify`/`subst`, and (5)'s
   `evaluate` (for the residual/Vieta completeness check, P1.5 §c.3). Moves after 3–5 because it
   composes all of them.
7. **`kernel/poly/`** (P1.4) — depends only on (1); genuinely orthogonal to 2–6 (it wraps `exact.py`'s
   polynomial functions, not the expression tree), so it can run **in parallel with waves 2–6**, not
   strictly after them. Listed here, not first, only because it is the lowest‑priority wave for the
   *specific* 6‑kind Phase‑1 target (none of the 6 `symbolic_*` kinds need GF(p)/Gröbner machinery
   yet) — see §7 for the explicit "can run in parallel" annotation.
8. **Re‑point the 6 `symbolic_*` handler bodies** in `idm/solve.py:532‑552` from `SYM.*` calls to
   `kernel.*` calls — the ONE edit to an existing file in all of Phase 1. Moves last because it is
   the integration point that depends on everything above; `@kind(...)` decorator arguments (name,
   declared tier) are byte‑identical before and after, so no other kind's dispatch is affected.
9. **One full‑arc audit** (`ci_attempts_audit.py`/`formal/verify.sh` equivalent), run exactly once,
   immediately before the Phase‑1 commit — per this workspace's standing "no repeated full‑arc
   audits" rule. Every wave 1–8 step is instead checked with a single‑file compile +
   `Print Assumptions`/pytest‑module‑scoped test (§7), never a repo‑wide re‑run mid‑iteration.

The registry "keeps working during migration" precisely because steps 1–7 touch **zero existing
files** (pure package addition) and step 8 changes only function *bodies* under names `_REG` already
knows — at every commit in between, `python -c "from idm import solve; solve.solve({'kind':
'symbolic_diff', ...})"` returns the same shape it does today, whether or not `kernel/` exists yet.

---

## 6. v0 expression‑kernel skeleton

First buildable increment (waves 1–2 of §5 only: `tiers.py`, `hashcons.py`, `nodes.py`, `numbers.py`,
`legacy.py`'s signatures). No rewrite engine, no assumptions engine, no solution objects, no poly
tower bodies — those are separate, later increments (§7). Stubs only; no full bodies, per the
reconciliation decisions in §3 (R2 fixed `Tier`, R6 wrapped number tower, R9 return‑not‑raise at the
public boundary — note `HoldError` below is used **only internally**, never crosses a public
`kernel.*` function's return).

```python
# idm/kernel/tiers.py
"""Shared status/tier vocabulary — R2, R5. No pillar-local status word is ever introduced downstream;
every kernel.* result's .to_dict() emits exactly these values."""
from __future__ import annotations
from enum import Enum

from ..certified import CERTIFIED, HOLD   # reused verbatim, not redefined (R5)
OK = "ok"                                  # solve.py's existing plain-success string, reused verbatim

class Tier(str, Enum):
    TH_COQC = "Th_coqc"
    EXACT = "exact"
    FINITE_DIAGNOSTIC = "finite_diagnostic"
    R_OPEN = "+R-Open"
    DR = "Dr"                              # FIXED — absent from P1.1's original draft (R2)


class HoldError(Exception):
    """INTERNAL control-flow only (R9) — raised and caught within a single kernel.* function's own
    body; NEVER propagates across the idm.kernel public boundary. A public function that would
    otherwise let this escape must catch it and return a status=HOLD result instead."""
    reason: str

class DomainUnsafeRewrite(HoldError): ...
class ResourceBudgetExceeded(HoldError): ...
```

```python
# idm/kernel/hashcons.py
"""Structural hashing + request-scoped interning (P1.1 §c.1). Request-scoped, NOT process-global —
a long-running idm/server.py must not accumulate unbounded memory across requests (P1.1 risk 2)."""
from __future__ import annotations
from typing import Dict

def struct_hash(type_tag: str, children_hashes: tuple, leaf_payload) -> int:
    """Pure function: (type tag, children's already-computed structural hashes, leaf payload) -> int.
    Called bottom-up at node construction; O(1) given already-built children."""

def canonical_order_key(node) -> tuple:
    """(type_rank, structural_hash, ...) — O(1) comparator key for Add/Mul operand sorting.
    Replaces idm.symbolic._key's O(size) tostr()-based comparator (symbolic.py:176)."""

class InternTable:
    """Request-scoped (constructed per solve()/kernel call, discarded after — NOT a module-level
    singleton). Structurally-equal subtrees intern to the SAME object, so equality reduces to
    `is` post-interning. Bounded by the same LoopGuardConfig-style caps the rewrite engine uses;
    an InternTable is never shared across two unrelated top-level kernel calls."""
    _by_hash: Dict[int, object]

    def intern(self, node): ...            # returns node, or an existing structurally-equal node
```

```python
# idm/kernel/nodes.py
"""The NEW kernel expression tree (P1.1 §a.1). Additive in Phase 1 (R1) — not yet the wire format
any kind speaks; the 6 symbolic_* kinds keep using idm.symbolic's legacy tuple tree through all of
Phase 1. This module exists so Phase 2 has a real, tested target to migrate onto."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional
from .tiers import Tier
from .numbers import Number    # ExactInteger | ExactRational | AlgebraicNumber | ComplexExact (R6)

class Expr:
    """Abstract base. Every concrete node is frozen + slots; __post_init__ (via object.__setattr__,
    since frozen) fills _hash (hashcons.struct_hash) and _order (hashcons.canonical_order_key),
    both computed bottom-up so construction cost is O(1) given already-built children."""
    __slots__ = ()
    _hash: int
    _order: tuple
    is_nonreadout: bool = False   # True on Undefined / Infinity / ComplexInfinity ONLY (§4 table)

    def __hash__(self): ...
    def __eq__(self, other): ...  # `self is other` after interning, else type+hash+structural compare

@dataclass(frozen=True, slots=True)
class Const(Expr):
    value: Number                 # ExactInteger | ExactRational | AlgebraicNumber | ComplexExact —
                                    # NEVER a bare Python float (R6); see kernel/numbers.py

@dataclass(frozen=True, slots=True)
class Symbol(Expr):
    name: str

# ---- explicit non-readout leaves — never produced silently (§4) ----
@dataclass(frozen=True, slots=True)
class Undefined(Expr):
    reason: str
    is_nonreadout: bool = True

@dataclass(frozen=True, slots=True)
class Infinity(Expr):
    sign: int                     # a SYMBOLIC placeholder for a limit's direction of approach,
    is_nonreadout: bool = True     # never a numeric value (I3/I4)

@dataclass(frozen=True, slots=True)
class ComplexInfinity(Expr):
    is_nonreadout: bool = True

# ---- algebraic structure ----
@dataclass(frozen=True, slots=True)
class Add(Expr):
    args: Tuple[Expr, ...]        # canonically sorted via hashcons.canonical_order_key, n-ary

@dataclass(frozen=True, slots=True)
class Mul(Expr):
    args: Tuple[Expr, ...]

@dataclass(frozen=True, slots=True)
class Pow(Expr):
    base: Expr
    exp: Expr

@dataclass(frozen=True, slots=True)
class Func(Expr):
    name: str                     # open registry (not idm.symbolic's closed FUNCS set) — a new
    args: Tuple[Expr, ...]         # special function registers without editing this module

# ---- relations / logic (net-new vs. idm.symbolic) ----
@dataclass(frozen=True, slots=True)
class Relation(Expr):
    op: str                        # "==" | "!=" | "<" | "<=" | ">" | ">="
    lhs: Expr
    rhs: Expr

# ---- the domain-safety escape valve (net-new) — NOT constructed by any Phase-1 rewrite path (§3 R4
#      resolution: Phase 1 ships HOLD-only; Piecewise stays a defined-but-unused node until Phase 2) ----
@dataclass(frozen=True, slots=True)
class Piecewise(Expr):
    branches: Tuple[Tuple[Expr, Expr], ...]     # (value_expr, condition_expr), first true wins
    otherwise: Optional[Expr] = None             # None outside every branch => Undefined(...), NEVER 0

# ---- calculus as nodes (net-new; representable, not auto-evaluating — see §4 Limit row) ----
@dataclass(frozen=True, slots=True)
class Derivative(Expr):
    expr: Expr; var: Symbol; order: int = 1

@dataclass(frozen=True, slots=True)
class Integral(Expr):
    expr: Expr; var: Symbol
    lower: Optional[Expr] = None
    upper: Optional[Expr] = None

@dataclass(frozen=True, slots=True)
class Limit(Expr):
    expr: Expr; var: Symbol; point: Expr; direction: str = "both"
    # NEVER auto-evaluated (I2). See kernel/eval.py's certified-bridge-or-HOLD contract, §4.
```

```python
# idm/kernel/numbers.py
"""The exact/certified number tower (P1.6, canonical per R6). Strict ladder: NO type auto-widens.
Every rung transition is the explicit coerce_up/coerce_down pair below — never a bare + or float()."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from typing import Optional, Union
from .tiers import Tier

@dataclass(frozen=True, slots=True)
class ExactInteger:
    value: int

@dataclass(frozen=True, slots=True)
class ExactRational:
    value: Q
    # Coercion FROM ExactInteger is total/lossless; TO ExactInteger is partial (denominator==1 only)
    # and must go through coerce_down() — never silent (R6 reasoning: bare Fraction+float auto-widens).

@dataclass(frozen=True, slots=True)
class AlgebraicNumber:
    """Canonical per R6: ball-based (subsumes P1.1's simpler exact-rational-endpoint case), handles
    complex roots, carries an explicit re-isolation contract for precision escalation."""
    min_poly: tuple                # Fraction coeffs, low->high
    interval: "RealBall | ComplexBall"   # isolating enclosure containing exactly one root
    index: int                     # index into the sorted-by-ball-center root list AT THIS PRECISION;
                                     # escalate_precision must HOLD, never guess, if re-isolation finds
                                     # overlapping balls (P1.6 §f risk 2)

@dataclass(frozen=True, slots=True)
class ComplexExact:
    """Exact complex number over ExactRational-or-AlgebraicNumber components (P1.1's rung, kept
    distinct from ComplexBall: this rung is EXACT, ComplexBall is a finite-precision ENCLOSURE)."""
    re: Union[ExactRational, AlgebraicNumber]
    im: Union[ExactRational, AlgebraicNumber]

@dataclass(frozen=True, slots=True)
class RealBall:
    lo: "mpmath.mpf"; hi: "mpmath.mpf"      # directed-rounding DOWN / UP
    prec_dps: int
    name: str = "R~"                          # self-disclosing non-exactness — never "the reals"

@dataclass(frozen=True, slots=True)
class ComplexBall:
    re: RealBall; im: RealBall
    prec_dps: int

Number = Union[ExactInteger, ExactRational, AlgebraicNumber, ComplexExact]

@dataclass(frozen=True)
class Certificate:
    """The numeric-layer view of the R5 shared result vocabulary."""
    value: Optional[Union[ExactInteger, ExactRational, AlgebraicNumber, ComplexExact, RealBall, ComplexBall]]
    status: str            # "ok" | CERTIFIED | HOLD  — from .tiers, never a new word
    tier: Tier
    bound: Optional["mpmath.mpf"] = None
    reason: Optional[str] = None

    def to_dict(self) -> dict: ...   # matches solve.py's _ok()/_readout() shape (R5)

def coerce_up(x, target_rung: type, *, prec_dps: int = 30) -> Certificate:
    """Z -> Q -> Algebraic -> RealBall -> ComplexBall. Never silent, never automatic — caller always
    names target_rung and (for ball targets) prec_dps. Tier of the result is downgraded honestly:
    exact input coerced to a ball comes back tier finite_diagnostic, NEVER exact (R9: returns,
    never raises, even on a nonsensical target_rung — that's a HOLD-status Certificate, not a crash)."""

def coerce_down(x, target_rung: type) -> Certificate:
    """RealBall -> Algebraic -> ExactRational -> ExactInteger, PARTIAL. Returns a HOLD-status
    Certificate (tier "exact", reason "not exactly representable at target rung") when the narrowing
    isn't exact — e.g. a ball whose width hasn't collapsed to a single rational."""
```

```python
# idm/kernel/legacy.py
"""Migration-only bridge: idm.symbolic's tuple/Fraction tree <-> kernel.nodes.Expr (R1). Used ONLY
where a kernel/ function needs the new tree; the 6 symbolic_* kinds do NOT round-trip through this
in Phase 1 — they keep speaking the legacy tree end to end (§5)."""
from __future__ import annotations

def from_legacy(tuple_tree) -> "nodes.Expr":
    """symbolic.py tuple tree -> kernel.nodes.Expr, for the node shapes idm.symbolic already has
    (Const|Symbol|Add|Mul|Pow|Func only in Phase 1 — Relation/Piecewise/Derivative/etc. have no
    legacy equivalent and are never produced by this function)."""

def to_legacy(e: "nodes.Expr"):
    """kernel.nodes.Expr -> symbolic.py tuple tree. Raises ValueError (a caller-error, R9's carve-out
    for genuine programming mistakes) on any node with no legacy equivalent (Piecewise, Relation,
    Matrix, Derivative, ...) — Phase 1 never calls this on such a node, so this path is untested-but-
    documented dead code until Phase 2 actually needs it."""
```

**Test that proves this increment (v0) is done:** for every existing `idm/symbolic.py` fixture tree
`t` used by `symbolic.py`'s current tests, `to_legacy(from_legacy(t)) == t` (round‑trip identity over
the Phase‑1 node subset); `Const(ExactRational(Q(1,3)))._hash == Const(ExactRational(Q(1,3)))._hash`
(structural hash stability); a fresh `InternTable` interns two independently‑built structurally‑equal
`Add` trees to the same object (`is`, not just `==`); `Tier("Dr")` round‑trips (R2 regression guard).

---

## 7. Implementation todolist (Phase 1, ordered, dependency‑aware)

Each item is buildable and testable in isolation; "single‑file check" means `python -m py_compile`
on the new file plus a scoped pytest module — **never** a full‑repo audit until item 22 (per the
workspace's standing "no repeated full‑arc audits" rule).

**Wave 0 — expression + number kernel (§6, no dependencies, ~pillar P1.1):**
1. `kernel/tiers.py` — `Tier` (5 values, R2‑fixed) + `HoldError`/`DomainUnsafeRewrite`/
   `ResourceBudgetExceeded`. **Test:** `set(Tier) == {"Th_coqc","exact","finite_diagnostic",
   "+R-Open","Dr"}` matches `solve.py`'s literal tier strings via a grep‑derived fixture list.
2. `kernel/hashcons.py` — `struct_hash`, `canonical_order_key`, `InternTable`. **Test:** two
   independently‑built structurally‑equal trees intern to the same object (`is`); hash stable
   across repeated calls.
3. `kernel/nodes.py` — `Const/Symbol/Add/Mul/Pow/Func/Undefined/Infinity/ComplexInfinity` (defer
   `Relation`/`Piecewise`/calculus nodes to item 9, once R4's rewrite engine needs `Piecewise` typed
   but unused). **Test:** construct small hand‑built trees, verify `__hash__`/`__eq__`/`_order` are
   stable and that `Undefined().is_nonreadout is True` while `Add(...).is_nonreadout is False`.
4. `kernel/numbers.py` — `ExactInteger/ExactRational/AlgebraicNumber/ComplexExact/RealBall/
   ComplexBall/Certificate/coerce_up/coerce_down` (bodies for `ExactInteger`↔`ExactRational` only;
   `AlgebraicNumber`/ball rungs are signature‑only stubs at this step). **Test:** round‑trip
   int↔`Fraction` coercion; assert `coerce_up(ExactRational(...), RealBall, prec_dps=30).tier ==
   Tier.FINITE_DIAGNOSTIC` (never `Tier.EXACT` — the R6/R9 honesty guarantee, tested directly).
5. `kernel/legacy.py` — `from_legacy`/`to_legacy` for the Phase‑1 node subset. **Test:**
   `to_legacy(from_legacy(t)) == t` for every fixture tree in `idm/symbolic.py`'s existing test
   module (single‑file scoped run, not a repo audit).

**Wave 1 — assumption/domain engine (§3 R3, depends on 1; ~pillar P1.2):**
6. `kernel/assumptions.py` — `PredKind`, `Interval` (exact‑ℚ, `lo=None`/`hi=None` = "no bound
   asserted," never a numeric `+∞`), `Predicate`, `SymbolDomain`, `AssumptionSet`, `closure()` with
   an initial ~6‑rule table (`EVEN⇒INTEGER`, `INTEGER⇒RATIONAL`, `RATIONAL⇒REAL`, `PRIME⇒POSITIVE`,
   `PRIME⇒INTEGER`, `POSITIVE⇒NONZERO`). **Test:** `closure(closure(a)) == closure(a)` (idempotence);
   asserting both `POSITIVE` and `NEGATIVE` on the same symbol raises `DomainContradiction`.
7. `query()`/`entails()`. **Test per rule** (P1.2's own mitigation, §f.1): the positive entailment
   case AND the "still `UNKNOWN` without the premise" negative case, for every rule in (6)'s table.
8. `domain_of_expr()` — implicit‑exclusion walk, `pow`/`log`/`sqrt` cases only (matches the three
   identities named in the mandate). **Test:** `domain_of_expr(parse("log(x)"))` yields a `POSITIVE`
   requirement on `x`; `domain_of_expr(parse("sqrt(x)"))` yields `NONNEG`.

**Wave 2 — rewrite engine (§3 R4, depends on 1, 6, 7; ~pillar P1.3):**
9. `kernel/nodes.py` gains `Piecewise` (typed, unused by any Phase‑1 rewrite path per R4's
   resolution). `kernel/engine.py` — `Pattern`/`Wildcard`/`match()`/`substitute()` over the **legacy**
   tree (R1). **Test:** a hand‑built `pow_pow_collapse` pattern matches `("pow",("pow","x",2),3)`.
10. `Guard`/`domain_gate(prop, on=var)` wired to `assumptions.entails()` (R3 resolution: this is a
    factory, not a second engine). **Test:** `domain_gate("integer", on="c").check()` returns `SAFE`
    only when the threaded `AssumptionSet` actually has that fact, else `UNKNOWN` — never guesses.
11. `RS_CORE_NORMALIZE` ruleset with exactly **one** rule: `pow_pow_collapse`, domain‑gated. `rewrite()`
    with `Strategy.FIXPOINT` + a non‑optional `LoopGuardConfig`. **Test:** `rewrite_safe` fires the
    collapse under `c: integer`; HOLDs at a domain‑violating sample point (regression test evaluating
    both sides numerically at that point via `kernel.eval`, per P1.3's risk‑1 mitigation) — this is
    the concrete, ground‑map‑named `symbolic.py:117` fix, tested as a fix.
12. Re‑point `idm/symbolic.py`'s `simplify()` pow‑case internally to call `rewrite_safe` when an
    `assumptions=` kwarg is supplied (optional, defaulted‑empty — **not** a change to `symbolic.py`'s
    public signature yet, this is prep for item 21). **Test:** `symbolic.simplify(e)` (no kwarg)
    is byte‑identical to today's output on the existing `symbolic.py` test fixtures.

**Wave 3 — numeric bridge (§3 R7, depends on 1, 4; ~pillar P1.6; can build in parallel with wave 2):**
13. `kernel/eval.py` — `ball_add`/`ball_mul`/`ball_apply` as thin wraps of `interval.py`'s `ieval`
    primitives; `AlgebraicNumber`/`RealBall` rungs in `numbers.py` get real bodies. **Test:**
    `ball_add` reproduces `interval.verified_range`'s bound on a known function/interval fixture.
14. `evaluate_exact()`/`evaluate_certified()`/`evaluate()` dispatcher, routing every `Func` node
    through `idm.functions`'s existing finite primitives (closing `symbolic.py:216‑218`'s bypass).
    **Test:** `evaluate_exact` on an all‑rational tree returns `ExactRational`, never a bare
    `mp.mpf`; `evaluate_certified` on `sin`/`exp` returns a `RealBall` tagged `finite_diagnostic`.

**Wave 4 — solution objects (depends on 1, 6, 11, 14; ~pillar P1.5):**
15. `kernel/solution.py` — `Solution`/`SolutionSet`/`ExceptionalCase`/`AmbientDomain` (R8‑renamed)
    + `solve()`'s degree‑1/2 branch, including the `ExceptionalCase` fix for a zero/symbolic leading
    coefficient (the concrete bug P1.5 §c.1 names in `symbolic.py`'s existing degree‑1 path).
    **Test:** `solve("a*x+b", "x")` with `a` unassumed now returns two `ExceptionalCase`s
    (`a≠0→x=−b/a`, `a=0∧b≠0→∅`) instead of silently falling through to an unevaluated `0**-1` node.
16. `verify()` — exact‑substitution path + the "never enumerate a parametric family" guard (P1.5
    §e's hardest readout‑first constraint). **Test:** calling `verify()` on a `Solution` with
    non‑empty `.params` and no symbolic‑identity path available raises/asserts rather than looping;
    a point solution collapses to an exact identity check.
17. Residual + exact‑Vieta completeness check on the polynomial‑root path (P1.5 §c.3, the concrete
    fix for `analysis.poly_roots`'s currently‑unenforced completeness claim). **Test:** a crafted
    cubic where a naive numeric root‑finder would under‑count sets `completeness="partial"` and is
    caught by the check, not silently reported as complete.

**Wave 5 — polynomial/algebra tower (§3 R8, depends only on 1 and 4; orthogonal — build in parallel
with waves 1–4; ~pillar P1.4):**
18. `kernel/poly/coeffring.py` — `CoeffRing` protocol + `QRing`/`ZRing`, wrapping `exact.py`'s
    existing `Fraction`/`int` ops as Layer‑1 adapters with **unchanged signatures**. **Test:**
    `exact.poly_add([1,2],[3,4]) == [4,6]` still holds post‑refactor (single‑file regression, per
    P1.4's own risk‑2 mitigation).
19. `kernel/poly/univariate.py` — `UPoly` + `add`/`mul`/`divmod_`/`gcd` (field case, `QRing`, first).
    **Test:** `gcd` over `QRing` matches `exact.poly_gcd`'s existing output on fixture polynomials.
20. `GFRing(p)` wrapping `crypto.py`/`exact.py`'s `modinv`/`tonelli_shanks`, prime‑only (`exact.is_prime`
    checked at construction). **Test:** `GFRing(7).inv(3) == exact.mod_inverse(3, 7)` exactly.

**Wave 6 — integration (depends on all of the above):**
21. Re‑point `idm/solve.py`'s `_sdiff`/`_ssimp`/`_sexp`/`_sint`/`_ssol`/`_sser` bodies
    (`solve.py:532‑552`) to call `kernel.*` then `.to_dict()`, instead of `SYM.*`. **Zero** change to
    `@kind(...)` decorator arguments, `_REG`, `_norm`, `_ok`, `_COQ_BACKED`, or the tier‑honesty pass.
    **Test:** the existing `symbolic_*` kind test suite passes byte‑identically on default
    (no‑assumptions) input; one **new** test per kind exercises an assumption‑bearing request and
    confirms the domain gate fires end‑to‑end (e.g. `symbolic_simplify` on `(x^2)^3` with
    `assume=["x:integer"]` collapses; without the assumption it does not, and returns `HOLD` with a
    named reason instead of silently guessing).
22. **One** full‑arc audit (`ci_attempts_audit.py` / `formal/verify.sh` equivalent), run exactly once,
    immediately before the Phase‑1 commit — the only repo‑wide check in this entire plan, per the
    workspace's standing workflow rule against repeated full‑arc audits during iteration.

**Explicitly deferred to Phase 2 (named, not silently dropped):** migrating the 6 kinds onto
`kernel/nodes.py`'s new tree (R1); retiring the three pre‑existing string‑`eval()` sites in
`functions.py`/`interval.py`/`solve.py` in favor of `kernel.to_callable` (R7); `Piecewise` actually
being *constructed* by a rewrite path instead of just typed (R4); Gröbner‑basis/elimination‑ideal
bodies and general ℤ[x] factorization (poly tower, P1.4 §g); nonlinear systems beyond single‑variable
substitution and non‑constant‑coefficient recurrences (P1.5 §g); a fourth `_COQ_BACKED` entry for
`pow_pow_collapse`‑under‑positivity or `even⇒integer` (both named as the smallest realistic first Coq
targets, neither attempted here); migrating the other 252 (of 258) kinds onto any part of this kernel.

---

*Grounding: all current‑code line references above are inherited unmodified from the six pillar
documents, each of which was written against a direct read of `idm/symbolic.py`, `idm/solve.py`,
`idm/exact.py`, `idm/interval.py`, `idm/certified.py`, `idm/functions.py`, `idm/crypto.py`,
`idm/analysis.py`, `idm/_bridge.py`, and `textbook/INFORMATION_DISCRETE_MATHEMATICS.md`. This merge
document introduces no new claim about the current codebase's line numbers or behavior beyond what
those six documents already state; its only additions are the module‑layout unification (§2), the
Reconciliation Ledger (§3.0), the tier‑flow diagram (§4), the migration ordering rationale (§5), and
the v0 skeleton fixes (§6: R2's `Dr` fix, R6's ball‑based `AlgebraicNumber`, R9's return‑not‑raise
public boundary).*