# P46 / P5 — the inertia lower-bound moonshot: honest analysis (Open)

**Status: `+R-Open`. Nothing in this memo proves or refutes P5. No Coq theorem is attached to P5
itself — this is a research memo, not a formal artifact.** Tier discipline: any claim below labelled
"solid" is a classical/elementary fact restated in this repo's own vocabulary, not a new theorem; any
claim labelled "conjectural" or "stuck" is exactly that, fenced, and left `[Open]`.

## 1. Precise statement of P5

Fix a symmetric sparse matrix `A ∈ ℝ^{n×n}` given by its nonzero pattern (a graph `G(A)` on `n`
vertices) and, for a numerical instance, its entries. `In(A) = (n₊, n₀, n₋)` is Sylvester's inertia
(the sign-count of eigenvalues, equivalently — when `A` is nonsingular — the sign-count of pivots of
*any* `LDLᵀ` factorization along *any* elimination order, by Sylvester's law of inertia, a classical
fact cited not re-derived here).

For an elimination order `π` on the vertices of `G(A)`, let `fill(A, π)` be the number of fill edges
produced by symmetric Gaussian elimination in that order (the standard graph-elimination fill count:
an edge `{i,j}` is created whenever both are still-unfactored neighbours of some already-eliminated
vertex `k`, and it was not already present). Let

  `fill*(A) = min_π fill(A, π)`

be the fill under the **best** ordering (the quantity nested-dissection / minimum-degree heuristics
try to approximate; computing `fill*` exactly is itself NP-hard in general, a separate classical fact
not needed below beyond noting it).

**P5 (the conjecture, restated precisely).** *Every arithmetic algorithm that computes `In(A)` for
sparse symmetric `A`, on every instance with elimination graph `G(A)`, must perform*
`Ω(fill*(A))` *arithmetic operations (additions/multiplications/comparisons over the reals or over a
field containing the entries), i.e. reading off the three inertia counts is, up to polylog factors, as
hard as computing a full symmetric factorization along the best possible ordering — no algorithm can
get the sign-counts "for free" relative to what elimination-based factorization already costs.*

Equivalently: sign-counting (`In(A)`) and full symmetric elimination (`LDLᵀ` along the best order) are
conjectured to be **arithmetic-complexity equivalent up to polylog(`n`)**. The conjecture is a
**lower bound** claim; the matching **upper bound** `In(A)` computable in `O(fill*(A))` (up to the cost
of finding a good order) is not conjectural — it is exactly what `LDLᵀ`-along-a-good-order already
delivers (§2 of `THEOREM.md`, "the readout rule in practice: inertia is the spectral readout";
`retained_spectral/inertia.py`). So P5 is entirely about whether that upper bound can be *beaten* by
some other algorithm that reads off only the sign-counts without paying for the fill.

This repo's own numbering: `feat/kernel-p5-solutions` and the shipped `feat/p4-resolved-inertia` work
(the `resolved_count_below` / `ResolvedInertia` machinery, `formal/IDM_ResolvedCount.v`) established
the *reading discipline* for the inertia readout (certain `+`/`−` vs instrument-`⊥`) but did not touch
— and does not bear on — the arithmetic-complexity question P5 asks. P5 is a genuinely separate,
harder question: not "how do we read inertia honestly" but "how cheap can reading inertia *ever* be."

## 2. The most promising attack, and exactly where it gets stuck

### 2a. The reduction-from-sign-of-determinant route

**The direction that DOES provably hold (solid, classical, restated here — not reproved).** When `A`
is nonsingular, Sylvester's law gives `n₀ = 0` and

  `sign(det A) = (−1)^{n₋}`

directly from the inertia counts (the determinant is the product of the eigenvalues, and pairing each
negative eigenvalue contributes one sign flip). So **any algorithm that computes `In(A)` also computes
`sign(det A)`** — this is a genuine, checkable reduction: `SIGN-DET ≤ INERTIA` in arithmetic-circuit
cost, with zero overhead beyond a parity check on `n₋`. This is the natural entry point for an
adversary argument: if one could show `SIGN-DET` requires `Ω(fill*(A))` arithmetic operations on
sparse symmetric `A`, P5 for the *sign-of-determinant fragment* would follow immediately, and then one
would still need a separate argument that the full three-way inertia count is no easier than
sign-of-determinant alone (plausible, since `n₋` fixes the parity but not the full triple, so this
second step is itself an unclosed gap, not just the first).

### 2b. The elimination-tree adversary — where the fill lower bound itself comes from, and why it does not transfer

The natural adversary move is to build a **family of sparse patterns** `{G_n}` for which `fill*(G_n)`
is provably large for *every* ordering — this half is genuinely available off the shelf, classically:
separator-based lower bounds (Lipton–Tarjan-style: a graph family whose *every* balanced separator has
size `Ω(s(n))` forces `fill*(G_n) = Ω(n · s(n)/n)`-type bounds via the standard elimination-tree /
nested-dissection argument; e.g. 2-D/3-D grid or expander-based families give `fill* = Ω(n log n)` or
`Ω(n^{4/3})` type separations, classical results cited, not re-derived here). **This gives a solid
`Ω(fill*)` combinatorial floor on the fill itself** — i.e., no ordering avoids a lot of fill on these
families. That is a statement purely about the graph `G(A)` and elimination orderings; it says nothing
yet about arithmetic-circuit complexity of an arbitrary algorithm.

**This is exactly where the attack gets stuck.** The gap between (i) "every elimination order on this
graph produces a lot of fill" and (ii) "every *arithmetic algorithm whatsoever* that outputs `In(A)`
on instances with this graph must perform a lot of arithmetic" is a gap between **combinatorial
graph-elimination lower bounds** (well understood) and **general arithmetic-circuit lower bounds**
(not well understood, for essentially any problem at this level of generality). Three concrete
obstructions surface immediately when trying to close it:

1. **Non-elimination algorithms are not ruled out.** The adversary bounds `fill(A, π)` over
   elimination orders `π`, but P5 quantifies over *all* arithmetic algorithms — including ones that
   never form an explicit `LDLᵀ` factorization at all (e.g. iterative eigenvalue-counting via
   Sturm sequences on a *different* basis, randomized trace-estimation of a spectral projector,
   polynomial-evaluation tricks on `det(A − σI)` at multiple `σ`, or algebraic short-cuts specific to
   a structured sub-family). Nothing in the separator argument forecloses such an algorithm being
   cheaper than `fill*` on the hard family — the adversary lives in the wrong category (graphs +
   orderings) to constrain it.

2. **Early termination is not accounted for.** `In(A)` is a triple of *counts*, not the full
   factorization; an algorithm is free to stop as soon as it has enough information to certify the
   three counts, without ever materializing every fill entry. The Declaration-Bound-style argument
   this repo already has machine-checked (`formal/IDM_DeclarationBound.v`, DB1–DB6: `Θ(1)` registers
   suffice for a **declared** threshold query vs `Θ(n log q)` bits for a **deferred** one) is the right
   *shape* of argument — a pigeonhole/pumping obstruction on how much can be forgotten — but it is
   built for a fooling-family over *bit strings streamed past a threshold query*, not for *arithmetic
   circuits computing a sign-count from a sparse symmetric input matrix*. Porting the pigeonhole
   argument requires a fooling family of matrices, all sharing the same sparsity pattern (so an
   algorithm cannot use the pattern alone to shortcut), whose inertia triples are pairwise distinguished
   only by information an `o(fill*)`-size computation provably cannot retain — and no such family, nor
   the counting argument that would certify it, has been constructed here.

3. **The general lower-bound toolbox does not reach this far.** Unconditional arithmetic-circuit lower
   bounds beyond linear/near-linear size are not known for essentially any explicit problem at this
   level of structure (this is a standing difficulty of algebraic complexity theory generally, not a
   gap specific to this attempt). An `Ω(fill*(A))` circuit lower bound for `In(A)` — a *superlinear*,
   instance-dependent bound tied to a graph-theoretic quantity — sits well beyond what the standard
   toolbox (degree arguments, partial derivatives / Nisan–Wigderson-style rank methods, elimination
   arguments for restricted models like read-once formulas) currently certifies for unrestricted
   arithmetic circuits. Stating this is a self-assessment of where the in-house attempt stalls, not an
   appeal to outside authority: the obstruction is that the *technique itself* (adversary over
   elimination trees) does not currently reach general algorithms, independent of who is asked.

**Conclusion of §2:** the reduction `SIGN-DET ≤ INERTIA` is solid and free. The fill-in floor
`fill*(G_n) = Ω(...)` on hard graph families is solid and classical. Neither, nor their composition,
currently closes P5, because the missing step — general arithmetic algorithms cannot beat the
elimination-tree floor — is not established by the separator/adversary technique and is not obviously
reachable by it. **P5 remains `[Open]`.**

## 3. What IS solid (recorded, not conjectural)

These are genuinely-true observations, none of which is P5 and none of which is claimed as a new
theorem beyond restating classical facts in this repo's terms:

- **(a) Trivial input-reading lower bound.** Any algorithm computing `In(A)` correctly on every
  instance sharing a pattern must read every explicit nonzero at least once in the worst case (an
  adversary can perturb any unread entry to flip a sign near a degenerate spectrum), giving
  `Ω(nnz(A))` arithmetic/read operations. This is strictly weaker than `Ω(fill*(A))` (always
  `fill*(A) ≥ nnz(A)` for the best order, since the original entries are never removed by elimination),
  so it is a correct but non-tight floor — it does not touch the conjecture's real content, which is
  about the *fill*, not the original nonzeros.
- **(b) The reduction `SIGN-DET ≤ INERTIA` (§2a)** — free, exact, checkable by Sylvester's law; the
  hard direction of P5 would follow from a fill-tight lower bound for `SIGN-DET` alone, which is itself
  unresolved and not claimed here.
- **(c) The matching upper bound is not conjectural.** `In(A)` computable in `O(fill(A, π))` for any
  chosen order `π` (one banded/sparse `LDLᵀ` pass, Sylvester's law) is classical and already the shipped
  behaviour of `retained_spectral/inertia.py` / `count_below_banded`; so the *only* open direction in
  P5 is the lower bound, not the upper bound. This narrows what future work needs to target.
- **(d) The Declaration Bound's pigeonhole shape (`formal/IDM_DeclarationBound.v`) is the closest
  machine-checked technique this repo has to the right proof *shape*** for a P5-style separation
  (declared-vs-deferred retained information), but it is proved for a bit-streaming threshold-query
  model, not for arithmetic circuits over sparse symmetric matrices, and porting it is an open
  construction problem (§2, obstruction 2), not a completed reduction.

## 4. Fence

**P5 is `[Open]` / `+R-Open`.** Nothing above is a proof or a refutation. No Coq file accompanies this
memo: no sub-lemma was found in the course of this analysis that is (i) genuinely true, (ii) strictly
weaker than P5, and (iii) a finite/combinatorial statement of the kind this repo's `formal/*.v` line
can capture axiom-free without re-deriving the classical spectral facts (Sylvester's law, the
separator-based fill lower bounds) that the argument leans on. The trivial `Ω(nnz(A))` bound in §3(a)
is true but adds nothing over what is already implicit in reading the input, so it was judged not worth
a standalone `.v` file. Should a genuine fooling-family construction for obstruction 2 in §2 ever be
found — a finite family of same-pattern matrices whose inertia triples require retaining
`ω(o(fill*))` bits to distinguish, in the discrete/combinatorial shape `IDM_DeclarationBound.v` already
handles — that would be the natural next machine-checked increment, and it would still only be a
**partial** result (a pigeonhole floor on *one* obstruction, not a full arithmetic-circuit lower bound),
not a proof of P5.


---

## 5. Update — multi-angle attack (adversarially verified). P5 still `[Open]`.

A four-angle attack (restricted lower bound · reductions · refutation · barrier), each candidate then
adversarially re-checked by an independent skeptic. **P5 was not closed** — the expected outcome for a
problem the brief itself rates hardest. What the attack *did* produce is a sharper, verified map, and one
genuine clarification of what P5 can even mean. Nothing below is formalized as a theorem; P5 stays Open.

### 5.1 The **universal** reading of P5 is false — so P5 must be the **existential** statement (the sharpening)
Consider the promise class `D(G)`: symmetric `A` with pattern `G`, `A_ii > 0`, strictly diagonally
dominant (`A_ii > Σ_{j≠i}|A_ij|`). By Gershgorin every eigenvalue is strictly positive, so
`In(A) = (n, 0, 0)` is read off in **`O(nnz(A))`** arithmetic (one pass summing `|A_ij|` per row, compare
to `A_ii`) — no elimination, no fill. A diagonally-dominant instance exists for **every** sparsity pattern
(e.g. `A_ii = deg(i)+1`, off-diagonals `−1`), including 2-D grid families with `fill*(G_n) = Ω(n log n)`
while `nnz = Θ(n)`. So on `D(G_n)` inertia costs `O(n) = o(fill*)`, and `fill*/nnz → ∞`.

Consequence: the **universal** reading — *"every* sparse symmetric `A` needs `Ω(fill*(A))`" — is
**refuted** (diagonally-dominant instances are an easy corner). P5 is only defensible as the
**existential / worst-case-instance** statement: *there is a family of sparse symmetric matrices with
`fill* = ω(nnz)` on which computing inertia needs `Ω(fill*)` arithmetic.* The hard content lives in
**indefinite** matrices near a degenerate spectrum, where the sign-count is not read off a definiteness
certificate. This is a real clarification of the conjecture, not progress on proving it. *(Verified: the
Gershgorin argument is mathematically correct; it does **not** refute the existential P5 — flagged
honestly as a sharpening, not a refutation.)*

### 5.2 Reductions — one solid, one false friend, one content-free (verified)
- **`SIGN-DET ≤ INERTIA`** (Sylvester, `O(1)` overhead) is the one unconditionally solid reduction: a
  lower bound on the sign-of-determinant transfers to inertia. Its converse is not claimed. A
  SIGN-DET lower bound is not itself established here or in the cited literature, so this yields no
  unconditional inertia bound.
- **Communication-complexity route — a false friend.** Unbounded-error 2-party communication complexity
  `= ⌈log₂ rank_±⌉` (Paturi–Simon) bounds the cost of a *Boolean matrix's sign pattern*, **not** the
  arithmetic-circuit cost of the inertia of a *numeric sparse matrix*. Circuit→protocol simulations exist
  only for *restricted* models (branching programs, streaming, cell-probe), which is exactly the barrier;
  there is no such simulation for **unrestricted** arithmetic circuits.
- The "transfer lemma" `cost(SIGN-DET) ≤ cost(INERTIA)+c ⇒ (SIGN-DET ≥ L ⇒ INERTIA ≥ L−c)` is a one-line
  arithmetic consequence of the above — **content-free** (subtraction on naturals), not worth a witness.

### 5.3 The Declaration-Bound pigeonhole instantiates to a one-pass inertia bit-bound — a corollary, not a new bound
The `formal/IDM_DeclarationBound.v` / `formal/IDM_ApproxCount.v` pigeonhole relabels cleanly to a
one-pass, deferred-threshold *inertia-count-below reader* on a diagonal-perturbation tridiagonal ladder,
giving `Ω(n)` **retained bits**. It is genuinely true and axiom-free — but the independent check found it
is **not a new lower bound**: it is the existing Declaration Bound with a spectral relabeling, and it does
**not** bear on P5, for four load-bearing reasons: (i) a single tridiagonal family, not all patterns;
(ii) a bounded one-pass-compress-then-decode model, not arbitrary arithmetic algorithms; (iii) **bits of
state**, an incommensurable cost model with **arithmetic operations** — no reduction between them is given;
(iv) tridiagonal matrices have **small** `fill* = O(n)`, so this family is deliberately *not* an
`Ω(fill*)` separation candidate. It is therefore left as a documented corollary, **not** added as a
standalone "inertia lower bound" witness (that would overclaim novelty).

### 5.4 The single hardest missing step (barrier)
The classical `fill*` lower bound is a **combinatorial floor on the elimination graph** — it counts what a
*factorization* (all `L` entries) must produce. Inertia needs only the **signs** of the pivots, not their
values; nothing in the fill argument references what an algorithm must *retain* to determine the three
signed counts `(n₊, n₀, n₋)`. A full existential-P5 proof needs an argument bounding the *information
content of a single arithmetic gate relative to a fooling family of indefinite matrices* — connecting the
bit-streaming separation (`IDM_DeclarationBound` DB4: deferred needs `Θ(n)`, declared needs `Θ(1)`) to an
**unrestricted arithmetic-circuit** cost. No current technique supplies that circuit↔information bridge;
naming that missing bridge precisely is the deliverable of this round, and it remains **`[Open]`**.

### 5.5 Verdict
P5 (existential form) is **`[Open]`** — neither proved nor refuted. Delivered, all honest: a proof that
the *universal* form is false (§5.1), a verified reduction map with one false friend named (§5.2), an
explicit note that the pigeonhole bit-bound is a Declaration-Bound corollary and not P5-relevant (§5.3),
and the single hardest missing step pinned down (§5.4). **No theorem was formalized; no conjecture was
dressed as a result.**

---

## 6. P5 in the **information language** — re-read under the locked semantics (the right frame)

§1–§5 attacked P5 in *classical* complexity vocabulary (fill, arithmetic circuits, communication
complexity). That is a borrowed frame. This project's own solve-law is: **translate the problem into our
readout-first semantics first, then use the mathematics locked to those semantics** — not general
complexity theory relabeled. Doing that changes what P5 even asks.

### 6.1 The translation
| classical | information-discrete reading |
|---|---|
| `fill` (the `L` entries an `LDLᵀ` factorization creates) | the **VOLUME** of retained state a full factorization produces — every `L` entry is a retained distinction the process holds |
| `In(A)` (inertia / sign-count) | a **BOUNDARY readout**: Sylvester makes it the complete congruence invariant, and **Haynsworth additivity** makes it *additive across a separator* — "the object that must be retained is the **boundary, not the volume**" (THEOREM.md, §"inertia is the spectral readout") |
| **P5:** does `In(A)` require `Ω(fill*)`? | **does a BOUNDARY readout require producing the VOLUME?** |

### 6.2 What the locked semantics predict
The READOUT rule is literally *"do not construct an object the readout does not require,"* and §A already
names fill as *"volume the readout never asked for."* So the framework **predicts P5 (`Ω(fill*)`) is the
wrong invariant**: inertia is a boundary readout and should owe only the **boundary**, i.e. `Ω(separator
cost)`, not the volume `fill*`. Haynsworth boundary-recursion computes inertia paying only the separator
inertias; for good separators that total is generally **`< fill*`** — consistent with §5.1's finding that
diagonally-dominant instances read inertia in `O(nnz) = o(fill*)`. `fill*` is a *volume* cost imposed from
outside; it is not the invariant a boundary readout is bound to.

### 6.3 The re-framed statement (info-P5) and the right tool
The right question is not "`Ω(fill*)`" but **"how much BOUNDARY must be RETAINED to decide the sign-count?"**
The locked tool is the **Declaration Bound** (`formal/IDM_DeclarationBound.v`): a *declared* query (the
shift `σ` known before the object is read) needs `Θ(1)` retained state; a *deferred* query (`σ` revealed
after) needs `Θ(boundary)`. So info-P5 reads: **a deferred inertia reading must retain `Ω(separator width)`
information.**

### 6.4 Why §5's own restricted bound (angle A) was the wrong family
The §5.3 one-pass `Ω(n)`-bit bound used a **tridiagonal ladder**, whose separator between consecutive
blocks has width **`O(1)`**. Its total retention `Ω(n)` is not fill-relevant precisely because tridiagonal
`fill* = O(n)` already equals the (unit) boundary sum. The information lens says the correct family is one
with **wide separators** — e.g. a 2-D grid, separator width `Θ(√n)` — where the deferred boundary-retention
is `Ω(√n)` *per cut*. That is the fill-relevant regime the classical framing obscured and the ladder missed.

### 6.5 Consequence — a sharper, honest position
- The honest lower bound on inertia in this framework is **boundary-retention** (`Ω(max separator width)`),
  provable in the shape of the Declaration Bound on the separator — **not** `Ω(fill*)`.
- The honest *upper* bound is the **boundary-recursion** cost (`Σ` separator inertias), generally `< fill*`.
- Therefore, in the locked semantics, **P5 as `Ω(fill*)` is very likely false as stated**; the defensible
  statement is *"inertia costs `Ω(max-separator)` and `O(boundary-recursion)`,"* both **boundary** quantities.

### 6.6 The genuinely new Coq targets this lens reveals (future, NOT rushed)
1. **Formalize discrete inertia-additivity (Haynsworth)** — `In(A) = In(A₁₁) + In(A/A₁₁)` for a symmetric
   `A` with invertible `A₁₁`, over `ℚ`, axiom-free. This is currently cited as classical, *not* in
   `formal/` — machine-checking it would **lock the "inertia is a boundary readout" claim** the whole
   translation rests on. This is a real new theorem, not a relabeling.
2. **The wide-separator deferred bound** — the Declaration-Bound pigeonhole on a `w`-wide separator's
   count-below profile, giving `Ω(w)` retained bits, on a family where `w = Θ(√n)` (fill-relevant, unlike
   the ladder).

Both are honest partial results toward **info-P5**, which remains **`[Open]`** — but now stated in the
invariant (boundary retention) the framework is actually locked to, rather than the borrowed `fill*`.
