# Fusion Dual Resistance: Exact Certificates and the Fixed-Distribution Barrier

**Status:** exact finite certificate machinery + a load-bearing no-go result for asymptotic use.  
**Claim boundary:** the fractional dual is a valid finite lower-bound certificate, but a **single fixed distribution over semi-filters cannot yield a super-linear general Boolean-circuit lower bound through probabilistic counting**.

## 1. Cover complexity is a set-cover number

For a target `A`, let `Filters(A)` be the semi-filters over `U=A^c` that are above at least one target point. For each fusion pair

\[
p=(E,H),
\]

let

\[
K_p=\{\mathcal F:\mathcal F\text{ does not preserve }(E,H)\}.
\]

Definition 21 of Cavalar--Oliveira makes

\[
\rho(A,\mathcal B)
\]

exactly the minimum number of sets `K_p` required to cover all target semi-filters.

## 2. Fractional dual certificate

Assign a nonnegative rational weight `y_F` to each target semi-filter. If

\[
\boxed{
\sum_{\mathcal F\in K_p}y_\mathcal F\le1
\qquad\text{for every fusion pair }p,
}
\]

then every integral fusion cover `Lambda` satisfies

\[
\boxed{
|\Lambda|\ge
\sum_{\mathcal F}y_\mathcal F.
}
\]

This is the ordinary fractional set-cover dual. `fusion_dual_certificate.py` constructs the finite cover matrix for every nontrivial two-bit Boolean function, solves the dual using IDM's exact-rational simplex, and independently rechecks every inequality with `Fraction` arithmetic. The integer optimum is computed independently by exact set-cover search.

The finite statement is completely valid. The important question is how large this dual objective can become asymptotically for general non-monotone circuit complexity.

## 3. Scaled certificate for the proof kernel

Clear denominators. Let `D>0` be a common denominator and set

\[
w_\mathcal F=D y_\mathcal F\in\mathbb N.
\]

Then

\[
\sum_{\mathcal F\in K_p}w_\mathcal F\le D
\qquad\forall p.
\]

If

\[
W=\sum_\mathcal F w_\mathcal F,
\]

any `k`-pair cover satisfies

\[
W\le kD,
\]

so

\[
\boxed{
\rho(A,\mathcal B)\ge
\left\lceil\frac WD\right\rceil.
}
\]

`formal/IDM_FusionDual.v` records the finite local-to-global aggregation skeleton. Concrete cover incidence remains certificate data that must be checked separately.

## 4. Distribution form

Normalize the dual weights to a distribution `mu` over semi-filters. Define

\[
\operatorname{kill}_\mu(p)
=
\Pr_{\mathcal F\sim\mu}
[\mathcal F\text{ does not preserve }p].
\]

For a fixed distribution,

\[
\varepsilon(\mu)=\sup_p\operatorname{kill}_\mu(p)
\]

and the scaled weights

\[
y_\mathcal F=\mu(\mathcal F)/\varepsilon(\mu)
\]

give the lower bound

\[
\rho(A,\mathcal B)\ge1/\varepsilon(\mu).
\]

This is an exact reformulation of the fractional dual.

## 5. Critical no-go: fixed distributions have only linear power here

The tempting programme was to find a single distribution `mu_n` such that every fusion pair has superpolynomially small kill probability. That programme is ruled out for the general non-monotone fusion setting by the probabilistic-counting limitation explained by Oliveira from Razborov's approximation-method argument.

In the fusion specialization, for **every fixed distribution** `alpha` over the relevant semi-filters, there exists a distribution over fusion pairs such that every semi-filter is covered with probability at least

\[
\frac1{8n+8}.
\]

Averaging implies that some individual pair has

\[
\operatorname{kill}_\alpha(p)\ge\frac1{8n+8}.
\]

Hence

\[
\boxed{
\frac1{\sup_p\operatorname{kill}_\alpha(p)}
\le 8n+8.
}
\]

But the left side is exactly the lower bound obtainable from one fixed normalized dual distribution. Therefore the **fractional-cover / fixed-FRSD method has an `O(n)` ceiling** in this general Boolean-circuit setting.

Reference: Igor Carboni Oliveira, *Notes on the Method of Approximations and the Emergence of the Fusion Method* (2018), Section 2.4, Lemma 3 and Theorem 6; the note explicitly concludes that a fixed distribution over semi-filters cannot be used with probabilistic counting to prove a super-linear non-monotone circuit lower bound.

This does not invalidate the integral cover complexity `rho`, which still characterizes the fusion method up to the established polynomial relationships. It invalidates only the hope that a **single global fractional dual** will produce the desired superpolynomial lower bound.

## 6. Consequence for IDM

The exact LP dual remains useful for:

- finite certification and regression tests;
- discovering symmetries and candidate adversarial semi-filters;
- measuring the integrality gap between fractional and integral fusion covers;
- calibrating restricted or monotone settings where fixed distributions can be powerful.

It is **not** the main asymptotic route to `P != NP`.

The branch must therefore distinguish two objects:

\[
\rho^*(A,\mathcal B)
=
\text{fractional cover optimum},
\]

\[
\rho(A,\mathcal B)
=
\text{integral cover complexity}.
\]

For the general non-monotone fusion problem, the former is linearly bounded in the input dimension under the fixed-distribution counting framework, while the latter can in principle be much larger.

## 7. The adaptive distribution route

After a candidate circuit `C` (or its induced fusion-pair family `Gamma_C`) is exposed, one may choose a distribution that **depends on that candidate**:

\[
\mu_C.
\]

If `C` has `s` relevant fusion pairs and one can establish

\[
\boxed{
\forall p\in\Gamma_C:
\operatorname{kill}_{\mu_C}(p)<1/s,
}
\]

then the union bound gives positive probability that a semi-filter sampled from `mu_C` survives every pair in `Gamma_C`. Therefore `Gamma_C` is not a cover and `C` cannot be correct.

Oliveira explicitly identifies this adaptive choice as the appropriate probabilistic direction for general circuits.

However, **mere existence of `mu_C` is equivalent to the circuit already being defeatable**: if a surviving semi-filter is known, a point mass on it works. Thus adaptivity becomes useful only if we can construct `mu_C` from transparent structural information about `C` without already knowing the lower-bound conclusion.

## 8. Readout-specific research target

This suggests the next genuinely nontrivial object:

### Adaptive Lineage Readout Adversary (ALRA) — OPEN

Given a size-`s` candidate SAT circuit `C`, use only its declared DAG, gate lineage, literal generators and retained distinctions to construct a distribution

\[
\mu_C=\operatorname{ALRA}(C)
\]

such that

\[
\max_{p\in\Gamma_C}
\operatorname{kill}_{\mu_C}(p)<1/s.
\]

Required guards:

1. `ALRA` cannot call SAT or use the correct output labels of the candidate inputs as an oracle.
2. The construction must use the **joint lineage of all gates**, not treat each pair independently; otherwise it falls back into the fixed-distribution/probabilistic-counting barrier.
3. It must handle sharing and arbitrary DeMorgan circuit DAGs, not formulas or OBDDs only.
4. The final contradiction must be stated against the actual gate-induced family `Gamma_C`.
5. Any probability argument must be candidate-adaptive in an explicit way.

This is now the preferred fusion/readout frontier.

## 9. Immediate executable programme

1. Keep the exact dual solver as a finite baseline and measure `rho/rho*` integrality gaps.
2. For small circuits, generate the actual gate-induced pair family `Gamma_C` rather than all arbitrary pairs.
3. Search for distributions optimized **only against Gamma_C**, then inspect how the optimum depends on circuit lineage.
4. Compare two circuits with identical sets of local pairs but different sharing/lineage; any successful Readout contribution should explain a difference that static fusion cover forgets.
5. Attempt to derive an analytic ALRA rule from retained boundary width, reconvergence, rank bottlenecks, or declaration timing.
6. Reject any candidate rule whose distribution can be fixed before seeing `C` and still claims super-linear general-circuit power.

The central question has therefore moved from a global FRSD to a **candidate-adaptive, lineage-aware adversary**.
