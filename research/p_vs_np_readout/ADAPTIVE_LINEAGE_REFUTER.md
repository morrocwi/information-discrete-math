# Adaptive Lineage Refuter (ALR): the Current Unrestricted-Circuit Frontier

**Status:** research target / open.  
**Claim boundary:** no SAT circuit lower bound is proved here.

## 1. Why the lane pivots again

The static fusion cover formulation is valid and powerful, but two successive audits eliminate the simplest ways of extracting a superpolynomial SAT lower bound:

1. terminal readout size and pure injectivity have only linear information headroom;
2. a single fixed distribution over semi-filters has only `O(n)` power under the probabilistic-counting limitation inherited from Razborov's approximation method.

For general non-monotone circuits, Oliveira's fusion exposition explicitly points to an **adaptive** strategy: first expose the candidate circuit `C`, then choose an adversarial distribution over semi-filters tailored to the gate-pair family `Gamma_C`.

Recent constructive gate-elimination work gives a second calibration point. A constructive lower bound supplies a **refuter**: an efficient procedure that takes a too-small circuit and returns a concrete input on which that circuit fails. This is the right operational target for a Readout/lineage attack.

## 2. Refuter target

Fix an explicit Boolean function family `f_n`; ultimately `f_n=SAT_n` under a frozen canonical encoding.

For a size bound `s(n)`, a refuter is an algorithm

\[
R_n:C\longmapsto x
\]

such that for every circuit `C` of size at most `s(n)`,

\[
\boxed{C(x)\ne f_n(x).}
\]

A refuter for every polynomial size bound against `SAT_n` would imply

\[
SAT\notin P/poly
\Longrightarrow
P\ne NP.
\]

This is stronger than an existential lower bound, so it is not expected to be easier automatically. Its advantage for IDM is that every stage has an explicit finite input/output contract.

## 3. Lineage object

For a DeMorgan circuit DAG `C`, define a gate record

\[
L_g=(g,\operatorname{op}(g),\operatorname{pred}(g),S_g,\mathsf{fanout}(g)),
\]

where `S_g` denotes the semantic set computed by gate `g` when needed for mathematical analysis, but the **algorithmic** refuter is not permitted to materialize an exponential truth table.

The retained lineage graph is

\[
\mathcal L(C)=\{L_g:g\in V(C)\}
\]

with sharing preserved. This is the information that static fusion throws away when it keeps only the unordered family of intersection pairs.

The research hypothesis is not that lineage itself proves hardness. It is that any new adaptive adversary must exploit constraints among many gate pairs that arise because they belong to one small shared DAG.

## 4. Adaptive semi-filter adversary

Given `C`, let `Gamma_C` be the fusion pairs induced by its AND gates after the standard normalization. An adaptive adversary may choose

\[
\mu_C
\]

after seeing `L(C)`.

A sufficient probabilistic refutation condition is

\[
\forall p\in\Gamma_C:
\Pr_{\mathcal F\sim\mu_C}[p\text{ kills }\mathcal F]<1/|\Gamma_C|.
\]

Then a union bound gives positive probability that one semi-filter survives all gate pairs.

This condition alone is not a method: a point mass on a known survivor is trivial. The algorithmic problem is to generate `mu_C` from circuit lineage without solving the target equivalence problem by brute force or oracle.

## 5. Readout-native construction protocol

A candidate ALR must obey the following pipeline:

\[
C
\xrightarrow{\text{normalize}}
\mathcal L(C)
\xrightarrow{\text{declare retained cuts}}
\mathcal R_C
\xrightarrow{\text{adaptive adversary}}
\mu_C
\xrightarrow{\text{decode}}
x.
\]

The retained state `R_C` may contain only quantities computable from the circuit syntax plus explicitly certified local facts. Candidate quantities include:

- reconvergent fanout structure;
- retained boundary width across chosen cuts;
- gate dominators / unavoidable lineage bottlenecks;
- repeated subcomputations;
- exact rank of explicitly represented local transfer matrices;
- declaration timing of input distinctions;
- normalized rewrite/simplification state.

The target answer `SAT(x)` cannot be inserted into `R_C`.

## 6. Convergent simplification as a canonical preprocessor

Carmosino--Dang--Jackman (2026) formalize circuit simplification as a convergent term-graph rewriting system over the DeMorgan and `{AND,OR,XOR}` bases. Convergence is valuable here because it gives a canonical simplified structural object up to the paper's equivalence notion, independent of rewrite order.

This suggests an admissible front end:

\[
C\mapsto N(C)
\]

where `N(C)` is the convergently simplified circuit. ALR should work on `N(C)`, so purely syntactic redundancy cannot inflate or disguise the retained-lineage measures.

This does **not** import their lower bound as ours. It is a normalization discipline for candidate invariants.

## 7. A necessary progress lemma

A lineage measure `Phi` becomes useful only if we can prove both:

\[
\Phi(N(C))\le B(|C|)
\]

for every small circuit, and

\[
\Phi(f_n)>B(s(n))
\]

for the target function in a representation-robust sense.

All earlier simple semantic measures fail here: rank, degree, log residual count and raw retained bits have only linear headroom or apply to restricted models.

Therefore ALR should search for a **multi-gate obstruction**, not a one-gate scalar progress potential. The natural unit is a lineage pattern or cut family whose simultaneous satisfaction is constrained by sharing.

## 8. Candidate multi-gate objects

### 8.1 Reconvergence matrix

For a family of circuit cuts `K_1,...,K_t`, record which retained distinctions are produced, forgotten and later reconverge. A candidate matrix

\[
M_C(i,j)=1
\]

may indicate that distinction `i` must cross/re-enter cut `j`. Rank alone is not enough, but forbidden submatrices or expansion properties might obstruct small DAGs.

### 8.2 Readout cut hypergraph

Construct a hypergraph whose vertices are gates/distinctions and whose hyperedges are minimal live boundaries needed to preserve a family of target interventions. Unlike OBDD width, the circuit is free to choose arbitrary sharing and order; the measure must be minimized over all cuts/normalizations before it can constrain unrestricted circuits.

### 8.3 Adaptive Horn witness

Rather than weighting all semi-filters globally, construct a semi-filter incrementally against the **actual ordered gate lineage**. At each gate, preserve only distinctions that remain relevant to future gates. This is the closest analogue of RCP/Readout closure. The hard lemma is to show that a small circuit cannot force bottom before the output while the adversary obeys the local update rule.

## 9. Model guards

An ALR candidate is rejected if any of the following occurs:

1. it enumerates the complete truth table of `C` or `SAT_n`;
2. it calls SAT, Circuit Equivalence, MCSP, or a comparably hard oracle inside the refuter;
3. it proves only an OBDD/formula/branching-program lower bound while claiming unrestricted circuits;
4. its distribution is actually fixed before seeing `C` and claims super-linear power from counting;
5. its measure changes under harmless circuit rewrites and the proof depends on that artifact;
6. it assumes every gate computes a distinct function or ignores fanout sharing;
7. it uses semantic sets `S_g` as if they were polynomial-size explicit data without proving how they are represented.

## 10. Immediate implementation plan

1. Implement a small DeMorgan circuit DAG datatype with sharing.
2. Implement semantics only for bounded diagnostics (`n<=4`) and keep syntax as the scalable representation.
3. Implement convergent/local normalization rules that are independently checked against truth tables in the bounded regime; do not claim identity with the 2026 rewrite system until every rule/scope is matched.
4. Extract actual AND-gate lineage `Gamma_C`.
5. Build the corresponding tiny fusion/Horn instance and compute: integral cover, fractional cover, and candidate-adaptive survivor.
6. Generate pairs of extensionally equal circuits with different syntax and ensure normalization removes fake differences.
7. Search for lineage statistics correlated with the minimum refutation size, then adversarially construct circuits that break each statistic.
8. Promote only a statistic that survives rewrite, sharing and basis audits to a theorem candidate.

The current open objective is not “find another hard SAT instance.” It is to find a **canonical, multi-gate lineage obstruction** that a small unrestricted circuit cannot bypass.
