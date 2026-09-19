# SAT through the Readout Universe + Readout Genesis lens

**Status:** research derivation.  This file does **not** claim `P != NP`.

This note applies the Readout Universe Lens Law *before* importing complexity-theory vocabulary and then checks the result against the Readout Genesis sufficiency/lineage discipline.

## 1. Exact finite translation

Let a CNF instance be `F` on variables `x_1,...,x_n` with clauses `C_1,...,C_m`.
The source is finite: no continuum or `N=infinity` premise is admitted.

Readout-Universe translation:

| SAT term | Readout term |
|---|---|
| assignment `a` | retained candidate configuration `epsilon=a` |
| clause | a finite grammar/constraint row |
| falsified clause | an obstruction readout |
| satisfying assignment | a configuration with zero obstruction |
| decision bit | terminal policy readout `Pi_F` |
| partial assignment | an accessible sub-grammar / declared intervention |
| discarded distinction | retained elsewhere, inaccessible, or proved non-load-bearing |
| deterministic computation | ordered retained trajectory / tape-indexed transform |

Define the exact finite obstruction vector

`r_F(a) = (1[C_1(a)=false],...,1[C_m(a)=false])`

and load

`V_F(a) = sum_j r_F(a)_j`.

Then, exactly,

`SAT(F)=1  <->  exists a, V_F(a)=0`,

`SAT(F)=0  <->  forall a, V_F(a)>=1`.

This is only a translation of finite SAT semantics.  It is not a complexity lower bound.

## 2. The key correction from Readout Universe

RD4 says that distinct generated histories are not silently identified at the root.  The append-only-record model shows how a visible contraction can coexist with total injective retention: the lost distinction is carried by the tape.

Therefore **RD4 does not imply that every SAT distinction must remain in working memory.**  A deterministic computation may discard a visible distinction while a larger physical/logical history remains injective.

The complexity-relevant object is instead **accessible retained load** under a declared reader.

Let

`J_t(h) = (R_t(h), T_t(h))`

be a jointly injective retained record, where `R_t` is visible/accessible to the next computational step and `T_t` is hidden or external tape.  Then

`h != h' and R_t(h)=R_t(h')  ->  T_t(h)!=T_t(h')`.

This is the **RD4 relocation lemma**: visible collapse does not destroy the distinction; it relocates it.

But if the downstream decoder reads only `R_t`, then

`R_t(h)=R_t(h') -> D(R_t(h))=D(R_t(h'))`.

Hence a load-bearing distinction that has left the accessible state must later be (i) re-accessed from retained tape, (ii) recomputed from still-accessible information, or (iii) proved irrelevant to the declared terminal readout.  This is the Readout-Universe sharpening of the Genesis Retain--Recompute--Resolve trichotomy.

## 3. Reader-relative completion

For an UNSAT decision, a sound finite completion certificate consists of cells `B_1,...,B_k` of assignment space with:

1. **coverage:** every assignment belongs to at least one `B_i`;
2. **local obstruction:** every assignment in each `B_i` falsifies at least one declared clause (or satisfies a stronger independently verified rejection predicate).

Then every assignment has positive obstruction and the formula is UNSAT.

This is the exact discrete counterpart of a fail-closed completion gate:

`resolved cells + zero uncovered witness tail -> exact NO readout`.

The accompanying Coq file proves this generic coverage theorem.  The Python fixture constructs and independently verifies the special DPLL/subcube instance.

## 4. Why this still does not prove P != NP

A general polynomial-time SAT decider is **not required** to emit a DPLL tree, a resolution proof, or one particular completion certificate.  Readout Universe A4 (accessibility) makes this explicit: derivability, existence, and current accessibility are distinct notions.

Therefore the missing theorem cannot be

`every UNSAT computation has a large DPLL certificate`.

It must quantify over the actual accessible trajectory of an arbitrary deterministic machine/circuit.

## 5. New proof ladder

The native ladder is now:

1. **RD translation** — finite SAT becomes a retained-difference obstruction problem. `[definition]`
2. **RD4 relocation** — a collision in visible state forces the distinction into the complementary retained record when the joint record is injective. `[Coq candidate]`
3. **No-early-collapse at the reader** — a decoder cannot recreate a decision distinction from identical accessible records. `[Coq candidate / existing decision-readout theorem]`
4. **Finite completion soundness** — a complete cover by locally rejected cells proves exact NO. `[Coq candidate]`
5. **RRR accessibility law** — a still-load-bearing distinction that leaves accessible state must be retained/re-accessed, recomputed, or semantically resolved. `[derived schema; universal cost form open]`
6. **Universal accessible-capacity theorem** — bound how much reader-relevant obligation one arbitrary Boolean gate / machine step can discharge after allowing sharing, tape access and recomputation. **[OPEN]**
7. **SAT demand theorem** — construct an explicit SAT family whose required accessible semantic demand exceeds every polynomial aggregate capacity. **[OPEN]**
8. Steps 6+7, with the already-built circuit/ledger transfer, would yield a superpolynomial SAT circuit lower bound and hence `P != NP`.

## 6. The load-bearing object to search for

Do **not** count total histories, all assignments, or all residual functions.  Equality is the standing negative control: exponentially many residual contexts can be handled by a linear-size shared circuit.

The desired quantity must therefore be reader-relative and sharing-aware.  Write provisionally

`AOb_t(F,C)` = accessible unresolved obstruction burden at cut `t` of circuit/trajectory `C`.

A valid candidate must satisfy all of:

- **reader-relative:** differences invisible to every declared future readout are quotiented out;
- **access-aware:** hidden tape does not count as current working information unless a future step actually reads it;
- **sharing-aware:** one shared subcomputation may discharge many syntactic obligations and is charged once;
- **recomputation-aware:** forgotten information may be rebuilt, but rebuilding consumes trajectory cost;
- **representation-stable:** renaming or harmless re-encoding cannot manufacture hardness;
- **answer-oblivious:** computing the quantity may not call SAT or circuit minimization.

The target theorem would have the form

`AOb(F_n) <= Capacity(C_n)` for every exact circuit `C_n`,

while an explicit family satisfies

`AOb(F_n) / per_gate_capacity(n) = n^{omega(1)}`

(or the weaker exact condition needed to escape every polynomial-size family).

At present this final pair is **Open**.  The contribution of this note is to remove an invalid inference from root-level RD4 to machine working-memory retention and to replace it with an accessibility-correct target.

## 7. Falsifiers / guards

Reject any proposed continuation if it:

- treats ontological/global tape retention as mandatory circuit working memory;
- counts a distinction that no declared future reader can expose;
- forbids recomputation or sharing without proving the restriction is without loss of generality;
- defines hardness by minimum circuit size or by the target SAT answer;
- derives an unrestricted lower bound only for a restricted proof system;
- silently promotes finite diagnostics into `P != NP`.

## Source lineage

Internal sources used for this translation:

- Readout Universe `v2/INFORMATION_DNA.md`: RD1--RD9; especially RD4 retention/injectivity and RAR A3--A4.
- Readout Universe `v2/TRANSLATION_PROTOCOL.md`: Lens Law, residual form and identifiability/accessibility gate.
- Readout Universe `v2/APPEND_ONLY_RECORD.md`: visible loss with injective tape retention.
- Readout Genesis Universal Technical Whitepaper v1.2.0: P4 retention-before-persistence, strong future-reader equivalence, sufficient-before-quotient rule, mandatory tape and closure/lineage ledger, and no borrowing of certainty across layers.
