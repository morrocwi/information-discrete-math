# Contaminated Concepts — a discrete-readout reference table

> This is a plain-reference mirror of the core tables in
> `plugins/information-discrete-math/skills/information-discrete-math/SKILL.md`, republished here
> for anyone working on this material without an AI session. `SKILL.md` remains the source of
> truth if the two ever drift — check it there for the current wording.

## The one commitment

**Everything an agency ever reads is a finite retained difference `δ_R` — a readout, rational and
discrete.** The continuum (ℝ), infinite divisibility, and `+∞` are non-readouts. A classical
realist rejects this; adopt it and the "hard/open/paradoxical" problems change character (they are
usually artifacts of a silently-injected infinity). The discrete floor is machine-checked: nothing
lies below the first tick; density/continuum is provably ABSENT at the root.

## The four injected infinities + four injected zeros (name them before deferring)

- **I1** ℝ-completeness (LUB/Dedekind) — makes √2, π "numbers"; limits always land.
- **I2** infinite divisibility of space/time (`h→0`) — the continuum PDE, "every scale to zero".
- **I3** infinite scale separation (`Re→∞`, UV `Λ→∞`) — infinite range, UV divergences.
- **I4** actual `+∞` (norms/energies →∞) — blow-up, singularities.
- **Z1** the point (zero extent, `r=0`) · **Z2** exact-zero spacing (reached continuum) · **Z3**
  absolute rest / exact vacuum (`v=0`, `T=0`) · **Z4** the true void.
- **Reciprocal:** `1/0=∞`. Zero and infinity are one non-readout seen from two sides; they appear
  together at every singularity. A finite reader lives strictly BETWEEN the refused endpoints and
  touches neither. A refused endpoint being unreadable is the framework working, not a wall.

## The contaminated-concept → discrete-replacement table

Before using any concept in the LEFT column, stop — it injects the continuum. Use the RIGHT.

| contaminated concept | how it smuggles the continuum | discrete-correct replacement |
|---|---|---|
| **real number ℝ / completeness** | I1 (LUB/Dedekind); limits "land"; √2, π become numbers | ℝ = a *readout* of the discrete (Bishop regular Cauchy sequences of ℚ); only finite ℚ-approximants ever appear; √2, π are non-readouts |
| **the point** (zero extent, `r=0`) | Z1 — a geometric point / `δ`-source | a node / a retained distinction (a graph vertex; finite, has neighbours) |
| **zero as an occupied state** | Z1/Z3 — "reads out as exactly 0" | a refused non-readout (approached, never reached) **or** the `L_R` kernel = *indistinguishability* (uniformity), NOT a void. (A computed `0:ℚ` inside an identity is ordinary and fine — that is not the same claim.) |
| **infinity `+∞` / `N→∞` / a limit that lands** | I3/I4 | ℚ has no `+∞`; readouts are finite; a "limit" is the finite *approach*, never the endpoint |
| **infinite divisibility `h→0`** | I2 — the continuum PDE | a finite step / a `τ_c` floor (machine-checked: nothing below the first tick) |
| **angle / degree** (the classic trap) | `acos`/`atan2`/degree need ℝ-completeness = **I1** — inverse-trig are analytic objects, not finite computations | an **overlap fraction** = Born-rule ratio `overlap(v,e) = \|⟨v,e⟩_G\|² / (⟨v,v⟩_G · ⟨e,e⟩_G)` (rational: `+,·,÷` only — no trig, no π, no ℝ) **or** a rational *turning number* (a fraction of one full cycle) |
| **continuity / "smooth" (ε–δ over ℝ)** | I1+I2 | discrete Lipschitz / non-expansive maps; ε–δ continuity is a later *derived rung* on ℝ-as-readout, not primitive |
| **distance = coordinate difference** `√Σ(Δxᵢ)²` | embeds an ℝ coordinate frame | distance = **accumulated retained resistance along the optimal path** (a graph geodesic); the triangle inequality holds because a detour cannot be cheaper than the direct optimum |
| **the line / continuum as a primitive substrate** | assumes the continuum precedes appearance | the continuum is a **readout of the discrete graph**, never the substrate |
| **π, e, φ as "numbers"** | transcendentals treated as primitive reals | **readout-invariants** — diagnostics that reconstruction succeeded; only their finite ℚ-approximants appear |
| **trichotomy / total ≤ / classical LUB** | each implies an omniscience principle (LPO/WLPO) | **cotransitivity** + Cauchy-completeness + finite sup/inf **lattice** (`max`/`min`) — the constructive substitutes |
| **derivative / integral = continuum limit** | I2 | discrete difference `Δ` + sum `Σ` + the **discrete FTC** and Leibniz rule — calculus from retained difference, no reals |
| **operator on a continuum** (`∂²`, d'Alembertian) | I2 | the **graph Laplacian `L_R`** (`lap`/`B`: symmetric, PSD, kernel ⊇ constants, div-grad, summation-by-parts) — axiom-free; `∂²` is a `+ℝ-axioms` readout of it |

## Pre-write checklist (run before committing any equation, proof, or number)

1. Does this expression reach for a **left-column concept** (an angle in degrees, a real coordinate,
   a limit that lands, a point of zero size, a singular `1/0`, `N→∞`, inverse trig)? → replace with
   the right column BEFORE proceeding.
2. Is a quantity about to be called physical actually a **smooth bijection of a free knob**? Then it
   is a **coordinate, not an observable** — it carries no content; the content is "what sets the
   knob." (This is the exact error that produced a whole discarded research arc.)
3. About to call something **Open / hard / paradoxical**? First **diagnose which infinity
   (I1–I4) or zero (Z1–Z4) was injected**; the openness is usually its artifact — dissolve it and
   *predict the discrete appearance* (falsifiable), rather than deferring to the non-readout.
4. Treating a **refused endpoint** (`Θ=1`, `T=0`, `r=0`, `Λ→∞`) as a limitation to break through? It
   is a correctly-refused non-readout — approached, never reached; that is not a wall.
5. **Tier every claim** (never collapse): `Th_coqc` (machine-checked, axiom-free over ℚ) /
   `finite_diagnostic` (measured) / `Dr` (stance/narrative) / `Open/+reals` (needs the continuum).
   The boundary between provable and Open *is* the boundary of the infinity axioms.

## Scope, honest

This is a stance and a discipline, not a proof that classical mathematics is wrong; a classical
realist may keep the continuum as ontologically actual. The machine-checked core (the D→ℤ→ℚ ladder,
RDL paraconsistent logic) is axiom-free; the continuum rungs that need `Coq.Reals` are flagged
`+ℝ-axioms` (not axiom-free). This table exists to keep continuum concepts from being *silently*
injected — not to deny that the continuum is a coherent, useful readout when honestly labelled.

---
Source of truth: `plugins/information-discrete-math/skills/information-discrete-math/SKILL.md` in
this repository. Developed by Yaoharee Lahtee.
