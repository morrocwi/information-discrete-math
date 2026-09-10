# Universal Semantic Capacity after the Readout Universe correction

**Status:** research theorem target / no-go audit.  
**Claim boundary:** this file does **not** prove a superlinear or superpolynomial lower bound for unrestricted Boolean circuits, `SAT notin P/poly`, or `P != NP`.

This note starts from the Readout Universe / Readout Genesis translation and asks what a valid analogue of the Navier--Stokes quantitative certificate can mean for an unrestricted Boolean circuit.

## 1. The crucial model correction: free fanout is not tape access

A standard Boolean circuit is a static DAG.  An input wire or a previously generated gate output may feed many later gates.  Fanout/rereading of a wire is not charged as a new Boolean gate.

Therefore an unrestricted circuit lower bound may **not** charge a computation merely because a semantic distinction is used again later.  The Readout-Universe distinction between global tape and currently accessible record remains useful for sequential machines, but a circuit-size argument must respect the circuit model's free reuse of existing wires.

This kills the naive rule

```text
future re-entry of a distinction -> pay a new memory/re-access gate.
```

The correct circuit-native object is **semantic generation**.

## 2. Circuit-native translation: a generated semantic algebra

For `n` Boolean inputs, begin with the input projections and optional basis constants:

\[
\mathcal G_0=\{x_1,\ldots,x_n,0,1\}.
\]

For a fixed finite basis `B` (for example DeMorgan), one gate chooses previously generated functions `g,h` and a basis operation `b` and generates one new extensional Boolean function

\[
f_{t+1}=b(g,h),
\qquad
\mathcal G_{t+1}=\mathcal G_t\cup\{f_{t+1}\}.
\]

Unary gates are the obvious one-input specialization.  Sharing is automatic: an element of `G_t` may be used any number of times later at no generation cost.

A size-`s` circuit is therefore a length-`s` semantic-generation ledger whose terminal generated set contains the target function.

This is the circuit-native Readout-Genesis reading of `RD2 generation + retained role identity`: each gate creates one new reader-role from already generated roles; it does not consume its parents.

## 3. Why a static reader quotient still cannot be the missing capacity theorem

Let `Q(f)` be any reader-relative quotient of the **input set** of an `n`-bit Boolean function.  Since the source has only `2^n` inputs,

\[
|Q(f)|\le 2^n,
\qquad
\log_2 |Q(f)|\le n.
\]

Likewise the family of all partial assignments has size `3^n`, so a residual-function profile under all restrictions has

\[
R(f)\le 3^n,
\qquad
\log_2 R(f)\le n\log_2 3.
\]

Thus a pure static information/cardinality charge over source states cannot by itself yield a superpolynomial gate lower bound.  This is the same information ceiling already exposed by Declaration Bound, now stated for the circuit-native setting.

The Equality negative control is stronger: an intermediate cut can have exponentially many distinct residual functions while the whole function has a linear-size shared circuit.  Hence even a large reader-relative chart is not a gate count.

## 4. The correct object must be trajectory/prefix dependent

A candidate lower-bound certificate must depend on the **generated prefix** and the target:

\[
\mathfrak A_f(\mathcal G_t,\mathcal L_t),
\]

where `L_t` carries the actual generation lineage, not merely the extensional set if lineage is needed by the verifier.

The object should be interpreted as an **adversarial unresolved burden**: how much target-specific semantic work remains after exactly the functions generated so far are available for free reuse.

It must satisfy all of the following guards.

1. **Extensional role guard.** Renaming gates or changing provenance without changing generated Boolean functions cannot create hardness.
2. **Free-fanout guard.** Reusing any member of `G_t` is free.
3. **Sharing guard.** A generated function is charged once, not once per future use.
4. **No-target-leakage guard.** Construction/evaluation of the certificate may not call SAT, minimum circuit size, circuit equivalence against SAT, or insert the correct answer.
5. **Basis declaration.** The admissible gate basis is explicit; a lower bound transfers between bases only through an explicit constant-factor simulation theorem.
6. **Barrier audit.** Any efficiently recognizable large extensional property is audited for Natural-Proofs risk; purely black-box oracle-stable arguments are audited for relativization.

## 5. Universal Semantic Capacity theorem schema

Let a circuit prefix generate

\[
\mathcal G_0\subset\mathcal G_1\subset\cdots\subset\mathcal G_s,
\]

with one gate-generation per step, and let

\[
A_t=\mathfrak A_f(\mathcal G_t,\mathcal L_t)\in\mathbb N.
\]

A valid **Universal Semantic Capacity (USC)** certificate would prove:

### Initial demand

\[
A_0\ge D_n(f).
\]

### Completion

If `f in G_s`, then

\[
A_s=0.
\]

### Gate-local discharge bound

For every admissible gate appended to every valid prefix,

\[
A_t-A_{t+1}\le K_n(t,\mathcal G_t,\mathcal L_t).
\]

If a uniform bound `K_n` applies, telescoping gives

\[
D_n(f)\le sK_n,
\qquad
s\ge \frac{D_n(f)}{K_n}.
\]

This is not new arithmetic; `IDM_TransformPotential.v` already formalizes the telescoping kernel.  The missing theorem is the existence of a non-circular `A_f` for which SAT has a superpolynomial demand/capacity ratio.

## 6. The discrete analogue of the NS `q_N` step

The Navier--Stokes lane does not stop at rank.  It constructs an explicit chart and then a quantitative certificate controlling how the inverse behaves on that chart.

The circuit analogue should likewise not be a symbolic `q_C` attached to a static state.  The natural quantitative object is a **discharge ratio on a generated prefix**:

\[
\chi_t(g;f)
=
\frac{A_t-A_{t+1}}{c(g)},
\]

where `c(g)=1` for one ordinary gate.  A universal capacity theorem is a certified upper bound

\[
\chi_t(g;f)\le K_n
\]

for every allowed gate and every legal prefix.  This is the finite discrete role played by the quantitative NS inverse step: structural distinguishability is upgraded to a numeric statement that one legal transform cannot remove arbitrary target-specific burden for free.

We deliberately do **not** call this quantity `q_C<1`: unlike the NS chart, no normed inverse operator has yet been constructed.  Naming an operator-free scalar `q_C` would hide the open step.

## 7. Static-measure capacity audit

Before searching for `A_f`, every static candidate `M(f)` must be tested against one-gate composition.  The exact diagnostic `semantic_capacity_audit.py` enumerates every 3-input Boolean function and all pairs under the declared binary basis operations and records one-gate jumps for:

- residual-function count under all partial restrictions;
- `log2` residual count;
- GF(2) algebraic degree;
- GF(2) ANF support;
- truth-table support;
- sensitivity-edge count.

The purpose is **falsification**, not extrapolation.  Passing at `n=3` is not a theorem; a candidate with a large one-gate jump is immediately unsuitable as a constant-capacity potential without an additional normalization theorem.

For residual profiles there is also an exact analytic composition rule:

\[
R(b(f,g))\le R(f)R(g)
\]

for every pointwise binary Boolean operation `b`, because each restriction of `b(f,g)` is determined by the corresponding pair of restricted functions.  Consequently

\[
\log R(b(f,g))\le \log R(f)+\log R(g).
\]

But `log R(f)=O(n)` for every `n`-bit function, so this route has an intrinsic linear information ceiling and cannot be the desired superpolynomial SAT certificate.

## 8. What remains after this audit

The search space is now narrower.

The missing object cannot be merely:

- current working-memory size;
- number of future residual contexts;
- rank of a static reader map;
- entropy/cardinality of a quotient of `2^n` input states;
- a static function measure whose only justification is that it looks large on SAT;
- re-access count, because circuit fanout is free.

It must be an **adaptive, target-specific, prefix-dependent obstruction** whose local update is independently checkable and whose total discharge requires many semantic-generation steps even under unrestricted sharing.

This is close in spirit to the existing fusion / approximation / gate-elimination lanes already audited in this branch.  Readout Universe contributes a disciplined interpretation:

```text
reader role, not gate name
+ generated record, not ontological memory
+ explicit accessibility
+ no early collapse
+ no borrowed certainty
```

but the superpolynomial SAT instance remains OPEN.

## 9. Next executable target: Adaptive Semantic Generation Adversary (ASGA)

Define an adversary state

\[
\mathcal A_t=\operatorname{Update}(f,\mathcal G_t,\mathcal L_t)
\]

with an integer burden `W(A_t)` such that:

1. `A_0` is constructible from the explicit target family without solving circuit minimization;
2. adding a gate updates `A_t` from the previous state and the new gate only;
3. the checker verifies the update locally;
4. if the target has been generated, `W(A_t)=0`;
5. for the target SAT family, every gate reduces `W` by at most a certified capacity;
6. Equality, parity, and small circuits with heavy sharing are mandatory negative controls.

A successful ASGA with superpolynomial initial burden relative to one-gate discharge would be a genuine new circuit-lower-bound method.  At present this is the single load-bearing research target; it is not established by the current corpus.
