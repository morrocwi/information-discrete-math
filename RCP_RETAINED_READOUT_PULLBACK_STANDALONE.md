# Retained Readout Pullback

## Native parameter sensitivity without an autodiff tape

**Status:** executable prototype + `finite_diagnostic` comparison  
**Algebraic identities:** `Th_coqc-elig`, not yet machine-checked  
**Information-mathematical interpretation:** `Dr`  
**Empirical claim:** none  
**External comparator:** `opt_einsum` 3.4.0 + Autograd 1.8.0

---

## 1. Outcome

RCP now returns the partition, all axis first moments, all linear-parameter
gradients, all coupling-parameter gradients, and all corresponding
log-partition gradients in one native retained-closure execution.

The implementation imports neither Junction Tree nor an autodiff package. It
uses the useful computational principle behind reverse mode—reuse one terminal
environment for many sensitivity readouts—but rebuilds that principle from
retained difference, declared readout, and finite closure.

On the seven measured order-4 cases, native Retained Readout Pullback (RRP)
reproduced the partition, moments, and all gradients to
\(\text{worst}\approx1.9\times10^{-10}\) against an independent
finite-difference reference — this is the **committed self-check** (see §6). In
a **separate** `opt_einsum` + Autograd comparison (requires the optional
`autograd` package; not in the committed JSON or CI) it agreed to at most
\(8.89\times10^{-16}\) and was the faster hot call in all seven. These are
bounded benchmark results, not a claim that RRP is faster for every graph,
dimension, order, backend, or hardware.

---

## 2. What was extracted from autodiff

Reverse-mode autodiff is usually presented through a computation graph, tape,
cotangents, and vector-Jacobian products. RRP does not import those objects as
foundational primitives. It extracts one operational fact:

> If many requested sensitivities depend on the same terminal readout, compute
> their shared terminal environment once and redistribute only the relevance
> needed by the declared readouts.

The translation is:

| Conventional autodiff object | Native information-mathematical object |
|---|---|
| forward computation graph | finite causal closure lineage |
| output cotangent | declared terminal relevance |
| reverse traversal | relevance unfold over retained records |
| shared backward subexpression | reused retained closure environment |
| gradient array | named sensitivity readout |
| unused gradient branch | distinction not exposed at the terminal boundary |
| tape/checkpoint | budgeted retained witness |

The correspondence is extensional and computational. It does not assert that
the two foundations are identical.

---

## 3. Finite parameter/readout grammar

For the implemented pairwise problem,

\[
Z(\alpha,\beta)=
\sum_x
\prod_i w_i e^{-\alpha_i x_i}
\prod_{e=(i,j)}e^{-\beta_e x_i x_j}.
\]

The declared sufficient-statistic readouts are

\[
\mu_i=\frac{1}{Z}\sum_x x_i\,W(x),
\qquad
\chi_e=\frac{1}{Z}\sum_x x_i x_j\,W(x),
\]

where \(W(x)\) is the finite product inside the sum. Finite algebra gives

\[
\frac{\partial\log Z}{\partial\alpha_i}=-\mu_i,
\qquad
\frac{\partial Z}{\partial\alpha_i}=-Z\mu_i,
\]

\[
\frac{\partial\log Z}{\partial\beta_e}=-\chi_e,
\qquad
\frac{\partial Z}{\partial\beta_e}=-Z\chi_e.
\]

No limiting derivative is needed to execute these formulas. They are exact
identities of the declared finite exponential parameterization, evaluated here
in binary64.

---

## 4. Retained Readout Pullback

At closure \(C\), let \(a_C\) be the relevance retained from its consumer and
let \(F_C\) be its local input records. RRP forms the same finite environment
already needed for readout:

\[
E_C(x_C)=a_C(x_{\partial C})
\prod_{f\in F_C}f(x_{\operatorname{scope}(f)}).
\]

An axis moment is read when its distinction closes:

\[
\mu_i=\frac{1}{Z}\sum_{x_C}x_i E_C(x_C).
\]

A coupling sensitivity is read exactly where its original pair record is
consumed:

\[
\chi_{ij}=\frac{1}{Z}\sum_{x_C}x_i x_j E_C(x_C).
\]

Therefore RRP never needs the full adjoint table of an original pair factor.
It retains only the scalar statistic named by the parameter/readout grammar.

This is the information-mathematical pullback:

\[
\text{terminal relevance}
\longmapsto
\text{local retained environment}
\longmapsto
\text{declared sensitivity}.
\]

It is called a pullback because terminal relevance is redistributed toward its
declared sources. The operational primitives remain finite records, finite
folds, and finite readouts.

---

## 5. Absorbing shared-environment reuse

The first RRP implementation reduced the same dense closure belief once per
coupling. That was correct but repeated the expensive scan. On complete
\(d=8\), external autodiff was still 1.13× faster.

The upgraded executor compiles a value-independent retained coordinate basis
\(B\), with one row per active distinction and one column per closure state.
For closure mass \(p\), one weighted Gram readout gives all local pair
statistics:

\[
G=(B\odot p)B^\mathsf{T},
\qquad
G_{ij}=\sum_x x_i x_j p(x).
\]

This is not a Jacobian or a pair-factor adjoint. It is a batch of explicitly
declared second-order readouts from one retained environment. It absorbs the
shared-work lesson of reverse mode while keeping the native ontology.

The batch path is admitted only when

\[
|\operatorname{scope}(C)|\,|E_C|\le 524{,}288
\]

float elements. Otherwise RRP falls back to local pair reductions. The
structural readout-basis cache holds at most four entries; one admitted basis
is at most 4 MiB in binary64.

After this change, complete \(d=8\) changed from an external-autodiff win to a
native RRP win by 1.41× in the recorded run.

---

## 6. Direct benchmark

All timings below are medians of 31 hot calls. Both sides reuse a compiled
structural plan. Factor construction and sensitivity execution remain inside
the timed call.

| graph | \(d\) | parameters | native RRP (ms) | `opt_einsum` + Autograd (ms) | external/native | faster |
|---|---:|---:|---:|---:|---:|---|
| sparse | 5 | 11 | 0.123 | 1.099 | 8.91× | native |
| sparse | 7 | 16 | 0.175 | 1.472 | 8.40× | native |
| sparse | 9 | 21 | 0.218 | 1.864 | 8.55× | native |
| sparse | 11 | 26 | 0.331 | 2.308 | 6.96× | native |
| complete | 5 | 15 | 0.140 | 1.207 | 8.63× | native |
| complete | 7 | 28 | 0.845 | 2.235 | 2.65× | native |
| complete | 8 | 36 | 2.065 | 2.915 | 1.41× | native |

Observed maximum differences:

- partition: \(1.11\times10^{-16}\);
- partition gradients: \(2.78\times10^{-16}\);
- log-partition gradients: \(8.89\times10^{-16}\);
- central finite-difference check: below \(10^{-9}\) in the test gate.

> **What the committed artifact proves — and what it does not.** The machine-readable file
> [`benchmarks/retained_readout_pullback_results.json`](benchmarks/retained_readout_pullback_results.json)
> records the **native self-check only**: `benchmark: native_retained_readout_pullback_self_check`,
> agreement of the native executor against an *independent tilted-factor contraction + central finite
> differences* reference (`worst_abs_difference ≈ 1.9×10⁻¹⁰`, `verdict: ACCEPT`, `tolerance 1e-9`) plus
> the native hot timings. It does **not** contain the `opt_einsum` + Autograd column of the table above.
> Those external figures come from a **separate run that requires `autograd`** (an optional dependency,
> not in `requirements.txt`, not exercised in CI). Treat the external comparison as a disclosed manual
> measurement, and the native correctness/timing as the reproducible, committed evidence.

Reproduce the committed native self-check:

```bash
python benchmarks/retained_readout_pullback_benchmark.py \
  --repeats 31 \
  --output benchmarks/retained_readout_pullback_results.json
```

Reproduce the external comparison (separate run; needs `numpy` + `opt_einsum` from
`requirements-bench.txt`, plus `pip install autograd`). The committed self-check command above needs
no third-party package.

---

## 7. Tool surface

The public prototype entry point is:

```python
from benchmarks.retained_fold_tree import (
    compile_retained_readout_pullback,
)

result = compile_retained_readout_pullback(problem, order=4)
pullback = result.retained_readout_pullback
```

It returns:

- `result.value`;
- `result.axis_first_moments`;
- `pullback.coupling_cross_moments`;
- `pullback.partition_linear_gradients`;
- `pullback.partition_coupling_gradients`;
- `pullback.log_partition_linear_gradients`;
- `pullback.log_partition_coupling_gradients`;
- explicit pullback work and retained-basis element counts.

---

## 8. Claim firewall and next frontier

What is established:

- the implemented finite identities agree with an independent central
  finite-difference reference on the tested matrix (**committed self-check**,
  `verdict: ACCEPT`);
- in a **separate, uncommitted** `opt_einsum`+Autograd run they also agreed and
  the native executor was faster on all seven recorded cases;
- the code has no Junction Tree or autodiff dependency.

What is not established:

- universal speed superiority;
- numerical stability for arbitrary signed or zero-valued factors;
- higher-order derivatives;
- arbitrary user-defined factor parameterizations;
- a machine-checked RRP theorem.

The next principled extension is a declared statistic interface:

\[
f_\theta(x)=\exp\!\left(-\sum_k\theta_k T_k(x)\right)
\quad\Rightarrow\quad
\partial_{\theta_k}\log Z=-E[T_k].
\]

That would generalize RRP from linear and pair couplings to any finite
exponential-family factor whose statistic \(T_k\) and scope are explicitly
declared, without promoting an unrestricted autodiff engine into the
foundation.
