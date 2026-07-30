# Readout Certification Standard

**Status:** normative project standard  
**Applies to:** exact kernels, numerical solvers, certified readouts, retained spectral, benchmarks, documentation, and formal-proof mappings

## 1. Purpose

A finite result can be trustworthy for several different reasons. This repository must never collapse those reasons into one word. Every public result must state:

1. the **source semantics** of the input record;
2. the **mathematical target**, when one is claimed;
3. the **evaluation arithmetic** actually used;
4. the **error or stability evidence** actually established;
5. the **decision rule**, when a discrete decision is returned; and
6. the **failure state** when the evidence is insufficient.

This standard makes those fields explicit and prevents observed numerical agreement from being promoted into a theorem.

## 2. Four distinct objects

### 2.1 Source record

A finite decimal token is represented as

\[
r=(n,k),\qquad \operatorname{val}(r)=n10^{-k}\in\mathbb Q.
\]

The token `0.350` therefore denotes the exact rational value \(350/1000=7/20\), while retaining scale metadata \(k=3\). Scale metadata is not automatically a statement of measurement uncertainty.

### 2.2 Target

A target is a separately named mathematical object \(T(x)\): an exact rational expression, a series value under stated hypotheses, an integral under stated regularity assumptions, an eigenvalue of a declared finite operator, or another explicitly defined quantity.

### 2.3 Computed readout

The algorithm returns a finite value \(q\). The representation of \(q\) may be exact rational, arbitrary precision, binary floating point, decimal floating point, an interval, or a multiword expansion. The representation must be disclosed.

### 2.4 Evidence object

Evidence is not the value itself. It is one of:

- a proof-backed enclosure \(T(x)\in[L,U]\);
- an exact equality proof;
- a finite stability observation;
- an empirical comparison;
- a formal proof reference; or
- no sufficient evidence, reported as `HOLD`.

## 3. Status vocabulary

| Status | Meaning | Permitted claim |
|---|---|---|
| `CERTIFIED` | A named target is enclosed by a proved bound under named hypotheses. Arithmetic error used by the implementation is included or eliminated. | `target ∈ [q-B,q+B]` |
| `STABLE` | A finite refinement sequence passed a disclosed stability test. Continuation of the observed asymptotic model is not proved. | `observed refinements are stable under this test` |
| `HOLD` | A hypothesis, enclosure, resource budget, or admissibility condition is absent. | no numerical conclusion |
| `exact` tier | A finite \(\mathbb Z/\mathbb Q\) computation has no rounding in its result. | exact relative to the declared source values |
| `Th_coqc` tier | The named mathematical statement has a checked proof mapping. | only the mapped theorem, not adjacent implementation claims |
| `finite_diagnostic` tier | A finite computation agrees with a comparator or tolerance test. | reproducible finite agreement, not target proof |
| `Dr` tier | Design or interpretation. | conceptual proposal only |
| `+ℝ-Open` tier | The continuum-level statement is deliberately unresolved. | no closure claim |

`CERTIFIED` and `Th_coqc` are independent axes. A bound may be mathematically proved without the Python implementation being formally verified; a Coq theorem may govern an abstract law without proving every floating-point execution.

## 4. Exact source semantics

### Theorem 4.1 — exact rational evaluation

Let an expression tree have finite decimal readouts at its leaves and operations \(+,-,\times,\div\), with every division denominator nonzero. If every internal node is evaluated using arbitrary-precision integers and rational pairs, the returned value equals the mathematical value of that expression in \(\mathbb Q\).

This theorem removes representation and arithmetic rounding relative to the declared source record. It does not remove measurement, model, discretization, or specification uncertainty.

### API rule

For exact decimal semantics, callers should pass strings such as `"0.35"`, not a previously rounded binary float. Passing a Python float means the exact dyadic float value is the source record.

## 5. Decision certification

Let a scalar target \(Q\) be known to satisfy

\[
Q\in[\widehat Q-E,\widehat Q+E],\qquad E\ge0,
\]

and let \(\tau\) be a threshold.

### Theorem 5.1 — operational threshold certificate

The enclosure certifies the threshold decision exactly when it does not intersect the threshold:

\[
[\widehat Q-E,\widehat Q+E]\cap\{\tau\}=\varnothing.
\]

Equivalently,

\[
|\widehat Q-\tau|>E.
\]

If \(E=0\) and \(\widehat Q=\tau\), equality is certified. In every other intersecting case the correct result is `UNCERTIFIED`, not a guessed Boolean.

Failure of this certificate does not imply that floating point is wrong. It means the supplied enclosure cannot determine the decision.

## 6. Floating-point boundary

For a forward error bound \(E\le c_A\kappa uS\), a sufficient runtime certificate is

\[
c_A\kappa uS<|\widehat Q-\tau|.
\]

The familiar normalized expression \(c_A\kappa u<\delta\) is therefore a **certification condition**, not an iff characterization of actual correctness. When it fails, escalation may be needed; failure itself is not proof of an incorrect result.

A direct determinant evaluation can collide at every binary precision with sufficient exponent range. This establishes a limitation of that evaluation path, not an impossibility theorem for every algorithm built from fixed-size machine words. Multiword expansions, interval arithmetic, exact integer methods, and source-token inspection are distinct computational models.

## 7. Arithmetic-error rule

A truncation bound is not a target certificate unless arithmetic error is also handled. A routine may issue `CERTIFIED` only when at least one of the following holds:

1. every operation contributing to the returned value and bound is exact;
2. directed-rounding interval arithmetic encloses every operation;
3. an error-free or compensated transformation supplies a rigorous bound; or
4. a formally justified implementation theorem covers the execution path.

An asymptotic expression containing an unspecified \(O(u^2)\) term is explanatory, not a runtime certificate.

## 8. Stability is not target error

Observed contraction of refinement gaps can be valuable. It may reveal a plateau and guide adaptive computation. It does not, by finite observation alone, prove that the sequence converges to a named target or that the observed ratio persists forever.

Therefore:

- `richardson`, `integral`, and `integral_nd` return `STABLE` when they rely only on observed contraction;
- geometric series, exact-rational exponential Taylor sums, and exact-rational Simpson quadrature with a supplied fourth-derivative bound may return `CERTIFIED`;
- any missing hypothesis produces `HOLD`.

## 9. Measurement and conformity decisions

An exact decimal token is not exact knowledge of a physical measurand. Applications involving measurements should carry a separate acquisition object, for example:

\[
(\text{record},\;\text{calibration model},\;\text{uncertainty set},\;\text{coverage statement}).
\]

Acceptance intervals, tolerance intervals, guard bands, and producer/consumer risk belong to this measurement layer. They must not be inferred from decimal scale alone.

## 10. Required public result fields

Every new solver result should expose or document:

- `value`;
- `status`;
- `bound` and what it bounds;
- `target`;
- `hypotheses`;
- `arithmetic`;
- `method`;
- `decision`, if any;
- `reason` for `HOLD`;
- `tier`;
- `formal_witness`, if mapped; and
- `resource_ledger` when cost is claimed.

## 11. Recommended execution architecture

```text
source token
    -> exact parse / declared source semantics
    -> fast approximate path
    -> rigorous enclosure test
        -> decision certified: return
        -> unresolved: escalate
    -> interval / increased precision / expansion / exact rational or integer path
        -> decision certified: return
        -> resource or hypothesis failure: HOLD
```

This architecture preserves speed in comfortable-margin cases and correctness at decision boundaries without pretending that one arithmetic dominates every workload.

## 12. Literature boundary

The project does not claim priority for catastrophic cancellation, condition numbers, interval certification, exact geometric predicates, decimal arithmetic, or measurement decision rules. The contribution is the integration of source-record semantics, evidence tiers, fail-closed decisions, and readout-first interpretation into one executable framework.

Relevant foundations include IEEE 754 floating-point arithmetic, classical forward/backward error analysis, exact geometric computation, interval arithmetic, decimal floating point, and measurement-uncertainty guidance.
