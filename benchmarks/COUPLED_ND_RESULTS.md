# Coupled 11-D Retained-Graph Compiler Benchmark

This benchmark removes the separability used by the first direct N-D test. It
uses eleven named coordinates and fifteen pair couplings:

\[
I_{11} =
\int_{[0,1]^{11}}
\exp\left(
  -\sum_{i=1}^{11}a_i x_i
  -\sum_{(i,j)\in E}b_{ij}x_ix_j
\right)
dx_1\cdots dx_{11}.
\]

The graph contains the ten chain edges \((i,i+1)\) and five chord edges
\((0,2),(2,4),(4,6),(6,8),(8,10)\). The integrand therefore cannot be written
as a product of eleven independent one-axis functions.

The prototype compiler:

1. reads the pair-coupling graph;
2. chooses a deterministic min-fill elimination order;
3. builds finite factor tables from a four-point Gauss-Legendre rule;
4. contracts the retained graph;
5. returns the partition readout and all eleven axis first moments;
6. reports induced width and a replayable work ledger.

## Full 11-D identity test

Command:

```bash
python3 benchmarks/coupled_nd_retained_compiler.py \
  --dimension 11 --nodes-per-axis 4
```

Environment: CPython 3.12.13, Linux x86-64.

| measurement | direct full tensor | retained-graph compiler |
|---|---:|---:|
| full configurations / factor samples | 4,194,304 | 284 |
| multiplication tokens | 155,189,259 | 17,635 |
| addition tokens | 50,331,648 | 4,848 |
| total work tokens | 209,715,211 | 22,767 |
| elapsed time | 49.454 s | 0.03451 s |
| partition readout | 0.1647096320396113 | 0.1647096320396113 |
| induced width | not compiled | 2 |

Measured reductions:

- configuration/factor-sample ratio: **14,768.68×**
- total-work-token ratio: **9,211.37×**
- elapsed ratio: **1,433.10×**

The partition difference was exactly zero in binary64. All eleven axis moments
were returned:

```text
0.48432272422543315
0.48142381909682910
0.47459804300955930
0.47493936058131150
0.46738148462418540
0.47040053842295704
0.46410189737409950
0.46587818335533860
0.45693577814888120
0.45945345474238786
0.45659073252515310
```

The maximum marginal difference from full enumeration was
\(5.551\times10^{-17}\).

## External tensor-contraction comparison

`opt_einsum` is an established external library that automatically searches
for tensor contraction paths and reports optimized FLOP counts and intermediate
sizes:

<https://dgasmith.github.io/opt_einsum/>

For the same factors, partition, and eleven first moments:

| measurement | retained compiler | `opt_einsum` greedy |
|---|---:|---:|
| partition | 0.1647096320396113 | 0.1647096320396113 |
| maximum axis difference | — | \(2.220\times10^{-16}\) |
| execution time, all 12 outputs | 0.03451 s | 0.00451 s |
| external path-search time | — | 0.00056 s |
| reported/estimated arithmetic work | 22,767 tokens | 11,808 optimized FLOPs |
| largest intermediate | implicit width 2 | 16 elements |

The external implementation is faster and reports a smaller arithmetic count.
Consequently, automatic sparse tensor contraction is **not** claimed as a new
algorithm here.

## What this does and does not establish

Established by execution:

- the problem is coupled and eleven-dimensional;
- the compiler finds bounded retained width automatically;
- it computes the same finite tensor readout without full enumeration;
- it returns all eleven marginal readouts;
- its explicit work ledger is reproducible.

Not established:

- novelty of variable elimination or contraction-path optimization;
- superiority over optimized tensor-network libraries;
- a rigorous real-number error enclosure;
- compression for dense or high-width coupling graphs.

This file records the first repeated-query compiler. That target now has an
executed follow-up:

> [`RETAINED_CONTRACTION_PROTOCOL.md`](../RETAINED_CONTRACTION_PROTOCOL.md)
> attaches the declaration, retained-readout lineage, tolerance, resource
> budget, witness, tier, and fail-closed verdict. The reverse-lineage compiler
> reduces the same all-output workload from 22,767 to 9,000 tokens and is
> compared with `opt_einsum`, TT-SVD, and TT-cross in
> [`COMPETITOR_RESULTS.md`](COMPETITOR_RESULTS.md).

The remaining mathematical target is formal verification that every emitted
finite elimination and the reverse unary-adjoint readout preserve the declared
boundary. Numeric execution remains `finite_diagnostic`; the protocol is not
described as a novelty theorem.
