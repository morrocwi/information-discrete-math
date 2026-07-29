# idm/ — the library facade

**What this folder does.** `idm/` is the installable package (`import idm`). It is a thin, tested
facade over the repository's verified modules: one unified dispatcher (`solve.py`, the `@kind(name,
tier)` registry with 267 registered kinds), a natural-language front end (`parse.py`), a certified-
readout re-export (`certified.py`), the finite elementary/calculus surface (`functions.py`), and
domain modules — `algebra`, `analysis`, `combopt`, `crypto`, `diffeq`, `discrete`, `exact`, `geometry`,
`hilbert` / `hilbert_open`, `integrate`, `interval`, `optimize`, `positivity`, `readouts`, `rcp`,
`series`, `special`, `stats`, `symbolic`, `transforms`, plus the zero-dependency REST layer
(`server.py`) and the exact-ℚ polynomial tower (`kernel/`, see `idm/kernel/poly/`).

**The PUBLIC API.**
- `import idm` then `idm.solve(problem_dict)` — the single dispatch entry point; `idm.kinds()` lists
  all registered kind names.
- `idm.parse(text)` / `idm.parse_and_solve(text)` — plain-language → structured problem → solve, or
  `HOLD` if the request isn't recognized.
- `idm.certified.*` (`geom_series`, `exp`, `simpson`, `richardson`, `integral`, `integral_nd`, …) —
  `Readout(value, bound, status, reason)` with `CERTIFIED`/`HOLD`.
- `idm.continuum.Continuum` — the continuum as a first-class **ℚ primitive** (a resolution-indexed exact-ℚ
  readout, never an ℝ object): `.at(N)` exact ℚ at resolution N; `.readout(ε)` returns `CERTIFIED` only on
  a **proven** tail bound (else an observed plateau is `finite_diagnostic`, or `HOLD` — never a fabricated
  limit); a ℚ-algebra (`+ - *`, scalar,
  `compose`) closed and exact pointwise. Canonical builders `geometric(r)`, `from_sequence(seq)`. Its
  algebra laws are machine-checked axiom-free over ℚ in `formal/IDM_Continuum.v`.
- The top-level convenience re-exports in `idm/__init__.py`: `pi`, `e`, `ln2`, `derivative`,
  `integral`, `limit`, `ode`, `evaluate`, `shortest_path`, `critical_path`, `widest_path`,
  `minimax_path`, `reachability`, `path_count`, `dashboard`.
- `idm.serve(host, port)` / `python3 -m idm.server` — the REST + OpenAPI 3 service
  (`POST /solve`, `GET /health`, Swagger UI at `/docs`).
- `from idm.kernel import poly` — the exact rational polynomial tower (see `idm/kernel/`, no
  top-level README of its own; treat `idm.kernel.poly.__init__.py`'s `__all__` as its contract).

**What NOT to import directly.** Do not import `idm/_bridge.py` or reach into `idm/solve.py`'s
private helpers (anything prefixed `_`, e.g. `_ok`, `_readout`, `_fn`) — they are registry wiring,
not a stable surface. Prefer `idm.solve({"kind": ...})` over calling a domain module's internal
handler function directly; the registry is what attaches the tier tag and the `CERTIFIED`/`ok`/`HOLD`
verdict. `idm.certified` is itself a re-export of `tools/certified_readout.py` — import from
`idm.certified`, not from the vendored `certified_readout` module, unless you are working inside
`tools/`.

**How to test it.** `pytest -q tests/test_idm_api.py tests/test_smoke.py` for the dispatch surface;
the full suite (`pytest -q`) also exercises `idm.kernel.poly` via `tests/test_kernel_*.py` and runs
the differential + adversarial harness (`tests/harness.py`) against every registered kind.

**Limits.** The registry currently reports 267 registered kinds, but only a named subset carries a
`Th_coqc` (`coq_theorem`) tag pointing into `formal/` — most exact handlers are `exact` (finite ℤ/ℚ
computation, no per-implementation Coq proof) or `finite_diagnostic` (declared-tolerance agreement).
Read the returned `status`/tier on every call rather than assuming machine-checked correctness; a
`HOLD` is a refusal, not a bug. The natural-language front end (`parse`) is a translation layer, not
a general NLP system — unrecognized phrasing returns `HOLD` rather than guessing a kind.
