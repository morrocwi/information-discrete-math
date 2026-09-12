# Existential Projection Readout: the Readout-Universe translation of NP

**Status:** structural reframing / exact finite semantics.  
**Claim boundary:** this note does **not** prove a lower bound for SAT, `NP not subset P/poly`, or `P != NP`.

## 1. Correction: SAT is not an observability/inverse problem

For a SAT instance the full finite formula encoding is already given to the algorithm.  If the source record is `F`, the identity reader

\[
q_{\mathrm{in}}(F)=F
\]

is exact and has no omitted input information.  In the Readout-Universe language, the input itself is fully identifiable.

Therefore the Navier--Stokes pattern

```text
partial observations -> quotient chart -> local inverse
```

cannot be transferred literally to SAT.  The N=1/N=2 NS certificates remain useful as a methodological lesson -- structural information is not enough; a quantitative transform certificate is needed -- but SAT's hard transform is not inversion.

## 2. SAT is an existential projection

Let `R(F,w)` be the polynomial-time verification relation saying that assignment `w` satisfies formula `F`.  For a formula with `m` witness bits,

\[
\operatorname{SAT}(F)
=
\bigvee_{w\in\{0,1\}^m} R(F,w)
=
(\pi_{\exists}R)(F).
\]

The decision bit is therefore a **projection readout** of a finite relation along the witness coordinate.

This is exactly compatible with the Readout-Universe doctrine that a reported quantity is a projection/readout with a role in a bounded graph: SAT is the Boolean existential projection of a verifier relation.

The finite Coq kernel `IDM_ExistentialProjection.v` records the exact semantics only.

## 3. YES/NO asymmetry under projection

For YES,

\[
\exists w\;R(F,w)=1
\]

so a single witness can certify the positive projection.

For NO,

\[
\forall w\;R(F,w)=0.
\]

A subcube/rejection-cover certificate is one way to prove the universal negative, and `IDM_ReadoutUniverseAccessibleCompletion.v` formalizes the generic finite completion step.  But an unrestricted SAT circuit is not required to emit that certificate.

Thus proof-complexity lower bounds remain restricted unless accompanied by a without-loss-of-generality simulation theorem.

## 4. Projection Transform Complexity (PTC)

For a declared computational model `M`, define schematically

\[
\operatorname{PTC}_{\mathcal M}(R)
=
\text{minimum admissible model cost for computing }\pi_{\exists}R.
\]

This is a research interface, not yet a lower-bound method.  If `M` is unrestricted Boolean circuits, defining `PTC` as the minimum circuit size simply renames circuit complexity.

A useful theorem therefore needs an **independent lower certificate**

\[
\operatorname{LB}_{\exists}(R)
\le
\operatorname{PTC}_{\mathcal M}(R)
\]

whose left-hand side is defined without SAT answers, circuit minimization, or an equivalent hidden oracle.

## 5. The correct capacity question

A circuit computes the projection by a semantic-generation ledger

\[
\mathcal G_0\to\mathcal G_1\to\cdots\to\mathcal G_s,
\]

where generated wires may be reused freely.  The missing Readout theorem is therefore:

> find an adaptive prefix certificate for existential projection whose burden cannot be discharged too rapidly by one new Boolean function-generation step, even with arbitrary sharing.

In notation, for an adversarial projection state `A_t`, prove

\[
W(A_t)-W(A_{t+1})\le K_n
\]

for every legal gate and

\[
W(A_0)>p(n)K_n
\]

for an explicit NP verifier family and every polynomial `p`, on arbitrarily large `n`.

Then any circuit computing the existential projection must have superpolynomial size.

## 6. Why this is a cleaner Readout-Genesis target

This reframing separates four notions that earlier sketches risked mixing:

1. **input retention** -- trivial for SAT because the whole formula is supplied;
2. **witness existence** -- the latent finite relation coordinate;
3. **projection** -- existential elimination of the witness coordinate;
4. **construction cost** -- the actual complexity question.

NoEarlyCollapse constrains illegal loss of a future-required record, but it cannot by itself force a SAT lower bound because a decider need not retain or reconstruct witnesses.  It only needs the projected bit.

Hence the decisive object must measure **projection-generation difficulty**, not witness-memory difficulty.

## 7. Relation to the current branch

- `IDM_DecisionReadout.v`: terminal one-bit readout can always be tiny; construction cost matters.
- `IDM_FreeRereadGuard.v`: full input access and free circuit fanout cannot be charged as memory hardness.
- `IDM_ReadoutUniverseAccessibleCompletion.v`: exact finite local-cover -> global-NO completion, restricted certificate route.
- `UNIVERSAL_SEMANTIC_CAPACITY.md`: gate-native prefix/capacity target.
- `FUSION_HORN_NORMAL_FORM.md` / `ADAPTIVE_LINEAGE_REFUTER.md`: existing adaptive/set-theoretic lower-bound lanes.
- `IDM_DemandCircuitDominance.v`: once a valid independent demand/capacity gap exists, transfer to circuit size is elementary.

## 8. Current frontier in one line

\[
\boxed{
\text{Find a non-circular, representation-robust lower certificate for the cost of }\pi_{\exists}
\text{ under unrestricted Boolean semantic generation.}
}
\]

That is the Readout-Universe/Genesis form of the unresolved circuit-lower-bound step.  Nothing currently in IDM, Genesis, Universe, or the finite NS inverse lane proves this superpolynomial certificate.
