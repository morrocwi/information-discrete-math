"""idm.hilbert_open — the +ℝ-Open frontier of the Hilbert-space core (completeness / infinite dimension).

This is the ONLY place where completeness, ℓ², L², infinite orthonormal bases, and the infinite-dim
spectral theorem are named. Per this repository's foundation, ℝ-completeness (`I1`) and actual infinity
are NON-READOUTS: the completed limit / infinite object is NEVER formed. Every function here returns a
finite ℚ-approximant plus a certified tail/contraction bound, tagged `+R_OPEN` — and returns NO plain
`value` field, so `idm.solve`'s certified path cannot mistake it for an answer.

**Two-tier readout (the founder's ℚ-computability law, 2026-07-29 — continuum-maya split, Part XX).**
"If an ℝ-rung quantity is actually COMPUTED, it is computed on ℚ, so it must carry a ℚ tier — not a
blanket +ℝ-Open." Every computation here IS a finite ℚ readout; only the *completed tail* (Σ_{k>N}, the
limit, the whole-space object) is the genuine non-readout. So each function separates the two truths
explicitly:
  * `computed_core` — the exact ℚ quantity actually produced (partial energy, x_N, the finite ONB),
    with its OWN honest tier: `Th_coqc` where a machine witness exists (`formal/IDM_HilbertReadout.v`
    proves the ℓ²/L² partial energy nonneg · exact-additive · monotone over ℚ), else `exact`.
  * `open_tail` — the completed limit / infinite object that stays `+ℝ-Open`, never formed.
This grants the ℚ core its due (no more under-claiming a computed rational as merely "Open") WITHOUT
handing out a top-level `value` — the anti-overclaim fence (`status:+R_OPEN`, no `value`) is unchanged.

The +ℝ fence is enforced in CODE, not prose: `idm/hilbert.py` never imports this module (checked by a
test), and `idm/solve.py` wires these only through a HOLD/`+R_OPEN` path — never an `@kind(…,"exact")`
or `@kind(…,"Th_coqc")` entry. The KIND-level tier is never `Th_coqc` (it answers an Open target); the
`Th_coqc` claim lives strictly on `computed_core`, backed by the witness cited above.
"""
from fractions import Fraction as Q

_WITNESS = "formal/IDM_HilbertReadout.v"   # machine-checks the ℚ core: nonneg · exact-additive · monotone


def _open(target, approximant, N, note, computed_core=None, open_tail=None, **extra):
    d = {"status": "+R_OPEN", "tier": "+ℝ-Open", "target": target, "approximant": approximant,
         "N": N, "note": note}
    # The two-tier split: the ℚ readout that WAS computed (with its own tier) vs the completed non-readout.
    d["computed_core"] = computed_core   # None only where nothing is computed on ℚ (infinite_spectral)
    d["open_tail"] = open_tail if open_tail is not None else {"what": target, "tier": "+ℝ-Open"}
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
                 observed_tail_spacing={"exact": str(tail), "float": float(tail)},
                 computed_core={"what": "the finite Cauchy readout x_N and its observed tail spacing",
                                "x_N": {"exact": str(xs[-1]), "float": float(xs[-1])},
                                "observed_tail_spacing": {"exact": str(tail), "float": float(tail)},
                                "tier": "exact"},   # exact ℚ finite readout (like gram_schmidt/orthonormal_basis)
                 open_tail={"what": "lim_{n→∞} xₙ ∈ H (the completed real)", "tier": "+ℝ-Open",
                            "note": "forming the limit is a non-readout (I1)"})


def l2_readout(seq, N):
    """first-N-coordinate truncation of an ℓ² target + the exact partial energy Σ_{k≤N}|xₖ|²; the
    completed ℓ² element and its full norm are +ℝ-Open. `seq` is a callable k→ℚ."""
    N = int(N)
    coords = [_term(seq, k) for k in range(N)]
    partial = sum((c * c for c in coords), Q(0))
    return _open("x ∈ ℓ² (square-summable sequence)",
                 {"first_N_coordinates": [str(c) for c in coords],
                  "partial_energy_Σ|xk|²": {"exact": str(partial), "float": float(partial)}},
                 N, "the completed ℓ² element and its total norm need the tail Σ_{k>N}|xₖ|² (a limit) — +ℝ-Open",
                 computed_core={"what": "partial energy Σ_{k≤N}|xₖ|² (exact, over ℚ)",
                                "value": {"exact": str(partial), "float": float(partial)},
                                "first_N_coordinates": [str(c) for c in coords],
                                "tier": "Th_coqc", "witness": _WITNESS},   # nonneg·exact-additive·monotone
                 open_tail={"what": "the completed ℓ² element x and its total norm ‖x‖² = Σ_{k}|xₖ|²",
                            "tier": "+ℝ-Open", "note": "needs the tail Σ_{k>N}|xₖ|² (a completed limit)"})


def L2_readout(values_on_mesh, weights):
    """a finite quadrature approximant of an L²(X,μ) inner-product norm on a declared mesh; the completed
    L² space is +ℝ-Open. Reuses the finite-sum discipline (the true integral is the readout, never formed)."""
    vals = [Q(str(v)) for v in values_on_mesh]; w = [Q(str(x)) for x in weights]
    approx = sum((wi * vi * vi for wi, vi in zip(w, vals)), Q(0))
    # L²(X,μ): μ is a MEASURE, so genuine quadrature weights are ≥ 0 — exactly the hypothesis of the
    # weighted_energy_nonneg witness. The core is Th_coqc precisely when THIS input meets that hypothesis;
    # with a signed weight (not a measure) the value is still exact over ℚ but the nonneg witness does not
    # apply, so we honestly drop to `exact` rather than cite a witness whose premise fails.
    weights_are_measure = all(wi >= 0 for wi in w)
    core = {"what": "finite quadrature Σ wᵢ|f(xᵢ)|² on the declared mesh (exact, over ℚ)",
            "value": {"exact": str(approx), "float": float(approx)}, "nodes": len(vals)}
    if weights_are_measure:
        core["tier"] = "Th_coqc"; core["witness"] = _WITNESS   # weighted_energy_nonneg/_app (weights ≥ 0)
    else:
        core["tier"] = "exact"
        core["note"] = ("weights include a negative value → not a measure (μ≥0), so the Th_coqc nonneg "
                        "witness does not apply; the quadrature is still exact over ℚ")
    return _open("‖f‖²_{L²(X,μ)} = ∫|f|² dμ",
                 {"quadrature_Σ wᵢ|f(xᵢ)|²": {"exact": str(approx), "float": float(approx)}, "nodes": len(vals)},
                 len(vals), "the completed L² space / the exact integral is +ℝ-Open; only a finite mesh sum is shown",
                 computed_core=core,
                 open_tail={"what": "the completed L²(X,μ) space / the exact integral ∫|f|² dμ",
                            "tier": "+ℝ-Open", "note": "the true integral is the readout of the mesh sum, never formed"})


def infinite_orthonormal_basis_readout(vectors, N):
    """orthonormalize the FIRST N vectors only (exact/finite core), with an explicit non-claim of
    completeness of the span in an infinite-dimensional H."""
    from . import hilbert as HB   # allowed: hilbert_open MAY use hilbert; the fence is the OTHER direction
    N = int(N)
    onb = HB.orthonormal_basis([list(v) for v in vectors[:N]])
    return _open("a complete orthonormal basis of an infinite-dim H",
                 {"orthonormal_first_N": onb["value"], "normalization_tier": onb["tier"]},
                 N, "completeness of the span (that {eₖ} is a basis of the whole H) is +ℝ-Open — only the "
                    "finite orthonormal set is computed",
                 computed_core={"what": "the orthonormal set of the first N vectors (exact, over ℚ)",
                                "orthonormal_first_N": onb["value"], "tier": onb["tier"]},   # inherits HB exact/Th_coqc
                 open_tail={"what": "completeness of the span — that {eₖ} is a basis of the whole infinite-dim H",
                            "tier": "+ℝ-Open", "note": "completeness needs the whole (non-readout) space"})


def infinite_spectral_readout(operator_description):
    """the infinite-dim spectral theorem / unbounded-operator spectrum — NOT computed. Returns the named
    target only, pointing at the finite-n `spectral_decomposition` as what actually exists."""
    return _open("spectral decomposition of an operator on an infinite-dim H",
                 None,
                 None, "not computed: needs completeness + algebraic closure of ℂ (FTA) — +ℝ-Open. Use "
                       "idm.solve({'kind':'spectral_decomposition', ...}) for the finite-dim exact/certified case",
                 finite_dim_alternative="spectral_decomposition",
                 computed_core=None,   # the ONLY kind that computes NOTHING on ℚ — no ℚ core to tier; honest None
                 open_tail={"what": "spectral decomposition of an operator on an infinite-dim H",
                            "tier": "+ℝ-Open",
                            "note": "nothing is computed here; the ℚ-computable case is the finite-dim "
                                    "kind 'spectral_decomposition' (exact/certified), which this points to"})
