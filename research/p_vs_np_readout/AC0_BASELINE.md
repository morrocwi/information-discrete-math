# First restricted baseline: SAT is not an AC0 decision readout

**Status:** standard external lower-bound theorem + explicit local reduction.  This is a restricted
complexity result, **not** P versus NP.

The point of this baseline is methodological: the readout lane should be able to reproduce a genuine
complexity lower bound in a model where lower bounds are known before attempting unrestricted
polynomial time.

## Local parity-to-CNF reduction

For input bits

\[
x_1,\ldots,x_n\in\{0,1\},
\]

introduce auxiliary Boolean variables

\[
y_0,\ldots,y_n.
\]

Impose

\[
y_0=0,
\qquad
y_i=y_{i-1}\oplus x_i,
\qquad
y_n=1.
\]

When `x_i=0`, encode equality with

\[
(\neg y_{i-1}\lor y_i)\land(y_{i-1}\lor\neg y_i).
\]

When `x_i=1`, encode inequality with

\[
(y_{i-1}\lor y_i)\land(\neg y_{i-1}\lor\neg y_i).
\]

The endpoint conditions are unit clauses `not y_0` and `y_n`.

The resulting 2-CNF is satisfiable exactly when

\[
\boxed{x_1\oplus\cdots\oplus x_n=1.}
\]

Each output clause is selected by one input bit using a constant-size local pattern.  Under a standard
fixed encoding this is an AC0 many-one reduction.

`parity_to_cnf_baseline.py` exhaustively checks the logical equivalence for all bit strings up to the
configured finite size.

## Restricted lower-bound consequence

The classical Furst--Saxe--Sipser / Ajtai / Håstad lower bounds give

\[
PARITY\notin AC^0.
\]

If CNF-SAT had polynomial-size constant-depth unbounded-fan-in AND/OR/NOT circuits, composing such a
circuit with the local reduction above would place PARITY in `AC0`, a contradiction.  Therefore

\[
\boxed{CNF\text{-}SAT\notin AC^0.}
\]

This is an actual lower bound on an answer-producing readout circuit class.  It is useful as a positive
control for the programme because the transfer theorem is explicit.

## Why this does not approach P directly

`AC0` is a tiny subclass of polynomial time.  General polynomial-time algorithms may use growing
depth, arbitrary intermediate representations, iteration, random access and nonlocal computation.
The parity reduction therefore does not constrain P.

The next ladder step must enlarge the admitted constructor class while retaining a provable
obstruction.  Any statement that silently identifies an AC0/local readout with an arbitrary P
computation violates `MODEL_GUARDS.md`.

## References

* Merrick Furst, James Saxe, Michael Sipser, parity lower bounds for bounded-depth circuits.
* Miklos Ajtai, constant-depth lower bounds.
* Johan Hastad, switching-lemma / small-depth circuit lower bounds.
