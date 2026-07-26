# RCP-Energy: Retained-Burden Planning from Information-Discrete Mathematics

## Scope and tier

RCP-Energy/1.0 is a finite mathematical planning protocol. It does not claim
that its stress tape is a measured building, that its thermal rule is a law of
nature, or that a computed saving will occur at a real facility. The current
implementation and results are `finite_diagnostic`. The general preservation
and minimality theorem is `Th_coqc-elig`, not yet `Th_coqc`.

The implementation uses only finite integers, exact `Fraction` readouts,
finite iteration, and declared `ACCEPT/HOLD/BLOCK` verdicts. No external
optimizer or continuum library produces `ours`.

## 1. Translation before calculation

The world-language prompt was “reduce electricity or oil.” Importing a
continuous power curve, differential thermal equation, or real-valued
optimization space at this point would violate Rule 0. RCP-Energy translates
the request first:

| world-language name | retained-information translation |
|---|---|
| time | a supplied finite ordered tape \(n=0,\ldots,N-1\) |
| energy | a count of declared rational quanta \(\lambda_E\) |
| temperature | a finite thermal record, not a point of \(\mathbb R\) |
| battery | a bounded retained storage count |
| solar/grid/diesel | named local source records |
| operating constraint | an admissibility predicate on one transition |
| impossible schedule | absence of a record; never \(+\infty\) |
| “best” schedule | the retained representative selected by a declared finite reader order |

For the registered challenge,

\[
N=96,\qquad \lambda_t=15\text{ minutes},\qquad
\lambda_E=\frac14\text{ kWh}.
\]

These are resolution declarations, not limits that later approach zero.

## 2. Finite state and action records

At tick \(n\), the exposed state is

\[
s_n=(b_n,\theta_n),
\]

where \(b_n\) is the stored-energy count and \(\theta_n\) is the thermal count.
The action is

\[
a_n=(c_n,u_n),
\]

where \(c_n\) is a cooling level and \(u_n<0,=0,>0\) respectively records
charging, rest, or discharging.

Every alphabet is explicitly finite:

\[
b_n\in\{0,\ldots,32\},\quad
\theta_n\in\{2,\ldots,14\},\quad
c_n\in\{0,1,2,3\},\quad
u_n\in\{-2,-1,0,1,2\}.
\]

There is no unbounded search domain and no completed continuum state space.

## 3. Local retained transition

Each supplied tick has integer records for base load \(L_n\), solar supply
\(S_n\), thermal ingress \(H_n\), grid capacity \(G_n\), and rational price
\(p_n\). The thermal record changes by

\[
\theta_{n+1}=\theta_n+H_n-2c_n.
\]

This is a finite recurrence. It is not introduced as a discretization of a
prior differential equation.

For charge level \(k=-u_n>0\),

\[
b_{n+1}=b_n+4k,\qquad C_n=5k.
\]

For discharge level \(k=u_n>0\),

\[
b_{n+1}=b_n-5k,\qquad D_n=4k.
\]

The unequal retained counts expose storage loss directly. Nothing is hidden
inside a real efficiency parameter.

The tick demand and unresolved source requirement are

\[
Q_n=L_n+2c_n+C_n,\qquad
R_n=Q_n-S_n-D_n.
\]

The source reader uses grid capacity first and retains diesel only for the
remaining distinction:

\[
g_n=\min(\max(R_n,0),G_n),\qquad
d_n=\max(R_n-g_n,0).
\]

All `min`/`max` operations are finite-lattice readouts. A transition is absent
when storage, thermal, or diesel bounds fail. Absence is not encoded as an
infinite number.

## 4. Retained Burden Algebra

A local transition exposes the exact burden record

\[
\beta_n=(d_n,g_n,k_n,w_n,q_n,p_n^\ast),
\]

where the coordinates are diesel, grid, rational source cost, battery wear,
curtailment, and peak grid use.

Consecutive records compose as

\[
\beta\otimes\gamma=
(\beta_d+\gamma_d,\,
 \beta_g+\gamma_g,\,
 \beta_k+\gamma_k,\,
 \beta_w+\gamma_w,\,
 \beta_q+\gamma_q,\,
 \max(\beta_p,\gamma_p)).
\]

The identity is the all-zero rational record. The peak uses finite join
`max`, not a norm on a continuum and not an infinity sentinel.

Alternative histories that end in the same state are indistinguishable to
every future local transition. The reader therefore keeps one representative:

\[
\beta\oplus\gamma=\operatorname{lexmin}(\beta,\gamma)
\]

under the preregistered order

\[
\text{diesel}\prec\text{grid}\prec\text{source cost}
\prec\text{wear}\prec\text{curtailment}\prec\text{peak}.
\]

The additive coordinates precede peak deliberately. Translation by any future
additive burden preserves their order; if all additive coordinates tie, a
smaller current peak cannot become worse after a future finite `max`. This is
the preservation condition that permits histories to collapse by exposed
state without losing the declared terminal answer.

If a future protocol moves peak earlier in the reader order, peak must become
an exposed state distinction or the protocol must retain a nondominated
frontier. Silently discarding it would be an invalid compression.

## 5. Why this is an RCP upgrade

RCP 1.0 controls factor contraction. RCP-Energy preserves the same control
plane while changing the finite execution algebra:

1. **DECLARE** the tape, resolutions, terminal readouts, reader priority, and
   resource budgets.
2. **PREFLIGHT** the maximum readable state count, candidate count, and work
   ledger before tick zero.
3. **ADMIT** only bounded local transitions.
4. **RETAIN** one least-burden representative per exposed state.
5. **REPLAY** the complete selected lineage without planning.
6. **WITNESS** the output by complete enumeration on the small problem or a
   reversed action-order execution plus exact replay on the 96-tick problem.
7. Return **ACCEPT**, **HOLD**, or **BLOCK**.

The protocol does not call a black-box solver and then wrap its answer. The
finite lineage and resource consumption are the computed object.

## 6. Preflight resource certificate

For storage alphabet \(B\), thermal alphabet \(\Theta\), action alphabet \(A\),
and tape length \(N\), the conservative bounds are

\[
S_{\max}=|B||\Theta|,
\qquad
C_{\max}=N\,S_{\max}|A|,
\qquad
W_{\max}=5C_{\max}+N.
\]

The full challenge declares

\[
|B|=33,\quad |\Theta|=13,\quad |A|=20,\quad N=96,
\]

so

\[
S_{\max}=429,\qquad C_{\max}=823{,}680,\qquad
W_{\max}=4{,}118{,}496.
\]

Execution is refused before tick zero if the declaration budgets less than
these conservative bounds.

## 7. Finite minimality argument

Let \(R_n(s)\) be the burden retained for state \(s\) after \(n\) ticks.

**Base.** At tick zero, the initial state has the zero burden and every other
state is absent.

**Step.** Assume \(R_n(s)\) is the least declared burden among all admissible
histories ending in \(s\). Extend every retained \(s\) by every finite action.
Local composition gives the burden of each length-\(n+1\) history. Histories
ending in the same next state have identical future-readable state; retaining
their lexicographically lesser burden preserves every declared additive
priority. Peak preservation follows from the final-coordinate finite join.
Therefore \(R_{n+1}\) retains a least representative for every reachable next
state.

By finite induction, selecting the least terminal record after \(N\) ticks
returns the least declared complete history.

This argument is implemented and tested, but has not yet been translated into
a Coq theorem. Current tier: `Th_coqc-elig`.

## 8. Preservation evidence

The six-tick problem has \(6^6=46{,}656\) complete action histories. The
protocol enumerates all of them independently of state merging; 9,324 are
admissible. Its terminal readout agrees exactly with RCP-Energy.

The 96-tick problem is executed twice with opposite action-enumeration order.
Both produce the same exact rational terminal output. The selected lineage is
then replayed transition by transition. This is strong executable evidence,
but not a substitute for the pending Coq theorem.

## 9. Claim boundary

Established at `finite_diagnostic`:

- exact rational state, transition, burden, and output records;
- no infinity sentinel or continuum solver;
- preflight resource bounds;
- full 96-tick action/state readouts;
- exact replay preservation;
- complete enumeration agreement on the registered small problem;
- action-order invariance on the full problem;
- fail-closed budget, boundary, and witness controls.

Not established:

- empirical savings at a real cold store;
- conversion from diesel electrical-output quanta to litres of fuel;
- optimality under an undeclared objective order;
- universal superiority over established energy solvers;
- a Coq proof of the general retained-burden induction;
- control-system safety for deployment.

The stress tape is a mathematical problem family. Real deployment requires
measured records, calibrated device bounds, independent engineering review,
and a separate safety layer.

