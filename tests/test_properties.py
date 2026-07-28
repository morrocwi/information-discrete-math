"""Property-based & universal coverage tests for the whole solver surface.

Where test_idm_api.py checks specific worked examples, this file enforces INVARIANTS across ALL 230
kinds — so a bug in a rarely-exercised kind (the kind that adversarial review kept finding) is caught:

  • every kind is invocable and returns a well-formed, correctly-tiered result on valid input;
  • the `Th_coqc` tag is never emitted without a `coq_theorem` mapping (no tier inflation);
  • a missing field or garbage input yields HOLD, never an uncaught exception (HOLD-not-crash);
  • out-of-domain parameters are rejected across the probability/geometry families (domain guards);
  • hypothesis fuzzes the number-theory / geometry cores against independent oracles (sympy).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idm

_ALLOWED_STATUS = {"ok", "CERTIFIED", "HOLD", "+R_OPEN"}
_ALLOWED_TIER = {"Th_coqc", "exact", "finite_diagnostic", "+ℝ-Open"}
_COQ_BACKED = idm.solve.__globals__["_COQ_BACKED"]

# ---- a valid input for every kind (status should be ok/CERTIFIED, not HOLD) ----
FIXTURES = {
    "constant": {"name": "pi"}, "exp": {"x": 0.4}, "function": {"name": "sin", "x": 1},
    "derivative": {"f": "exp(x)", "x": 1}, "evaluate": {"expr": "2+3*4"},
    "gamma": {"z": 5}, "beta": {"a": 2, "b": 3}, "digamma": {"x": 2},
    "erf": {"x": 1}, "erfc": {"x": 1}, "Ei": {"x": 1}, "E1": {"x": 1}, "li": {"x": 2},
    "Si": {"x": 1}, "Ci": {"x": 1}, "fresnel_S": {"x": 1}, "fresnel_C": {"x": 1},
    "airy_Ai": {"x": 1}, "lambert_W": {"x": 1},
    "bessel_J": {"n": 0, "x": 1}, "bessel_I": {"n": 0, "x": 1},
    "legendre_P": {"n": 3, "x": "0.5"}, "hermite_H": {"n": 3, "x": "0.5"},
    "chebyshev_T": {"n": 3, "x": "0.5"}, "chebyshev_U": {"n": 3, "x": "0.5"},
    "laguerre_L": {"n": 3, "x": "0.5"},
    "elliptic_K": {"m": "0.5"}, "elliptic_E": {"m": "0.5"},
    "hyp2f1": {"a": 1, "b": 1, "c": 2, "x": "0.5"}, "hyp1f1": {"a": 1, "b": 2, "x": "0.5"},
    "polylog": {"s": 2, "x": "0.5"}, "dirichlet_eta": {"s": 2}, "dirichlet_beta": {"s": 2},
    "hurwitz_zeta": {"s": 2, "a": 1}, "zeta": {"s": 2},
    # number theory
    "polynomial_positivity": {"polynomial": "x**4*y**2 + x**2*y**4 + 1 - 3*x**2*y**2", "variables": ["x", "y"]},
    "gcd": {"a": 48, "b": 36}, "lcm": {"a": 4, "b": 6}, "factorial": {"n": 10},
    "factorize": {"n": 360360}, "divisors": {"n": 28}, "num_divisors": {"n": 36},
    "sigma": {"n": 28, "k": 1}, "totient": {"n": 36}, "mobius": {"n": 30}, "mertens": {"N": 10},
    "liouville": {"n": 12}, "von_mangoldt": {"n": 8}, "is_prime": {"n": 97},
    "primality_certificate": {"n": 97}, "next_prime": {"n": 100}, "prime_pi": {"N": 100},
    "primes": {"N": 50}, "primitive_root": {"p": 7}, "fibonacci": {"n": 50}, "lucas": {"n": 10},
    "catalan": {"n": 10}, "bell": {"n": 5}, "bernoulli": {"n": 6}, "partition": {"n": 100},
    "derangements": {"n": 5}, "stirling2": {"n": 5, "k": 2}, "multinomial": {"ks": [2, 2, 1]},
    "comb_with_rep": {"n": 5, "k": 3}, "perm_count": {"n": 5, "k": 2}, "faulhaber": {"power": 2, "N": 10},
    "crt": {"residues": [2, 3, 2], "moduli": [3, 5, 7]}, "bezout": {"a": 240, "b": 46},
    "mod_inverse": {"a": 3, "m": 11}, "modinv": {"a": 3, "m": 11}, "modpow": {"base": 2, "exp": 10, "mod": 1000},
    "modular_sqrt": {"a": 2, "p": 7}, "jacobi_symbol": {"a": 5, "n": 21}, "legendre_symbol": {"a": 5, "p": 7},
    "digital_root": {"n": 12345, "base": 10}, "base_convert": {"n": 255, "base": 16},
    "integer_root": {"n": 27, "k": 3}, "integer_sqrt": {"n": 144}, "is_perfect_square": {"n": 144},
    "diophantine_linear": {"a": 3, "b": 6, "c": 9}, "pell": {"D": 7}, "continued_fraction": {"num": 415, "den": 93, "terms": 10},
    "discrete_log": {"g": 2, "h": 22, "p": 29},
    # crypto
    "rsa_keygen": {"p": 61, "q": 53, "e": 17}, "rsa_encrypt": {"m": 65, "e": 17, "n": 3233},
    "rsa_decrypt": {"c": 2790, "d": 2753, "n": 3233}, "ec_add": {"P": [5, 1], "Q": [5, 1], "a": 2, "p": 17},
    "ec_mul": {"k": 3, "P": [5, 1], "a": 2, "p": 17},
    # linear algebra
    "matrix_add": {"A": [[1, 2]], "B": [[3, 4]]}, "matrix_multiply": {"A": [[1, 2], [3, 4]], "B": [[5, 6], [7, 8]]},
    "matrix_determinant": {"matrix": [[1, 2], [3, 4]]}, "matrix_inverse": {"matrix": [[1, 0], [0, 1]]},
    "matrix_transpose": {"matrix": [[1, 2, 3], [4, 5, 6]]}, "matrix_trace": {"matrix": [[1, 2], [3, 4]]},
    "matrix_rank": {"matrix": [[1, 2], [2, 4]]}, "matrix_power": {"matrix": [[1, 1], [0, 1]], "k": 3},
    "matrix_exp": {"matrix": [[0, 1], [0, 0]]}, "char_poly": {"matrix": [[2, 0], [0, 3]]},
    "eigenvalues": {"matrix": [[2, 0], [0, 3]]}, "null_space": {"matrix": [[1, 2], [2, 4]]},
    "rref": {"matrix": [[1, 2, 3], [4, 5, 6]]}, "solve_linear": {"A": [[2, 1], [1, 3]], "b": [3, 5]},
    "matrix_solve": {"A": [[2, 1], [1, 3]], "b": [3, 5]},
    "least_squares": {"A": [[1, 1], [1, 2], [1, 3]], "b": [1, 2, 2]},
    "hermite_normal_form": {"matrix": [[2, 4], [6, 8]]}, "smith_normal_form": {"matrix": [[2, 4], [6, 8]]},
    "gershgorin": {"matrix": [[2, "0.1"], ["0.1", 3]]},
    # vectors / polynomials
    "dot": {"u": [1, 2, 3], "v": [4, 5, 6]}, "cross": {"u": [1, 0, 0], "v": [0, 1, 0]},
    "vector_norm": {"v": [3, 4]}, "convolution": {"a": [1, 1, 1], "b": [1, 1]},
    "poly_add": {"a": [1, 2], "b": [3, 4]}, "poly_mul": {"a": [1, 1], "b": [1, 1]},
    "poly_eval": {"coeffs": [1, 2, 3], "x": 2}, "poly_derivative": {"coeffs": [1, 2, 3]},
    "poly_integral": {"coeffs": [1, 2, 3]}, "poly_divmod": {"a": [-6, 11, -6, 1], "b": [-1, 1]},
    "poly_gcd": {"a": [-1, 0, 1], "b": [-1, 1]}, "poly_from_roots": {"roots": [1, 2, 3]},
    "poly_roots": {"coeffs": [-6, 11, -6, 1]}, "rational_roots": {"coeffs": [-6, 11, -6, 1]},
    "interpolate": {"points": [[0, 1], [1, 3], [2, 7]], "x": 3},
    # analysis / integration
    "integral": {"f": "exp(-x**2)", "a": "-6", "b": "6", "eps": "1e-8"},
    "improper_integral": {"f": "exp(-x)", "a": 0, "b": "inf"},
    "singular_integral": {"f": "1/sqrt(x)", "a": "1e-30", "b": 1},
    "oscillatory_integral": {"f": "sin(x)", "a": 0, "b": 6.283185307},
    "double_integral": {"f": "x*y", "ax": 0, "bx": 1, "ay": 0, "by": 1},
    "multidim_integral": {"f": "x*y", "vars": ["x", "y"], "bounds": [[0, 1], [0, 1]], "n": 20},
    "gauss_quadrature": {"f": "x**2", "a": 0, "b": 1, "n": 5}, "arc_length": {"f": "x**2", "a": 0, "b": 1},
    "root_find": {"f": "x*x-2", "a": 0, "b": 2}, "minimize": {"f": "(x-3)**2+1", "a": 0, "b": 6},
    "fixed_point": {"g": "cos(x)", "x0": 1}, "summation": {"term": "k**2", "a": 1, "b": 10},
    "regularized_sum": {"power": 1},
    # limits / series
    "limit": {"seq": "(1+1/n)**n"}, "limit_infinity": {"f": "(2*n+1)/(n+1)"},
    "limit_oneside": {"f": "sin(x)/x", "a": 0, "side": "+"}, "certified_limit": {"seq": "(1+1/n)**n", "eps": "1e-9"},
    "lhopital": {"num": "sin(x)", "den": "x", "a": 0}, "series_sum": {"term": "1/2**n", "N": 50},
    "series_accelerate": {"term": "(-1)**n/(2*n+1)", "N": 30}, "convergence_test": {"term": "1/n**2", "N": 200},
    "taylor_series": {"f": "exp(x)", "x0": 0, "n": 5}, "laurent_series": {"f": "1/z", "x0": 0, "lo": -2, "hi": 2},
    "pade": {"coeffs": ["1", "1", "1/2", "1/6"], "m": 2, "n": 2}, "geometric_series": {"r": "1/3", "eps": "1e-12"},
    "fourier_series": {"f": "x", "n": 3, "period": 6.283185307},
    # transforms / complex
    "laplace_transform": {"f": "exp(2*t)", "s": 3}, "inverse_laplace": {"F": "1/(s-1)", "t": 1},
    "mellin_transform": {"f": "exp(-x)", "s": 2}, "fourier_transform": {"f": "exp(-x**2)", "omega": 1, "T": 10},
    "fft": {"x": [1, 2, 3, 4]}, "ifft": {"x": [1, 2, 3, 4]}, "z_transform": {"x": [1, 2, 3], "z": 2},
    "contour_integral": {"f": "1/z", "center": 0, "radius": 1}, "argument_principle": {"f": "z", "center": 0, "radius": 2},
    "residue_integral": {"num": "1", "den": "z**2+1"},
    # symbolic
    "symbolic_diff": {"expr": "x**3", "var": "x"}, "symbolic_integrate": {"expr": "x**2", "var": "x"},
    "symbolic_solve": {"expr": "x**2-2", "var": "x"}, "symbolic_series": {"expr": "exp(x)", "var": "x", "x0": 0, "n": 5},
    "simplify": {"expr": "x+x+1"}, "expand": {"expr": "(x+1)**3"},
    # ODE/PDE
    "ode": {"f": "y", "x0": 0, "y0": 1, "xT": 1},
    "ode_system": {"f": ["y", "-x"], "vars": ["x", "y"], "x0": 0, "y0": [1, 0], "xT": 1},
    "ode_bvp": {"q": "0", "r": "0", "a": 0, "b": 1, "alpha": 0, "beta": 1, "at": 0.5},
    "pde_heat": {"init": "sin(pi*x)", "alpha": 1, "L": 1, "T": "0.05", "Nx": 10, "Nt": 40,
                 "bc": {"left": 0, "right": 0}, "at": [0.5, 0.05]},
    "pde_wave": {"init": "sin(pi*x)", "init_vel": "0", "c": 1, "L": 1, "T": "0.1", "Nx": 10,
                 "bc": {"left": 0, "right": 0}, "at": [0.5, 0.1]},
    "pde_laplace": {"Nx": 8, "Ny": 8, "bc": {"top": 1, "bottom": 0, "left": 0, "right": 0}, "at": [4, 4]},
    "pde_poisson": {"f": "0", "box": [1, 1], "Nx": 8, "Ny": 8, "bc": {"top": 1, "bottom": 0, "left": 0, "right": 0}, "at": [4, 4]},
    "sturm_liouville": {"potential": "0", "L": 3.14159265, "N": 100, "n_eigs": 3},
    # optimization (continuous)
    "gradient": {"f": "x**2+y**2", "vars": ["x", "y"], "point": [1, 2]},
    "gradient_descent": {"f": "(x-1)**2+(y-2)**2", "vars": ["x", "y"], "x0": [0, 0]},
    "newton_min": {"f": "(x-1)**2", "vars": ["x"], "x0": [0]},
    "newton_system": {"F": ["x**2-2"], "vars": ["x"], "x0": [1]},
    "lagrange_min": {"f": "x**2+y**2", "constraints": ["x+y-1"], "vars": ["x", "y"], "x0": [1, 1]},
    # combinatorial optimization / graphs
    "knapsack": {"values": [60, 100, 120], "weights": [10, 20, 30], "capacity": 50},
    "subset_sum": {"nums": [3, 34, 4, 12, 5, 2], "target": 9}, "coin_change": {"coins": [1, 2, 5], "amount": 11},
    "lcs": {"a": "ABCBDAB", "b": "BDCAB"}, "edit_distance": {"a": "kitten", "b": "sitting"},
    "dijkstra": {"n": 3, "edges": [[0, 1, 2], [1, 2, 3]], "source": 0},
    "bellman_ford": {"n": 3, "edges": [[0, 1, 2], [1, 2, 3]], "source": 0},
    "bipartite_matching": {"nL": 2, "nR": 2, "edges": [[0, 0], [1, 1]]},
    "assignment": {"cost": [[1, 2], [3, 4]]}, "spanning_tree_count": {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
    "chromatic_number": {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]},
    "linear_program": {"c": [3, 2], "A": [[1, 1], [1, 3]], "b": [4, 6], "sense": "max"},
    "sat": {"clauses": [[1, -2], [2, 3]], "n_vars": 3},
    "mst": {"n": 4, "edges": [[0, 1, 1], [1, 2, 2], [2, 3, 3], [0, 3, 10]]},
    "max_flow": {"n": 4, "edges": [[0, 1, 3], [0, 2, 2], [1, 3, 2], [2, 3, 3]], "source": 0, "sink": 3},
    "topological_sort": {"n": 4, "edges": [[0, 1], [1, 2], [0, 2], [2, 3]]},
    "connected_components": {"n": 4, "edges": [[0, 1], [2, 3]]}, "is_bipartite": {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
    "shortest_path": {"matrix": [[0, 3, None], [3, 0, 1], [None, 1, 0]], "source": 0, "target": 2},
    "widest_path": {"matrix": [[0, 3, None], [3, 0, 1], [None, 1, 0]], "source": 0, "target": 2},
    "minimax_path": {"matrix": [[0, 1], [1, 0]], "source": 0, "target": 1},
    "critical_path": {"matrix": [[0, 1], [0, 0]], "source": 0, "target": 1},
    "reachability": {"matrix": [[0, 1], [0, 0]], "source": 0, "target": 1},
    "path_count": {"matrix": [[0, 1], [0, 0]], "source": 0, "target": 1},
    # sets / logic
    "set_operation": {"op": "intersection", "a": [1, 2, 3], "b": [2, 3, 4]}, "powerset": {"set": [1, 2, 3]},
    "truth_table": {"expr": "a or not a", "vars": ["a"]},
    # statistics
    "binomial": {"n": 10, "k": 3, "p": "1/2"}, "poisson": {"lam": 2, "k": 1},
    "hypergeometric": {"N": 50, "K": 5, "n": 10, "k": 2}, "geometric": {"p": "1/3", "k": 2},
    "normal": {"x": 1.96, "mu": 0, "sigma": 1}, "describe": {"data": [2, 4, 4, 4, 5, 5, 7, 9]},
    "z_test": {"sample_mean": 105, "mu0": 100, "sigma": 15, "n": 30},
    "t_test": {"sample_mean": 105, "mu0": 100, "sample_std": 15, "n": 30},
    "chi_square_test": {"observed": [10, 20, 30, 40], "expected": [25, 25, 25, 25]},
    "regression": {"x": [0, 1, 2, 3], "y": [1, 3, 5, 7], "degree": 1},
    "multiple_regression": {"X": [[1, 1], [2, 1], [1, 2], [2, 2]], "y": [6, 8, 7, 9]},
    "markov_absorbing": {"P": [[1, 0, 0], ["1/2", 0, "1/2"], [0, 0, 1]], "absorbing": [0, 2]},
    "stationary": {"P": [["1/2", "1/2"], ["1/4", "3/4"]]},
    "bayes_update": {"prior": ["1/2", "1/2"], "likelihood": ["9/10", "1/10"]},
    # geometry
    "orient": {"a": [0, 0], "b": [1, 0], "c": [0, 1]}, "convex_hull": {"points": [[0, 0], [1, 0], [1, 1], [0, 1]]},
    "polygon_area": {"points": [[0, 0], [4, 0], [4, 3], [0, 3]]}, "triangle_area": {"a": [0, 0], "b": [4, 0], "c": [0, 3]},
    "point_in_polygon": {"point": [2, 1], "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]},
    "segments_intersect": {"p1": [0, 0], "p2": [2, 2], "p3": [0, 2], "p4": [2, 0]},
    "closest_pair": {"points": [[0, 0], [5, 5], [1, 0]]}, "distance": {"p": [0, 0], "q": [3, 4]},
    "in_circle": {"a": [0, 0], "b": [1, 0], "c": [0, 1], "d": ["1/4", "1/4"]},
    # certification (interval)
    "interval_enclose": {"expr": "x**2", "box": {"x": [1, 2]}},
    "verified_range": {"expr": "x**2-2*x", "var": "x", "a": 0, "b": 3},
    "certified_root": {"expr": "x**2-2", "var": "x", "a": 1, "b": 2},
    "certified_min": {"expr": "(x-3)**2+1", "var": "x", "a": 0, "b": 6},
    # readouts
    "readouts": {"data": [3, -1, 4, 1, -5, 9]},
    # H1 · Hilbert-space mathematical core (finite-dim exact / finite_diagnostic)
    "inner_product": {"u": [1, 2, 3], "v": [4, 5, 6]},
    "norm_squared": {"v": [3, 4]},
    "cauchy_schwarz_check": {"u": [1, 2], "v": [3, 4]},
    "is_orthogonal": {"u": [1, 0], "v": [0, 1]},
    "gram_matrix": {"vectors": [[1, 0], [1, 1]]},
    "gram_schmidt": {"vectors": [[1, 1, 0], [1, 0, 1]]},
    "orthonormal_basis": {"vectors": [[3, 4]]},
    "projection_matrix": {"basis": [[1, 0, 0]]},
    "project": {"v": [1, 2, 3], "basis": [[1, 0, 0], [0, 1, 0]]},
    "is_idempotent": {"M": [[1, 0], [0, 0]]},
    "adjoint": {"M": [[2, [0, 1]], [[0, -1], 3]]},
    "is_self_adjoint": {"M": [[2, 0], [0, 3]]},
    "is_unitary": {"M": [[0, 1], [1, 0]]},
    "is_normal": {"M": [[2, 0], [0, 3]]},
    "gershgorin_bound": {"M": [[2, 1], [1, 3]]},
    "operator_norm": {"M": [[3, 0], [0, 4]]},
    "characteristic_poly": {"M": [[2, 0], [0, 3]]},
    "spectral_decomposition": {"M": [[2, 1], [1, 2]]},
    "tensor_product": {"a": [1, 2], "b": [3, 4]},
    "partial_trace": {"M": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "dims": [2, 2], "keep": 0},
    "choi_matrix": {"cp_map_generators": [[[1, 0], [0, 1]]]},
    "is_completely_positive": {"choi": [[1, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 1]]},
    "is_separable_ppt": {"rho": [["1/2", 0, 0, "1/2"], [0, 0, 0, 0], [0, 0, 0, 0], ["1/2", 0, 0, "1/2"]], "dims": [2, 2]},
    # H1 · +ℝ-Open frontier (returns +R_OPEN, never certified)
    "completeness_readout": {"cauchy_seq": ["1", "3/2", "7/5", "17/12"], "N": 3},
    "l2_readout": {"seq": ["1", "1/2", "1/4", "1/8", "1/16"], "N": 5},
    "L2_readout": {"values_on_mesh": [1, 1, 1], "weights": ["1/3", "1/3", "1/3"]},
    "infinite_orthonormal_basis_readout": {"vectors": [[1, 0], [0, 1], [1, 1]], "N": 2},
    "infinite_spectral_readout": {"operator_description": "d/dx on L2"},
}


def test_fixtures_cover_every_kind():
    """the fixture table must contain a valid input for every registered kind (no coverage gap)."""
    missing = sorted(set(idm.kinds()) - set(FIXTURES))
    assert not missing, f"no valid-input fixture for: {missing}"


def test_every_kind_invocable_and_well_formed():
    """each kind, on valid input, returns a well-formed result: a status in the allowed set, a tier in
    the allowed set, and (unless HOLD) a value. The vast majority must actually COMPUTE, not HOLD."""
    holds, computed, opens, bad = [], 0, 0, []
    for k in sorted(idm.kinds()):
        r = idm.solve(dict(kind=k, **FIXTURES[k]))
        if not isinstance(r, dict) or r.get("status") not in _ALLOWED_STATUS:
            bad.append((k, r)); continue
        if r["status"] == "HOLD":
            holds.append(k)
        elif r["status"] == "+R_OPEN":                # a +ℝ-fenced frontier readout: NO value by design
            opens += 1
            assert "value" not in r, f"{k}: +R_OPEN must NOT carry a certified value (the fence)"
            assert r.get("tier") == "+ℝ-Open" and "approximant" in r, f"{k}: malformed +R_OPEN"
        else:
            computed += 1
            assert "value" in r, f"{k}: non-HOLD result without a value"
            assert r.get("tier") in _ALLOWED_TIER, f"{k}: bad tier {r.get('tier')}"
    assert not bad, f"malformed results: {bad}"
    # a valid-input fixture should resolve (compute exactly OR return a fenced frontier readout) for the
    # overwhelming majority of kinds
    assert computed + opens >= int(0.95 * len(idm.kinds())), \
        f"only {computed} computed + {opens} +R_OPEN of {len(idm.kinds())}; HOLDs: {holds}"


def test_tier_honesty_invariant():
    """Th_coqc may be emitted ONLY for kinds with a named theorem mapping, and always with a
    coq_theorem reference; every other computed result is `exact` or `finite_diagnostic`."""
    offenders = []
    for k in sorted(idm.kinds()):
        r = idm.solve(dict(kind=k, **FIXTURES[k]))
        if r.get("tier") == "Th_coqc":
            if k not in _COQ_BACKED or "coq_theorem" not in r:
                offenders.append(k)
    assert not offenders, f"Th_coqc without a proof mapping (tier inflation): {offenders}"


def test_missing_fields_hold_not_crash():
    """every kind called with NO fields must return a dict with an allowed status — never raise."""
    bad = []
    for k in sorted(idm.kinds()):
        try:
            r = idm.solve({"kind": k})
        except Exception as ex:                       # a dispatcher crash is the bug we forbid
            bad.append((k, f"RAISED {type(ex).__name__}: {ex}")); continue
        if not isinstance(r, dict) or r.get("status") not in _ALLOWED_STATUS:
            bad.append((k, r))
    assert not bad, f"missing-field call did not HOLD cleanly: {bad}"


def test_garbage_input_holds_not_crash():
    """garbage field values must never crash the dispatcher (HOLD is the correct refusal)."""
    junk = {"n": "not-a-number", "matrix": "nope", "f": "%%%", "expr": ")(", "points": 42,
            "a": None, "b": {}, "coeffs": "x", "data": None, "p": [1, 2]}
    bad = []
    for k in sorted(idm.kinds()):
        try:
            r = idm.solve(dict(kind=k, **junk))
        except Exception as ex:
            bad.append((k, f"RAISED {type(ex).__name__}: {ex}")); continue
        if not isinstance(r, dict) or r.get("status") not in _ALLOWED_STATUS:
            bad.append((k, r))
    assert not bad, f"garbage input crashed or returned malformed: {bad}"


def test_domain_guards_reject_invalid():
    """out-of-domain parameters across the probability & geometry families must HOLD, not fabricate."""
    invalid = [
        {"kind": "binomial", "n": 10, "k": 3, "p": 2},           # p > 1
        {"kind": "binomial", "n": -1, "k": 0, "p": "1/2"},        # negative n
        {"kind": "geometric", "p": 0},                            # p not in (0,1]
        {"kind": "poisson", "lam": -1, "k": 1},                   # negative rate
        {"kind": "normal", "x": 0, "sigma": 0},                   # σ ≤ 0
        {"kind": "normal", "x": 0, "sigma": -1},
        {"kind": "hypergeometric", "N": 5, "K": 99, "n": 2, "k": 1},  # K > N
        {"kind": "in_circle", "a": [0, 0], "b": [1, 1], "c": [2, 2], "d": [3, 3]},  # collinear
        {"kind": "certified_root", "expr": "1/x", "var": "x", "a": -1, "b": 1},     # pole, not root
        {"kind": "linear_program", "c": [1], "A": [[1], [-1]], "b": [0, -1], "sense": "max"},  # infeasible
    ]
    for prob in invalid:
        r = idm.solve(prob)
        held = r.get("status") == "HOLD" or (isinstance(r.get("value"), dict) and r["value"].get("status") in ("HOLD", "infeasible"))
        assert held, f"{prob['kind']} accepted invalid input: {r}"


# ---------------------- hypothesis: fuzz the exact cores against oracles ----------------------
try:
    from hypothesis import given, strategies as st, settings, HealthCheck
    import sympy
    _HYP = True
except Exception:                                     # pragma: no cover
    _HYP = False

if _HYP:
    _S = settings(max_examples=60, deadline=None, suppress_health_check=[HealthCheck.too_slow])

    @_S
    @given(n=st.integers(min_value=2, max_value=10**12))
    def test_prop_is_prime_matches_sympy(n):
        assert idm.solve({"kind": "is_prime", "n": n})["value"] == bool(sympy.isprime(n))

    @_S
    @given(a=st.integers(min_value=1, max_value=10**9), b=st.integers(min_value=1, max_value=10**9))
    def test_prop_gcd_lcm(a, b):
        g = idm.solve({"kind": "gcd", "a": a, "b": b})["value"]
        l = idm.solve({"kind": "lcm", "a": a, "b": b})["value"]
        assert a % g == 0 and b % g == 0 and g == sympy.gcd(a, b) and g * l == a * b

    @_S
    @given(n=st.integers(min_value=2, max_value=10**10))
    def test_prop_factorize_reconstructs(n):
        f = idm.solve({"kind": "factorize", "n": n})["value"]
        prod = 1
        for p, e in f.items():
            assert sympy.isprime(int(p)); prod *= int(p) ** e
        assert prod == n

    @_S
    @given(r=st.integers(min_value=2, max_value=10**6), k=st.integers(min_value=2, max_value=8))
    def test_prop_integer_root_roundtrip(r, k):
        n = r ** k
        assert idm.solve({"kind": "integer_root", "n": n, "k": k})["value"] == r
        if r > 2:                                     # n between consecutive k-th powers has no integer root
            assert idm.solve({"kind": "integer_root", "n": n + 1, "k": k})["value"] is None

    @_S
    @given(ax=st.integers(-50, 50), ay=st.integers(-50, 50), bx=st.integers(-50, 50),
           by=st.integers(-50, 50), cx=st.integers(-50, 50), cy=st.integers(-50, 50))
    def test_prop_orient_antisymmetric(ax, ay, bx, by, cx, cy):
        f = lambda A, B, C: idm.solve({"kind": "orient", "a": A, "b": B, "c": C})["value"]["orientation"]
        assert f([ax, ay], [bx, by], [cx, cy]) == -f([ax, ay], [cx, cy], [bx, by])

    @_S
    @given(roots=st.lists(st.integers(-6, 6), min_size=1, max_size=4, unique=True))
    def test_prop_rational_roots_are_roots(roots):
        from idm.exact import poly_from_roots, poly_eval
        coeffs = poly_from_roots(roots)               # low-order-first exact coefficients
        found = idm.solve({"kind": "rational_roots", "coeffs": [int(c) for c in coeffs]})["value"]
        got = {int(v["float"]) for v in found}
        assert set(roots) <= got                      # every actual integer root must be reported
        from fractions import Fraction
        for v in found:                               # and every reported root is genuine
            num, den = v["exact"].split("/")
            assert poly_eval([Fraction(int(c)) for c in coeffs], Fraction(int(num), int(den))) == 0
