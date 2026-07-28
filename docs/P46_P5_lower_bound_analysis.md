# P5 as a readout question — does a boundary readout pay for volume? (`+ℝ-Open`)

**Status: `+ℝ-Open`. Stated in this framework's own semantics.** No Coq theorem is attached to P5; this is
a research memo, not a formal artifact. Nothing here is claimed proved or refuted. This memo is written
**entirely in the readout-first (information-discrete) language** — the framework's solve-law is to
translate a problem into these semantics first, then reason with the mathematics locked to them. Where the
external record uses a different name for one of our objects, that correspondence is stated once and kept
external; it is never the floor.

## 1. The object, translated

P5 (external form) asks: must computing the inertia `In(A)` of a sparse symmetric object cost as much as
its full symmetric factorization?

In this framework's vocabulary:

- A full factorization retains a **volume** — every `L` entry it creates is a retained distinction the
  elimination holds. *(The external record calls this volume the `fill`; we read it as volume.)*
- The inertia `In(A) = (n₊, n₀, n₋)` is a **boundary readout**. It is the complete congruence invariant
  (Sylvester — everything else in `A` is representation-dependent, an artefact of how it was written), and
  by **Haynsworth additivity** it is additive across a separator of the graph of `L_R`, so *the object it
  retains is the **boundary**, not the volume* (THEOREM.md, §"inertia is the spectral readout").

So P5, translated: **does the boundary readout require producing the volume?**

## 2. The framework's stance (the READOUT rule)

The READOUT rule is *"do not construct an object the readout does not require."* §A already names the fill
a poor elimination order creates as *"volume the readout never asked for."* So the framework's stance is
that inertia owes only the **boundary** (`Ω(separator)`), never the volume. Posing P5 as a volume cost
measures a boundary readout against an invariant it is not bound to. The framework therefore **predicts
against** the volume framing — a hedged stance, not a proof.

## 3. Two readings that survive in our vocabulary

- **A definiteness certificate is a cheap boundary readout.** When the retained differences all agree in
  sign at the diagonal (a positive-diagonal, diagonally-dominant object — every retained row-difference is
  dominated by its own diagonal), the inertia is `(n, 0, 0)`, read off in one pass over the retained
  entries — no elimination, no volume. Such an object exists over *every* boundary graph. So the **hard**
  inertia readouts live only in **indefinite** objects near a degenerate spectrum, where the sign-count is
  not read off a definiteness certificate. Not every object's inertia is a hard readout — the worst-case
  reading is what P5 must be about (its universal-over-all-objects form does not survive this).
- **Sign-of-determinant is a coarser readout of the same retained object.** By Sylvester,
  `sign(det A) = (−1)^{n₋}` — a one-bit coarsening of the inertia triple. A lower bound on the coarser
  reading transfers to the finer one; the converse is not claimed.

## 4. The locked question (info-P5) and the locked tool

The right question is not the volume but: **how much of the boundary must be RETAINED to decide the
sign-count?** The tool locked to that question is the **Declaration Bound** (`formal/IDM_DeclarationBound.v`,
machine-checked): a *declared* reading (the shift `σ` fixed before the object is read) retains `Θ(1)`; a
*deferred* reading (`σ` revealed after the object is read) retains `Θ(boundary)`.

**info-P5:** *a deferred inertia reading of an object whose separator has width `w` must retain `Ω(w)`* —
the Declaration Bound on the **separator**, not the whole object. Whether this composes across the
separator tree of `L_R` to a total matching the boundary-recursion cost is `[Open]`.

The restricted attempt recorded earlier used a tridiagonal ladder, whose separators have width `1`; its
`Ω(n)` retention is not boundary-relevant, because the boundary sum there is already `O(n)`. The
boundary-relevant family has **wide separators** — a 2-D grid of `L_R`, separator width `Θ(√n)` — where the
deferred boundary-retention is `Ω(√n)` per cut. That is the regime the volume framing obscured and the
ladder missed.

## 5. Honest position

- The honest lower bound on inertia in this framework is **boundary-retention** (`Ω(max separator width)`),
  in the shape of the Declaration Bound on the separator.
- The honest cost of computing it is the **boundary-recursion** (`Σ` separator inertias, Haynsworth) — a
  boundary quantity, generally smaller than the volume.
- **info-P5 is `[Open]`**, stated in the boundary-retention invariant the framework is actually bound to —
  not the borrowed volume invariant.

## 6. The Coq targets this reading names (future — not done here, none formalized)

1. **Discrete Haynsworth inertia-additivity over `ℚ`** — `In(A) = In(A₁₁) + In(A / A₁₁)` for symmetric `A`
   with invertible `A₁₁`, axiom-free. Currently cited classical, not in `formal/`. Machine-checking it
   **locks the "inertia is a boundary readout" claim** the whole reading rests on — a genuinely new
   theorem, not a relabeling of an existing one.
2. **The wide-separator deferred bound** — the Declaration-Bound pigeonhole on a `w`-wide separator's
   count-below profile, on a family with `w = Θ(√n)`.

Both are honest partial results toward info-P5, which remains `+ℝ-Open`. Nothing above is a theorem; no
conjecture is dressed as a result.
