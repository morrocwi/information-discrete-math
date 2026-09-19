# Clause-Presence Encoding Size Guard

**Purpose:** prevent a valid linear lower bound from being misreported as a superpolynomial SAT lower bound.

For `n` propositional variables, the raw clause-presence encoding used by
`sat_clause_essentiality_refuter.py` has one bit for each non-tautological
clause.  Each variable is absent, positive, or negative, hence

\[
M(n)=3^n
\]

raw input bits (including the empty clause).

The sharing-aware essential-input DAG bound gives

\[
M(n)\le 2s+1,
\]

so

\[
\boxed{s\ge \frac{3^n-1}{2}.}
\]

This is exponential in the *underlying variable count* `n`, but the circuit's
actual input length in this encoding is

\[
N=M(n)=3^n.
\]

Therefore the same bound is simply

\[
\boxed{s\ge \frac{N-1}{2}=\Omega(N).}
\]

It is a constructive linear lower-bound baseline for this padded/raw encoding,
not a superpolynomial lower bound in the input length.  It gives neither
`SAT notin P/poly` nor `P != NP`.

## Why keep it

The result is still useful because it validates an unrestricted shared-DAG
refuter mechanism end to end:

1. inspect the candidate's syntactic input lineage;
2. find an omitted essential clause bit when `M>2s+1`;
3. construct an explicit pair of encodings differing only in that bit;
4. know one member is SAT and the other UNSAT from the construction itself;
5. because the circuit omits the bit, it gives the same answer on both;
6. output a concrete counterexample without a SAT/equivalence oracle.

The next research step must obtain additional charge **after every relevant
input bit is already present**.  Input presence alone can never exceed a linear
bound in the real encoding length.
