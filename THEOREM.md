# Finite Readout and Decision Certification Theorems

This document is the canonical claim boundary for Information Discrete Mathematics. It separates exact source semantics, target certification, finite stability, formal proof mappings, numerical diagnostics, and interpretation.

## 1. Claim taxonomy

A public result belongs to one or more explicitly named classes:

- **exact:** finite \(\mathbb Z/\mathbb Q\) evaluation, exact relative to the declared source values;
- **CERTIFIED:** a named target lies in a proved enclosure under named hypotheses;
- **STABLE:** a finite refinement sequence passed a disclosed stability test, without a target-distance theorem;
- **Th_coqc:** the named abstract theorem has a machine-checked proof mapping;
- **finite_diagnostic:** reproducible finite numerical evidence or comparator agreement;
- **Dr:** design or interpretation;
- **+ℝ-Open:** a continuum-level statement deliberately left unresolved;
- **HOLD:** the hypotheses, enclosure, or resources required for a stronger conclusion are absent.

No class is silently promoted into another.

## 2. Source readouts

### Definition 2.1 — finite decimal readout

A finite decimal readout is a pair

\[
r=(n,k)\in\mathbb Z\times\mathbb N,
\qquad
\operatorname{val}(r)=n10^{-k}\in\mathbb Q.
\]

The scale \(k\) records the decimal form of the source token. It is not, without an acquisition contract, a measurement-uncertainty model.

Addition and multiplication are

\[
(n,k)\oplus(m,j)=
\left(n10^{p-k}+m10^{p-j},p\right),
\qquad p=\max(k,j),
\]

\[
(n,k)\otimes(m,j)=(nm,k+j).
\]

### Theorem 2.2 — exact rational evaluation

Let a finite expression tree have finite decimal readouts at its leaves and operations \(+,-,\times,\div\), with nonzero denominators. If every node is evaluated using arbitrary-precision integer numerators and denominators, the returned rational equals the mathematical value of the expression in \(\mathbb Q\).

**Proof.** Integers are closed under addition and multiplication. Scale alignment multiplies numerators by integer powers of ten. Rational division appends a nonzero integer denominator. Structural induction over the finite expression tree gives the result. \(\square\)

### Boundary

The theorem eliminates conversion and arithmetic rounding relative to the declared source record. It does not eliminate measurement uncertainty, model error, discretization error, or an incorrect specification.

## 3. A precision-parametric direct-evaluation collision

### Theorem 3.1 — direct determinant collision

Consider a normalized radix-2 format with precision \(p\ge3\), round-to-nearest ties-to-even, correctly rounded multiplication and subtraction, and sufficient exponent range. Let

\[
N=2^{p-1},
\qquad
A_p=\begin{pmatrix}N&N-1\\N+1&N\end{pmatrix}.
\]

Every matrix entry is exactly representable, and

\[
\det A_p=N^2-(N-1)(N+1)=1.
\]

If the determinant expression is evaluated by rounding the two products separately and then subtracting, the computed result is zero.

**Proof.** The first product is exactly \(N^2\). The second exact product is \(N^2-1\). At the binade containing \(N^2\), the precision-\(p\) spacing is large enough that \(N^2-1\) rounds to \(N^2\) under ties-to-even. The subtraction therefore receives equal representable operands and returns zero. \(\square\)

### Corollary 3.2

Direct rounded evaluation of \(ad-bc\) is not a universally correct exact-singularity predicate over unrestricted exactly representable integer inputs.

### Scope of the corollary

This is a limitation of the stated evaluation path. It is not a proof that every algorithm using fixed-size floating-point words must fail. Multiword expansions, exact integer arithmetic, interval methods, source-token inspection, and symbolic preprocessing are different computational models.

A fused multiply-add removes one intermediate rounding. A single FMA does not, in general, evaluate a difference of two products with only one rounding; it may repair special witnesses when the other product is exactly available.

## 4. Certified discrete decisions

Let \(Q\) be a scalar target and \(\tau\) a decision threshold.

### Definition 4.1 — proved enclosure

An algorithm supplies a target certificate when it proves

\[
Q\in[L,U].
\]

A symmetric certificate may be written

\[
Q\in[\widehat Q-E,\widehat Q+E],\qquad E\ge0.
\]

### Theorem 4.2 — operational threshold certificate

The enclosure determines the threshold decision exactly when

\[
[L,U]\cap\{\tau\}=\varnothing,
\]

or when \(L=U=\tau\), which certifies equality.

For a symmetric enclosure, strict-side certification is equivalent to

\[
|\widehat Q-\tau|>E.
\]

**Proof.** If \(U<\tau\), every admissible target lies below the threshold. If \(L>\tau\), every admissible target lies above it. If \(L=U=\tau\), equality is exact. In all other cases the enclosure contains values on, or potentially on both sides of, the threshold, so the evidence does not determine a unique decision. \(\square\)

### Corollary 4.3 — normalized sufficient condition

If a rigorous forward error bound has the form

\[
E\le c_A\kappa uS
\]

and the computed estimate satisfies

\[
c_A\kappa uS<|\widehat Q-\tau|,
\]

the decision is certified. A formulation \(c_A\kappa u<\delta\) is therefore a sufficient certification condition after normalization.

It is not an iff statement about actual floating-point correctness. When the inequality fails, the result is unresolved by that bound, not necessarily wrong.

## 5. Target certification versus finite stability

### 5.1 Target certificate

A routine may return `CERTIFIED(q,B)` only when it establishes

\[
|q-T(x)|\le B
\]

under named hypotheses and includes every error source used by the implementation. A truncation theorem alone is insufficient if arithmetic error is ignored.

### 5.2 Stability result

Suppose finite refinements \(q_0,q_1,\ldots,q_N\) have contracting observed gaps. This is evidence of finite stability. Without an independently justified contraction theorem or target enclosure, it does not prove that:

- the pattern continues for all future refinements;
- the sequence converges;
- the limit equals a named target; or
- the last observed gap bounds target error.

Such routines return `STABLE`, not `CERTIFIED`.

### 5.3 Equality and termination

For \(Q\ne\tau\), a convergent certified enclosure process may eventually separate from the boundary. For \(Q=\tau\), interval refinement alone may not terminate with equality. Exact algebra, a symbolic identity, or a domain-specific separation theorem is required to certify equality in finite time.

## 6. Current certified-readout API

The public API in `idm.certified` follows this table:

| Routine | Status on success | Evidence |
|---|---|---|
| `geom_series` | `CERTIFIED` | exact rational partial sum and exact geometric tail |
| `exp` | `CERTIFIED` | exact rational Taylor sum and a proved geometric majorant of the remaining terms |
| `simpson` | `CERTIFIED` | exact rational node arithmetic plus caller-supplied fourth-derivative bound |
| `richardson` | `STABLE` | observed Richardson-diagonal contraction |
| `richardson_apriori_certified` | `STABLE` | conditional order-model envelope; asymptotic entry is not proved |
| `integral` | `STABLE` | observed finite trapezoid refinement contraction |
| `integral_nd` | `STABLE` | observed finite tensor-trapezoid refinement contraction |

A missing derivative bound, inexact quadrature node arithmetic, failed contraction test, invalid domain, or exhausted resource budget produces `HOLD`.

## 7. Formal spine and what it proves

The repository's formal layer contains machine-checked finite laws. The proof tier attaches only to the named statement.

### 7.1 Genesis and discrete floor

`formal/IDM_Genesis.v` exhibits a first distinction over \(\mathbb N\) and the absence of an integer strictly between \(0\) and \(1\). This is an axiom-free theorem about the chosen discrete model. The philosophical claim that it is ontologically primitive remains `Dr`.

### 7.2 Number construction

Integer ring identities and rational field constructions are finite algebraic mathematics. Any use of `Coq.Reals` or a completed real-number construction must be labelled separately with its imported assumptions.

### 7.3 Graph-Laplacian identity

`formal/IDM_Keystone.v` proves the algebraic identity

\[
\Phi^T L\Phi=\sum_{(i,j,w)}w(\Phi_i-\Phi_j)^2
\]

under the declared graph definitions, together with nonnegativity for nonnegative weights. Calling this quantity retained information is an interpretation layered over the identity.

### 7.4 Exact finite calculus

`formal/IDM_Calculus.v` and `formal/IDM_Bridge.v` prove telescoping and summation-by-parts identities, including

\[
\sum_{n=0}^{N-1}(f_{n+1}-f_n)=f_N-f_0.
\]

These are exact finite identities. They do not, without additional hypotheses, prove convergence to a continuum derivative or integral.

### 7.5 Certified geometric tail

`formal/IDM_Certified.v` supplies the machine-checked finite law used by the rational geometric-series certificate. Code-to-proof mapping must identify the exact theorem and all implementation assumptions.

## 8. Numerical linear algebra boundary

Exact algebraic singularity, backward-stable solution of a nearby system, and numerical rank under a tolerance are different targets.

- Exact determinant predicates may require exact or adaptive arithmetic.
- Numerical solvers should use factorization, residuals, backward error, condition estimates, and rank-revealing methods rather than branching on a naively computed determinant.
- A finite operator spectrum is exact only relative to that declared operator and arithmetic; approximation to a continuum operator requires a separate discretization theorem or diagnostic tier.

## 9. Measurement boundary

The exact value of a recorded token is not the exact value of a physical quantity. A measurement claim requires separate information about calibration, quantization, uncertainty, and decision risk. Decimal scale alone cannot supply these.

## 10. Recommended implementation architecture

```text
exact source parse
    -> fast numerical evaluation
    -> rigorous enclosure
        -> enclosure excludes boundary: return certified decision
        -> enclosure intersects boundary: escalate
    -> interval / increased precision / expansion / exact arithmetic
        -> certified decision
        -> HOLD if hypothesis or budget fails
```

This is a division of labour, not a claim that exact rational arithmetic replaces floating point generally.

## 11. Novelty boundary

The following are classical and are not claimed as new:

- catastrophic cancellation;
- floating-point condition and stability analysis;
- interval decision certification;
- exact and adaptive geometric predicates;
- fixed-point, decimal, rational, and arbitrary-precision arithmetic;
- measurement guard bands and conformity decisions.

The project contribution is the readout-first synthesis: exact source-record semantics, explicit evidence tiers, fail-closed decision APIs, formal finite laws, and executable finite methods within one framework.

## 12. Reproducibility

Run:

```bash
pytest -q
python3 tools/certified_readout.py
bash formal/verify.sh
```

The precision-parametric determinant test is implemented in `idm/readout_boundary.py` and exercised by `tests/test_readout_boundary.py`. The test simulates ties-to-even significand rounding at each declared precision rather than checking only the underlying integer identity.

## 13. Canonical standard

The normative engineering contract, status vocabulary, and required result fields are in:

- `docs/READOUT_CERTIFICATION_STANDARD.md`
- `METHOD.md`
- `AGENTS.md`

Where older prose conflicts with these documents, this theorem boundary and the certification standard govern.
