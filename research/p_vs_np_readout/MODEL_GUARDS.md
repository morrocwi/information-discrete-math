# Model guards for the P-vs-NP readout lane

These guards are load-bearing.  Violating one invalidates any claimed implication to `P != NP`.

## G1 — Terminal-readout collapse

For a Boolean language `L`, the terminal answer itself is a sufficient one-bit readout:

\[
q(x)=L(x),\qquad D=\mathrm{id}.
\]

Therefore the complexity of a decision problem cannot be lower-bounded from the cardinality or
dimension of its **terminal sufficient quotient**.  Complexity must enter through the cost of the
trajectory that constructs the terminal readout.

This is why the Navier--Stokes question "how small is the sufficient state?" changes character in
complexity theory.  For SAT, the unconstrained terminal sufficient state is already as small as it
can be.

## G2 — No target-answer leakage

A proposed readout constructor may not call SAT, insert a known SAT/UNSAT label, fit against held-out
answers, or use an equivalent oracle.  Otherwise `q=L` makes every language look trivial.

This is the computational specialization of Readout Genesis's `target_answer_as_parameter` firewall.

## G3 — No over-sufficiency

A polynomial-time decision algorithm for SAT is required to output one bit.  It is **not** required,
from one execution state, to:

* reconstruct a satisfying witness;
* reconstruct the full formula;
* answer every counterfactual restriction without rerunning;
* preserve all intervention responses;
* preserve all future search branches;
* provide a human-readable UNSAT proof.

Demanding those stronger outputs can create genuine lower bounds against a stronger model while saying
nothing about P versus NP.

SAT self-reducibility does not remove this guard: a decision algorithm may be rerun polynomially many
times on restricted formulas to recover a witness if SAT is in P.  That does not imply that one run's
internal readout must already encode all counterfactual answers.

Accordingly, the general Readout Genesis state-sufficiency checklist must be narrowed to the exact
complexity question.  Extra dynamic/intervention sufficiency may be studied, but it must be labelled as
a stronger model.

## G4 — Restricted-model lower bounds stay restricted

A mixed fiber for a chosen syntactic summary, exponential resolution proof size, large OBDD width,
high treewidth, high Nullstellensatz degree, or an AC0 lower bound is valuable, but none constrains an
arbitrary polynomial-time Turing machine without a separately proved simulation/transfer theorem.

The transfer theorem is never implicit.

## G5 — Counting computation states is not a time lower bound

A polynomial-space machine can have exponentially many possible configurations while representing its
current configuration with polynomially many bits.  Showing that a decision partition has many
possible states, histories or residual formulas therefore does not imply that one input requires
superpolynomial time.

Any state-count argument must connect to a per-input traversal requirement, not merely to the size of
the global configuration space.

## G6 — Pure black-box readout arguments relativize

If the proof continues to work unchanged when all algorithms receive an arbitrary oracle, it cannot
settle P versus NP by itself: Baker--Gill--Solovay give oracle worlds with both `P^A=NP^A` and
`P^B!=NP^B`.

The eventual load-bearing theorem must therefore use a non-black-box property of ordinary computation
or another ingredient whose failure under oracle substitution is explicit.

## G7 — Low-degree algebra alone is not an escape certificate

Arithmetizing formulas or readouts can be useful, but the load-bearing step must be checked against the
Aaronson--Wigderson algebrization barrier.  "We used polynomials" is not evidence that relativization
has been overcome strongly enough.

## Consequence

The honest target is no longer a smaller terminal state.  It is a lower bound on the **construction
trajectory**:

\[
\boxed{
\text{input formula}
\xrightarrow[\text{ordinary deterministic computation}]{\text{retained trajectory}}
\text{one-bit exact decision readout}
}
\]

To prove `P != NP`, one must establish that this trajectory has superpolynomial worst-case cost for
SAT while respecting G1--G7.  That is the current open frontier of this lane.
