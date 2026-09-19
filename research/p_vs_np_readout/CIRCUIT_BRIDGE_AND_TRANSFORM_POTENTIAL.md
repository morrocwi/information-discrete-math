# Circuit Bridge and Readout Transform Potential

**Status:** standard complexity bridge + IDM theorem schema + open SAT lower-bound target.  
**Claim boundary:** this document does **not** prove `P != NP` or `SAT notin P/poly`.

## 1. Replace the universal-machine bridge by a standard circuit bridge

A direct lower bound against every polynomial-time Turing machine is not necessary. The standard
simulation theorem gives

\[
\mathbf P\subseteq \mathbf{P}/\mathrm{poly}.
\]

Consequently,

\[
SAT\in\mathbf P
\Longrightarrow
\exists c\;\forall n:\ \operatorname{CircuitSize}(SAT_n)\le n^c.
\]

Therefore the stronger non-uniform statement

\[
\boxed{SAT\notin \mathbf{P}/\mathrm{poly}}
\]

would immediately imply

\[
\boxed{P\ne NP}.
\]

This is the preferred bridge for the readout programme because a Boolean circuit is already a finite
DAG of local transformations. It fits the IDM retained-lineage and RCP boundary language without
assuming that an arbitrary machine stores a special intervention-complete state.

## 2. Readout Transform Complexity (RTC)

For a declared computational model \(\mathcal M\), define

\[
RTC_{\mathcal M}(f)
=
\min\{\operatorname{cost}(C): C\in\mathcal M,\ C\text{ computes }f\}.
\]

For unrestricted bounded-fanin Boolean circuits, this is ordinary circuit size up to the precise gate
basis and encoding convention.

The terminal readout of SAT is only one bit. The research target is therefore not terminal information
size but the minimum local transform cost needed to construct that bit.

## 3. Gate-local transform-potential theorem schema

Let

\[
C_0,C_1,\ldots,C_s
\]

be a circuit construction trajectory, where one legal gate is added at each step. Let
\(\Phi(C_i)\in\mathbb N\) be a potential satisfying

\[
\Phi(C_{i+1})\le \Phi(C_i)+\Delta
\]

for every legal gate addition. If

\[
\Phi(C_0)=0,\qquad \Phi(C_s)\ge G,
\]

then finite telescoping gives

\[
\boxed{G\le s\Delta}.
\]

Hence

\[
\boxed{s\ge G/\Delta}.
\]

`formal/IDM_TransformPotential.v` records the finite arithmetic skeleton of this statement. The theorem
is elementary; the hard part is constructing a useful \(\Phi\).

## 4. What a P-vs-NP-capable potential must do

To prove `SAT notin P/poly` through this route, the potential family \(\Phi_n\) must satisfy all of:

1. **Explicitness.** It is mathematically defined for every partial circuit on \(n\)-bit inputs.
2. **Gate locality.** One allowed gate changes the potential by at most a controlled amount \(\Delta_n\).
3. **Large SAT target.** \(\Phi_n(SAT_n)/\Delta_n\) is superpolynomial in \(n\).
4. **Representation robustness.** The lower bound applies to arbitrary circuits in the declared basis,
   including sharing/reuse; it cannot secretly assume formulas, OBDDs, bounded width, monotonicity, or
   a fixed variable order.
5. **No target leakage.** Computing or defining the potential cannot assume the SAT answer in the
   construction step.
6. **Barrier audit.** If the property induced by \(\Phi\) is constructive, large, and useful against
   small circuits, it must be examined against Natural Proofs. Algebraic variants must be audited
   against algebrization.

The load-bearing open statement is therefore not the telescoping theorem. It is:

\[
\boxed{
\exists\Phi_n:\quad
\frac{\Phi_n(SAT_n)}{\max\text{ one-gate progress}}
= n^{\omega(1)}.
}
\]

## 5. Why the obvious IDM invariants are insufficient by themselves

Several native IDM quantities are valuable for restricted models but hit an information ceiling for
unrestricted circuits.

### 5.1 Retained-state cardinality

There are only \(2^n\) inputs of length \(n\). An injectivity argument can force at most \(n\) retained
bits from input counting alone. This can give sharp streaming/space lower bounds but not a
superpolynomial circuit-size lower bound.

### 5.2 Communication-matrix rank

For a balanced input partition, any Boolean communication matrix has dimension at most
\(2^{n/2}\times2^{n/2}\), so

\[
\log_2\operatorname{rank}(M_f)\le n/2.
\]

Rank can be extremely useful against formulas, branching programs, bounded depth, or algebraic
models, but a simple additive `log-rank per gate` potential cannot exceed a linear lower bound for a
general \(n\)-input Boolean function.

### 5.3 Number of residual functions at one cut

At a cut after \(k\) variables there are at most \(2^k\) prefixes, hence at most \(2^k\) distinct
residual functions. Therefore

\[
\log_2 N_{\rm residual}\le k\le n.
\]

This is enough to obtain exponential **width** for OBDDs because width itself is \(N_{\rm residual}\),
but converting the same quantity into a gate-local unrestricted-circuit potential loses the
exponential and yields only an \(O(n)\)-scale logarithm.

### 5.4 Algebraic degree and monomial support

For multilinear Boolean representations,

\[
\deg(f)\le n,\qquad
\#\operatorname{monomials}(f)\le2^n.
\]

Thus degree and log-support also have only linear headroom if one-gate progress is bounded additively.
They remain useful in restricted algebraic models but cannot by themselves establish a
superpolynomial unrestricted Boolean-circuit lower bound.

## 6. The current positive routes

The programme should now use the simple invariants as **components**, not as the final potential.
Three routes remain plausible research lanes:

### A. Fusion / two-dimensional cover complexity

Cavalar and Oliveira (2025) reduce Boolean circuit lower bounds to explicit two-dimensional cover
problems through the fusion method and a set-theoretic notion they call discrete complexity. This is
structurally close to IDM's finite readout/fusion language. Their framework gives an externally
established circuit-complexity bridge, so adapting retained differences to their cover objects is more
promising than inventing a new unrestricted-circuit model from scratch.

### B. Constructive refuters / SAT-solver-specific properties

Known work on constructive circuit lower bounds shows that properties useful specifically against SAT
solver circuits can avoid the naive interpretation of the Natural Proofs barrier that would require
rejecting all small circuits. A readout intervention family can be interpreted as a test set that
searches for a counterexample to a proposed SAT circuit. The missing step is an efficient universal
refuter construction.

### C. Rank as a component of a stronger invariant

Weak Rank Principle lower bounds show that rank obstructions can become hard after encoding into weak
proof systems. For unrestricted circuits, rank alone is too small as a gate-local potential, but it may
serve as a local obstruction inside a fusion/cover or refuter measure whose global value has
superpolynomial range.

## 7. Current target

The immediate target is now:

> **Readout-Fusion Potential Problem.** Construct an explicit set/graph/cover object from `SAT_n` whose
> complexity lower-bounds unrestricted Boolean circuit size through an established fusion theorem, and
> express that complexity as a retained-distinction potential that can be attacked with IDM exact
> combinatorics.

This avoids three earlier dead ends at once:

- it does not infer time from terminal-state size;
- it does not assume an OBDD/read-once computation;
- it does not require a new simulation theorem from arbitrary Turing machines.

The remaining difficulty is exactly where modern circuit complexity says it should be: proving a
strong explicit lower bound for the resulting combinatorial object.

## References

- Standard simulation theorem: `P subseteq P/poly`.
- Razborov and Rudich, *Natural Proofs*, JCSS 1997.
- Aaronson and Wigderson, *Algebrization*, TOCT 2009.
- Cavalar and Oliveira, *Boolean Circuit Complexity and Two-Dimensional Cover Problems*, ECCC TR25-033 / 2025.
- Carmosino, Dang and Jackman, *Convergent Gate Elimination and Constructive Circuit Lower Bounds*, 2026.
