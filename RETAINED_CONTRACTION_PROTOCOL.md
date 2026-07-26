# Retained Contraction Protocol (RCP) 1.0

RCP is the finite-information contract around a tensor or factor contraction.
It does **not** introduce a new contraction-path optimizer. It makes the input
boundary, allowed elimination, resource cost, numerical tolerance, lineage,
and preservation evidence explicit and fail-closed.

Implementation: [`tools/retained_contraction_protocol.py`](tools/retained_contraction_protocol.py).

## 1. Translation into the information language

| Tensor language | Retained-information language |
|---|---|
| tensor/factor | finite local record of retained couplings |
| index | named retained distinction |
| shared index | coupling shared by two or more records |
| contraction | finite accumulation over an internal distinction |
| contraction path | causal order in which internal distinctions are closed |
| intermediate tensor | temporary retained record |
| largest intermediate | peak temporary retained-information storage |
| FLOP estimate | arithmetic cost ledger |
| output indices/readouts | declared terminal boundary |

Closing an internal distinction does not silently erase its influence. Its
values are accumulated into the next retained record. What disappears is the
distinction as an exposed output coordinate.

## 2. Mathematical object

Let the retained coupling hypergraph be

\[
G_R=(V_R,E_R,s),
\]

where \(V_R\) is a finite set of named distinctions, \(E_R\) is a finite set
of factor scopes, and \(s(v)\in\mathbb N_{>0}\) is the finite size of axis
\(v\). Let \(B\subseteq V_R\) be the exposed boundary and
\(I=V_R\setminus B\) the internal distinctions.

An admissible path is a permutation

\[
p=(v_1,\ldots,v_{|I|})
\]

of exactly the internal distinctions. It may neither eliminate a boundary
distinction nor leave an internal distinction open.

For an admissible path \(p\), let \(C_p(T)\) be the terminal finite readout.
Path selection may minimize cost and peak retained storage:

\[
p^\*=\arg\min_{p\in P_{\mathrm{adm}}(G_R)}
\left(\operatorname{Work}(p),\operatorname{PeakRetained}(p)\right).
\]

RCP does not prescribe the optimizer used to find \(p^\*\). Min-fill,
variable elimination, `einsum`, and `opt_einsum` may all supply a candidate
path.

## 3. Declaration before tick 0

Every run declares:

1. `resolution_lambda`: the finite axis resolution;
2. `axis_sizes`: every named retained axis and its finite size;
3. `boundary_axes`: axes that must remain exposed;
4. `output_names`: every terminal scalar/readout promised to the consumer;
5. `tolerance`: maximum permitted preservation difference;
6. `max_work_tokens` and `max_peak_elements`: resource budgets;
7. arithmetic substrate and honesty tier.

No declaration means no certified contraction.

## 4. Protocol

### P1 — DECLARE

Create an `RCPDeclaration`. Resolution, output boundary, tolerance, and
resource budget are fixed before execution.

### P2 — MAP

Translate every local table to a `RetainedFactor(name, scope)`. Together they
form \(G_R\).

### P3 — ADMIT

`plan_contraction` checks:

- every factor axis was declared;
- factor and output names are unique;
- the path eliminates every and only internal distinction once;
- the compiled terminal scope equals the declared boundary.

A malformed path returns `BLOCK`.

### P4 — PREFLIGHT

The protocol symbolically replays the path. For every elimination it records:

- input factors;
- joined and output scopes;
- output table size;
- multiplication and addition tokens.

It derives planned work, peak retained elements, peak rank, and a SHA-256
lineage digest. A run that exceeds either resource budget returns `BLOCK`
before contraction.

### P5 — EXECUTE

The low-level finite executor performs the admitted contraction. RCP is
executor-independent.

### P6 — CERTIFY

The executor supplies its terminal readout and measured work ledger. A
preservation witness supplies the same declared outputs by one of:

- independent full finite enumeration (benchmark use);
- a second admissible implementation/path;
- an exact finite proof;
- a verified transformation theorem.

For a finite diagnostic, preservation requires

\[
\delta_\lambda(C_p(T),C_w(T))
=
\max_k |C_p(T)_k-C_w(T)_k|
\leq\varepsilon.
\]

The certificate contains the declaration, lineage digest, path, every output,
componentwise differences, maximum difference, planned/measured work, peak
retained elements, witness method, and tier.

### P7 — VERDICT

- `ACCEPT`: admissible, inside budget, ledger agrees, all declared outputs are
  present, and the witness agrees within tolerance.
- `HOLD`: execution exists but evidence is insufficient—for example no
  witness, path disagreement, non-finite output, or plan/ledger mismatch.
- `BLOCK`: malformed declaration/path or a resource/consumer-contract
  violation.

Only `ACCEPT` may be consumed as a certified result.

### P8 — TIER AND FENCE

The present Python implementation emits `finite_diagnostic`. It certifies a
finite execution at the declared tolerance. It is not yet `Th_coqc`, does not
prove a theorem about completed real numbers, and does not certify a claim
about the physical world.

## 5. Relationship to `opt_einsum`

`opt_einsum` searches contraction paths and reports optimized arithmetic cost
and intermediate size. In RCP terms it can implement part of **P4** and the
executor in **P5**.

RCP adds the parts that a path optimizer does not know by itself:

- information-language declaration and boundary;
- admissibility relative to that boundary;
- framework resource budget;
- retained lineage;
- independent preservation evidence;
- fail-closed verdict and honesty tier.

Therefore the path optimizer is an interchangeable engine inside the
protocol, not the protocol itself.

## 6. Current claim boundary

RCP 1.0 establishes an executable protocol design and numeric certificate
schema. Its planner and verdict behavior are covered by Python tests. The
preregistered breadth suite in
[`benchmarks/RCP_TEN_PROBLEM_RESULTS.md`](benchmarks/RCP_TEN_PROBLEM_RESULTS.md)
reports 10/10 accepted topologies, six direct-enumeration witnesses, external
agreement for all ten, and four required fail-closed controls.

It does not yet establish:

- novelty of contraction or path optimization;
- a rigorous roundoff interval for arbitrary binary64 contractions;
- preservation without an independent witness;
- a Coq proof that every admitted symbolic elimination preserves the declared
  finite readout.

The next mathematical step is to formalize finite factors, one elimination
step, and induction over an admissible path in Coq, then connect the Python
lineage to the verified path representation.
