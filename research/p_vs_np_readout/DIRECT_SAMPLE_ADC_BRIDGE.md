# Direct-Sample Adaptive Defect Capture Bridge

**Status:** structural/quantitative bridge supplied; unrestricted SAT lower-bound constructor OPEN.

## 1. Imported finite-certificate pattern

The external finite measurement result supplies a reusable quantitative architecture:

\[
q<1,\qquad \|A\|\delta+qr\le r
\]

implies a certified local branch and an error bound.  The important structural lesson is not the Navier--Stokes Jacobian itself.  It is the finite-first discipline:

\[
\text{raw finite observations}
\to
\text{direct certificate map}
\to
\text{strict margin}
\to
\text{certified conclusion},
\]

with unknown remainder kept explicit and `HOLD` when the margin is not proved.

No file or theorem in the external project is modified by this lane.

## 2. SAT direct sample map

For a candidate SAT circuit/predictor `C`, a restriction state `z=(F,R)` gives a locally checkable defect bit

\[
D_C(z)=1
\]

when either

1. at a nonterminal state,
   \[
   C(F,R)\ne C(F|_{x=0},R\setminus\{x\})\vee C(F|_{x=1},R\setminus\{x\}),
   \]
   for the declared split variable `x`; or
2. at a terminal state, `C` disagrees with direct syntactic leaf truth.

For a finite support

\[
H_C=(z_1,\ldots,z_m),
\]

define the raw direct-sample vector

\[
\boxed{\mathcal S_{H_C}(C)=(D_C(z_1),\ldots,D_C(z_m)).}
\]

No SAT oracle and no reconstruction of the full SAT truth table are needed to verify these coordinates.

## 3. Exact capture parameter

For integer weights `w_i>=0`, let

\[
M=\sum_i w_i,\qquad
H=\sum_i w_i D_C(z_i),\qquad
q_C=1-\frac{H}{M}.
\]

Then the existing Adaptive Defect Capture kernel proves the exact finite gate

\[
\boxed{q_C<1\Longrightarrow H>0\Longrightarrow\exists i:\ D_C(z_i)=1.}
\]

If

\[
M\le pH,
\]

then

\[
\boxed{1-q_C=\frac HM\ge\frac1p.}
\]

Thus independent sampling from the support has expected trial count at most `p`, assuming support generation and one local verification trial are polynomial-time.

## 4. Robust sample/support margin

The direct-sample architecture becomes useful only if it survives implementation error.  Let

- `H_*` = ideal certified defect mass,
- `\hat H` = implemented defect mass,
- `E` = certified loss/error bound,
- `M` = total mass.

The robust finite kernel uses

\[
H_*\le \hat H+E
\]

and

\[
M+pE\le pH_*.
\]

Then

\[
\boxed{M\le p\hat H,}
\]

so the implemented sampler still satisfies

\[
\boxed{1-\hat q_C=\frac{\hat H}{M}\ge\frac1p.}
\]

This is the discrete capture analogue of preserving a certified branch after measurement/remainder uncertainty is charged against a strict margin.

If either inequality is unavailable, the correct state is `HOLD`.

## 5. Finite support versus unrestricted lower bound

The following are already supplied in this branch:

- exact local defect verifier;
- local-to-global restriction-defect theorem;
- candidate-adaptive finite mass kernel;
- polynomial hitting-support -> inverse-polynomial capture kernel;
- finite restricted constructors using syntax closure / tractable frontiers;
- finite outer-hitting synthesis for a declared small candidate DSL;
- oracle-free finite CEGIS baseline;
- Fusion/Horn survivor -> concrete mismatch bridge.

The missing theorem is **not** another local verification lemma.  It is the unrestricted constructor:

> For every Boolean circuit `C` below a declared polynomial size budget, construct in polynomial time a support/distribution `H_C` using only the circuit DAG/lineage and independently checkable SAT restriction rules, such that either a defect is returned directly or
>
> \[
> 1-q_C\ge n^{-O(1)}.
> \]

The constructor may be candidate-adaptive, but it may not call SAT, circuit equivalence, MCSP, or an equivalent target oracle.

## 6. Separation chain

If such a constructor is proved for every polynomial gate budget, then every polynomial-size candidate circuit for SAT has a verified defect.  Hence

\[
\boxed{SAT\notin P/poly.}
\]

The final implication is standard and is isolated in `formal/IDM_SATNotInPpolyImpliesPneqNP.v`:

\[
P=NP\Longrightarrow SAT\in P\Longrightarrow SAT\in P/poly.
\]

Therefore

\[
\boxed{SAT\notin P/poly\Longrightarrow P\ne NP.}
\]

This last logical transfer is easy.  The load-bearing OPEN statement remains the unrestricted direct-sample/hitting-support construction above.

## 7. Claim boundary

### Supplied

- direct raw restriction-sample map;
- exact local verification semantics;
- exact `q_C<1` capture gate;
- inverse-polynomial capture from polynomial hitting support;
- robust capture transfer under a certified finite error budget;
- final logical implication `SAT notin P/poly -> P != NP` under the standard class-inclusion premises.

### OPEN

- unrestricted polynomial-time construction of `H_C` / `mu_C` for every undersized SAT circuit;
- inverse-polynomial capture margin for that constructor;
- `SAT notin P/poly`;
- `P != NP`.
