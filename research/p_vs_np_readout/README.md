# Computational Readout Completion for P vs NP

**Status:** research programme / open. **This directory does not claim a proof of `P != NP` or `P = NP`.**

The purpose of this lane is to transfer the strongest reusable ideas from Readout Genesis, IDM and the
Navier--Stokes readout/EPSC work into complexity theory without importing the target answer or silently
restricting the computational model.

The key correction made at the start is simple but load-bearing:

> A small sufficient readout is not evidence of an easy decision problem.  Every Boolean decision
> problem has the one-bit readout `q(x)=L(x)`.  The cost of **constructing** the readout is therefore part
> of the theorem.

This is also consistent with the Readout Genesis firewall that forbids `target_answer_as_parameter`.

---

## 1. Decision-readout objects

For each input length `n`, let

\[
X_n = \{\text{valid encodings of instances of length }n\},
\qquad
L_n:X_n\to\{0,1\}.
\]

For SAT, `L_n(F)=1` iff `F` is satisfiable.

A decision readout is a map

\[
q_n:X_n\to R_n
\]

with a decoder

\[
D_n:R_n\to\{0,1\}.
\]

It is **exactly decision-sufficient** when

\[
\boxed{D_n(q_n(x))=L_n(x)\quad\forall x\in X_n.}
\]

Define a mixed decision fiber by

\[
\exists x,y\in X_n:
q_n(x)=q_n(y),\qquad L_n(x)\ne L_n(y).
\]

Equivalently, define the finite worst-case omitted-decision defect

\[
\beta_{\rm dec}(q_n)=
\begin{cases}
0,&L_n\text{ is constant on every fiber of }q_n,\\
1,&\text{some fiber contains both labels.}
\end{cases}
\]

The Coq file `formal/IDM_DecisionReadout.v` machine-formalizes the structural direction:
if a mixed fiber exists, no decoder from that readout can be correct on all instances.

---

## 2. The first negative theorem: one-bit degeneracy

For every Boolean language `L`, choose

\[
q(x)=L(x),\qquad D(b)=b.
\]

Then

\[
D(q(x))=L(x)
\]

with a one-bit readout.

Therefore none of the following, by itself, can separate P from NP:

* readout cardinality;
* output dimension;
* number of decision classes;
* information-theoretic compression of the **final answer**.

The missing quantity is computational construction cost.

---

## 3. Resource-aware factorization theorem

Let `C` be any deterministic computational class that contains the identity map and is closed under
composition.  Then

\[
\boxed{
L\in C
\iff
\exists q,D\in C\text{ such that }L=D\circ q.
}
\]

**Proof.**

* If `q,D in C`, closure under composition gives `D o q in C`, so `L in C`.
* If `L in C`, take `q=L` and `D=id`.

For `C=P`, this gives

\[
\boxed{
SAT\in P
\iff
\text{SAT has a polynomial-time constructible, polynomial-time decodable exact readout.}
}
\]

This theorem is intentionally a **boundary result**, not a solution: merely asking for an efficient
minimal sufficient quotient is exactly as hard as the original P-vs-NP question.

This is the complexity-theoretic analogue of the point reached in the finite Navier--Stokes lane:
a minimal exact sufficient quotient can exist mathematically while the acceleration question becomes
"compute the quotient efficiently."  In SAT the effect is even sharper because the unconstrained
minimal decision quotient has only two labels.

---

## 4. Computational epsilon-completion (CEPSC)

To transfer the EPSC logic, use a refinement family

\[
q_{n,0},q_{n,1},\ldots,q_{n,K}
\]

with explicit restriction/forgetting maps between adjacent levels.  At level `k`, the decision defect
is whether any retained fiber still mixes YES and NO instances:

\[
\beta^{\rm dec}_{n,k}(r)=1
\iff
\exists x,y:\ q_{n,k}(x)=q_{n,k}(y)=r,
\ L_n(x)\ne L_n(y).
\]

An exact fail-closed decision gate is possible only when

\[
\boxed{\beta^{\rm dec}_{n,k}(q_{n,k}(x))=0.}
\]

For complexity, however, a second requirement is essential:

\[
\boxed{
C(q_{n,k})+C(D_{n,k})\le \operatorname{poly}(n).
}
\]

A sequence whose defect tends to zero only on average, or only for sampled formulas, is an
average-case/heuristic result and is not a proof that SAT is in P.

A sequence requiring superpolynomial `k`, superpolynomial construction work, or a SAT oracle in the
readout has not escaped NP-hardness.

---

## 5. Exact finite collision fixture

`readout_sat_frontier.py` contains two 3-CNF formulas with four variables and eight clauses.
The syntactic profile readout retains

* number of variables;
* number of clauses;
* multiset of clause lengths;
* multiset of per-variable positive/negative occurrence counts.

The two formulas have the **same** profile readout, while one is SAT and the other is UNSAT.  Hence
that readout has a mixed decision fiber.

Moreover, disjoint renamed copies amplify the collision to arbitrarily large instances.  If `A` is
the satisfiable fixture and `B` the unsatisfiable fixture, then for every `k>=1`,

\[
A^{\sqcup k}\text{ is SAT},\qquad
B^{\sqcup k}\text{ is UNSAT},
\]

while the profile readouts remain equal.  Thus this particular answer-oblivious coarse readout fails
at unbounded input size, not only in one toy case.

This is a genuine lower bound for the declared readout family.  It is **not** a lower bound for all
polynomial-time algorithms.

---

## 6. Barrier audit before any P-vs-NP claim

Any candidate proof in this programme must be rejected if it lives entirely inside one of the known
barriers.

### B1. Relativization

Baker--Gill--Solovay constructed oracles `A,B` with

\[
P^A=NP^A,
\qquad
P^B\ne NP^B.
\]

The collision lemmas and the abstract readout-factorization theorem relativize: they remain true after
adding an oracle to both constructor and decoder.  Therefore **those lemmas alone cannot settle
P vs NP**.

A successful next theorem must contain a genuinely non-black-box ingredient that does not survive an
arbitrary oracle substitution.

### B2. Algebrization

Replacing Boolean objects by low-degree polynomial extensions is not automatically enough.  The
Aaronson--Wigderson algebrization barrier was designed precisely to capture many such
arithmetization-based arguments.  A polynomial/readout attack must state why its load-bearing step
does not algebrize.

### B3. Natural proofs

A circuit lower-bound route based on a large, efficiently recognizable property separating hard from
small-circuit functions risks the Razborov--Rudich Natural Proofs barrier.  If the programme moves to
circuits, every proposed property must be audited for constructivity, largeness and usefulness.

---

## 7. The current load-bearing target

The next theorem cannot merely say "two formulas collide under a chosen summary."  It must constrain
**every polynomial-time constructor** without assuming the conclusion.

A useful target form is:

### Uniform Non-Black-Box Readout-Cost Lower Bound (UNRCLB) — OPEN

For every deterministic machine `M` and every constant `c`, if `M` is correct on all 3-SAT instances,
then there are arbitrarily large inputs `F` for which

\[
T_M(F)>|F|^c.
\]

To make this a Readout theorem rather than a renamed P-vs-NP statement, the programme seeks an
intermediate machine-explicit object

\[
q_{M,t}(F)
\]

constructed from the actual transition table, retained computation history and formula structure,
with four required properties:

1. **No target leakage.** `q_{M,t}` cannot call SAT, an NP oracle, or insert the correct output.
2. **Machine explicit.** The construction inspects `M`'s transition structure; it is not a black-box
   input/output argument.
3. **Decision obstruction.** If `M` halts too early, the induced readout must have a certified mixed
   YES/NO fiber or another independently checkable correctness contradiction.
4. **Barrier escape.** The load-bearing implication must be shown not to relativize, and any algebraic
   component must be checked against algebrization.  A circuit property must be checked against Natural
   Proofs.

At present property 3 for **all** polynomial-time machines is OPEN; proving it would be the actual
breakthrough.

---

## 8. Two attack lanes to pursue

### Lane A — non-black-box machine/readout diagonalization

Try to construct adversarial 3-CNF families from the transition structure of a candidate polynomial
SAT decider.  The first test is whether the construction suffers the classical self-encoding size
blow-up: encoding `T(n)` computation steps normally costs order `T(n)` or more, so a naive fixed-point
formula cannot defeat an arbitrary `n^c` machine.  Any claimed diagonal construction must close this
size equation explicitly rather than hide it.

### Lane B — omitted-witness completion / proof complexity

For a NO instance, interpret the unexamined assignment space as an omitted-witness tail.  A rejection
certificate must establish that no omitted assignment satisfies the formula.  Restricted proof
systems (resolution, bounded-width systems, local consistency, restricted branching programs) permit
real lower bounds and therefore provide a controlled test bed for CEPSC.

The missing bridge is universal: a lower bound for one restricted proof system does not constrain an
arbitrary polynomial-time SAT algorithm.  Any upgrade must state a sound simulation theorem from the
full machine model into the certificate/readout model.  Without that bridge the result remains a
restricted-model lower bound.

---

## 9. Immediate research protocol

Every proposed P-vs-NP lemma is classified as one of:

* `Th_coqc` — finite structural statement machine-checked in Coq;
* `exact` — exact finite computation/proof outside Coq;
* `finite_diagnostic` — bounded experiment;
* `Dr` — declared mathematical derivation using standard external theorems;
* `Open` — the load-bearing unproved step.

No finite experiment is promoted to a complexity-class separation.

Current ledger:

| object | status |
|---|---|
| mixed fiber blocks exact decoding | `Th_coqc` candidate file committed |
| one-bit answer readout is exact | `Th_coqc` candidate file committed |
| sufficient coarse readout lifts to a refinement | `Th_coqc` candidate file committed |
| profile-readout SAT/UNSAT collision | `exact` finite fixture |
| collision amplification for profile readout | `Dr` + executable finite checks |
| resource-aware factorization equivalence | standard exact derivation |
| pure readout lemmas alone settle P vs NP | **refuted by barrier audit** |
| UNRCLB for unrestricted polynomial-time SAT machines | `Open` |

The research lane should be judged by whether it closes the last row without breaking the three
barrier checks, not by the number of finite collisions generated.

---

## References used for the barrier audit

* Stephen Cook, *The P versus NP Problem*, Clay Mathematics Institute problem description.
* Theodore Baker, John Gill, Robert Solovay, "Relativizations of the P=?NP Question," SIAM Journal on
  Computing 4(4), 1975, 431--442, DOI: 10.1137/0204037.
* Alexander Razborov, Steven Rudich, "Natural Proofs," Journal of Computer and System Sciences 55(1),
  1997, 24--35.
* Scott Aaronson, Avi Wigderson, "Algebrization: A New Barrier in Complexity Theory," ACM Transactions
  on Computation Theory 1(1), 2009.
