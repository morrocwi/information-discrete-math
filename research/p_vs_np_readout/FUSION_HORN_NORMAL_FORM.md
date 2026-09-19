# Fusion Cover Complexity as a Horn-Closure Readout

**Status:** exact re-expression of the Cavalar--Oliveira fusion framework in IDM/Readout language.  
**Novelty claim:** none at present; the paper already uses the same forward-propagation closure in the proof of its fusion upper bound. The contribution of this note is the explicit Horn/readout normalization and its use as a research interface.

## 1. External theorem bridge

For a non-trivial target set \(A\subseteq\Gamma\) and generator family
\(\mathcal B\subseteq\mathcal P(\Gamma)\), Cavalar and Oliveira define the cover complexity
\(\rho(A,\mathcal B)\). Their fusion theorem gives

\[
\boxed{\rho(A,\mathcal B)\le D_\cap(A\mid\mathcal B)}
\]

and their converse gives

\[
D_\cap(A\mid\mathcal B)\le \rho(A,\mathcal B)^2.
\]

For Boolean functions, discrete complexity captures DeMorgan circuit complexity, and their graph-to-function transference gives a direct route from two-dimensional graph intersection lower bounds to Boolean circuit lower bounds.

Reference: Cavalar--Oliveira, ECCC TR25-033 (2025), Theorem 22, Theorem 24, Lemma 13.

## 2. Semi-filter state

Let

\[
U=A^c=\Gamma\setminus A.
\]

A semi-filter \(\mathcal F\subseteq\mathcal P(U)\) is nonempty, upward closed, and excludes the empty set:

\[
\varnothing\notin\mathcal F,
\qquad
E\in\mathcal F,\ E\subseteq H\subseteq U
\Longrightarrow H\in\mathcal F.
\]

For \(a\in A\), being **above** \(a\) means

\[
a\in B\in\mathcal B
\Longrightarrow
B\cap U\in\mathcal F.
\]

Thus the generator slices selected by the declared target point are compulsory retained states.

## 3. Fusion pairs are Horn implications

For a pair \((E,H)\) of subsets of \(U\), preservation means

\[
E\in\mathcal F\ \wedge\ H\in\mathcal F
\Longrightarrow
E\cap H\in\mathcal F.
\]

Introduce one propositional atom \(p_S\) for every \(S\subseteq U\), interpreted as

\[
p_S=1\iff S\in\mathcal F.
\]

Then every fusion pair is exactly the Horn implication

\[
\boxed{p_E\wedge p_H\to p_{E\cap H}}.
\]

Upward closure is the family of unary Horn implications

\[
S\subseteq T\subseteq U:
\qquad p_S\to p_T.
\]

The bottom condition is

\[
\boxed{p_{\varnothing}=0}.
\]

For a fixed \(a\), the `above-a` conditions are positive unit seeds

\[
p_{B\cap U}=1
\qquad
(a\in B\in\mathcal B).
\]

Therefore existence of a semi-filter above \(a\) preserving a declared pair family \(\Lambda\) is exactly feasibility of a finite Horn closure that never derives \(p_{\varnothing}=1\).

## 4. Minimal retained closure

For a point \(a\in A\) and pair family \(\Lambda\), define

\[
\operatorname{Cl}_\Lambda(a)
\]

as the least family of subsets of \(U\) obtained by:

1. seeding every \(B\cap U\) for \(a\in B\in\mathcal B\);
2. closing upward under inclusion;
3. whenever \((E,H)\in\Lambda\) and both \(E,H\) are present, adding \(E\cap H\);
4. repeating until a fixed point is reached.

This is standard Horn forward chaining. The fixed point is unique because the operator is monotone on a finite lattice.

Then

\[
\boxed{
\exists\text{ semi-filter above }a\text{ preserving }\Lambda
\iff
\varnothing\notin\operatorname{Cl}_\Lambda(a).
}
\]

The forward direction is immediate because every such semi-filter contains the least closure. For the reverse direction, if the least closure omits the empty set, the closure itself is a semi-filter above \(a\) preserving \(\Lambda\).

This is the Horn/readout normalization of the propagation construction used in the proof of the fusion upper bound.

## 5. Cover complexity normal form

By Definition 21 of cover complexity,

\[
\rho(A,\mathcal B)
=
\min\{|\Lambda|:\text{ no semi-filter preserves }\Lambda\text{ and is above any }a\in A\}.
\]

Using the closure equivalence,

\[
\boxed{
\rho(A,\mathcal B)
=
\min\Bigl\{|\Lambda|:
\forall a\in A,
\ \varnothing\in\operatorname{Cl}_\Lambda(a)
\Bigr\}.
}
\]

Equivalently,

\[
\boxed{
\rho(A,\mathcal B)>k
\iff
\forall\Lambda\ (|\Lambda|\le k),
\ \exists a\in A:\
\varnothing\notin\operatorname{Cl}_\Lambda(a).
}
\]

This is the form most compatible with Readout Genesis.

## 6. Readout interpretation

The dictionary is:

| Fusion object | Readout/IDM interpretation |
|---|---|
| \(a\in A\) | declared target world/input |
| \(B\cap U\) | generator distinction retained because it agrees with \(a\) |
| semi-filter \(\mathcal F\) | adversarial unresolved completion |
| \((E,H)\) | one admitted binary fusion/intersection rule |
| preservation | local consistency with that fusion |
| \(\varnothing\) | contradiction / bottom `Sbot` |
| \(\operatorname{Cl}_\Lambda(a)\) | minimal retained causal closure |
| \(\rho(A,\mathcal B)\) | minimum number of fusion rules forcing bottom for every target point |

This is not merely analogy: the closure equations are the same finite monotone propagation equations.

## 7. SAT graph specialization

Take an even input length \(m=2n\) and let \(SAT_m:\{0,1\}^{m}\to\{0,1\}\) be a fixed canonical SAT encoding predicate (invalid encodings receive a fixed declared value, e.g. 0).

Let \(N=2^n\) and split an input string into two \(n\)-bit blocks. Define

\[
G^{SAT}_n
=
\{(u,v)\in[N]\times[N]:
SAT_{2n}(\operatorname{bin}(u)\operatorname{bin}(v))=1\}.
\]

Under the standard bijection \(\phi(u,v)=\operatorname{bin}(u)\operatorname{bin}(v)\), the associated Boolean function is exactly \(SAT_{2n}\).

Cavalar--Oliveira Lemma 13 and Theorem 22 therefore give the conditional research chain

\[
\boxed{
\rho(G^{SAT}_n,\mathcal G_{N,N})
\le
D_\cap(G^{SAT}_n\mid\mathcal G_{N,N})
\le
\operatorname{CircuitSize}(SAT_{2n})
}
\]

(up to the precise DeMorgan/intersection counting convention).

Hence a superpolynomial lower bound in \(n\) for the explicit SAT graph cover complexity would imply

\[
SAT\notin P/poly
\Longrightarrow
P\ne NP.
\]

The bridge is standard/external; the open work is the cover lower bound.

## 8. New load-bearing target

The problem can now be stated without machine-model ambiguity:

> **SAT Fusion-Horn Lower-Bound Problem.** Prove that for every constant \(c\), for sufficiently large \(n\), every pair family \(\Lambda\) with \(|\Lambda|\le n^c\) leaves some satisfiable encoding \(a\) whose minimal Horn closure avoids bottom:
>
> \[
> \exists a\in SAT_{2n}^{-1}(1):
> \varnothing\notin\operatorname{Cl}_\Lambda(a).
> \]

This statement is still as difficult as the desired circuit lower bound through the established fusion bridge; it is **not** claimed proved.

What IDM contributes is a precise finite engine for attacking it:

- retained closure/fold semantics;
- exact SAT/Horn forward chaining;
- retained-difference and bottom-vs-neutral discipline;
- rank/linear-algebra invariants as possible local certificates;
- a CostLedger for rule count, closure depth, live boundary and recomputation.

## 9. Immediate experiments

1. Implement exact Horn closure for finite \((A,\mathcal B,\Lambda)\).
2. Verify the closure/semi-filter equivalence exhaustively on tiny ground sets.
3. Compute exact \(\rho\) for tiny Boolean functions and compare with their intersection constructions.
4. Test whether rank, width, entropy, or lineage measures predict which fusion pairs are globally reusable.
5. Search for explicit SAT subfamilies where every small \(\Lambda\) has a surviving target point.
6. Audit every proposed lower-bound measure against unrestricted arbitrary subset pairs \((E,H)\); restricting the pair language would silently weaken the circuit model.
