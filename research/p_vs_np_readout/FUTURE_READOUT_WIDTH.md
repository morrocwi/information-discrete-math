# Future-Readout Width: the Readout-Genesis Quotient Behind OBDD Lower Bounds

**Status:** exact finite derivation + restricted-model lower bound.  
**Claim boundary:** this is an OBDD / ordered-read-once state lower bound, **not** a proof of `P != NP`.

This note makes one part of the Readout Genesis-to-complexity bridge exact.  The strong Genesis
quotient condition says that two retained states may be identified only when every declared future
readout agrees under every allowed future intervention.  For a Boolean function under a fixed variable
order, this is exactly equality of residual Boolean functions after a prefix assignment.

---

## 1. Future-readout equivalence

Let

\[
f:\{0,1\}^n\to\{0,1\}
\]

and fix a variable order `sigma`.  After the first `k` variables have been assigned a prefix `a`, let

\[
f_a(b):=f(a,b)
\]

be the residual Boolean function on the remaining suffix variables.

Define

\[
\boxed{
a\sim_k a'
\iff
\forall b,\;f_a(b)=f_{a'}(b).
}
\]

The class `[a]_{\sim_k}` is the minimal exact future-readout state at level `k`: two prefixes can be
merged precisely when no future suffix assignment can distinguish them at the terminal Boolean
readout.

Let

\[
N_k(f,\sigma)
:=
\#\{f_a:a\in\{0,1\}^k\}
\]

be the number of distinct residual future-readout signatures.

---

## 2. Width theorem

Consider any deterministic layered ordered read-once branching program that follows `sigma`.  Let
`s_k(a)` be its state after reading prefix `a`, and suppose it computes `f` exactly.

If

\[
s_k(a)=s_k(a'),
\]

then the computation has the same state and sees the same future suffix `b`, hence must return the same
terminal answer for every `b`.  Therefore

\[
\boxed{
s_k(a)=s_k(a')\Longrightarrow a\sim_k a'.}
\]

Taking the contrapositive, inequivalent future-readout classes require distinct states.  Thus

\[
\boxed{
\operatorname{width}_k\ge N_k(f,\sigma).
}
\]

and consequently

\[
\boxed{
\operatorname{size}\ge \max_k N_k(f,\sigma).
}
\]

For a reduced OBDD this bound is tight at each level up to the usual convention about skipped tests:
its nodes represent distinct residual subfunctions.  The theorem is standard branching-program/OBDD
mathematics; the contribution here is to identify it as the exact finite specialization of Readout
Genesis future-readout equivalence, not to claim a new OBDD lower-bound method.

---

## 3. Exact equality family

Define

\[
EQ_m(x_1,\ldots,x_m,y_1,\ldots,y_m)=1
\iff
(x_1,\ldots,x_m)=(y_1,\ldots,y_m).
\]

Use the **block order**

\[
\sigma_{\rm block}=(x_1,\ldots,x_m,y_1,\ldots,y_m).
\]

At the middle layer `k=m`, each prefix `a in {0,1}^m` induces

\[
(EQ_m)_a(y)=1\iff y=a.
\]

If `a != a'`, choose the future intervention `y=a`. Then

\[
(EQ_m)_a(a)=1,\qquad (EQ_m)_{a'}(a)=0.
\]

Hence every pair of distinct prefixes has distinct future-readout signature, so

\[
\boxed{
N_m(EQ_m,\sigma_{\rm block})=2^m
}
\]

and every ordered read-once branching program respecting the block order has

\[
\boxed{
\operatorname{width}_m\ge 2^m.
}
\]

This is a direct Declaration-Bound-style injectivity proof: the future query family recovers the whole
`m`-bit prefix.

---

## 4. Ordering negative control

The same Boolean function under the interleaved order

\[
\sigma_{\rm int}=(x_1,y_1,x_2,y_2,\ldots,x_m,y_m)
\]

has at most three distinct residual states at every level:

1. the already-failed constant-0 residual;
2. the still-equal residual on the untouched pairs;
3. after reading an `x_i` but before `y_i`, one of two pending-bit residuals; counting together with
   the failed state yields width at most 3.

The executable exact truth-table counter in `future_readout_width.py` verifies the full residual-width
sequence.  For `m>=2`, the maximum is

\[
\max_k N_k(EQ_m,\sigma_{\rm block})=2^m,
\qquad
\max_k N_k(EQ_m,\sigma_{\rm int})=3.
\]

This negative control is essential: the exponential lower bound is about the declared order/model,
not about `EQ_m` under unrestricted computation.

---

## 5. Relation to RCP/RFT

The result is the Boolean analogue of IDM retained-boundary closure.  After a prefix is closed, the
machine must retain exactly enough boundary information to preserve every declared terminal readout.
Under block-ordered equality, the entire `m`-bit prefix remains relevant to the future `y` boundary, so
there are `2^m` distinguishable retained states.  Under interleaving, each pair is closed immediately;
once a pair matches, only the global still-equal flag and one pending bit need survive.

Thus the same function can have exponentially different retained width depending on closure order.
This mirrors the RCP dependence on induced width rather than on the raw global configuration count.

---

## 6. Literature reconciliation

This future-subfunction method is established in OBDD and knowledge-compilation theory.  In particular,
Bova and Slivovsky relate OBDD lower bounds for graph CNFs to many distinct subfunctions and prove
exponential OBDD lower bounds for bounded-degree CNF families using expander structure.  Amarilli,
Monet and Senellart connect OBDD/structured-DNNF compilation size to pathwidth/treewidth, and Capelli
and Mengel study width under quantification.

Accordingly, this file is a **reconciliation theorem** for the Readout architecture and a validation
baseline.  It becomes relevant to P vs NP only if a later theorem transports such a retained-state
obstruction to a substantially more general computational model.

---

## 7. Next bridge

The restricted theorem has the exact shape we want:

\[
\text{many future readouts}
\Rightarrow
\text{many inequivalent retained states}
\Rightarrow
\text{large width}.
\]

The load-bearing open question is how far the middle implication survives when a machine may:

- reread variables;
- choose queries adaptively;
- recompute instead of retaining information;
- use unrestricted Boolean circuits rather than one ordered read-once path.

The next research target is therefore a **recomputation-aware future-readout bound**, expressed as a
time-space or state-transition cost ledger rather than static state size alone.  Any successful theorem
must specify the machine model and be audited against known lower-bound barriers before it is connected
to `P` versus `NP`.
