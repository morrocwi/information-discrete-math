# Weak Rank Principle Bridge: an Algebraic Hardness Lane for IDM

**Status:** established external lower-bound programme + exact finite IDM-compatible base checks.  
**Claim boundary:** this note does **not** prove `P != NP`, `NP != coNP`, or a new PCR lower bound.

A second attack lane emerges from the exact-linear-algebra side of IDM rather than from Boolean
readout collisions alone.  Let

\[
X\in\mathbb F^{m\times n},\qquad
Y\in\mathbb F^{n\times m},\qquad m>n.
\]

For every field,

\[
\operatorname{rank}(XY)\le n.
\]

Therefore, for any matrix `A` with `rank(A)>n`, the equation

\[
\boxed{XY=A}
\]

is unsatisfiable.  This is the weak rank principle: an algebraic generalization of the weak
pigeonhole principle.

---

## 1. Why this belongs in the P-vs-NP research lane

The base obstruction is entirely finite and exact.  It speaks the native IDM language:

- retained finite matrices;
- exact multiplication;
- an invariant (`rank`) that cannot increase through a factorization bottleneck of dimension `n`;
- a fail-closed decision: `rank(A)>n` certifies that `XY=A` has no solution.

Unlike a coarse SAT profile, the obstruction is algebraic and structural.  It is therefore a useful
second lane for testing whether Readout/IDM invariants can support lower-bound arguments that go beyond
pure black-box collision counting.

---

## 2. Current external frontier (2026)

Garlik, Gryaznov, Ren and Tzameret, *The Weak Rank Principle: Lower Bounds and Applications*, ECCC
TR26-133 (August 2026), prove exponential lower bounds for algebraic and standard-CNF encodings of the
weak rank principle in Polynomial Calculus Resolution over `F_2`, including a bamboo-tree encoding.
They also construct proof-complexity generators, obtain Sherali--Adams hardness results, and connect the
principle to formal circuit-lower-bound statements.

The consequence for this project is important but limited:

\[
\boxed{
\text{weak-rank hardness in restricted proof systems}
\not\Rightarrow P\ne NP.
}
\]

It supplies a current hard family and a sophisticated lower-bound mechanism against which an IDM
translation can be tested.

Reference: ECCC TR26-133, https://eccc.weizmann.ac.il/report/2026/133/

---

## 3. Retained-bottleneck reading

View the factorization

\[
\mathbb F^m\xrightarrow{Y}\mathbb F^n\xrightarrow{X}\mathbb F^m.
\]

Every vector is forced through an `n`-dimensional retained interface.  The image of the composite can
therefore retain at most `n` independent output distinctions:

\[
\boxed{
\dim\operatorname{im}(XY)\le n.
}
\]

If the target `A` exposes more than `n` independent distinctions,

\[
\operatorname{rank}(A)>n,
\]

then the proposed factorization fails the invariant-completion gate.  This is a precise algebraic
instance of the Readout Genesis rule that a quotient/bottleneck may not merge distinctions required by
the declared invariant.

This interpretation adds no mathematical strength to the classical rank inequality, but it aligns the
rank principle with the same retained-state language used by the SAT intervention and RCP lanes.

---

## 4. Exact finite checker

`weak_rank_principle.py` implements exact arithmetic over `F_2` and exhaustively checks the small
instances

- `(m,n)=(2,1)`;
- `(m,n)=(3,1)`;
- `(m,n)=(3,2)`;

against `A=I_m`.

For every enumerated pair `(X,Y)` it verifies

\[
\operatorname{rank}(XY)\le n<m=\operatorname{rank}(I_m)
\]

and hence `XY != I_m`.  These are finite diagnostics only; the general theorem is standard linear
algebra, not inferred from enumeration.

---

## 5. How it connects to the Readout lane

There are now two complementary obstruction mechanisms in this branch:

### A. Future-readout distinguishability

\[
\text{many residual functions}
\Rightarrow
\text{many retained states}
\Rightarrow
\text{OBDD/read-once width lower bound}.
\]

### B. Rank bottleneck

\[
\text{factor through dimension }n
\Rightarrow
\operatorname{rank}\le n
\Rightarrow
\text{target rank}>n\text{ impossible}.
\]

The second is attractive because rank methods can survive transformations that defeat simple
cardinality/readout counting.  But a P-vs-NP proof would still require a bridge from an unrestricted
polynomial-time SAT computation to a rank obstruction that cannot be bypassed by another algorithmic
representation.

---

## 6. Research target

The next nontrivial question is not to reprove `rank(XY)<=n`.  It is to search for a machine-explicit
matrix/readout construction

\[
M,F\longmapsto A_{M,F},X_{M,F},Y_{M,F}
\]

with the following properties:

1. construction is polynomial and does not call SAT or import the target answer;
2. a too-cheap correct SAT computation would force a low-rank factorization;
3. some explicit hard formula family forces a certified rank excess;
4. the contradiction is not merely a relativizing input-output collision argument;
5. the construction is audited against algebrization and Natural-Proofs-style barriers.

Property 2 is the load-bearing open bridge.  Until it is proved, the weak-rank lane is a structured
source of hard instances and invariants, not a P-vs-NP solution.
