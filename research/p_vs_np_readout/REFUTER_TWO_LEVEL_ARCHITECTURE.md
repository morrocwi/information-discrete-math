# SAT Refuter: Two-Level Architecture

**Status:** inner localization has certified finite/polytime islands; outer circuit-hitting theorem remains OPEN.

## 1. Why two levels are necessary

The current fixed-point lane proves a local statement on a chosen CNF restriction tree:

\[
SAT(F)=SAT(F|_{x=0})\vee SAT(F|_{x=1}).
\]

If a candidate `C` is wrong on a chosen root formula `F`, then some internal restriction equation or certified frontier/boundary equation must fail.  This is an **inner localization theorem**.

It does not tell us how to choose a formula `F` on which a globally small candidate circuit is wrong.  That is the **outer hitting problem**.

Therefore the unrestricted refuter must be factored as

\[
\boxed{C\xrightarrow{\text{outer}}\mathcal F_C
\xrightarrow{\text{inner}}z
\xrightarrow{\text{local verifier}} C\ne SAT.}
\]

## 2. Inner layer: localization / closure

Given a candidate formula `F`, the inner layer may use:

- local SAT restriction equations;
- direct terminal truth;
- independently sound syntax closure;
- certified tractable frontiers such as a 2-SAT solver;
- memoized restriction DAG sharing;
- a declared backdoor set.

The quantitative accounting is

\[
d_{root}\le
\sum_{v\in observed}\Delta_C(v)
+
\sum_{\ell\in frontier}\epsilon_C(\ell).
\]

If every frontier target is certified exactly, all `epsilon` values are locally checkable.  A wrong root then forces an exposed local/frontier defect.

### Parameterized backdoor support

If `k` declared variables are expanded and every resulting frontier lies in an independently solved tractable class, at most

\[
\boxed{2^{k+1}-1}
\]

states are visited.  `formal/IDM_BackdoorSupportBudget.v` proves the exact finite recurrence.  Hence `k=O(log n)` gives polynomial inner support.

`tractable_frontier_support.py` provides a concrete 2-SAT frontier implementation and fails closed when the declared backdoor does not reach the certified class.

## 3. Outer layer: circuit hitting

The outer constructor must inspect the actual shared circuit DAG and generate a polynomial family of candidate formulas/states

\[
\mathcal F_C=\{F_1,\ldots,F_m\},\qquad m\le poly(n,|C|),
\]

such that every circuit below the claimed size threshold is forced into at least one locally detectable inconsistency:

\[
\boxed{
C\text{ below threshold}
\Longrightarrow
\exists F\in\mathcal F_C:\text{ InnerDetect}(C,F)=1.
}
\]

This is stronger than merely saying that a wrong `C` has a defect somewhere.  The finite fixed-point theorem already gives existence somewhere; the outer theorem must **construct a small search region from the lineage of `C` without a target oracle**.

## 4. Why the inner success does not prove the outer theorem

Several guards already rule out shortcuts:

- terminal output is one bit but construction may be hard;
- a local defect has only a constant-size signature alphabet but finding a representative can be exponential;
- raw restriction branch counts overcount because DAG sharing can be exponential;
- raw gate-value signatures can realize `2^|C|` states;
- a semantic-oracle leaf rejector collapses every negative instance to one step and is forbidden;
- fixed global fusion duals have only the previously recorded linear ceiling in the general nonmonotone setting.

Thus

\[
\boxed{\text{polytime inner verifier}\not\Rightarrow\text{polytime outer refuter}.}
\]

## 5. Connection to Adaptive Defect Capture

Let `S_C` be all local certificates produced from the outer formula family plus inner supports.  If

\[
|S_C|\le p(n,|C|)
\]

and it hits at least one defect, then the hitting-support kernel gives

\[
1-q_C\ge\frac1{p(n,|C|)}.
\]

Therefore the final constructive interface is

\[
\boxed{
\text{Outer Lineage Hitting}
+
\text{Certified Inner Closure}
\Longrightarrow
\text{inverse-polynomial ADC capture}.
}
\]

## 6. Exact frontier

### Closed / finite

- local defect semantics and verifier;
- wrong-root -> local/boundary defect on a complete finite restriction tree;
- partial-tree quantitative frontier accounting;
- sound negative closure and sharing;
- ADC mass arithmetic;
- polynomial hitting support -> inverse-polynomial capture;
- unit-closure compression on a calibrated family;
- certified 2-SAT frontier prototype;
- exact `2^(k+1)-1` backdoor-tree state budget.

### OPEN / load-bearing

The principal target is now:

> **Outer Lineage Hitting Theorem.** For every candidate circuit below each polynomial gate budget, construct from its DAG/lineage in polynomial time a polynomial-size family of valid SAT formula states such that certified inner closure exposes a defect.

Equivalently, if this is coupled to the unrestricted Fusion/Horn bridge in a way that defeats every below-threshold circuit, it is the desired general SAT circuit lower-bound breakthrough.

No `SAT notin P/poly` or `P != NP` claim is made at the current stage.
