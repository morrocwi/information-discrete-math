# Readout Transform Complexity: the Missing Resource in a P-vs-NP Attack

**Status:** structural boundary / research definition.  
**Claim boundary:** no P-vs-NP separation is claimed.

The accumulated results in this branch force a distinction that was implicit in IDM but becomes
load-bearing in complexity theory:

\[
\boxed{
\text{information retained by an answer}
\neq
\text{computational work needed to construct that answer}.
}
\]

SAT makes the separation extreme.  Its terminal decision readout contains one bit, but the minimum
uniform cost of constructing that bit is exactly the open problem.

---

## 1. Input-information ceiling

Let the encoded input length be `n`, so the legal instance set satisfies

\[
X_n\subseteq\{0,1\}^n.
\]

Then

\[
|X_n|\le 2^n,
\qquad
\log_2|X_n|\le n.
\]

Hence a lower-bound proof based **only** on the need to distinguish source inputs by an injective
binary retained state can force at most `n` bits of retained information.

The IDM Declaration Bound reaches exactly this kind of ceiling on its hard deferred-query family: all
`2^n` source words must remain distinguishable, forcing `n` retained bits in the worst case.

This is a sharp information lower bound, but it is not a superpolynomial time lower bound.

---

## 2. Why counting more trajectories does not fix it

A computation may have many possible states or histories across all inputs, but a polynomial-space
machine can already have exponentially many possible configurations while storing only a polynomial
number of bits at one time.  Counting the global set of histories therefore does not imply that one
input needs a long trajectory.

To lower-bound time, the proof must constrain the **allowed transition that turns one retained state
into the next**.

This is the point where a pure Readout-equivalence argument ends and computational complexity begins.

---

## 3. Transform complexity

Fix a computational model `M` with a declared primitive operation/transition set.  For a readout
function

\[
f_n:X_n\to\{0,1\},
\]

define its transform complexity schematically as

\[
\boxed{
\mathrm{RTC}_{\mathsf M}(f_n)
:=
\min\{\text{cost of an admissible }\mathsf M\text{-construction computing }f_n\}.
}
\]

The exact cost type depends on the model:

- Turing/RAM model: worst-case transitions/time plus work space;
- Boolean circuit model: gate count/depth;
- branching program: nodes/length/width;
- OBDD: ordered nodes/width;
- proof system: proof/refutation size, degree, width and space;
- RCP/RFT: work tokens, retained boundary and recomputation ledger.

The information content of the terminal answer can remain one bit throughout.

---

## 4. P-vs-NP target in this language

For a standard uniform deterministic model,

\[
P=NP
\]

would imply a fixed polynomial `p` such that

\[
\mathrm{RTC}_{\rm uniform}(SAT_n)\le p(n).
\]

Thus a sufficient separation theorem has the form

\[
\boxed{
\forall c\;\exists^\infty n:
\mathrm{RTC}_{\rm uniform}(SAT_n)>n^c.
}
\]

If instead one proves that SAT needs superpolynomial **unrestricted Boolean circuit size**, the result is
stronger: it separates NP from `P/poly`, and hence also separates P from NP.

---

## 5. The universal-simulation guard

A lower bound inside IDM's native FOLD/DECISION/RCP operation set implies a lower bound for ordinary P
only if there is a separately proved polynomial-overhead simulation theorem

\[
\boxed{
P\subseteq \mathrm{Poly}(\mathsf{IDM\text{-}native})
}
\]

for the exact computational model used by the lower bound.

A catalogue covering many solver kinds is not such a theorem.  Without this simulation bridge, an IDM
lower bound is a lower bound for an IDM-declared machine class and must remain labelled that way.

Conversely, making the IDM primitive set universal by allowing an arbitrary polynomial-time
subroutine would trivialize the representation distinction and simply restate P versus NP.

---

## 6. Current obstruction ladder

The branch now has a model ladder whose strength is explicit:

| layer | retained/transform obstruction | status |
|---|---|---|
| coarse syntactic SAT readout | mixed SAT/UNSAT fiber | exact finite fixture; weak model |
| fixed ordered read-once | future residual functions force width | exact theorem pattern / OBDD-known |
| DAG evaluator with recomputation | black pebbling time-space | model reconciliation / known theory |
| algebraic proof language | weak-rank invariant / PCR-SA hardness | strong 2026 external results |
| unrestricted Boolean circuit | superpolynomial circuit lower bound for an NP function | OPEN |
| uniform deterministic polynomial time | superpolynomial SAT transform cost | OPEN = load-bearing P-vs-NP frontier |

The purpose of the lower layers is not to masquerade as the last row.  They are controlled test beds
for discovering an invariant that survives progressively more powerful computational representations.

---

## 7. Candidate invariant requirements

A useful new invariant `K` for the unrestricted frontier should satisfy all of:

1. **efficient source definition:** `K` is defined without the SAT answer or an NP oracle;
2. **subadditivity/composition law:** one cheap computation step can change `K` only by a bounded amount;
3. **large endpoint gap:** an explicit SAT family requires a superpolynomial total change or burden;
4. **representation robustness:** arbitrary polynomial-time re-encoding cannot erase the burden for free;
5. **nonrelativizing load-bearing step:** the contradiction does not survive arbitrary oracle
   substitution unchanged;
6. **algebrization/Natural-Proofs audit:** if algebraic or circuit properties are used, the relevant
   barrier hypotheses are checked explicitly.

The missing ingredient is property 2 together with 3 for a model broad enough to simulate all of P.

---

## 8. Where IDM may still contribute

IDM already supplies three pieces that are useful for searching for such an invariant:

- exact finite invariants and rank/determinant algebra;
- retained boundary and causal lineage accounting;
- fail-closed cost and claim ledgers.

The research question is therefore sharpened to:

\[
\boxed{
\text{Can a retained invariant be found whose change per ordinary computation step is bounded,}
\newline
\text{but whose SAT endpoint burden is superpolynomial?}
}
\]

If no such invariant can be made representation-robust, the Readout programme remains a framework for
restricted lower bounds rather than a route to P versus NP.  That distinction is now explicit and
testable.
