# Lineage-Conditioned Antichecker Frontier

## Status

**OPEN breakthrough target.**  This note deliberately concentrates the P-vs-NP
lane on one load-bearing objective.  It does not claim `SAT notin P/poly` or
`P != NP`.

The existing IDM transfer chain is already sufficient once an unrestricted
lower-bound premise is supplied.  The remaining work is therefore not another
bookkeeping bridge.  It is to produce a non-circular, sharing-aware obstruction
that defeats every circuit below the relevant size threshold.

---

## 1. Direct target

For a candidate SAT circuit `C`, a finite certificate `z` is checked by an
oracle-free verifier `V(C,z)`.  The present certificate language contains:

- SAT witness anchors `(F,a)` with `a |= F` and `C(F)=0`;
- directly checkable negative anchors (empty clause, certified tractable
  frontiers, etc.);
- terminal boundary defects;
- restriction fixed-point defects

\[
C(F) \ne C(F|_{x=0})\vee C(F|_{x=1});
\]

- equivalent Fusion/Horn survivors when they can be converted to a concrete
  locally checkable mismatch.

A **Lineage-Conditioned Constructive Antichecker (LCCA)** for a size bound
`B(n)` is a constructor which, after seeing the actual shared DAG of `C`,
produces an efficiently samplable weighted support `mu_C` satisfying

\[
|C|\le B(n),\ C\ne SAT_n
\quad\Longrightarrow\quad
\Pr_{z\sim\mu_C}[V(C,z)=1]\ge {1\over p(n)}
\]

for a fixed polynomial `p`, without using SAT, equivalence, MCSP, or the target
answer as an oracle.

Writing

\[
q_C:=\Pr[V(C,z)=0],
\]

the target is

\[
\boxed{1-q_C\ge 1/p(n).}
\]

This is exactly the quantitative premise consumed by
`IDM_AdaptiveDefectCapture.v`, `IDM_RobustDefectCapture.v`, and
`IDM_ADCSeparationChain.v`.

---

## 2. Readout Genesis / Readout Universe typing

The constructor is admitted only if it obeys the same order as the root
architecture:

\[
\text{circuit DAG + formula state}
\to\text{sufficient retained lineage}
\to\text{declared intervention}
\to\text{returned local record}
\to\text{defect}
\to\text{bounded claim}.
\]

The rules are operational, not metaphorical:

1. **State sufficiency.**  If a proposed sampler forgets a circuit distinction
   that changes the chosen future tests, the sampler state must be refined.
2. **Dynamic commutation.**  SAT restriction is applied as an explicit
   transformation of the formula state; it is not identified with fixing a
   candidate-circuit input wire unless that translation has been proved.
3. **Lineage preservation.**  DAG sharing is retained.  Unfolding to a tree is
   not an admissible lower-bound charge.
4. **No Early Collapse.**  Candidate states may be merged only after all
   declared future readers agree.
5. **Invariant completion.**  If a quotient hides a distinction detected by a
   required anchor/restriction/Fusion reader, refine it.
6. **Forbidden imports.**  No target answer, SAT oracle, equivalence oracle,
   MCSP oracle, or free semantic leaf rule may enter the constructor.
7. **World-bound anchors.**  A target label is usable only when independently
   certified (e.g. an explicit satisfying assignment or a direct syntactic /
   tractable negative certificate).

---

## 3. What has now been killed

### 3.1 Fixed local-reader amplification

Adding more fixed local identities does not by itself produce inverse-polynomial
margin.  On the exact finite genuine-circuit benchmark (5,684 distinct
DeMorgan functions with at most two gates), the family consisting of boundary,
restriction, symmetry, unit-propagation, and subsumption identities has a wrong
candidate with only one violated test among 3,986 tests.

`fixed_reader_anchor_amplification.py` records this negative control.

### 3.2 World-bound anchors help, but do not close the asymptotic problem

Adding independently certified SAT-witness anchors and empty-clause UNSAT
anchors raises the finite minimum to 96 violations among 4,337 tests.  This is
a real finite amplification effect, but it cannot be extrapolated to arbitrary
large circuits: a candidate may concentrate its errors on formulas outside any
fixed tractable anchor family.

### 3.3 Raw branch / residual / signature counting

These remain invalid shortcuts.  Shared circuits can compress exponentially
many paths or residual functions, and a gate-value signature space can itself
have size exponential in the number of gates.

### 3.4 Fixed candidate-independent sampling

A fixed sampler cannot be the final theorem.  Under the contrary hypothesis
that an exact small target circuit exists, adding a small equality patch can
produce a polynomial-size candidate whose error is concentrated on a single
input.  Any local test family of bounded incidence then has a patch location
with exponentially small mass under a fixed distribution.  Therefore the
sampler must be candidate-adaptive (or the proof must use a different global
obstruction).

### 3.5 Self-oracle shortcut

Encoding the whole candidate circuit into a SAT query only gives the familiar
linear-scale route: a circuit of size `s` requires `Omega(s log s)` description
bits, while an `n`-bit SAT circuit can only be queried on `n`-bit instances.
For unrestricted nonuniform `s=n^k` circuits there is no uniform access to a
larger member of the circuit family.  Full-candidate self-analysis therefore
cannot be treated as a free same-length SAT query.

---

## 4. The stronger route: magnify a smaller unrestricted lower bound

The direct SAT target above is stronger than necessary.  To rule out polynomial
SAT circuits it is enough to prove `NP not subset P/poly` using any NP language.
Hardness magnification gives a substantially weaker numerical threshold for a
meta-complexity target.

Let `N=2^m` be the truth-table input length.  For the standard hard-gap
parameters of Gap-MCSP, known hardness-magnification theorems state (in the
relevant regime) that a lower bound of the form

\[
\boxed{\operatorname{CC}(\operatorname{GapMCSP}_N)>N^{1+\varepsilon}}
\]

for some fixed `epsilon>0` already implies

\[
NP\not\subseteq P/poly,
\]

and hence

\[
SAT\notin P/poly\quad\text{and}\quad P\ne NP.
\]

This does **not** make the lower bound routine: no superlinear lower bound for
an explicit single-output function is currently known against unrestricted
Boolean circuits.  It does, however, replace a superpolynomial SAT lower bound
by the weakest currently known magnification threshold that is naturally
aligned with IDM's readout/circuit-description machinery.

---

## 5. Fusion form of the magnified target

For a discrete target `A` with generators `B`, let

\[
\rho(A,B)
\]

be the Fusion cover complexity: the minimum number of pairs `(E,H)` required to
cover every semi-filter above a positive point.

The Fusion lower-bound interface gives

\[
\rho(A,B)\le D_{\cap}(A\mid B)\le \operatorname{CC}(A)
\]

(up to the declared circuit convention / translation).

Therefore a single concrete combinatorial theorem is sufficient for the
magnified route:

### Magnified Fusion Margin (MFM) — OPEN

For the hard-gap MCSP parameters and some `epsilon>0`, prove

\[
\boxed{
\rho(\operatorname{GapMCSP}_N,\mathcal B_N)>N^{1+\varepsilon}.
}
\]

A quantitative candidate-adaptive strengthening is:

> For every family `Lambda` of at most `N^(1+epsilon)` realizable Fusion pairs,
> construct (or prove the existence of) a distribution over semi-filters that
> preserve `Lambda` with residual survivor mass at least `1/poly(N)`.

This is the Fusion analogue of `1-q_C >= 1/poly`.

The current `FusionDual` and residual-cover-debt kernels already supply the
local arithmetic once such a survivor / dual mass theorem is available.

---

## 6. Why Gap-MCSP is the primary attack surface

The input is itself a finite truth table, so there is no domain-translation
ambiguity between the readout object and the Boolean input.  The YES side has
small circuit descriptions as explicit witnesses, while the hardness
magnification threshold is only slightly superlinear.  This matches three
existing IDM strengths:

1. finite declaration / future-readout accounting;
2. size-preserving circuit-to-ledger lineage;
3. Fusion/Horn cover debt and exact dual certificates.

The primary research object is therefore no longer an invented scalar `H_N`.
It is the concrete cover graph / survivor system of Gap-MCSP, with every charge
traced to an actual pair or retained semi-filter.

---

## 7. Single research programme from this point

Work proceeds only on the following chain:

\[
\boxed{
\text{Gap-MCSP finite target}
\to\text{Fusion cover graph}
\to\text{candidate-adaptive survivor / dual margin}
\to\rho>N^{1+\varepsilon}
\to NP\not\subseteq P/poly
\to SAT\notin P/poly
\to P\ne NP.
}
\]

Every proposed invariant must be tested against:

- DAG sharing and common-subexpression elimination;
- redundant gates and DeMorgan rewrites;
- recomputation / retained-input escape routes;
- sparse patches;
- target-oracle leakage;
- fixed-distribution collapse;
- encoding-length inflation;
- the equality residual-width counterexample;
- exact finite circuits on small instances.

A proposal that survives only by assuming the desired Gap-MCSP lower bound,
MCSP recognition, SAT, or circuit equivalence is rejected as circular.

---

## 8. Claim ledger

| Item | Status |
|---|---|
| local SAT restriction/boundary verifier | finite formal candidate / executable |
| ADC finite mass arithmetic | finite formal candidate |
| robust EPSC-style capture margin | finite formal candidate |
| genuine tiny-circuit five-sample hitting support | exact finite diagnostic |
| fixed-reader amplification failure | exact finite diagnostic |
| world-bound-anchor finite amplification | exact finite diagnostic |
| essential-input shared-DAG baseline | linear formal candidate |
| direct unrestricted SAT LCCA | **OPEN** |
| Gap-MCSP `N^(1+epsilon)` unrestricted circuit LB | **OPEN** |
| MFM cover-complexity theorem | **OPEN** |
| `SAT notin P/poly` | **NOT PROVED** |
| `P != NP` | **NOT PROVED** |

The purpose of this note is to prevent further architectural diffusion: the
only acceptable next breakthroughs are a genuine MFM/LCCA lemma, a rigorous
counterexample killing a proposed route, or a verified finite experiment that
changes the MFM/LCCA formulation.
