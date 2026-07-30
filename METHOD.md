# METHOD — the evidence-first solve loop

> A computation is not trustworthy because it produced digits. It is trustworthy only to the extent that its source semantics, target, arithmetic, evidence, and decision rule are explicit.

This method is the project-wide process for exact, numerical, formal, and interpretive work.

## 0. Separate interpretation from mathematical correctness

The retained-distinction language is the project's interpretive framework. It may guide modelling and algorithm design, but a theorem or numerical certificate must remain valid from its explicit definitions and hypotheses alone. No reviewer is required to accept the interpretation in order to check the mathematics.

## 1. DECLARE the source contract

State what the input record means before computing.

- A decimal token such as `0.350` may be assigned exact rational semantics \(350/1000\).
- A Python float is an exact finite dyadic record, not the decimal token from which it may have originated.
- Decimal scale is metadata; it is not automatically measurement uncertainty.
- Physical measurements require a separate calibration and uncertainty model.

No source contract means no exactness claim.

## 2. NAME the target

Write the object being approximated or decided:

\[
T(x),\qquad Q=g(x),\qquad D(Q;\tau).
\]

Distinguish exact algebraic singularity from numerical rank, a finite operator from a continuum operator, and a stability plateau from a named limit.

## 3. CHOOSE the evidence tier before choosing the tool

| Needed result | Required evidence |
|---|---|
| exact value over \(\mathbb Z/\mathbb Q\) | exact arithmetic |
| theorem | proof or checked witness |
| target enclosure | rigorous truncation + arithmetic error bound |
| discrete decision | enclosure separated from its boundary |
| numerical exploration | finite diagnostic |
| interpretation | `Dr` |
| unresolved continuum claim | `+ℝ-Open` |

Do not use evidence from one row as if it established another.

## 4. EXPRESS the finite computation

Use the lightest representation that can support the required evidence:

- integers and `Fraction` for exact decimal and rational arithmetic;
- interval or directed-rounding arithmetic for target enclosures;
- floating point for fast diagnostics or certified fast paths with a rigorous error bound;
- adaptive precision or exact fallback near a decision boundary;
- Coq witnesses for named formal statements.

The retained tools \(D_\varepsilon\), \(I_\varepsilon\), \(L_R\), FOLD, and DECISION remain available as project-native constructions. They do not remove the need to disclose the arithmetic actually executed.

## 5. ACCOUNT for every error source

A target bound must include all relevant components:

\[
E_{\mathrm{total}}
\le
E_{\mathrm{source}}+E_{\mathrm{model}}+E_{\mathrm{discretization}}+E_{\mathrm{truncation}}+E_{\mathrm{arithmetic}}.
\]

Terms may be zero, but none may be silently omitted.

- Exact rational evaluation can make \(E_{\mathrm{arithmetic}}=0\) relative to the declared record.
- A Taylor or quadrature remainder alone is not a certificate if the implementation's rounding error is unbounded.
- An unspecified \(O(u^2)\) term is not a computable certificate.
- Agreement with a library is a diagnostic, not an error proof.

## 6. CERTIFY the decision, not merely the number

Given a proved enclosure

\[
Q\in[\widehat Q-E,\widehat Q+E],
\]

a threshold decision at \(\tau\) is certified when

\[
|\widehat Q-\tau|>E.
\]

If the enclosure intersects the boundary, return `UNCERTIFIED` or escalate. Certificate failure means unresolved, not wrong.

Never branch on approximate equality with `==`. Equality requires a singleton enclosure, exact arithmetic, or a domain-specific separation theorem.

## 7. ESCALATE only when required

Use the staged path:

```text
fast approximation -> enclosure test -> adaptive/interval/exact fallback -> HOLD
```

A fixed fast path is appropriate in comfortable-margin cases. Decision-dominated cases require more information, not ideological preference for one arithmetic.

## 8. RETURN an honest status

- `CERTIFIED`: a named target lies within the returned bound under named hypotheses.
- `STABLE`: finite refinements passed a disclosed stability test; no target-distance proof is implied.
- `HOLD`: the needed hypothesis, enclosure, or resource budget is absent.
- `exact`: exact finite \(\mathbb Z/\mathbb Q\) result, without an automatic claim about physical truth.
- `Th_coqc`: only the named mapped theorem is machine checked.
- `finite_diagnostic`: reproducible numerical evidence.
- `Dr`: interpretation or design.
- `+ℝ-Open`: explicitly unresolved.

## 9. REPORT cost as data

When complexity or performance matters, provide:

- input size and representation;
- algorithm and implementation path;
- arithmetic precision;
- hardware and software environment;
- warm-up and compilation treatment;
- repeated timings and uncertainty;
- comparator workload equivalence;
- failure and non-convergence cases; and
- a `CostLedger`, not an adjective.

## 10. STOP at the proven boundary

A finite result may be exact, certified, stable, diagnostic, or interpretive. Each is useful. The method's discipline is to stop exactly where the evidence stops.

The normative API and theorem details are in `docs/READOUT_CERTIFICATION_STANDARD.md` and `THEOREM.md`.
