# Quick Start — `idm` in 10 minutes

Every snippet below is copy-runnable from a fresh Python session (`import idm`), and every output shown
was produced by running it. `idm` is a **readout-first** solver: results are exact over ℚ where
possible, carry an honesty **tier**, and it returns **HOLD** (never a wrong answer or a crash) when it
cannot make a readout.

## 0. Install & import

From a checkout: `pip install -e .` (or just run with `PYTHONPATH=.`). Then:

```python
import idm
idm.__version__          # -> "1.5.0"
len(idm.kinds())         # -> 269 supported problem kinds
```

## 1. Two ways to ask

**Typed convenience** — one call, no dict to assemble:

```python
idm.factorize(360360).value          # {'2': 3, '3': 2, '5': 1, '7': 1, '11': 1, '13': 1}
idm.gcd(48, 36).value                # 12
```

**Structured `solve`** — the general form; every kind is reachable this way:

```python
idm.solve({"kind": "factorize", "n": 360360})["value"]     # same result
```

## 2. The `Result` object

`idm.solve(...)` (and every convenience wrapper) returns a `Result`. It **is a `dict`** — `r["status"]`,
`json.dumps(r)`, and `isinstance(r, dict)` all work — with typed accessors on top:

```python
r = idm.factorize(97)
r.status        # 'ok'
r.value         # {'97': 1}
r.tier          # 'exact'
r.is_ok         # True    (a resolved result carrying a value)
r.is_hold       # False
r.to_dict()     # a plain dict copy
```

Prefer exceptions to status checks? `raise_for_hold()` raises `idm.SolveHold` (with the solver's own
reason) on a HOLD and returns `self` otherwise, so it chains:

```python
idm.factorize(97).raise_for_hold().value       # {'97': 1}

try:
    idm.solve({"kind": "nope"}).raise_for_hold()
except idm.SolveHold as e:
    print(e)          # unknown problem kind 'nope'
```

Three honest states: `is_ok` (a value was produced), `is_hold` (no readout made), and `is_open` (an
open-tail `+ℝ-Open` readout — a finite approximant + a certified tail bound, with **no** plain value).

## 3. Exact algebra & calculus

```python
# every root of a ℚ-polynomial, real AND complex, exact, with multiplicity
idm.solve_roots([-2, 0, 0, 1]).value            # x^3 - 2: {'num_real': 1, 'num_complex': 2, ...}

# complete exact ℚ linear solve (unique / infinite family / inconsistent)
idm.solve_matrix([[2, 1], [1, 3]], [3, 5]).value["solution_type"]      # 'unique'

# exact general solution of a linear constant-coefficient ODE (from its characteristic coeffs)
idm.solve_ode([2, -3, 1]).value["general"]      # 'C1*e^x + C2*e^(2*x)'

# exact symbolic integral of a rational function
idm.integrate_rational([1], [1, 0, 1]).value["integral"]   # '(1/sqrt(1))*arctan((x + 0)/sqrt(1)) + C'

# exact eigenvalues as algebraic objects, with completeness reported honestly
idm.solve({"kind": "exact_eigenvalues", "matrix": [[0, 1], [2, 0]]}).value["completeness"]   # 'complete'
```

## 4. Certified numerics (a value **and** a proven error bound)

```python
# ∫ e^(-x^2) dx over [-6, 6] to 1e-8 — a certified readout (√π), not a bare float
idm.solve_integral("exp(-x**2)", "-6", "6", 1e-8).value["digits"]      # '1.7724538509055159...'
```

## 5. Graphs (exact, over the tropical semirings)

```python
INF = float("inf")
idm.shortest_path([[0, 3, INF], [3, 0, 1], [INF, 1, 0]])       # [[0, 3, 4], [3, 0, 1], [4, 1, 0]]
```

## 6. When it can't: HOLD, never a wrong answer

```python
# a genuinely open / out-of-scope request holds honestly, with a reason
r = idm.solve({"kind": "all_roots", "coeffs": [9999, -4242, 1313, -77, 1]})
r.is_hold, r.reason[:40]      # (True, 'the built resultant carries 73-bit coeffic')
```

## 7. Discover what's available (no guessing field names)

```python
idm.kinds()                       # the full list (269)
idm.describe("all_roots")         # {'kind', 'tier', 'signature', 'doc', 'verify', ...}
idm.schema("gcd")["fields"]       # ['a', 'b']   — the parameters this kind reads
idm.example("linear_ode")         # a real, on-file example dict, as a string
```

The same discovery is available as a CLI: `python -m idm list --tier exact`, `python -m idm describe
factorize`, `python -m idm example linear_ode`.

## 8. Every claim carries a tier — read each on its own tier

| tier | meaning |
|---|---|
| `Th_coqc` | a named machine-checked theorem in `formal/` governs the result (a `coq_theorem` is attached) |
| `exact` | exact, finite, decidable ℤ/ℚ computation — no floating point in the result |
| `finite_diagnostic` | numeric to a declared tolerance |
| `+ℝ-Open` | an honest open-tail readout — approximant + certified bound, no plain value |

`idm` never inflates a tier: `HOLD` is a real, honest outcome, not a failure to hide.

---

Next: the full kind reference is [`../SOLVER.md`](../SOLVER.md) and [`../API.md`](../API.md); the
readout-first foundations are in [`../textbook/INFORMATION_DISCRETE_MATHEMATICS.md`](../textbook/INFORMATION_DISCRETE_MATHEMATICS.md).
