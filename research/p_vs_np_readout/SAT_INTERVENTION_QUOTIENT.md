# SAT Intervention Quotient: from Readout Genesis to a Cost-Coupled Complexity Target

**Status:** research derivation / restricted theorems + open unrestricted bridge.  
**Claim boundary:** this document does **not** prove `P != NP` or `P = NP`.

This note revises the first P-vs-NP readout attack after re-reading the actual IDM and Readout Genesis
machinery.  The decisive correction is that Readout Genesis does not define a sufficient state only by
its present terminal output.  For a declared horizon/intervention family it requires equality of all
future readouts under the allowed interventions.  For SAT this suggests studying the residual decision
profile under partial assignments.

---

## 1. Intervention readout

Let `F(X,Y)` be a CNF formula.  `X` is the exposed intervention boundary and `Y` is the still-hidden
witness/internal variable set.  For a partial or total assignment `rho` on `X`, define

\[
\mathsf{IR}_F(\rho)
:=
\mathsf{SAT}(F\!\upharpoonright_\rho).
\]

The **SAT intervention signature** is the whole function

\[
\boxed{
\Sigma_F:\rho\longmapsto \mathsf{IR}_F(\rho).
}
\]

and intervention equivalence is

\[
\boxed{
F\equiv_I G
\iff
\Sigma_F=\Sigma_G.
}
\]

This is the SAT specialization of the strong Readout Genesis condition that two quotient states may be
identified only when their future declared readouts agree for every allowed intervention.

The quotient

\[
\mathcal Q_I=\{F\}/\!\equiv_I
\]

is therefore a query-relative sufficient state object.  It is deliberately stronger than the one-bit
readout `SAT(F)`.

---

## 2. Generic intervention separation lemma

Suppose a compiler stores a finite record

\[
C(F)\in R
\]

and a decoder answers every declared intervention query:

\[
D(C(F),\rho)=\mathsf{IR}_F(\rho).
\]

Then record equality forces intervention-signature equality:

\[
\boxed{
C(F)=C(G)
\Longrightarrow
\Sigma_F=\Sigma_G.
}
\]

Equivalently, if some intervention separates two formulas,

\[
\exists\rho:\mathsf{IR}_F(\rho)\ne\mathsf{IR}_G(\rho),
\]

then any exact all-intervention compiler must retain different records for `F` and `G`.

This is exactly the information-theoretic skeleton of the IDM Declaration Bound: a deferred record
that must answer an as-yet-unselected member of a query family has to separate every source object whose
query-response profiles differ.

---

## 3. Exact binary witness family

For a bit string

\[
b=(b_1,\ldots,b_m)\in\{0,1\}^m,
\]

define the satisfiable unit-CNF

\[
F_b
=
\bigwedge_{i=1}^m
\begin{cases}
(x_i),&b_i=1,\\
(\neg x_i),&b_i=0.
\end{cases}
\]

Every `F_b` is satisfiable.  For the fixed query family

\[
\rho_i:=\{x_i=1\},
\]

we have

\[
\boxed{
\mathsf{SAT}(F_b\!\upharpoonright_{\rho_i})=b_i.
}
\]

Hence

\[
b\ne c
\Longrightarrow
\Sigma_{F_b}\ne\Sigma_{F_c}.
\]

There are `2^m` distinct intervention profiles although the ordinary top-level SAT answer is `1` for
every member of the family.

Therefore any exact compiled record that, **without rereading the source formula**, must later answer
all `m` queries has to distinguish all `2^m` formulas.  If the record alphabet is binary, the IDM
Declaration Bound pigeonhole argument gives a worst-case lower bound

\[
\boxed{S\ge m\text{ bits}.}
\]

`research/p_vs_np_readout/sat_intervention_quotient.py` checks this identity exhaustively on finite
cubes.

This is a real lower bound for the declared compiled/deferred-query model.  It is not a P-vs-NP
separation.

---

## 4. First no-go theorem: pure retained-space cannot settle P vs NP

For an arbitrary CNF `F`, the identity compiler

\[
C_{\rm id}(F)=\operatorname{enc}(F)
\]

uses only `O(|F|)` bits.  With unbounded decoder time, the decoder can reconstruct each restricted
formula and decide it by exhaustive search.

Therefore no argument that measures **only static retained record size** can prove that SAT needs a
superpolynomial representation: storing the input itself is always a polynomial-size exact retained
record.

The missing resource is online computation time.

The corrected complexity object is therefore not

\[
\operatorname{size}(C(F))
\]

alone, but a cost pair such as

\[
\boxed{
\bigl(\operatorname{CompileCost},\operatorname{RecordBits},\operatorname{QueryCost}\bigr).
}
\]

This is the SAT analogue of IDM's rule that complexity claims require an explicit cost ledger.

---

## 5. Polynomial-time intervention bridge

Assume `SAT in P`, witnessed by a deterministic algorithm `A` with polynomial running time.
Use the identity compiler `C_id(F)=enc(F)`.  Given a partial assignment `rho`, construct
`F|rho` in polynomial time and run `A`.

Hence

\[
\boxed{
SAT\in P
\Longrightarrow
\text{every CNF has an }O(|F|)\text{-bit intervention record with polynomial query time.}
}
\]

Consequently, an unconditional theorem of the following form would imply `P != NP`:

> There exists an explicit polynomial-size CNF family `F_n` such that **every** exact representation
> of `F_n` with polynomially bounded record size requires superpolynomial time for some declared
> intervention query, even when the decoder is an arbitrary deterministic algorithm.

This is a legitimate target, but proving it is already a major lower-bound problem.  It must not be
presented as if the identity compiler had been excluded for free.

---

## 6. Residual-SAT circuit bridge

Split a polynomial-size CNF as `F_n(X,Y)` and define the total-assignment intervention function

\[
\boxed{
g_{F_n}(a)=1
\iff
\exists y\;F_n(a,y)=1.}
\]

This is precisely the query-response function of the intervention quotient on the exposed variables.

If `SAT in P`, then `g_{F_n}` is computable in polynomial time from `(F_n,a)`; for an explicit
polynomial-size family, standard machine-to-circuit simulation yields polynomial-size Boolean circuits
for `g_{F_n}`.

Thus an explicit family satisfying

\[
\boxed{
\operatorname{CircuitSize}(g_{F_n})=n^{\omega(1)}
}
\]

would imply `P != NP` (indeed, a sufficiently explicit NP function outside `P/poly` gives a stronger
nonuniform separation).

Conversely, Cook-Levin/Tseitin-style encodings show why this target is broad: NP verifier computations
can be represented by polynomial-size CNF with exposed input variables and existential internal
variables.  The intervention profile therefore contains the usual circuit-lower-bound frontier rather
than bypassing it.

This is the cleanest current bridge between Readout Genesis intervention sufficiency and mainstream
complexity theory.

---

## 7. RCP/RFT interpretation

IDM's RCP/RFT architecture closes an internal distinction only after its effect on the declared
terminal boundary has been retained.  For CNF variable elimination, the SAT analogue is:

\[
\text{eliminate }y
\quad\longrightarrow\quad
\text{retain the residual Boolean relation on the live boundary}.
\]

For restricted compilation languages (OBDD, FBDD, DNNF, structured d-DNNF), the size of this retained
boundary object is controlled by graph-width-like parameters and can be exponential.  This is already a
well-developed knowledge-compilation literature; these restricted lower bounds are therefore a
validation target for the readout formalism, not a novelty claim.

The unrestricted barrier is the same one that matters for P vs NP: a general polynomial-time machine is
not required to expose an OBDD/DNNF/elimination table as its retained state.

---

## 8. What the programme should attack next

The earlier target `UNRCLB` was too close to simply restating `P != NP`.  The sharper intermediate
object is now the **intervention response function** `g_F` plus a machine-explicit cost measure.

Three staged targets are useful:

1. **Restricted recovery target — CLOSED/KNOWN TEMPLATE.** Re-derive known exponential OBDD/DNNF or
   elimination-width lower bounds as retained-boundary theorems.  This tests the machinery against
   established complexity results.
2. **General compiled-query target — OPEN.** Prove a superpolynomial lower bound for a representation
   model strictly more general than the restricted knowledge-compilation languages, while keeping the
   decoder polynomial-time.
3. **General circuit target — OPEN / load-bearing.** Produce an explicit residual-SAT function `g_F`
   requiring superpolynomial unrestricted Boolean circuits or an equivalent non-black-box machine lower
   bound, with explicit audits for relativization, algebrization and Natural Proofs.

Only stage 3 is close enough to settle P vs NP.  Stages 1-2 are useful only if their simulation bridge
is stated exactly.

---

## 9. Literature reconciliation

This note does not claim that intervention compilation, OBDD/DNNF width, or preprocessing complexity is
new.  Relevant established lines include:

- Cadoli, Donini, Liberatore, Schaerf, *Preprocessing of Intractable Problems*, Information and
  Computation 176 (2002), 89-120.
- Amarilli, Capelli, Monet, Senellart, work connecting knowledge-compilation size to treewidth/pathwidth
  (extended versions arXiv:1709.06188 and arXiv:1811.02944).
- Capelli and Mengel, *Knowledge Compilation, Width and Quantification*, arXiv:1807.04263.

The IDM/Readout contribution in this research lane is the common retained-information formulation,
explicit cost ledger, fail-closed claim discipline, and the attempt to identify a non-black-box bridge
beyond these restricted models.
