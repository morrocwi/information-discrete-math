# Direct N-D Work-Token Benchmark

This benchmark answers a narrow engineering question:

> When the same separable \(d\)-dimensional discrete quadrature is evaluated by
> visiting the full tensor grid versus retaining and composing every named axis,
> how many weighted kernel samples are required?

It does **not** use radial coordinates or replace eleven dimensions with one
radial integral. The problem has all coordinates \(x_1,\ldots,x_d\):

\[
I_d =
\int_{[0,1]^d}
\exp\left(-\sum_{j=1}^{d}x_j\right)
dx_1\cdots dx_d
= (1-e^{-1})^d.
\]

Both internal paths use the same five-point Gauss-Legendre rule on each axis.
The direct path visits all \(5^d\) tuples. The axis-preserving path independently
computes and returns all \(d\) axis readouts, then combines them through

\[
\exp\left(-\sum_j x_j\right)=\prod_j\exp(-x_j).
\]

## Work-token definition

One **sample token** is one weighted kernel sample. Multiplications used to
combine the retained axis readouts are listed separately. The conservative
`total_work_tokens` value is:

\[
\text{sample tokens}+\text{combine tokens}.
\]

This unit is reproducible and implementation-independent. Wall-clock results
are also shown, but they are environment-dependent and the microsecond IDM path
should be benchmarked in repeated batches before making a production speed
claim.

## Actual 11-D full-tensor run

Command:

```bash
python3 benchmarks/direct_nd_work_tokens.py \
  --dimension 11 --nodes-per-axis 5
```

Environment: CPython 3.12.13, Linux x86-64. Results:

| measurement | direct 11-D tensor | axis-preserving IDM |
|---|---:|---:|
| dimensions returned | combined scalar | 11 axis readouts + combined scalar |
| sample tokens | 48,828,125 | 55 |
| combine tokens | 0 | 10 |
| total work tokens | 48,828,125 | 65 |
| value | 0.006438713027660086 | 0.0064387130276600864 |
| absolute error vs analytic value | \(2.695\times10^{-14}\) | \(2.694\times10^{-14}\) |
| direct/IDM absolute difference | \multicolumn{2}{c}{\(8.674\times10^{-19}\)} |
| elapsed time, one run | 27.124 s | 0.00001865 s |

Measured ratios:

- sample-token ratio: **887,784.09×**
- total-work-token ratio: **751,201.92×**
- one-run wall-clock ratio: 1,454,614.70× (indicative, not a portable claim)

Every retained axis readout was independently computed and returned:

```text
[0.6321205588283172] × 11 axes
```

## External 4-D baseline: SciPy `nquad`

SciPy documents that `nquad(..., full_output=True)` returns `neval`, the number
of integrand evaluations. It therefore supplies an external sample-token count
without estimating from source code:

<https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.nquad.html>

Command:

```bash
python3 benchmarks/direct_nd_work_tokens.py \
  --dimension 4 --nodes-per-axis 5 \
  --scipy-dimension 4 --eps 1e-10
```

| measurement | SciPy `nquad` | axis-preserving IDM |
|---|---:|---:|
| sample tokens | 194,481 | 20 |
| combine tokens | 0 | 3 |
| total work tokens | 194,481 | 23 |
| value | 0.1596613001511853 | 0.1596613001509423 |
| absolute error vs analytic value | \(2.776\times10^{-17}\) | \(2.430\times10^{-13}\) |
| requested tolerance | \(10^{-10}\) | \(10^{-10}\) |
| meets requested tolerance | yes | yes |
| elapsed time, one run | 0.06844 s | 0.00000864 s |

At the same declared \(10^{-10}\) tolerance:

- sample-token ratio: **9,724.05×**
- total-work-token ratio: **8,455.70×**

The same-grid direct four-dimensional tensor test is stricter as an identity
check: it used 625 sample tokens versus IDM's 23 total tokens, and both paths
returned exactly the same binary64 value in this run.

## Scope fence

The reduction is earned by the integrand's explicit separability. It is not
available for an arbitrary coupled N-D function. The engineering claim
supported by this benchmark is therefore:

> When an N-D problem exposes a retained separable structure, an axis-preserving
> finite computation can produce the same tensor-quadrature readout without
> enumerating the full tensor grid, changing sample growth from \(n^d\) to
> \(dn\), plus \(d-1\) combination operations.

Future benchmarks should add coupled, low-rank, sparse-grid, and adversarial
non-separable cases so the system can report when compression is unavailable.
