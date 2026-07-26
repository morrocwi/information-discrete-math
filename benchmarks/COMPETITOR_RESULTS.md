# RCP vs opt_einsum, Tensor Train, and TT-cross

This benchmark compares the partition and all eleven named axis first moments
of the same coupled, non-separable finite tensor.

## Reproduce

The project benchmark dependencies used for this run were:

```bash
python3 -m pip install opt_einsum==3.4.0 tensorly==0.9.0
python3 -m pip install --no-deps ttml==1.0
python3 -m pip install autoray==0.9.0 tqdm==4.69.1 pandas scikit-learn
```

Run:

```bash
python3 benchmarks/competitor_benchmark.py \
  --dimension 11 \
  --nodes-per-axis 4 \
  --tt-rank 8 \
  --repeats 7 \
  --tolerance 1e-12
```

Measured environment: CPython 3.12.13, Linux x86-64, NumPy 2.5.1. Timings are
the median of seven complete method calls in one process.

## Result

| method | input regime | median wall time | slower than RCP | maximum output difference |
|---|---|---:|---:|---:|
| **RCP reverse-lineage** | explicit sparse factor graph | **0.000673 s** | 1.00× | witness difference \(2.776\times10^{-16}\) |
| `opt_einsum` 3.4.0 | explicit sparse factor graph | 0.004193 s | **6.23×** | \(2.776\times10^{-16}\) |
| Oseledets TT-SVD, TensorLy | dense tensor | 0.493597 s | **733.54×** | \(1.499\times10^{-15}\) |
| TensorLy TT-cross | dense tensor API | 0.475825 s | **707.13×** | \(2.109\times10^{-15}\) |
| TTML DMRG TT-cross | black-box callable | 0.020024 s | **29.76×** | \(3.886\times10^{-16}\) |

Every method was inside the declared \(10^{-12}\) tolerance and returned all
twelve outputs: the partition plus eleven distinct first moments.

The RCP certificate returned:

```text
status                         ACCEPT
planned work tokens            9,000
measured work tokens           9,000
peak retained elements            16
maximum witness difference     2.776e-16
tier                           finite_diagnostic
```

## Input and retained storage

| measurement | RCP | opt_einsum | TT-SVD | dense TT-cross | callable TT-cross |
|---|---:|---:|---:|---:|---:|
| local factor entries / tensor entries / function calls | **284** | 284 local entries | 4,194,304 entries | 4,194,304-entry API input | 14,848 calls; 9,760 unique |
| peak intermediate / resulting representation | **16** | 16 | 2,080 TT entries | 2,080 TT entries | 2,080 TT entries |

RCP reports 9,000 work tokens. `opt_einsum` reports an estimated 11,808 FLOPs
for the twelve repeated contractions. Those counts use different conventions,
so the repository reports both but does not treat one token as definitionally
identical to one external FLOP.

## Why RCP wins this workload

The first retained compiler repeated the contraction once for each output. The
new engine contracts the partition once and traverses the executed lineage
backward once. Unary-factor adjoints yield all eleven first moments. This
reduces the retained compiler from 22,767 to 9,000 work tokens.

TT-SVD and TT-cross solve a more general representation problem: construct a
Tensor Train that can approximate the global tensor. RCP solves the declared
terminal-query problem directly. Because the sparse coupling graph is already
known and has induced width 2, inferring or materializing a global
representation is unnecessary for these outputs.

## Claim boundary

This is a measured win for:

- eleven dimensions and four nodes per axis;
- the declared sparse pair-coupling graph;
- induced width 2;
- partition plus all eleven first moments;
- the listed library versions and machine.

It is not universal superiority over Tensor Train, TT-cross, or `opt_einsum`.
TT-cross may be preferable for a black box with no disclosed factor graph. TT
may be preferable when a reusable global approximation must answer many future
queries. `opt_einsum` may win for a single contraction or another graph/backend.

The result establishes a concrete architecture regime, not a novelty theorem.
