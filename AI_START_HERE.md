# AI_START_HERE.md — read this before touching any single file

> [!WARNING]
> **Do not infer the capability of this repository from a single module.** This is a 266-kind
> unified solver with five distinct solving surfaces (below), a machine-checked Coq arc, and a
> benchmarked spectral product. Reading one file — one kind's implementation, one test, one demo
> — and generalizing from it will under- or over-claim what is here. Follow the discovery order
> below before writing any capability, coverage, correctness, or speed claim about this repo.

## What this project is

**Information Discrete Mathematics (`idm`)** — a readout-first computational mathematics library.
The stance: everything a program can return is a finite, discrete, rational **readout**; the
continuum (π, e, an integral, an eigenvalue, an ODE solution) is *reconstructed* from finite
operations, never assumed via a floating-point library call. Every result carries a **tier tag**
(`Th_coqc` / `exact` / `finite_diagnostic` / `Dr`) declaring how strong its warrant is, and
certified paths ship a proven error bound with an `ACCEPT`/`HOLD` verdict rather than a bare
number. See `README.md` for the full framing and `THEOREM.md` for the tier definitions.

## Discovery order — do these in sequence, don't skip ahead

1. **`capabilities.json`** (repo root, if present) — machine-readable capability manifest. If it
   is not present in your checkout, treat `idm.kinds()` (step 2) as the live source of truth
   instead — do not assume absence of the file means absence of capability.
2. **`python -c "import idm; print(len(idm.kinds()), idm.kinds())"`** — the live, authoritative
   list of registered solver kinds. At the time this doc was written this returned **266** kinds.
   Any count printed in prose (including in this file, `README.md`, or badge images) can drift;
   this command is the ground truth on your checkout, always re-run it rather than trusting text.
3. **`API_INDEX.md`** (this directory) — searchable table: capability → Python API → tier →
   verification file. Also read the existing `API.md` (library usage patterns) and `INDEX.md`
   (repo map).
4. **`pytest -q`** — the full test suite, including the differential harness (`tests/harness.py`,
   checks `idm.solve` against an independent oracle — sympy/mpmath — for kinds that have one) and
   the adversarial harness (hostile/malformed input into every registered kind; requires the
   result never silently claims a stronger tier than it earned).
5. **`python prove_it_full.py`** — recomputes ~1278 continuum-frontier problems (physics,
   biochem, networks, number theory, cosmology) as finite-discrete readouts against an independent
   `mpmath` reference, printed live on your machine.
6. **`BENCHMARK_CLAIMS.md`** (repo root, if present) — read this **before repeating any
   performance/speed number** from this repo. If it is not present in your checkout, do not
   assert a speed claim beyond what you can reproduce yourself from `retained_spectral/competition/`
   and `retained_spectral/reproduce.ipynb` (see README's "Featured math product" section) —
   correctness claims never depend on this file, but a speed number without it is unverified.

## The primary API — `idm.solve` / `idm.kinds`

```python
import idm
idm.kinds()                          # -> list of 266 registered kind names
idm.solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
# -> {"kind": "integral", "status": "CERTIFIED", "tier": "finite_diagnostic",
#     "value": {...}, "bound": {...}, "method": "..."}
```

`idm.solve(problem)` takes a **structured** dict — the caller declares `kind` first (translate the
world-language question into an information-language declaration, then solve; see
`METHOD.md`) — and dispatches through the registry in `idm/solve.py` (`@kind(name, tier)` /
`_REG[name] = (fn, tier)`). One entry point, 266 kinds, tier-tagged results. `idm.kinds()` returns
the live registry keys — confirmed by reading `idm/solve.py` and importing the package.

**Note on tiers:** the tier string a kind's `@kind(...)` decorator declares in the source is not
always the tier the call actually returns — `idm/solve.py`'s `solve()` runs a tier-honesty pass
that downgrades a declared `Th_coqc` to `exact` unless that specific kind has a named Coq theorem
behind it (see `API_INDEX.md` for the exact list and worked examples). Always read the returned
`"tier"` field, not the decorator, when making a tier claim about a specific kind.

## The five solver surfaces

Every one of these is real, importable code in this checkout — verified while writing this file.

| # | Surface | Entry point | What it's for |
|---|---|---|---|
| 1 | **Unified solver** | `idm.solve(problem)` / `idm.kinds()` (`idm/solve.py`) | One dispatcher over all 266 kinds, tier-tagged results |
| 2 | **Exact CAS** | `idm.kernel.poly` (`idm/kernel/poly/`) — `linsolve`, `groebner`, `limits`, `ode_linear`, `factorize`, `eigen`, `subresultant`, ... | Domain-parametrized exact ℚ[x]/ℤ[x]/GF(p)[x] polynomial algebra — no floating point |
| 3 | **Retained Spectral** | `retained_spectral/` — `engine.native_eigvals_from_tridiagonal`, `retained_mode.modes`, `inertia.count_below_banded` / `resolved_count_below` | Schrödinger-spectrum / tridiagonal-eigenvalue solver, benchmarked product (see README "Featured math product") |
| 4 | **`idm.certified`** | `idm.certified.integral`, `idm.certified.integral_nd`, `idm.certified.geom_series`, `idm.certified.exp`, ... (`idm/certified.py`) | Certified computation: value + proven bound + `ACCEPT`/`HOLD`. Note `integral`/`integral_nd` are actually `Th_coqc`-tier (Coq-backed, see `THEOREM.md` §7), not a lower tier — check `API_INDEX.md` per-API rather than assuming |
| 5 | **Formal proofs** | `formal/verify.sh`, `formal/*.v` | Coq 8.20 arc backing the `Th_coqc` tier — compiles every listed theorem and checks `Print Assumptions` reports "Closed under the global context" (axiom-free over ℚ) |

## How to VERIFY correctness

```bash
pytest -q                 # full suite: unit + differential (oracle-checked) + adversarial harness
python prove_it_full.py   # ~1278 continuum-frontier problems vs independent mpmath reference
bash formal/verify.sh     # compiles + axiom-checks the Coq arc backing Th_coqc results
```

`bash formal/verify.sh` lists its own theorem set (`THMS=(...)` in the script) — read the script
to get the exact, current count on your checkout rather than trusting a badge or prose number;
badges in `README.md` can lag the script (at the time this doc was written the script's own array
had more entries than the README badge stated — always trust the script over the badge).

## How to VERIFY speed (never assume it from prose)

The only benchmarked speed claims live in the **Retained Spectral** product
(`retained_spectral/competition/`) and are reproducible via
`retained_spectral/reproduce.ipynb` (also runnable on Google Colab from a clean machine — see the
link in `README.md`'s "Featured math product" section). Before repeating any speed number:

1. Read `BENCHMARK_CLAIMS.md` if it exists in your checkout.
2. Otherwise, re-run the benchmark yourself from `retained_spectral/competition/` and cite your
   own run's JSON output — do not restate a number from prose you have not reproduced.
3. Note the stated caveat in `README.md`: the headline speed numbers require Numba (JIT-compiled
   native kernel); without it the run falls back to a much slower pure-Python path and
   `run_competition` fails closed (`HOLD`) rather than silently reporting the slow numbers as the
   headline. Correctness never depends on Numba — only the wall-clock claim does.

## Root docs map (read these, don't duplicate them)

- `README.md` — framing, the Retained Spectral benchmark headline, reproduction instructions
- `API.md` — library usage patterns and `idm.solve` kind groups
- `INDEX.md` — repo map
- `THEOREM.md` — the tier system (`Th_coqc` / `exact` / `finite_diagnostic` / `Dr`) defined precisely
- `METHOD.md` — the translate-first discipline behind structured `solve(problem)` calls
- `API_INDEX.md` (this directory) — the searchable capability table this doc points to next
