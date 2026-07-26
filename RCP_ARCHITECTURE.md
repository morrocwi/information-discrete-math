# Readout-First Retained Contraction Architecture

This document explains the architecture behind Retained Contraction Protocol
(RCP) from the information philosophy of Information Discrete Mathematics.
The executable specification is
[`tools/retained_contraction_protocol.py`](tools/retained_contraction_protocol.py);
the many-readout engine is
[`benchmarks/retained_reverse_compiler.py`](benchmarks/retained_reverse_compiler.py).

## 1. The architectural decision

Conventional tensor pipelines commonly begin with one of these objects:

- a complete tensor;
- a black-box function from which a tensor is sampled;
- a list of arrays plus an Einstein summation expression.

RCP begins earlier. It first asks:

> Which distinctions are retained, which couplings are actually given, which
> terminal readouts are requested, and at what finite resolution can two
> terminal readouts no longer be distinguished?

The compiler therefore does not treat the full Cartesian tensor
\(n^d\) as the default mathematical object. The default object is the finite
retained record

\[
\mathcal R_\lambda =
\left(G_R,F,B,Q,\varepsilon,\mathcal B\right),
\]

where:

- \(\lambda\) is the declared finite resolution;
- \(G_R=(V_R,E_R,s)\) is the retained coupling hypergraph;
- \(F=\{f_e\}_{e\in E_R}\) is the set of finite local factor tables;
- \(B\subseteq V_R\) is the exposed tensor boundary;
- \(Q\) is the list of promised terminal readouts;
- \(\varepsilon\) is the declared indistinguishability tolerance;
- \(\mathcal B\) is the work/storage budget.

The full tensor

\[
T(i_1,\ldots,i_d)=\prod_{e\in E_R}f_e(i_e)
\]

is a possible derived readout of this record. It is not automatically
materialized.

## 2. Architecture at a glance

```text
problem statement
      │
      ▼
translation gate ── declare λ, retained distinctions, couplings
      │
      ▼
retained hypergraph IR ── local factor tables, never implicit full tensor
      │
      ▼
terminal query boundary ── partition + named axis readouts
      │
      ▼
structural planner ── admissible min-fill elimination path
      │
      ▼
RCP preflight ── planned work, peak retained width, lineage digest
      │ ACCEPT
      ▼
forward contraction DAG ── partition readout
      │
      ▼
reverse lineage pass ── adjoints of every retained local record
      │
      ▼
query extraction ── all axis moments in one compiled program
      │
      ├──────── external/independent witness
      ▼
RCP certificate ── ACCEPT / HOLD / BLOCK + tier + honesty fence
```

The control plane is RCP. The execution engine can be the shipped reverse
compiler, an `opt_einsum` backend, another tensor compiler, or a future
formally verified executor.

## 3. Information-philosophical principles

### 3.1 Translation precedes formalization

A tensor is not imported as an unexplained object “from the world.” It is
translated into:

- named distinctions \(V_R\);
- finite sizes \(s(v)\);
- local couplings \(E_R\);
- readable values \(F\);
- a declared terminal boundary \(B,Q\).

This prevents the implementation from confusing its representation with the
thing represented. The factor graph is a finite readout model at
\(\lambda\), not a claim that reality is literally a Python array.

### 3.2 Relations precede the global state space

The full space contains

\[
\prod_{v\in V_R}s(v)
\]

configurations. But the information supplied by the problem may contain only
unary and pairwise couplings. RCP retains those supplied relations directly.

For the benchmark, eleven axes with four states have \(4^{11}=4{,}194{,}304\)
global entries. The declared local record has only 284 factor entries. Creating
the global tensor first would add distinctions the terminal query never asks
the machine to expose.

This is not a metaphysical proof that global configurations do not exist. It
is a computational rule: do not pay to form an unrequested representation.

### 3.3 The terminal readout defines relevance

RCP declares all promised outputs before execution. In the benchmark:

\[
Q=(Z,\mu_1,\ldots,\mu_{11}),
\]

where \(Z\) is the partition readout and every \(\mu_i\) is a named first
moment.

An intermediate is relevant only insofar as it can affect \(Q\). This reverses
the conventional order “construct a general representation, then ask a
question.” RCP compiles the representation around the question.

### 3.4 Contraction is closure, not annihilation

When an internal axis \(v\) is contracted, its name no longer appears on the
exposed scope. Its influence is accumulated:

\[
m(S)=\sum_{i_v}\prod_{f\in\operatorname{bucket}(v)}f(i_v,i_S).
\]

The distinction is closed at the boundary, not treated as though it never
existed. The generated message \(m\) retains the effect needed by later
readouts.

### 3.5 The path is finite causal lineage

An elimination path is not merely a performance hint. It is the causal order
that transforms local retained records into the terminal record.

Every RCP step records:

- the eliminated distinction;
- the records that entered;
- joined and outgoing scopes;
- arithmetic work;
- outgoing retained table size.

The SHA-256 lineage digest binds the declaration, factors, and path. It is a
replay identifier, not a mathematical proof by itself.

### 3.6 Equality is always declared at a resolution

For floating execution, RCP never upgrades binary64 equality into unrestricted
mathematical identity. It tests:

\[
\delta_\lambda(C_p,C_w)
=
\max_k |C_p[k]-C_w[k]|
\leq \varepsilon.
\]

The benchmark uses \(\varepsilon=10^{-12}\). Its observed maximum difference
against the external witness is \(2.776\times10^{-16}\). The certificate tier
is therefore `finite_diagnostic`, not `Th_coqc`.

### 3.7 Resource cost is part of admissibility

A readout that cannot be retained inside the declared machine envelope is not
an admissible execution. Before tick 0, RCP computes:

\[
\operatorname{Work}(p),\qquad
\operatorname{PeakRetained}(p).
\]

Exceeding the declared budget returns `BLOCK`; a run is not launched in the
hope that the operating system will decide its mathematical status.

### 3.8 Failure is retained as a result

RCP has three terminal control states:

- `ACCEPT`: the declared finite readout is admissible and witnessed;
- `HOLD`: a readout exists but its preservation evidence is insufficient;
- `BLOCK`: the declaration, path, resource envelope, or consumer contract is
  invalid.

The architecture retains uncertainty instead of converting it into a silent
number.

### 3.9 Validation is horizontal

The certificate does not become valid because an authority names it valid. It
contains executable evidence: declaration, lineage, work ledger, output,
witness, differences, and tolerance. Another person can run the same
benchmark, challenge the workload, replace the witness, or falsify the
implementation.

External literature is used to identify prior algorithms and prevent novelty
overclaiming—not as a substitute for execution.

## 4. The many-readout compiler

### 4.1 Why the first prototype was insufficient

The first coupled compiler computed:

1. the partition \(Z\);
2. one modified contraction for each of eleven moments.

It therefore traversed the same retained graph twelve times. Reusing only the
elimination order preserved correctness but not the maximum reusable
information.

### 4.2 One forward pass

The reverse compiler performs the admitted elimination once:

\[
Z=C_p(F).
\]

It retains the finite contraction DAG—not the full tensor. On the 11-D
benchmark the maximum temporary factor has only 16 elements because the
induced width is 2.

### 4.3 One reverse lineage pass

The compiler then sends terminal influence backward through the exact executed
DAG. If \(a_m\) is the adjoint of a generated message \(m\), the finite chain
rule produces adjoints for every input factor in its bucket.

For a unary factor \(u_i(k)\), the partition derivative satisfies:

\[
\frac{\partial Z}{\partial u_i(k)}
=
\sum_{\text{all configurations except }i}
\prod_{e\neq u_i}f_e.
\]

The unnormalized first moment is therefore:

\[
N_i
=
\sum_k
x_i(k)\,u_i(k)\,
\frac{\partial Z}{\partial u_i(k)},
\qquad
\mu_i=\frac{N_i}{Z}.
\]

All eleven moments are extracted from one forward and one reverse traversal.
No \(4^{11}\) tensor is formed, and no contraction is repeated once per axis.

### 4.4 Symbolic work plan

Before execution, `plan_reverse_work` prices:

- local factor sampling;
- forward multiplies and accumulations;
- reverse multiplies and accumulations;
- terminal moment extraction.

For the benchmark:

| component | work tokens |
|---|---:|
| local factor samples | 284 |
| forward multiply | 1,465 |
| forward accumulate | 404 |
| reverse multiply | 5,408 |
| reverse accumulate | 1,296 |
| terminal readouts | 143 |
| **total** | **9,000** |

The executor independently produces the same ledger. A mismatch returns
`HOLD`.

## 5. Why this architecture can beat the comparison methods

### 5.1 Against repeated `opt_einsum`

`opt_einsum` is designed to choose and execute efficient pairwise contraction
paths. The baseline reuses its greedy path but executes one contraction for
each of twelve outputs.

RCP compiles the set of outputs as one query program. It pays once for the
forward contraction and once for reverse lineage. The benchmark therefore
measures a speed advantage while retaining the same 16-element peak
intermediate.

This does **not** prove that the RCP path optimizer is better—RCP currently
uses deterministic min-fill, while `opt_einsum` supplies more path strategies.
The measured advantage comes from query fusion and reverse reuse.

### 5.2 Against TT-SVD

The Tensor-Train representation writes a global tensor approximately as a
chain of three-index cores. This can reduce storage from exponential to
\(O(dnr^2)\) when TT ranks remain small.

TT-SVD nevertheless begins from a complete input tensor. On the benchmark it
must receive 4,194,304 entries before producing 2,080 TT-core entries. RCP
receives 284 declared local factor entries and never constructs the global
array.

RCP wins because the problem already discloses a low-width coupling graph. It
does not first forget that structure and then infer a compressed global
representation.

### 5.3 Against TT-cross

TT-cross is stronger than dense TT-SVD when only a black-box tensor entry
function is available. It infers a low-rank TT representation from selected
entries rather than all \(n^d\) entries.

The callable TT-cross baseline queried 14,848 entries (9,760 unique) and built
2,080 TT parameters. RCP used 284 local factor entries and a peak intermediate
of 16 because its input explicitly declared the coupling graph.

The architectural distinction is:

- TT-cross **discovers** compressibility from value queries;
- RCP **compiles** already-declared relational structure.

The comparison is useful, but the information supplied to the methods is not
identical. The report therefore labels the input regime for every result.

## 6. Complexity boundary

For uniform axis size \(n\) and induced width \(w\), the retained forward pass
has the familiar structural dependence

\[
O(d\,n^{w+1})
\]

up to graph/factor constants. The reverse pass has the same exponential
dependence on \(w\) with an additional bucket-size factor. The architecture is
powerful when \(w\ll d\), not when every axis couples densely to every other
axis.

TT methods can win when:

- only a black-box entry function is available;
- the retained coupling graph is unknown;
- graph width is large but TT rank is small under a good axis ordering;
- a reusable global TT approximation must answer many later, unanticipated
  queries;
- only one scalar contraction is requested and an optimized tensor backend
  amortizes its path and kernel overhead.

RCP should route rather than pretend to dominate in those regimes. A future
planner can select `retained-elimination`, `opt_einsum`, or `TT-cross` as an
execution engine while preserving one declaration/certificate contract.

## 7. What is and is not presently novel

Established prior work includes:

- Tensor-Train decomposition and TT-SVD;
- TT-cross interpolation;
- variable elimination and tensor contraction;
- reverse-mode differentiation of finite computational graphs;
- extracting marginals from factorized graphical models.

RCP therefore does not label those algorithms new.

The candidate research contribution is narrower: a readout-first protocol
that binds retained-information translation, terminal-query compilation,
pre-execution resource admissibility, replayable lineage, independent
preservation evidence, and fail-closed tiered verdicts. Whether that complete
combination is novel requires a dedicated literature review and peer
challenge; the current repository does not treat benchmark superiority as a
novelty proof.

## 8. Next mathematical layer

The strongest next step is not another timing table. It is a finite proof:

1. define finite factors and scopes in Coq;
2. prove one admissible elimination preserves the boundary readout;
3. prove preservation by induction over an admissible path;
4. define the reverse program;
5. prove the unary-adjoint moment identity;
6. bind the Python lineage serialization to the verified path object.

Only then should path preservation move from `finite_diagnostic` toward
`Th_coqc`.

## 9. Breadth evidence

The architecture is exercised across ten fixed topologies in
[`benchmarks/RCP_TEN_PROBLEM_RESULTS.md`](benchmarks/RCP_TEN_PROBLEM_RESULTS.md).
The suite includes an adverse clique to expose width-dependent cost and four
negative controls to verify that unsupported runs do not receive `ACCEPT`.
The development history and instructions for future AI reviewers are recorded
in [`LETTER_TO_AI_REVIEWERS.md`](LETTER_TO_AI_REVIEWERS.md).

## References

- I. V. Oseledets, “Tensor-Train Decomposition,” *SIAM Journal on Scientific
  Computing* 33(5), 2011. DOI:
  <https://doi.org/10.1137/090752286>
- I. V. Oseledets and E. E. Tyrtyshnikov, “TT-cross approximation for
  multidimensional arrays,” *Linear Algebra and its Applications* 432(1),
  2010. DOI: <https://doi.org/10.1016/j.laa.2009.07.024>
- `opt_einsum` path documentation:
  <https://optimized-einsum.readthedocs.io/en/stable/path_finding.html>
- TensorLy Tensor-Train documentation:
  <https://tensorly.org/stable/modules/generated/tensorly.decomposition.tensor_train.html>
- TTML DMRG TT-cross documentation:
  <https://ttml.readthedocs.io/en/latest/_modules/ttml/tt_cross.html>
