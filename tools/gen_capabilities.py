#!/usr/bin/env python3
"""Generate capabilities.json from the live idm.solve registry.

Deterministic, re-runnable: run it twice in a row and the output file is
byte-identical (this is asserted by tests/test_capabilities_manifest.py).

Usage:
    python tools/gen_capabilities.py            # writes ./capabilities.json
    python tools/gen_capabilities.py --check     # exit 1 if the file would change
    python tools/gen_capabilities.py --out PATH  # write elsewhere (for scratch runs)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make `import idm` work no matter how this script is invoked (as
# `python tools/gen_capabilities.py`, via an absolute path, or from a
# different cwd) — mirrors what running it from the repo root would give.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_registry():
    """Return {kind_name: tier} straight from the live idm.solve registry.

    idm/__init__.py rebinds the package attribute `idm.solve` to the
    *function* `_solve.solve`, so the submodule object (which still holds
    the private `_REG` dict populated by the `@kind(...)` decorator) has to
    be fetched from sys.modules rather than via attribute access.
    """
    import idm  # noqa: F401  (import for side effect: populates sys.modules)

    solve_module = sys.modules["idm.solve"]
    reg = solve_module._REG  # {name: (fn, tier)}
    return {name: tier for name, (_fn, tier) in reg.items()}


def _read_pyproject_version(pyproject_path: Path) -> str:
    text = pyproject_path.read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    if not m:
        raise RuntimeError(f"could not find version = \"...\" in {pyproject_path}")
    return m.group(1)


# ---------------------------------------------------------------------------
# Curated DOMAIN classification, by kind name.
#
# Every kind in the live registry (266 at time of writing) is looked up
# against these sets, first match wins in the order below. Anything not
# claimed by an earlier domain falls into 'other'. This keeps the mapping
# total and exhaustive by construction — nothing can be silently dropped.
# ---------------------------------------------------------------------------

DOMAIN_ORDER = [
    "hilbert",
    "spectral",
    "certified",
    "pde",
    "linear_algebra",
    "geometry",
    "logic",
    "number_theory",
    "exact_algebra",
    "calculus",
    "other",
]

DOMAIN_MEMBERS: dict[str, set[str]] = {
    # Functional analysis / operator / Hilbert-space and quantum-operator
    # readouts (idm.hilbert, idm.hilbert_open).
    "hilbert": {
        "L2_readout", "l2_readout", "completeness_readout",
        "infinite_orthonormal_basis_readout", "infinite_spectral_readout",
        "orthonormal_basis", "gram_schmidt", "gram_matrix", "sturm_liouville",
        "adjoint", "is_self_adjoint", "is_normal", "is_unitary",
        "is_idempotent", "is_orthogonal", "operator_norm", "projection_matrix",
        "project", "inner_product", "norm_squared",
        "choi_matrix", "is_completely_positive", "is_separable_ppt",
        "partial_trace", "tensor_product",
    },
    # Eigenvalue / spectrum readouts (retained_spectral surface).
    "spectral": {
        "eigenvalues", "gershgorin", "gershgorin_bound",
        "char_poly", "characteristic_poly", "spectral_decomposition",
    },
    # Rigorously-bounded / interval-certified readouts (idm.certified).
    "certified": {
        "certified_limit", "certified_min", "certified_root",
        "verified_range", "interval_enclose", "cauchy_schwarz_check",
        "polynomial_positivity", "rational_limit",
    },
    # Partial and ordinary differential equations.
    "pde": {
        "pde_heat", "pde_laplace", "pde_poisson", "pde_wave",
        "ode", "ode_bvp", "ode_system", "linear_ode",
    },
    # Finite-dimensional linear algebra (matrices, vector spaces over Q/R).
    "linear_algebra": {
        "matrix_add", "matrix_determinant", "matrix_exp", "matrix_inverse",
        "matrix_multiply", "matrix_power", "matrix_rank", "matrix_solve",
        "matrix_trace", "matrix_transpose", "null_space", "rref",
        "smith_normal_form", "hermite_normal_form", "solve_linear",
        "least_squares", "vector_norm",
    },
    # Euclidean / computational geometry.
    "geometry": {
        "distance", "cross", "dot", "triangle_area", "polygon_area",
        "point_in_polygon", "in_circle", "orient", "convex_hull",
        "closest_pair", "segments_intersect",
    },
    # Discrete logic / boolean structures / set theory.
    "logic": {
        "sat", "truth_table", "set_operation", "assignment",
    },
    # Number theory / arithmetic / combinatorics / cryptography.
    "number_theory": {
        "gcd", "lcm", "factorial", "binomial", "is_prime", "factorize",
        "divisors", "totient", "primes", "modpow", "mod_inverse", "modinv",
        "crt", "fibonacci", "bernoulli", "bell", "catalan", "lucas",
        "stirling2", "partition", "derangements", "multinomial",
        "comb_with_rep", "perm_count", "powerset", "digital_root",
        "integer_sqrt", "is_perfect_square", "jacobi_symbol",
        "legendre_symbol", "mobius", "mertens", "von_mangoldt", "sigma",
        "num_divisors", "prime_pi", "primitive_root", "primality_certificate",
        "next_prime", "discrete_log", "modular_sqrt", "pell",
        "diophantine_linear", "base_convert", "ec_add", "ec_mul",
        "rsa_encrypt", "rsa_decrypt", "rsa_keygen", "liouville",
    },
    # Exact symbolic algebra (polynomials, algebraic manipulation).
    "exact_algebra": {
        "expand", "simplify", "symbolic_diff", "symbolic_integrate",
        "symbolic_series", "symbolic_solve",
        "poly_add", "poly_derivative", "poly_divmod", "poly_eval",
        "poly_from_roots", "poly_gcd", "poly_integral", "poly_mul",
        "poly_roots", "rational_roots", "integer_root", "groebner_basis",
        "continued_fraction", "pade", "bezout",
        "real_root", "algebraic_arith", "all_real_roots",
    },
    # Analysis: integration, series, transforms, root/optimum finding,
    # special functions.
    "calculus": {
        "integral", "improper_integral", "singular_integral",
        "oscillatory_integral", "gauss_quadrature", "residue_integral",
        "multidim_integral", "double_integral", "contour_integral",
        "derivative", "limit", "limit_infinity", "limit_oneside", "lhopital",
        "taylor_series", "laurent_series",
        "fourier_series", "fourier_transform", "laplace_transform",
        "inverse_laplace", "mellin_transform", "z_transform", "fft", "ifft",
        "series_sum", "series_accelerate", "regularized_sum", "summation",
        "convergence_test", "arc_length", "convolution",
        "gradient", "gradient_descent", "newton_min", "newton_system",
        "minimize", "root_find", "fixed_point", "lagrange_min",
        "faulhaber", "geometric_series", "geometric", "interpolate",
        "argument_principle", "exp",
        # special functions
        "Ci", "E1", "Ei", "Si", "airy_Ai", "bessel_I", "bessel_J", "beta",
        "chebyshev_T", "chebyshev_U", "digamma", "dirichlet_beta",
        "dirichlet_eta", "elliptic_E", "elliptic_K", "erf", "erfc",
        "fresnel_C", "fresnel_S", "gamma", "hermite_H", "hurwitz_zeta",
        "hyp1f1", "hyp2f1", "hypergeometric", "laguerre_L", "lambert_W",
        "legendre_P", "li", "polylog", "zeta",
    },
    # 'other' is populated by whatever no earlier domain claims (see below):
    # generic evaluation utilities, statistics/probability, graph
    # algorithms, and combinatorial-optimization DP.
    "other": set(),
}


def build_domains(kind_names: list[str]) -> dict[str, list[str]]:
    """Classify every kind name into exactly one domain, in DOMAIN_ORDER."""
    remaining = set(kind_names)
    domains: dict[str, list[str]] = {d: [] for d in DOMAIN_ORDER}
    for domain in DOMAIN_ORDER[:-1]:  # everything except 'other'
        members = DOMAIN_MEMBERS[domain] & remaining
        domains[domain] = sorted(members)
        remaining -= members
    # whatever nothing claimed goes to 'other'
    domains["other"] = sorted(remaining)
    return domains


def generate(repo_root: Path = REPO_ROOT) -> dict:
    kind_tiers = _load_registry()
    kind_names = sorted(kind_tiers.keys())

    version = _read_pyproject_version(repo_root / "pyproject.toml")
    domains_raw = build_domains(kind_names)

    domains = {
        domain: {"kinds": kinds, "count": len(kinds)}
        for domain, kinds in domains_raw.items()
    }

    manifest = {
        "project": {
            "name": "information-discrete-math",
            "version": version,
            "primary_api": "idm.solve",
            "total_problem_kinds": len(kind_names),
        },
        "interfaces": {
            "python": "idm.solve",
            "rest": "idm.server",
            "cli": "idm-serve",
        },
        "domains": domains,
        "verification": {
            "unit_tests": "pytest -q",
            "formal_proofs": "bash formal/verify.sh",
            "full_battery": "python prove_it_full.py",
        },
    }
    return manifest


def render(manifest: dict) -> str:
    # sort_keys=False: key order above is the intentional, readable order.
    # A trailing newline keeps the file POSIX-friendly and diff-stable.
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out", type=Path, default=REPO_ROOT / "capabilities.json",
        help="output path (default: <repo-root>/capabilities.json)",
    )
    ap.add_argument(
        "--check", action="store_true",
        help="don't write; exit 1 if regenerating would change the file",
    )
    args = ap.parse_args(argv)

    manifest = generate()
    text = render(manifest)

    if args.check:
        existing = args.out.read_text(encoding="utf-8") if args.out.exists() else None
        if existing != text:
            sys.stderr.write(f"capabilities.json is stale: {args.out}\n")
            return 1
        return 0

    args.out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
