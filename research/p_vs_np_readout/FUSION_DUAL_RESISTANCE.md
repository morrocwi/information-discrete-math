# Fusion Dual Resistance: Exact Lower-Bound Certificates

**Status:** standard set-cover LP duality specialized to Fusion/Horn cover complexity; exact finite certificate machinery implemented.  
**Claim boundary:** no asymptotic SAT lower bound is claimed here.

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

This is the ordinary fractional set-cover dual. It is especially useful here because each constraint is a direct, finitely checkable statement about one pair `(E,H)` and the semi-filters that it kills.

`fusion_dual_certificate.py` constructs the full finite cover matrix for every nontrivial two-bit Boolean function, solves this dual using IDM's exact-rational simplex, and independently rechecks every dual inequality with Python `Fraction` arithmetic. The integer optimum is computed independently by exact set-cover search.

## 3. Scaled certificate for a proof kernel

Clear denominators. Let `D>0` be a common denominator and set

\[
w_\mathcal F=D y_\mathcal F\in\mathbb N.
\]

Then the certificate conditions become

\[
\sum_{\mathcal F\in K_p}w_\mathcal F\le D
\qquad\forall p.
\]

If the total weight is

\[
W=\sum_\mathcal F w_\mathcal F,
\]

then any `k`-pair cover satisfies

\[
W\le kD,
\]

hence

\[
\boxed{
\rho(A,\mathcal B)\ge
\left\lceil\frac WD\right\rceil.
}
\]

`formal/IDM_FusionDual.v` records the finite aggregation skeleton used by a scaled certificate. The cover-incidence facts remain explicit finite certificate data and must be checked separately; the Coq lemma does not manufacture those facts.

## 4. Distribution form

The dual has a useful normalized interpretation. Let `mu` be a probability distribution over target semi-filters and define the violation probability of a pair

\[
\operatorname{kill}_\mu(p)
=
\Pr_{\mathcal F\sim\mu}
[\mathcal F\text{ does not preserve }p].
\]

If

\[
\boxed{
\sup_p\operatorname{kill}_\mu(p)\le\varepsilon,
}
\]

then choosing

\[
y_\mathcal F=\mu(\mathcal F)/\varepsilon
\]

is dual-feasible, so

\[
\boxed{
\rho(A,\mathcal B)\ge1/\varepsilon.
}
\]

This gives a clean adversarial-readout formulation:

> Construct a distribution of unresolved completions such that no single legal fusion rule destroys more than an `epsilon` fraction of the surviving readout mass.

We call such a distribution an **epsilon fusion-resistant semi-filter distribution (FRSD)**.

## 5. Why this is a better asymptotic target

The original lower-bound statement quantifies over every small pair family `Lambda`:

\[
\forall\Lambda,\ |\Lambda|\le k,\ \exists\mathcal F\text{ surviving all pairs.}
\]

The dual form asks for one weighted adversary satisfying local inequalities against every individual pair:

\[
\exists\mu\ \forall p:\operatorname{kill}_\mu(p)\le\varepsilon.
\]

Once such a distribution is constructed, the lower bound follows by summing local constraints. This is exactly the kind of local-to-global retained-cost certificate that IDM can search and verify.

It does **not** make the unrestricted circuit problem easy: the pair `(E,H)` may be arbitrary subsets of the complement, so proving a strong uniform bound on its kill probability remains the load-bearing difficulty.

## 6. SAT consequence target

For the SAT graph `G_n^SAT` on `N=2^n` by `N=2^n` vertices, the fusion/circuit transference gives a route from

\[
\rho(G_n^{SAT},\mathcal G_{N,N})
\]

to circuit lower bounds for the corresponding `2n`-bit SAT predicate.

Therefore a family of explicit FRSDs with

\[
\varepsilon_n=n^{-\omega(1)}
\]

would imply a superpolynomial cover lower bound, hence a superpolynomial DeMorgan circuit lower bound for that SAT encoding and therefore `SAT notin P/poly`.

The open problem has now been reduced to the following concrete object-construction task:

\[
\boxed{
\textbf{SAT-FRSD:}
\quad
\text{construct explicit }\mu_n\text{ over SAT semi-filters with }
\sup_p\operatorname{kill}_{\mu_n}(p)=n^{-\omega(1)}.
}
\]

No such construction is currently established in this repository.

## 7. Candidate ingredients to test

1. **Canonical semi-filters** induced by target points or coordinate cuts. Cheap to define; likely too weak, but useful as a baseline.
2. **Randomized upward closures** seeded by SAT-compatible retained distinctions. Need exact control of arbitrary-pair violation probability.
3. **Rank-conditioned mixtures.** Use exact rank/weak-rank invariants only to condition or stratify the distribution, not as the final measure.
4. **Lineage mixtures.** Weight semi-filters by how many independent generator lineages they retain. This is native to Readout Genesis but must be shown robust against arbitrary subset pairs.
5. **LP-discovered finite patterns.** Solve exact duals on small structured SAT slices, canonicalize the optimal weights, and search for a symbolic family rather than extrapolating numerically.

The fifth route is the immediate executable programme.
