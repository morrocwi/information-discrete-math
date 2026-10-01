# Lineage Hitting-Support Route

**Status:** finite reduction kernel + exact search-cost guard; efficient unrestricted constructor OPEN.

## 1. Local SAT defect certificates

For a candidate `C` on normalized CNF restriction states, define the internal defect predicate

\[
V_C(F,i)=1
\iff
C(F)\ne C(F|_{x_i=0})\vee C(F|_{x_i=1}).
\]

At a terminal state, the boundary defect is

\[
B_C(F)=1
\iff
C(F)\ne Eval(F),
\]

where `Eval(F)` is direct truth on a fully assigned formula.

The fixed-point localization lane proves the finite implication

\[
C(F_{root})\ne SAT(F_{root})
\Longrightarrow
\text{some local or boundary defect exists in the restriction tree}.
\]

Verification of one supplied defect is local and oracle-free.

## 2. Adaptive Defect Capture

Let `S_C` be a finite support of candidate defect certificates.  Under uniform weights,

\[
1-q_C
=
\frac{|\{z\in S_C:V(C,z)=1\}|}{|S_C|}.
\]

`formal/IDM_DefectHittingSupport.v` proves the cleared-denominator reduction:

if

\[
C\text{ is wrong}\Longrightarrow
\exists z\in S_C:\ V(C,z)=1
\]

and

\[
|S_C|\le p(n),
\]

then

\[
|S_C|\le p(n)\,M_{hit},
\]

so whenever `S_C` is nonempty,

\[
\boxed{1-q_C\ge 1/p(n).}
\]

Thus the probabilistic-looking ADC frontier reduces to an explicit combinatorial object:

> construct a polynomial-size support that hits at least one defect of every wrong small candidate.

## 3. Constant defect alphabet is not enough

The internal verifier sees only

\[
(C(F),C(F_0),C(F_1))\in\{0,1\}^3,
\]

so there are only eight internal signature types.  Boundary certificates see

\[
(C(F),Eval(F))\in\{0,1\}^2,
\]

so there are only four boundary signature types.  An omniscient representative support therefore has at most twelve types.

This does **not** give an efficient constructor.

`defect_signature_support.py` uses

\[
F_n=x_1\wedge\cdots\wedge x_n
\]

and the candidate `C=0`.  The candidate has no internal recursion defect.  Its only defect is the unique satisfying terminal assignment `(1,...,1)`.  Under left-first restriction order this is the final node visited, so exact search scans

\[
\boxed{2^{n+1}-1}
\]

restriction states before finding the defect, while the final signature support has only a constant number of representatives.

Therefore

\[
\boxed{\text{small defect alphabet}\not\Rightarrow\text{cheap defect search}.}
\]

This is the same construction-cost firewall that already invalidates terminal-bit and readout-cardinality arguments.

## 4. What the constructor may use

A valid constructor

\[
\mathcal H:C\mapsto S_C
\]

may inspect the actual shared circuit DAG, gate types, fanout, syntactic formula transformations, declared restriction maps, and independently sound local closure rules.

It may **not** use:

- a SAT oracle;
- an equivalence oracle for `C` versus SAT;
- an omniscient enumeration of all restriction states hidden outside the charged cost;
- a leaf rejector defined by `not SAT(F)`;
- witness diversity before existential projection as a hardness surrogate.

## 5. Exact load-bearing theorem

The next target is:

### Lineage Hitting-Support Theorem — OPEN

For every polynomial gate budget `s(n)`, construct in polynomial time from a candidate circuit `C` of size at most `s(n)` a support `S_C` such that

\[
|S_C|\le poly(n,s(n)),
\]

and

\[
C\ne SAT_n
\Longrightarrow
\exists z\in S_C:\ V(C,z)=1.
\]

Combined with the hitting-support reduction and local verifier, this yields an inverse-polynomial ADC capture bound.

However this theorem by itself is still a **refuter interface**.  To prove a SAT circuit lower bound one must additionally show, for every circuit below the claimed size threshold, that it is not the exact SAT circuit and that the constructor produces the corresponding defect without importing the target answer.  In the current lane this is intended to be coupled to the existing Fusion/Horn circuit bridge and candidate-adaptive lineage obstruction.

## 6. Current proof chain

\[
\text{shared circuit }C
\to
\text{lineage-aware support }S_C
\to
\text{local defect mass}
\to
1-q_C\ge1/poly
\to
\text{verified defect}
\to
C\ne SAT.
\]

Closed components:

- local defect verification;
- finite fixed-point localization once a wrong root/input is given;
- ADC mass arithmetic;
- polynomial hitting-support -> inverse-polynomial capture reduction;
- negative controls for oracle leaves, branch counting, raw signature counting, witness diversity, and constant signature alphabets.

OPEN component:

\[
\boxed{\text{efficient candidate-adaptive lineage hitting-support construction with an unrestricted SAT lower-bound guarantee}.}
\]

No `P != NP` claim is made.
