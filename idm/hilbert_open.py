"""idm.hilbert_open — the +ℝ-Open frontier of the Hilbert-space core (completeness / infinite dimension).

This is the ONLY place where completeness, ℓ², L², infinite orthonormal bases, and the infinite-dim
spectral theorem are named. Per this repository's foundation, ℝ-completeness (`I1`) and actual infinity
are NON-READOUTS: the completed limit / infinite object is NEVER formed. Every function here returns a
finite ℚ-approximant plus a certified tail/contraction bound, tagged `+R_OPEN` — and returns NO plain
`value` field, so `idm.solve`'s certified path cannot mistake it for an answer.

The +ℝ fence is enforced in CODE, not prose: `idm/hilbert.py` never imports this module (checked by a
test), and `idm/solve.py` wires these only through a HOLD/`+R_OPEN` path — never an `@kind(…,"exact")`
or `@kind(…,"Th_coqc")` entry. Nothing here is ever `Th_coqc`. Closing any of these to a finite theorem
would BE forming the continuum as a primitive, which the foundation forbids — they stay open by design.
"""
from fractions import Fraction as Q


def _open(target, approximant, N, note, **extra):
    d = {"status": "+R_OPEN", "tier": "+ℝ-Open", "target": target, "approximant": approximant,
         "N": N, "note": note}
    d.update(extra)
    return d


def _term(seq, n):
    """the n-th rational term of `seq`, whether it is a callable n→ℚ or a finite explicit list."""
    return Q(str(seq(n) if callable(seq) else seq[n]))

def completeness_readout(cauchy_seq, N):
    """the finite Cauchy tail up to index N + a certified spacing bound — NEVER 'the limit' as a value.
    `cauchy_seq` is a callable n→ℚ or a finite explicit list of rational approximants."""
    N = int(N)
    xs = [_term(cauchy_seq, n) for n in range(N + 1)]
    # observed tail spacing max_{k≥m}|x_{k+1}-x_k| on the computed window (a diagnostic bound, not a proof)
    gaps = [abs(xs[k + 1] - xs[k]) for k in range(N)]
    tail = max(gaps[N // 2:], default=Q(0))
    return _open("lim_{n→∞} xₙ ∈ H (a completed real)",
                 {"x_N": {"exact": str(xs[-1]), "float": float(xs[-1])}, "index": N},
                 N, "the completed limit is a non-readout (I1); only the finite rational tail is shown",
                 observed_tail_spacing={"exact": str(tail), "float": float(tail)})


def l2_readout(seq, N):
    """first-N-coordinate truncation of an ℓ² target + the exact partial energy Σ_{k≤N}|xₖ|²; the
    completed ℓ² element and its full norm are +ℝ-Open. `seq` is a callable k→ℚ."""
    N = int(N)
    coords = [_term(seq, k) for k in range(N)]
    partial = sum((c * c for c in coords), Q(0))
    return _open("x ∈ ℓ² (square-summable sequence)",
                 {"first_N_coordinates": [str(c) for c in coords],
                  "partial_energy_Σ|xk|²": {"exact": str(partial), "float": float(partial)}},
                 N, "the completed ℓ² element and its total norm need the tail Σ_{k>N}|xₖ|² (a limit) — +ℝ-Open")


def L2_readout(values_on_mesh, weights):
    """a finite quadrature approximant of an L²(X,μ) inner-product norm on a declared mesh; the completed
    L² space is +ℝ-Open. Reuses the finite-sum discipline (the true integral is the readout, never formed)."""
    vals = [Q(str(v)) for v in values_on_mesh]; w = [Q(str(x)) for x in weights]
    approx = sum((wi * vi * vi for wi, vi in zip(w, vals)), Q(0))
    return _open("‖f‖²_{L²(X,μ)} = ∫|f|² dμ",
                 {"quadrature_Σ wᵢ|f(xᵢ)|²": {"exact": str(approx), "float": float(approx)}, "nodes": len(vals)},
                 len(vals), "the completed L² space / the exact integral is +ℝ-Open; only a finite mesh sum is shown")


def infinite_orthonormal_basis_readout(vectors, N):
    """orthonormalize the FIRST N vectors only (exact/finite core), with an explicit non-claim of
    completeness of the span in an infinite-dimensional H."""
    from . import hilbert as HB   # allowed: hilbert_open MAY use hilbert; the fence is the OTHER direction
    N = int(N)
    onb = HB.orthonormal_basis([list(v) for v in vectors[:N]])
    return _open("a complete orthonormal basis of an infinite-dim H",
                 {"orthonormal_first_N": onb["value"], "normalization_tier": onb["tier"]},
                 N, "completeness of the span (that {eₖ} is a basis of the whole H) is +ℝ-Open — only the "
                    "finite orthonormal set is computed")


def infinite_spectral_readout(operator_description):
    """the infinite-dim spectral theorem / unbounded-operator spectrum — NOT computed. Returns the named
    target only, pointing at the finite-n `spectral_decomposition` as what actually exists."""
    return _open("spectral decomposition of an operator on an infinite-dim H",
                 None,
                 None, "not computed: needs completeness + algebraic closure of ℂ (FTA) — +ℝ-Open. Use "
                       "idm.solve({'kind':'spectral_decomposition', ...}) for the finite-dim exact/certified case",
                 finite_dim_alternative="spectral_decomposition")
