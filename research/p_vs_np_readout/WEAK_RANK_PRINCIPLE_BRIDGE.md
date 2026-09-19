# Weak Rank Principle Bridge: an Algebraic Proof-Strength Lane for IDM

**Status:** established external lower-bound programme + exact finite IDM-compatible base checks.  
**Claim boundary:** this note does **not** prove `P != NP`, `NP != coNP`, or a new PCR lower bound.

A second attack lane emerges from the exact-linear-algebra side of IDM rather than from Boolean
readout collisions alone. Let

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

is unsatisfiable. This is the weak rank principle: an algebraic generalization of the weak pigeonhole
principle.

---

## 1. Why this belongs in the P-vs-NP research lane

The base obstruction is entirely finite and exact. It speaks the native IDM language:

- retained finite matrices;
- exact multiplication;
- an invariant (`rank`) that cannot increase through a factorization bottleneck of dimension `n`;
- a fail-closed decision: `rank(A)>n` certifies that `XY=A` has no solution.

Unlike a coarse SAT profile, the obstruction is algebraic and structural. It is therefore useful for
testing the **proof strength** of retained-information formalisms and for building hard encodings for
restricted proof systems.

A crucial correction is that the semantic weak-rank instance is **not computationally hard for a
system that already has exact rank reasoning**. IDM can treat the obstruction as a direct certificate.
The 2026 hardness results concern proof systems whose restricted proof language cannot efficiently
formalize the required rank reasoning. Hardness is therefore representation/proof-system relative.

---

## 2. Current external frontier (2026)

Garlik, Gryaznov, Ren and Tzameret, *The Weak Rank Principle: Lower Bounds and Applications*, ECCC
TR26-133 (August 2026), prove exponential lower bounds for algebraic and standard-CNF encodings of the
weak rank principle in Polynomial Calculus Resolution over `F_2`, including a bamboo-tree encoding.
They also construct proof-complexity generators, obtain Sherali--Adams hardness results, and connect the
principle to formal circuit-lower-bound statements.

The paper explicitly explains the source of hardness: weak rank expresses unsatisfiable matrix
identities, and difficulty arises when the proof system cannot efficiently formalize matrix-rank
reasoning. It also shows that weak rank is powerful enough, in an appropriate bounded-arithmetic theory,
to formalize Smolensky-style `AC^0[p]` circuit lower bounds.

The consequence for this project is important but limited:

\[
\boxed{
\text{weak-rank hardness in restricted proof systems}
\not\Rightarrow P\ne NP.
}
\]

Reference: ECCC TR26-133, https://eccc.weizmann.ac.il/report/2026/133/

---

## 3. Retained-bottleneck reading

View the factorization

\[
\mathbb F^m\xrightarrow{Y}\mathbb F^n\xrightarrow{X}\mathbb F^m.
\]

Every vector is forced through an `n`-dimensional retained interface. The image of the composite can
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

then the proposed factorization fails the invariant-completion gate. This is a precise algebraic
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

and hence `XY != I_m`. These are finite diagnostics only; the general theorem is standard linear
algebra, not inferred from enumeration.

---

## 5. What weak rank teaches the Readout programme

There are now three complementary obstruction mechanisms in this branch:

### A. Future-readout distinguishability

\[
\text{many residual functions}
\Rightarrow
\text{many retained states}
\Rightarrow
\text{OBDD/read-once width lower bound}.
\]

### B. Retention/recomputation

\[
\text{dependency DAG}
\Rightarrow
\text{pebbling schedule}
\Rightarrow
\text{time/space trade-off in the declared evaluator model}.
\]

### C. Rank bottleneck

\[
\text{factor through dimension }n
\Rightarrow
\operatorname{rank}\le n
\Rightarrow
\text{target rank}>n\text{ impossible}.
\]

Weak rank adds a lesson missing from pure collision counting: a statement can be semantically trivial
for one representation and exponentially difficult to establish inside another proof language. This is
exactly why a P-vs-NP attack must specify the computational/proof representation rather than treating
'information amount' as representation-independent computational difficulty.

---

## 6. Stronger use inside IDM

Because exact rank reasoning is natural in IDM, the productive direction is not to pretend `XY=A` is
hard for IDM. It is to use weak rank as a **calibration axiom/theorem family**:

1. certify the semantic rank obstruction exactly;
2. encode the same instance into CNF/algebraic proof systems;
3. measure which retained proof languages can recover the short rank argument and which undergo blow-up;
4. compare this representation gap against the 2026 PCR/SA lower-bound literature;
5. test whether a more general retained invariant can transport rank reasoning into stronger circuit or
   proof models.

This turns WRank into a controlled laboratory for the central question: when does a compact invariant
in one representation force large resources in another?

---

## 7. Research target

The next nontrivial question is not to reprove `rank(XY)<=n`. It is to search for a machine-explicit
matrix/readout construction

\[
M,F\longmapsto A_{M,F},X_{M,F},Y_{M,F}
\]

with the following properties:

1. construction is polynomial and does not call SAT or import the target answer;
2. a too-cheap correct SAT computation would force a low-rank factorization or low-dimensional retained
   proof object;
3. some explicit hard formula family forces a certified rank excess;
4. the contradiction is not merely a relativizing input-output collision argument;
5. the construction is audited against algebrization and Natural-Proofs-style barriers.

Property 2 is the load-bearing open bridge. Until it is proved, the weak-rank lane is a proof-strength
calibration family and a source of invariants, not a P-vs-NP solution.
