# RCP Ten-Problem Topology Suite

This suite tests whether Retained Contraction Protocol (RCP) works beyond one
hand-picked graph. Ten topologies were fixed in code before timing:

1. chain;
2. cycle;
3. star;
4. balanced binary tree;
5. two-by-four ladder;
6. three-by-three grid;
7. chain with length-two chords;
8. chain with long skip edges;
9. two disconnected cycles;
10. a complete graph as an adverse high-width case.

Every problem uses four finite Gauss-Legendre states per named axis and asks
for the partition plus the first moment of every axis. No problem is reduced
to one dimension or to one scalar output.

## Reproduce

Install the external witness:

```bash
python3 -m pip install numpy opt_einsum
```

Run:

```bash
python3 benchmarks/rcp_ten_problem_suite.py \
  --nodes-per-axis 4 \
  --repeats 7 \
  --direct-dimension-limit 8
```

The measured run used CPython 3.12.13, Linux x86-64, NumPy 2.5.1, and
`opt_einsum` 3.4.0. Timings are medians of seven complete calls in one
process.

## Preregistered acceptance rule

Before arithmetic, every problem declares:

- the finite resolution: four nodes on every axis;
- all terminal outputs;
- absolute tolerance \(10^{-12}\);
- maximum work budget 50,000,000 tokens;
- maximum peak retained table 1,000,000 elements;
- query strategy: one forward contraction plus one reverse-lineage pass.

A problem counts as passed only if:

1. path/resource preflight returns `ACCEPT`;
2. planned work equals the independent execution ledger;
3. partition and all axis moments are returned;
4. every readout agrees with `opt_einsum` within \(10^{-12}\);
5. full finite enumeration also agrees when \(d\leq8\);
6. the final RCP certificate returns `ACCEPT`.

## Result: 10/10 accepted

| problem | \(d\) | edges | width | outputs | retained entries | implicit \(4^d\) | work tokens | peak | RCP median | `opt_einsum` median | external/RCP | max difference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P01 chain | 4 | 3 | 1 | 5 | 64 | 256 | 753 | 16 | 0.000167 s | 0.000656 s | 3.93× | \(1.110\times10^{-16}\) |
| P02 cycle | 5 | 5 | 2 | 6 | 100 | 1,024 | 3,490 | 16 | 0.000338 s | 0.001222 s | 3.62× | \(1.665\times10^{-16}\) |
| P03 star | 6 | 5 | 1 | 7 | 104 | 4,096 | 1,491 | 16 | 0.000358 s | 0.001340 s | 3.74× | \(2.220\times10^{-16}\) |
| P04 binary tree | 7 | 6 | 1 | 8 | 124 | 16,384 | 1,636 | 16 | 0.000416 s | 0.001372 s | 3.29× | \(2.220\times10^{-16}\) |
| P05 ladder | 8 | 10 | 2 | 9 | 192 | 65,536 | 7,845 | 16 | 0.000504 s | 0.002339 s | 4.64× | \(1.110\times10^{-16}\) |
| P06 3×3 grid | 9 | 12 | 3 | 10 | 228 | 262,144 | 19,030 | 64 | 0.000623 s | 0.003082 s | 4.95× | \(1.665\times10^{-16}\) |
| P07 chordal | 11 | 15 | 2 | 12 | 284 | 4,194,304 | 9,000 | 16 | 0.000656 s | 0.004140 s | 6.31× | \(2.220\times10^{-16}\) |
| P08 sparse-skip | 12 | 16 | 3 | 13 | 304 | 16,777,216 | 22,793 | 64 | 0.000806 s | 0.005158 s | 6.40× | \(3.886\times10^{-16}\) |
| P09 disconnected | 10 | 10 | 2 | 11 | 200 | 1,048,576 | 6,982 | 16 | 0.000509 s | 0.002997 s | 5.89× | \(1.110\times10^{-16}\) |
| P10 clique | 6 | 15 | 5 | 7 | 264 | 4,096 | 260,947 | 1,024 | 0.001138 s | 0.002393 s | 2.10× | \(1.665\times10^{-16}\) |

Summary:

- RCP certificates: **10/10 `ACCEPT`**
- planned work = measured work: **10/10**
- inside declared tolerance against `opt_einsum`: **10/10**
- additionally checked by direct full enumeration: **6/10**
- largest difference against `opt_einsum`:
  \(3.886\times10^{-16}\)
- largest difference against direct enumeration:
  \(1.665\times10^{-16}\)
- RCP faster than repeated `opt_einsum` for this all-readout query:
  **10/10**

`opt_einsum` is used as an independent execution witness, not as an authority.
The small cases receive a second, structurally different witness by explicit
enumeration of every finite configuration.

## Fail-closed controls: 4/4

The same run deliberately supplied invalid evidence:

| control | expected | observed |
|---|---|---|
| elimination path omits an internal axis | `BLOCK` | `BLOCK` |
| declared work budget is too small | `BLOCK` | `BLOCK` |
| terminal readout has no witness | `HOLD` | `HOLD` |
| witness is deliberately changed by \(10^{-3}\) | `HOLD` | `HOLD` |

These controls matter because a protocol that returns `ACCEPT` for every input
has not tested anything.

## What the suite shows

### 1. Correctness is not tied to one topology

The same declaration, path preflight, forward/reverse execution, work ledger,
witness comparison, and verdict contract works across connected,
disconnected, low-width, and high-width graphs.

### 2. All named dimensions survive as terminal readouts

An axis may be closed internally during contraction, but its effect is retained
in the reverse-lineage readout. P08 returns thirteen outputs from a
twelve-dimensional coupled problem without constructing its 16,777,216-entry
global tensor.

### 3. Structural width remains the real cost boundary

The clique is intentionally adverse. Its induced width rises to 5, peak
storage to 1,024 elements, and work to 260,947 tokens. RCP remains correct,
but the result exposes the expected width dependence rather than hiding it.

### 4. Query fusion drives the measured time advantage

The external baseline reuses one greedy path but performs one contraction for
the partition and one for each axis moment. RCP contracts once and reverses the
executed lineage once. The suite demonstrates this advantage for the declared
many-readout workload; it does not prove a better universal path optimizer.

## Claim boundary

Established at tier `finite_diagnostic`:

- ten finite factor-graph workloads execute successfully;
- every declared output is returned;
- independent finite witnesses agree inside \(10^{-12}\);
- work is predictable before execution and matches the execution ledger;
- invalid path, resource, and witness conditions fail closed.

Not established:

- universal superiority over tensor-network or Tensor-Train methods;
- a theorem for arbitrary graphs, arithmetic substrates, or completed real
  numbers;
- a rigorous interval enclosure for every binary64 rounding step;
- a Coq proof of forward and reverse preservation;
- novelty of variable elimination, reverse-mode accumulation, or marginal
  extraction.

The suite is evidence of implemented protocol breadth, not a substitute for
formal proof or broader external replication.
