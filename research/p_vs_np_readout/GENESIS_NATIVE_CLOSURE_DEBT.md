# Genesis-Native Cut/Closure Debt for the P-vs-NP Lane

**Status:** internal derivation / research target.  
**Claim boundary:** this note does **not** prove `P != NP`, a superpolynomial SAT lower bound, or a new unrestricted-circuit lower bound.

This note deliberately starts from Readout Genesis and the established IDM artifacts before importing any external lower-bound formalism.

## 1. Internal facts we are allowed to use

Readout Genesis v1.2 supplies five load-bearing rules.

1. **Strong future-reader equivalence.** A quotient state may identify two source states only when every declared future readout, under every declared intervention, agrees.
2. **NoEarlyCollapse.** If an encoding erases a distinction that a later readout can still require, no downstream solver may recreate that distinction from the collapsed record alone. The allowed repair is to enlarge state, restore lineage/tape, or increase resolution.
3. **Mandatory closure/lineage ledger.** `L_cl` is a required structured record whose role is `closure_and_lineage_ledger`.
4. **Cut action.** `S_cut` consumes `boundary`, `cut_currents`, and `closure_ledger`; its declared purposes are `unresolved_boundary_obligation`, `information_crossing`, and `interface_cost`.
5. **Invariant completion.** If a quotient merges states separated by a required invariant, the partition must be refined.

IDM supplies matching finite machinery.

- `IDM_DeclarationBound.v`: deferred future queries can force an injective retained record and hence a bit lower bound.
- `IDM_FutureReadoutWidth.v`: the branch lane already formalizes the generic `future queries -> injective middle state` mechanism for block-ordered equality.
- `tools/retained_contraction_protocol.py`: eliminating an internal distinction joins every active factor coupled to it and retains the remaining joined scope; work, peak retained elements and peak retained rank are explicitly ledgered.
- `tools/retained_burden_algebra.py`: reader-equivalent histories may share one representative, but burden composition is explicit (`sum` or `max`) and absence is not replaced by a fake infinity.
- `IDM_Schur.v`: in an exact finite linear-algebra atom, eliminating an internal degree of freedom produces a boundary complement rather than erasing its effect.
- `IDM_Reduction.v`: the repository's own solver kernels reduce to FOLD or bounded-witness DECISION; this is a theorem about IDM's solver architecture, **not** a theorem that every polynomial-time algorithm has this form.

## 2. The semantic cut obligation

Consider any finite ordered computation/closure ledger and a cut `t`. Let

- `H_t` be admissible histories on the past side of the cut;
- `U_t` be the declared family of future continuations/interventions;
- `O_t(h,u)` be the final readout after continuing history `h` with `u`.

Define the future signature

\[
\sigma_t(h)=(O_t(h,u))_{u\in U_t}.
\]

The Genesis sufficiency condition says that a retained boundary encoding `B_t` is legal only if

\[
B_t(h)=B_t(h')\Longrightarrow \sigma_t(h)=\sigma_t(h').
\]

Hence the minimal exact boundary state is the quotient by equality of future signatures. This is the already-formalized future-readout-width mechanism. It is useful, but by itself it is only a state/width lower bound.

## 3. Why raw retained bits cannot settle P vs NP

For an input of `N` bits, storing the entire input is always a sufficient retained record of `N` bits. Therefore no pure information-retention argument on one input can force more than `O(N)` bits without imposing an additional model restriction.

This is the internal reason the P-vs-NP lane must move from **retained state size** to **the cost of discharging closure obligations**.

## 4. Closure debt

At a cut, let `Omega_t` be the family of semantic obligations that remain unresolved: each obligation records a distinction whose two sides still have different allowed future readouts.

A closure/compute step `ell` may discharge some subset

\[
K(\ell)\subseteq \Omega_t.
\]

A valid ledger must eventually discharge every obligation needed by the terminal reader, while respecting causality and parent lineage.

The **closure debt** at the cut is not the number of input bits. It is the minimum number of legal future closure entries needed to discharge all current semantic obligations:

\[
\operatorname{CD}_t
=
\min\{|L|:\;L\text{ is a legal lineage-respecting continuation and discharges }\Omega_t\}.
\]

### Important audit

Taken literally, `CD_t` can collapse into "the size of the smallest remaining circuit" and therefore merely rename the original circuit-lower-bound problem. It becomes useful only if we exhibit a **separately computable or locally certifiable lower bound** on `CD_t` from Genesis/IDM invariants.

So `closure debt` is a target object, not yet a lower-bound method.

## 5. Retain--Recompute--Resolve: the Genesis-native trichotomy

Let `d` be a semantic distinction created before a cut. Suppose there exists an allowed future continuation under which changing `d` can change the terminal readout. If a computation removes `d` from the currently exposed state, then exactness forces at least one of three events before that future dependence is used:

1. **RETAIN:** an encoding of the semantic effect of `d` remains on the boundary;
2. **RECOMPUTE:** the effect of `d` is reconstructed from still-available information, and the reconstruction work is charged;
3. **RESOLVE:** a certified closure step proves that the future reader is now insensitive to the distinction, so the obligation legitimately disappears.

If none occurs, two histories that differ in a future-readable way have been collapsed with no admissible route for recovery, contradicting NoEarlyCollapse / state sufficiency.

This is currently a **schema derived from the Genesis contract**, not yet a standalone Coq theorem, because a theorem must first freeze the exact machine interface for "available information", "recompute", and "resolve".

For a semantic obligation `d`, the accounting form is

\[
\boxed{
\chi_{\mathrm{retain}}(d,t)
+
\chi_{\mathrm{recompute}}(d,t)
+
\chi_{\mathrm{resolve}}(d,t)
\ge 1
}
\]

whenever `d` remains future-relevant across the cut.

This is stronger as a research guide than a retained-bit count because it explicitly admits the standard escape hatch "forget and compute again" and forces that escape hatch into the cost ledger instead of pretending it does not exist.

## 6. Delayed-return multiplicity

Genesis explicitly audits delayed-return/memory sufficiency. This suggests a second object. For each semantic distinction `d`, count the number of separated future regions in which its effect becomes relevant again after an interval where it is not exposed:

\[
\operatorname{DR}(d)=
\#\{\text{future re-entry episodes of }d\}.
\]

A naive sum of `DR(d)` is **not** a lower bound: a retained representation can be reused across arbitrarily many episodes. The meaningful quantity is a tradeoff:

- retain the semantic effect across the interval and pay boundary burden;
- or drop it and pay reconstruction when the effect returns;
- or resolve it permanently.

This is the direct Genesis analogue of the retain/recompute tradeoff seen operationally in RCP and pebbling, but the charge is defined semantically by future readers rather than by a chosen elimination graph.

## 7. Quotient before charging: symmetry and reader equivalence

Genesis requires query-relative symmetry and reader equivalence before treating distinctions as separate. Therefore the obligation set must be quotiented before any count:

\[
\widetilde\Omega_t
=
\Omega_t / (\text{reader equivalence + admissible query-relative symmetry}).
\]

This prevents fake lower bounds obtained by counting syntactic copies, variable renamings, ordering artifacts, or provenance that the target reader does not distinguish.

The burden must be charged only on semantically distinct future-readout obligations.

## 8. The provenance firewall

Genesis requires lineage for reproducibility, but an ordinary Boolean circuit is not required to preserve historical provenance when two wires compute extensionally identical Boolean functions.

Therefore a P-vs-NP lower bound may **not** charge a circuit merely for losing provenance. A charged obligation must be semantic: erasing it must permit two source situations that some allowed future reader distinguishes.

This is a critical firewall. Any lower bound that relies only on `lineage_slots` as bookkeeping proves a lower bound for a stronger Genesis-compliant machine, not for unrestricted Boolean circuits.

## 9. The contraction firewall

RCP's rule that eliminating a variable joins every active coupling gives genuine exponential-in-boundary costs for variable-elimination/contraction algorithms. But an arbitrary Boolean circuit is not required to perform variable elimination.

Therefore

\[
\text{large RCP induced width}\not\Rightarrow\text{large unrestricted circuit size}
\]

without a separate simulation theorem. RCP remains a controlled restricted-model lane and a source of candidate boundary invariants.

## 10. The circuit-to-ledger bridge we actually need

Define a **semantic Genesis ledger** to keep only extensional obligations required by the Boolean readout, with no provenance-only charges.

### Circuit-to-Genesis Semantic Ledger (CGSL) — OPEN AS A FORMAL BRIDGE

For every fan-in-two DeMorgan circuit `C` computing Boolean function `f`, construct in topological order a Genesis semantic ledger `L(C)` such that

1. its terminal reader is exactly `f`;
2. every charged cut obligation is future-readout semantic, not provenance-only;
3. every circuit gate creates at most `O(1)` ledger entries;
4. sharing/fanout is preserved rather than unfolded into a formula;
5. `|L(C)| = O(|C|)`;
6. no target answer or truth table is imported into the constructor.

This bridge should be elementary, but it must be written explicitly because every later lower-bound transfer depends on it.

If `GCC(f)` is the minimum size of such a semantic closure ledger, CGSL gives

\[
GCC(f)\le O(\operatorname{CircuitSize}(f)).
\]

Thus a superpolynomial lower bound on `GCC(SAT_N)` would imply a superpolynomial circuit lower bound. The difficulty has not disappeared: `GCC` is deliberately close to circuit complexity. The point is to expose a ledger on which Genesis-native invariants can act.

## 11. What Genesis adds beyond an unordered closure cover

`L_cl` and `Tape` retain **order, parentage, sharing and delayed return**. An unordered family of closure rules forgets all four.

This suggests studying a sequential adversarial object:

\[
\mathcal A_0
\xrightarrow{\ell_1}
\mathcal A_1
\xrightarrow{\ell_2}
\cdots
\xrightarrow{\ell_s}
\mathcal A_s,
\]

where `A_t` is a compressed family of still-admissible future-readout states after seeing the first `t` ledger entries. The update must be computable from ledger syntax and certified local facts; it may not solve circuit equivalence or SAT internally.

The target is a **causal closure adversary** that survives every semantic ledger of polynomial size for an explicit SAT encoding. Such an adversary would be a constructive refuter of small circuits.

## 12. Multi-resource burden, not another scalar potential

Genesis explicitly separates invariant multiplicity, rank multiplicity, generation multiplicity and raw ordering count. Retained Burden Algebra already supports a finite vector whose coordinates compose by different rules (`sum` or `max`).

The next internal experiment should therefore track a vector

\[
\mathfrak B_t=
(
\text{future-distinction burden},
\text{boundary burden},
\text{recompute burden},
\text{closure multiplicity},
\text{generation multiplicity},
\text{reconvergence/delayed-return burden}
),
\]

rather than immediately collapsing everything to one scalar `Phi`.

The hypothesis to test is a tradeoff theorem of the form

\[
\boxed{
\text{a cheap gate may reduce one burden component only by retaining,}
\atop
\text{recomputing, or certifiably resolving the corresponding semantic debt.}
}
\]

A useful theorem would need to be representation-robust and valid under fanout sharing. Simple rank, raw state count and fixed-distribution measures are already known in this branch to be insufficient on their own.

## 13. The exact next theorem targets

1. **Formalize CGSL** for the DeMorgan basis with sharing preserved.
2. **Formalize a finite Retain--Recompute--Resolve interface** where available past information and reconstruction operations are explicitly typed; prove the trichotomy as a NoEarlyCollapse corollary.
3. **Define a semantic cut-debt certificate** after quotienting reader symmetries; incidence facts must be exact.
4. **Build tiny exact diagnostics** (`n <= 4`) that enumerate shared circuits and verify that extensionally equivalent rewrites have the same semantic debt even when provenance differs.
5. **Search for a multi-resource gate tradeoff** and actively construct counterexamples to every candidate law.
6. Promote a law only if it survives sharing, rewrites, basis changes, input rereading/recomputation, and the raw-input-storage counterexample.

The load-bearing open question is now more precise than "closure debt":

\[
\boxed{
\text{Does SAT force a superpolynomial cumulative Retain--Recompute--Resolve burden}
\atop
\text{for every polynomial-size semantic Genesis ledger?}
}
\]

Nothing in the current IDM/Genesis corpus proves this. The value of the reformulation is that every known escape hatch is now explicit in the ledger: retain, recompute, resolve, or fail exactness. The missing breakthrough is a SAT family for which **all three legal escape routes cannot remain polynomial simultaneously**.
