# number theory
from idm._solve_core import *  # noqa: F401,F403

@kind("gcd", "Th_coqc")
def _gcd(p): return _ok("gcd", __import__("math").gcd(int(p["a"]), int(p["b"])), "Euclid")
@kind("lcm", "Th_coqc")
def _lcm(p): return _ok("lcm", X.lcm(int(p["a"]), int(p["b"])), "a·b/gcd")
@kind("factorial", "Th_coqc")
def _fac(p): return _ok("factorial", X.factorial(int(p["n"])), "finite product")
@kind("binomial", "Th_coqc")
def _bin(p): return _ok("binomial", X.binomial(int(p["n"]), int(p["k"])), "finite product")
@kind("is_prime", "Th_coqc")
def _isp(p):
    n = int(p["n"]); val = X.is_prime(n)
    # a composite verdict is a proof (there is a witness); a prime verdict is a proof only below the
    # deterministic Miller–Rabin bound — above it, "prime" is probabilistic, so tier down honestly.
    certified = (val is False) or (n < X.MR_DET_BOUND)
    tier = "Th_coqc" if certified else "finite_diagnostic"
    method = ("deterministic Miller–Rabin (first 13 primes, n < %d)" % X.MR_DET_BOUND) if certified else \
             "Miller–Rabin strong probable prime (n ≥ %d — beyond the deterministic bound, NOT proven)" % X.MR_DET_BOUND
    return {"kind": "is_prime", "status": "ok", "value": val, "tier": tier, "method": method}
@kind("factorize", "Th_coqc")
def _fz(p): return _ok("factorize", {str(k): v for k, v in X.factorize(int(p["n"])).items()}, "trial division + Pollard ρ")
@kind("divisors", "Th_coqc")
def _dv(p): return _ok("divisors", X.divisors(int(p["n"])), "from factorization")
@kind("totient", "Th_coqc")
def _tot(p): return _ok("totient", X.totient(int(p["n"])), "Euler φ from factorization")
@kind("primes", "Th_coqc")
def _pr(p): return _ok("primes", X.primes_up_to(int(p["N"])), "sieve of Eratosthenes")
@kind("modpow", "Th_coqc")
def _mp(p): return _ok("modpow", pow(int(p["base"]), int(p["exp"]), int(p["mod"])), "square-and-multiply")
@kind("mod_inverse", "Th_coqc")
def _mi(p): return _ok("mod_inverse", X.mod_inverse(int(p["a"]), int(p["m"])), "extended Euclid")
@kind("crt", "Th_coqc")
def _crt(p): return _ok("crt", X.crt([int(r) for r in p["residues"]], [int(m) for m in p["moduli"]]), "Chinese remainder")
@kind("fibonacci", "Th_coqc")
def _fib(p): return _ok("fibonacci", X.fibonacci(int(p["n"])), "fast doubling")
@kind("bernoulli", "Th_coqc")
def _ber(p): return _ok("bernoulli", X.bernoulli(int(p["n"])), "finite recurrence ΣC(m+1,k)B_k=0")
@kind("partition", "Th_coqc")
def _par(p): return _ok("partition", X.partition(int(p["n"])), "Euler pentagonal recurrence")
@kind("catalan", "Th_coqc")
def _cat(p): return _ok("catalan", X.catalan(int(p["n"])), "C(2n,n)/(n+1)")
@kind("stirling2", "Th_coqc")
def _st(p): return _ok("stirling2", X.stirling2(int(p["n"]), int(p["k"])), "recurrence")
@kind("bell", "Th_coqc")
def _bel(p): return _ok("bell", X.bell(int(p["n"])), "Σ Stirling2")
@kind("continued_fraction", "Th_coqc")
def _cf(p): return _ok("continued_fraction", X.continued_fraction(int(p["num"]), int(p.get("den", 1)), int(p.get("terms", 20))), "Euclidean CF expansion")
