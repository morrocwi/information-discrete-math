# P vs NP Closure Audit — IDM / Readout Genesis Lane

**Status:** architecture substantially closed; Millennium separation **not proved**.  
**Claim boundary:** this document identifies exactly what is now formalized and the one semantic lower-bound premise that remains open. It must not be cited as a proof of `P != NP`.

## 1. What is now closed structurally

The branch now has an explicit finite chain from ordinary shared Boolean circuits into the Genesis accounting language and back out to circuit lower bounds.

### A. Circuit -> semantic ledger (CGSL)

`formal/IDM_CircuitGenesisBridge.v` defines a fan-in-two DeMorgan DAG and compiles it to one ledger entry per gate. The compiler preserves:

- the original gate descriptors and parent references;
- DAG sharing (there is no formula unfolding);
- topological gate indices;
- full finite semantics; and
- the terminal Boolean reader.

Thus the elementary bridge has exact size overhead 1 ledger entry per circuit gate in this model.

### B. NoEarlyCollapse -> Retain/Recompute/Resolve

`formal/IDM_RetainRecomputeResolve.v` formalizes the Genesis-native three-channel consequence. If two histories have different future readouts, an exact decoder cannot receive equal values simultaneously in all three channels:

\[
R(h)=R(h'),\quad Q(h)=Q(h'),\quad C(h)=C(h')
\]

where `R` is retained semantic information, `Q` is a recomputation seed, and `C` is a certified resolved/closure record.

With decidable equality on the finite channels this yields

\[
\boxed{
O(h,u)\ne O(h',u)
\Longrightarrow
R(h)\ne R(h')\;\lor\;Q(h)\ne Q(h')\;\lor\;C(h)\ne C(h').
}
\]

The same file proves finite set-cover-style aggregation for explicitly listed semantic obligations.

### C. The recomputation degeneracy is explicit

The same file also proves a no-go theorem: if the complete source history is allowed as the recomputation seed and the decoder may invoke the target readout at uncharged cost, every future-readout problem becomes trivially exact.

Therefore an RRR theorem relevant to `P vs NP` must charge the computational cost of constructing and using the recompute channel. Merely bounding retained state is insufficient.

### D. Semantic-ledger lower bounds transfer back to circuits

`formal/IDM_CircuitLedgerTransfer.v` proves the bookkeeping implication:

\[
\bigl[\forall L\text{ correct},\; |L|>B\bigr]
\land
\bigl[C\mapsto L(C),\;|L(C)|\le |C|\bigr]
\Longrightarrow
\forall C\text{ correct},\; |C|>B.
\]

So a genuine lower bound proved inside the semantic-ledger model is no longer stranded there; under the CGSL hypotheses it transfers directly to the corresponding DeMorgan circuit model.

### E. Resource-aware RRR arithmetic is isolated

`formal/IDM_RRRCostLowerBound.v` proves the finite kernel

\[
D\le R+Q+C,
\qquad
R\le s\kappa_R,
\quad Q\le s\kappa_Q,
\quad C\le s\kappa_C
\]

implies

\[
\boxed{
D\le s(\kappa_R+\kappa_Q+\kappa_C).
}
\]

Hence an independently certified demand `D` exceeding every polynomial gate budget times the allowed per-gate capacity would yield a superpolynomial circuit lower bound.

This arithmetic is easy; identifying a valid SAT demand/capacity pair is the hard part.

## 2. Negative controls that rule out fake completions

The branch deliberately contains counterexamples to several tempting but invalid completions.

### Raw future-signature count is not circuit size

For equality on two `m`-bit blocks, fixing the first block yields exactly `2^m` distinct future residual functions. Nevertheless a shared DeMorgan DAG computes equality with `6m-1` non-input gates in the explicit diagnostic `rrr_circuit_audit.py`.

Therefore

\[
\#\{\text{future residuals}\}
\not\le O(\text{circuit gates})
\]

in general. One shared gate can participate in resolving exponentially many semantic contexts.

### Raw retained bits are not time

The full input itself is an `O(n)`-bit sufficient seed. Any argument that ignores decoder/recomputation work merely moves the hard computation into the decoder.

### Variable-elimination width is not unrestricted circuit size

RCP gives honest work/peak-boundary lower bounds for declared contraction/elimination schedules, but arbitrary Boolean circuits are not required to follow such schedules.

### Provenance is not semantic complexity

Genesis retains lineage for reproducibility, but an ordinary circuit may merge extensionally identical computations. A lower bound may charge only distinctions that a declared future Boolean reader can still separate, never provenance alone.

## 3. The exact remaining theorem

After the above bridges are closed, the entire lane reduces to one genuinely load-bearing statement.

We need an explicit, non-circular semantic demand `H_n` for the canonical SAT Boolean function, together with a capacity accounting valid for **every** small shared circuit, such that:

\[
\boxed{
H_n(SAT_n)
>
B(n)\,K_n
}
\]

for every polynomial gate budget `B(n)` for sufficiently large `n`, while every `B(n)`-gate circuit has total legal Retain/Recompute/Resolve capacity at most `B(n) K_n`.

Equivalently, one may construct a uniform refuter

\[
\mathcal R_n(C)=x
\]

that, from the syntax/lineage of every circuit `C` below the proposed bound and without a SAT/equivalence oracle, outputs a concrete input satisfying

\[
C(x)\ne SAT_n(x).
\]

Either form would provide the missing unrestricted-circuit lower bound ingredient.

## 4. Requirements on the missing SAT invariant/certificate

A candidate `H_n` is admissible only if all of the following hold:

1. **No circular definition.** It cannot be defined as minimum circuit size, minimum remaining work, or another quantity already equivalent to the desired lower bound.
2. **No target leakage.** Its certificate/checker cannot call SAT, circuit equivalence, MCSP, or import the correct output table.
3. **Semantic, not syntactic.** Harmless rewrites, variable renamings and shared equivalent subcircuits cannot create fake hardness.
4. **Sharing-aware.** Its per-gate capacity theorem must permit one gate to service many contexts, as the equality negative control demonstrates.
5. **Recomputation-aware.** Keeping/re-reading the input or an intermediate seed is legal, but the actual decoder/reconstruction work must enter the ledger.
6. **Basis/simulation discipline.** Any bound first proved in a restricted model must come with an explicit simulation/transfer theorem before being claimed for unrestricted circuits.
7. **Barrier audit.** A final separation argument must be checked against relativization, algebrization and Natural-Proofs-style obstacles rather than assuming that a renamed invariant escapes them.

## 5. Final status

The IDM/Readout Genesis corpus now supplies a coherent **architecture for expressing** an unrestricted circuit lower bound:

\[
\text{Circuit}
\to
\text{Genesis semantic ledger}
\to
\text{RRR obligation/cost accounting}
\to
\text{ledger lower bound}
\to
\text{circuit lower bound}.
\]

The first, second and last arrows have finite formal candidates on this branch; the arithmetic cost kernel is also formalized. What remains is not another bridge or bookkeeping lemma. It is the substantive lower-bound theorem:

\[
\boxed{
\text{SAT has superpolynomial semantic RRR demand relative to every small shared circuit.}
}
\]

Nothing presently proved in IDM or Readout Genesis establishes that statement. Declaring `P != NP` before this premise is independently proved would simply hide the Millennium problem inside the definition of “demand”, “closure debt”, or “recompute cost”.

Accordingly the correct branch status is:

- **architecture:** closed enough to attack the target;
- **finite structural lemmas:** formal candidates, pending CI where newly added;
- **restricted lower-bound controls:** present;
- **unrestricted SAT lower bound:** `OPEN`;
- **P vs NP:** `OPEN`.
