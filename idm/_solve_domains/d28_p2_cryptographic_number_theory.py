# P2 · cryptographic number theory (exact, certificate-bearing)
from idm._solve_core import *  # noqa: F401,F403

@kind("primality_certificate", "Th_coqc")
def _pcert(p):
    v = CY.is_prime(p["n"])
    # certified compositeness/primality → Th_coqc; a probable prime above the bound → finite_diagnostic
    tier = "Th_coqc" if v.get("certified") else "finite_diagnostic"
    return {"kind": "primality_certificate", "status": "ok", "value": _norm(v), "tier": tier,
            "method": "Miller–Rabin (first 13 primes) with a checkable witness; deterministic below "
                      "%d, probable above" % CY.MR_DET_BOUND}
@kind("modinv")
def _minv(p):
    r = CY.modinv(int(p["a"]), int(p["m"]))
    return {"kind": "modinv", "status": r.get("status", "ok"), "value": _norm(r), "method": "extended Euclidean inverse"}
@kind("rsa_keygen")
def _rkg(p):
    r = CY.rsa_keygen(p["p"], p["q"], p.get("e", 65537))
    return {"kind": "rsa_keygen", "status": r.get("status", "ok"), "value": _norm(r), "method": "exact RSA keypair"}
@kind("rsa_encrypt")
def _renc(p): return _ok("rsa_encrypt", CY.rsa_encrypt(p["m"], p["e"], p["n"]), "exact modular exponentiation")
@kind("rsa_decrypt")
def _rdec(p): return _ok("rsa_decrypt", CY.rsa_decrypt(p["c"], p["d"], p["n"]), "exact modular exponentiation")
@kind("ec_add", "Th_coqc")
def _ecadd(p): return _ok("ec_add", CY.ec_add(p["P"], p["Q"], p["a"], p["p"]), "exact elliptic-curve point addition over F_p")
@kind("ec_mul", "Th_coqc")
def _ecmul(p): return _ok("ec_mul", CY.ec_mul(p["k"], p["P"], p["a"], p["p"]), "exact EC scalar multiply (double-and-add) over F_p")
