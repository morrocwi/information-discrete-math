# P1 — number theory (advanced)
from idm._solve_core import *  # noqa: F401,F403

@kind("diophantine_linear", "Th_coqc")
def _dio(p):
    r = X.diophantine_linear(int(p["a"]), int(p["b"]), int(p["c"]))
    return {"kind": "diophantine_linear", "status": "ok" if r else "HOLD", "tier": "Th_coqc",
            "value": {"x0": r[0], "y0": r[1], "dx": r[2], "dy": r[3]} if r else None, "method": "extended Euclid",
            **({} if r else {"reason": "no integer solution (gcd(a,b) ∤ c)"})}
@kind("pell", "Th_coqc")
def _pell(p):
    r = X.pell(int(p["D"])); return {"kind": "pell", "status": "ok" if r else "HOLD", "tier": "Th_coqc",
        "value": {"x": r[0], "y": r[1]} if r else None, "method": "continued fraction of √D",
        **({} if r else {"reason": "D is a perfect square — no nontrivial solution"})}
@kind("modular_sqrt", "Th_coqc")
def _msqrt(p):
    r = X.tonelli_shanks(int(p["a"]), int(p["p"])); return {"kind": "modular_sqrt", "status": "ok" if r is not None else "HOLD",
        "tier": "Th_coqc", "value": r, "method": "Tonelli–Shanks", **({} if r is not None else {"reason": "a is a quadratic non-residue mod p"})}
@kind("mobius", "Th_coqc")
def _mob(p): return _ok("mobius", X.mobius(int(p["n"])), "μ(n) from factorization")
@kind("mertens", "Th_coqc")
def _mert(p): return _ok("mertens", X.mertens(int(p["N"])), "Σ μ(k)")
@kind("liouville", "Th_coqc")
def _liou(p): return _ok("liouville", X.liouville(int(p["n"])), "λ(n)=(−1)^Ω(n)")
@kind("von_mangoldt")
def _vm(p): return _ok("von_mangoldt", X.von_mangoldt(int(p["n"])), "Λ(n)=ln p if n=p^k else 0")
