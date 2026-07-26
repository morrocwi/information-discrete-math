# Information Discrete Math

> ## There is no need to use continuum mathematics to solve mathematical problems in the modern world.

**A readout-first mathematical foundation — developed by Yaoharee Lahtee.**

The claim above is a claim about **computation**: every mathematical problem that has an answer is
answered by a **finite, discrete, rational** computation — no actual continuum (ℝ-completeness, `h→0`,
reached `+∞`) is ever needed as a primitive. This is demonstrated, not asserted: **1000/1000** problems
ประถม→PhD, **100/100** classically-continuous problems (integrals, derivatives, limits, ODEs, special
functions) reproduced from the discrete, **48/48 + 34/34** breadth (algebra→optimization), **21/21**
paradox-dissolution (topology · manifolds · PDE), and 16 axiom-free Coq witnesses for the operator keystone
`B(Φ,Φ)=I(Φ)`, the exact FTCC bridge, and the finite core theorems (`formal/`). *(Honest fence: this is
about computing the answers and dissolving the paradoxes — refusing to inject the non-readout — not about
deciding the classical completed-continuum questions in their own terms, which the framework declines to
form. See Parts XX–XXI.)*

Everything an agency ever reads is a **finite retained difference** — a *readout*, rational and
discrete. The continuum (ℝ-completeness, infinite divisibility `h→0`, actual `+∞`, a point of zero
size, a continuum angle in degrees) is a **non-readout**: real as a boundary, never as an
appearance. This repository packages that stance as an installable Claude Code skill that keeps
continuum concepts from being *silently injected* into your mathematics, physics, and geometry.

## What it gives you

- **The contaminated-concept → discrete-replacement table** — the exact substitution for each
  continuum concept that tends to sneak in: real numbers, limits, **angles/degrees** (the classic
  inverse-trig trap → Born-rule overlap fraction), points of zero size, zero, infinity, distance,
  continuity, π, derivatives, and operators.
- **A pre-write checklist** — five checks to run before committing any equation, proof, or number,
  so a real coordinate, a landing limit, or a singularity never slips through.
- **The machine-checked discrete number ladder** `D → ℤ → ℚ → ℝ` — the continuum built as a *readout*
  of the discrete root (Bishop regular Cauchy sequences of ℚ), ~123 axiom-free constructive theorems;
  discrete calculus (`Δ`, `Σ`, discrete FTC) with no reals.
- **Operator-first** — information is the central axis: the retained-information operator is the
  graph Laplacian `L_R`, whose Dirichlet energy *is* the retained-information functional; geometry
  and distance are readouts of it.


## The textbook

The full foundational treatise — **[textbook/INFORMATION_DISCRETE_MATHEMATICS.md](textbook/INFORMATION_DISCRETE_MATHEMATICS.md)** — carries the foundation from ONE primitive (the retained difference) up through logic (RDL), the number tower `D→ℤ→ℚ→ℝ` (the continuum as a readout of the discrete root), discrete analysis, geometry (distance as retained resistance; angle without trig; **π,φ,golden rotation as readout-invariants**), the retained-information operator, a **philosophy of mathematics** (what a number/unit/symbol/equation *is*), the **closure of the continuum** (discrete derivative/integral/limit/ODE/special-function), and dedicated chapters on **abstract algebra, linear algebra, complex analysis, and combinatorics/graph theory** — every axiom, definition, and major theorem tier-tagged, with machine-checked witnesses. See **[INDEX.md](INDEX.md)** for the full structure map.

## For AI agents — compute with it directly

- **[AI_COMPUTE.md](AI_COMPUTE.md)** — quick-start for an AI that must produce a math answer: the tool
  decision-table, the 6-step process, and copy-paste examples.
- **[METHOD.md](METHOD.md)** — tools (nouns) vs process (verb); the light+sharp solve loop.
- **[tools/idm_tools.py](tools/idm_tools.py)** — the tested tool library (`D_eps`, `I_eps`,
  `limit_eps`, `ode_rk4`, …); run `python3 tools/idm_tools.py` for the self-check.
- **Machine-checked:** 16 axiom-free Coq witnesses under `formal/` — `bash formal/verify.sh` compiles all + confirms *Closed under the global context* (keystone `B(Φ,Φ)=I(Φ)`, FTCC bridge, RDL non-explosion, finite theorems).
- **Validation:** `1000/1000` (grade-school→PhD), `100/100` (continuous problems reproduced from the
  discrete), `48/48` + `34/34` (algebra→optimization), `21/21` (paradox-dissolution) — under `validation/`.

## Install (via public git)

```
/plugin marketplace add https://github.com/morrocwi/information-discrete-math.git
/plugin install information-discrete-math@yaoharee-lahtee-math
```

To load it automatically every session, add a pointer to it in your `~/.claude/CLAUDE.md`, or invoke
it with `/information-discrete-math` before any mathematical work.

## The one commitment (a stance, tier `Dr`)

The discrete floor is machine-checked (nothing lies below the first tick; density/continuum is
provably absent at the root). A classical realist may keep the continuum as ontologically actual —
this is a discipline against *silent* injection, not a claim that classical mathematics is wrong.
The core ladder (D→ℤ→ℚ, paraconsistent logic) is axiom-free; continuum rungs needing `Coq.Reals` are
flagged `+ℝ-axioms`.

## License

MIT — see [LICENSE](LICENSE). Developed by Yaoharee Lahtee. AI-assisted; the core stance and results
are the author's.
