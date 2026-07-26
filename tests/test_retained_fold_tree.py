"""RFT / Retained Readout Pullback correctness — native executor vs an independent reference."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks"))
from coupled_nd_retained_compiler import PairwiseProblem, default_problem
from retained_fold_tree import compile_retained_readout_pullback, reference_readouts


def _complete(d):
    lin = tuple(0.15 + 0.03 * a for a in range(d))
    cpl = tuple((i, j, 0.04 + 0.01 * ((i * d + j) % 5)) for i in range(d) for j in range(i + 1, d))
    return PairwiseProblem(d, lin, cpl)


def test_rft_matches_reference_contraction():
    # native RFT (forward fold + downward relevance unfold) must equal the independent tilted-factor
    # contraction to machine precision, on both a sparse and a complete graph.
    for prob in (default_problem(5), default_problem(9), _complete(5), _complete(7)):
        res = compile_retained_readout_pullback(prob, 4)
        Z, mu, chi = reference_readouts(prob, 4)
        assert abs(res.value - Z) < 1e-10
        assert max(abs(a - b) for a, b in zip(res.axis_first_moments, mu)) < 1e-10
        p = res.retained_readout_pullback
        assert max(abs(a - b) for a, b in zip(p.coupling_cross_moments, chi)) < 1e-10
        # exponential-family gradient identities
        assert all(abs(g - (-res.value * m)) < 1e-9 for g, m in zip(p.partition_linear_gradients, res.axis_first_moments))
        assert all(abs(g - (-m)) < 1e-12 for g, m in zip(p.log_partition_linear_gradients, res.axis_first_moments))


def test_rft_gradients_match_finite_differences():
    prob = default_problem(5)
    res = compile_retained_readout_pullback(prob, 4)
    p = res.retained_readout_pullback
    grad = p.log_partition_linear_gradients + p.log_partition_coupling_gradients
    base = list(prob.linear) + [s for _l, _r, s in prob.couplings]
    d = prob.dimension

    def logZ(theta):
        lin = tuple(theta[:d]); cpl = tuple((l, r, theta[d + e]) for e, (l, r, _s) in enumerate(prob.couplings))
        return math.log(reference_readouts(PairwiseProblem(d, lin, cpl), 4)[0])

    h = 1e-6
    for k in range(len(base)):
        tp = base[:]; tm = base[:]; tp[k] += h; tm[k] -= h
        fd = (logZ(tp) - logZ(tm)) / (2 * h)
        assert abs(grad[k] - fd) < 1e-6
