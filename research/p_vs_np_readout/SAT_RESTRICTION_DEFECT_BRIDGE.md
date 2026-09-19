# SAT Restriction-Defect Bridge

**Status:** exact finite local-to-global theorem kernel + open complexity frontier.  
**Claim boundary:** this note does not prove `SAT notin P/poly` or `P != NP`.

## 1. Why this lane is different from explicit semantic-set fusion

For SAT, materializing the full target set or its complement is not an acceptable scalable operational primitive for a constructive refuter. The target nevertheless has an exact local law that uses only syntactic restrictions:

\[
\boxed{
SAT(F)=SAT(F|_{x_i=0})\lor SAT(F|_{x_i=1}).
}
\]

At a fully assigned leaf the target value is syntactically decidable.

This gives a finite measurement interface that never needs the whole SAT truth table at once.

## 2. Restriction defect operator

For a candidate Boolean predictor/circuit `C`, define the local restriction defect

\[
\Delta_C(F,i)
=
C(F)\oplus
\Bigl(C(F|_{x_i=0})\lor C(F|_{x_i=1})\Bigr).
\]

At terminal leaves define

\[
\epsilon_C(L)=C(L)\oplus SAT(L),
\]

where `SAT(L)` is direct syntactic evaluation because no variables remain.

Thus a candidate is an exact local solution when every internal defect and every leaf error is zero.

## 3. Exact quantitative local-to-global inequality

Let `T_F` be the finite binary restriction tree of `F`. With Boolean distance

\[
d(a,b)=\mathbf 1[a\ne b],
\]

`IDM_SATRestrictionDefect.v` proves the finite inequality

\[
\boxed{
 d(C(F),SAT(F))
 \le
 \sum_{v\in\mathrm{Int}(T_F)}\Delta_C(v)
 +
 \sum_{\ell\in\mathrm{Leaf}(T_F)}\epsilon_C(\ell).
}
\]

The proof uses only:

\[
d(a,c)\le d(a,b)+d(b,c)
\]

and the Boolean OR Lipschitz inequality

\[
d(a\lor b,c\lor d)\le d(a,c)+d(b,d).
\]

Consequently, zero total defect forces the correct root value.

This is a direct discrete quantitative-certification analogue of the finite EPSC pattern

\[
\rho\le \alpha(\sigma+\tau),
\]

with the crucial difference that the SAT reader is existential restriction rather than a smooth inverse map.

## 4. Partial-tree / unresolved-tail form

A complete `2^n` restriction tree is not a polynomial resource. Therefore the formal kernel also allows frontier leaves to carry separately certified error budgets `beta_l` rather than silently pretending the omitted subtree is exact.

For a partial tree,

\[
\boxed{
 d_{root}
 \le
 \sum_{v\in observed}\Delta_v
 +
 \sum_{\ell\in frontier}\beta_\ell.
}
\]

If a frontier bound is unavailable, the correct Readout state is HOLD. Setting an unknown tail to zero is forbidden.

This is the direct computational counterpart of finite inner certificate + separately controlled unresolved tail.

## 5. Fixed-point interpretation

Define a restriction transfer operator

\[
(\mathcal T_i C)(F)
=
C(F|_{x_i=0})\lor C(F|_{x_i=1}).
\]

SAT satisfies

\[
\boxed{SAT=\mathcal T_i SAT}
\]

for every admissible variable restriction, together with exact terminal boundary data.

Hence the SAT truth function is the unique exact solution on each finite restriction tree to:

```text
local OR recursion
+ terminal boundary truth.
```

The circuit lower-bound problem can therefore be reframed as follows:

> Can a polynomial-size unrestricted circuit family realize a zero-defect solution of this entire restriction system for every encoded formula length?

A proof that every polynomial-size candidate has a nonzero defect somewhere would refute that candidate as an exact SAT circuit.

## 6. Why this does not already prove a lower bound

The complete restriction tree has exponential size. A small circuit could, in principle, satisfy all local identities without the proof checking every node individually; indeed such a circuit would simply be a SAT circuit.

Therefore

\[
\Delta_C\equiv0 + \text{correct leaves}
\Longrightarrow C=SAT
\]

is a characterization, not a separation theorem.

The missing quantitative result must compress the local constraints without borrowing the target answer.

## 7. New load-bearing target: compressed defect observability

The next target is to find a polynomially representable/sampleable certificate `M(C)` such that

\[
M(C)=0
\Longrightarrow
\Delta_C(F,i)=0
\quad\text{for every required restriction node},
\]

or, contrapositively, every too-small candidate yields a certified sampled/local defect.

A useful certificate must satisfy:

1. it is constructed from circuit syntax, restrictions and directly checkable leaf facts;
2. it does not enumerate the full truth table or full restriction tree;
3. it respects free fanout and sharing;
4. it cannot call SAT/equivalence as a subroutine;
5. omitted restriction regions carry explicit tail debt rather than being set to zero;
6. Equality/parity/easy-SAT families remain mandatory negative controls.

This is the SAT-side analogue of moving from structural observability to a finite quantitative measurement certificate.

## 8. Relation to fusion / RCD

The Horn/fusion lane and the restriction-defect lane are complementary:

- fusion/RCD measures how many semantic closure rules are required to eliminate adversarial semi-filters;
- restriction defect measures whether a candidate respects SAT's exact existential recursion on actual formula restrictions.

The first has a precise cover-complexity bridge but an explicit semantic-set/interface problem; the second has a clean syntactic measurement interface but still needs a compressed global lower-bound invariant.

The strongest next experiment is to use restriction-defect samples to construct or update an adaptive lineage adversary rather than choosing a fixed target-only distribution.
