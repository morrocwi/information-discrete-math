"""Barrier-aware finite experiments for the P-vs-NP readout research lane.

This file deliberately proves/diagnoses only finite statements.  It does NOT
claim P != NP.  Its job is to prevent two invalid shortcuts:

1. a coarse finite readout can merge SAT and UNSAT instances;
2. a one-bit exact readout always exists if it is allowed to call SAT itself,
   so readout cardinality alone cannot yield a P-vs-NP lower bound.

Run:
    python research/p_vs_np_readout/readout_sat_frontier.py
"""

from itertools import product


SAT_BASE = (
    (-1, -3, -4),
    (-1, -3, 4),
    (-1, -2, -4),
    (-1, 3, 4),
    (1, -2, -3),
    (1, 2, 3),
    (1, 2, 4),
    (1, 3, -4),
)

UNSAT_BASE = (
    (-1, -2, -3),
    (-1, -2, 3),
    (1, -2, -4),
    (1, -2, 4),
    (2, -3, -4),
    (2, -3, 4),
    (2, 3, -4),
    (2, 3, 4),
)


def satisfies(clauses, bits):
    """Exact Boolean evaluation of a CNF under a complete assignment."""
    for clause in clauses:
        if not any(
            bits[abs(lit) - 1] if lit > 0 else not bits[abs(lit) - 1]
            for lit in clause
        ):
            return False
    return True


def brute_sat(clauses, n_vars):
    """Finite exact SAT oracle used only as a checker for small fixtures."""
    for bits in product((False, True), repeat=n_vars):
        if satisfies(clauses, bits):
            return True, bits
    return False, None


def profile_readout(clauses, n_vars):
    """A deliberately coarse, answer-oblivious syntactic readout.

    It retains:
      * variable count,
      * clause count,
      * multiset of clause lengths,
      * multiset of per-variable (positive, negative) occurrence counts.

    It forgets how those occurrences are wired together across clauses.
    """
    pos = [0] * n_vars
    neg = [0] * n_vars
    for clause in clauses:
        for lit in clause:
            if lit > 0:
                pos[lit - 1] += 1
            else:
                neg[-lit - 1] += 1
    return (
        n_vars,
        len(clauses),
        tuple(sorted(map(len, clauses))),
        tuple(sorted(zip(pos, neg))),
    )


def rename_copy(clauses, copy_index, block_size=4):
    """Rename a base formula into a disjoint variable block."""
    offset = copy_index * block_size
    return tuple(
        tuple((abs(lit) + offset) if lit > 0 else -(abs(lit) + offset) for lit in clause)
        for clause in clauses
    )


def disjoint_copies(clauses, k, block_size=4):
    out = []
    for i in range(k):
        out.extend(rename_copy(clauses, i, block_size))
    return tuple(out)


def verify_base_collision():
    sat_a, witness = brute_sat(SAT_BASE, 4)
    sat_b, _ = brute_sat(UNSAT_BASE, 4)
    sig_a = profile_readout(SAT_BASE, 4)
    sig_b = profile_readout(UNSAT_BASE, 4)

    assert sat_a is True
    assert sat_b is False
    assert sig_a == sig_b

    return {
        "status": "PASS",
        "claim": "profile readout has a mixed SAT/UNSAT fiber",
        "sat_witness": witness,
        "shared_readout": sig_a,
    }


def verify_collision_amplification(max_k=8):
    """Check the structural signature collision after disjoint-copy amplification.

    SAT status for arbitrary k follows mathematically from conjunction of disjoint
    copies: k copies of SAT_BASE are satisfiable; any conjunction containing an
    UNSAT_BASE copy is unsatisfiable.  We only need to recompute the finite readout
    here, which is cheap for all displayed k.
    """
    rows = []
    for k in range(1, max_k + 1):
        a = disjoint_copies(SAT_BASE, k)
        b = disjoint_copies(UNSAT_BASE, k)
        sig_a = profile_readout(a, 4 * k)
        sig_b = profile_readout(b, 4 * k)
        assert sig_a == sig_b
        rows.append(
            {
                "k": k,
                "n_vars": 4 * k,
                "n_clauses": 8 * k,
                "same_readout": True,
                "SAT_family_label": True,
                "UNSAT_family_label": False,
            }
        )
    return rows


def answer_bit_readout(clauses, n_vars):
    """The forbidden shortcut: q(F)=SAT(F).

    It is one bit and perfectly sufficient, but computing q is exactly the target
    decision problem.  This demonstrates why representation size/cardinality alone
    cannot separate P from NP.
    """
    return brute_sat(clauses, n_vars)[0]


def verify_answer_leakage_demo():
    qa = answer_bit_readout(SAT_BASE, 4)
    qb = answer_bit_readout(UNSAT_BASE, 4)
    assert qa is True and qb is False
    return {
        "status": "PASS",
        "readout_bits": 1,
        "warning": "TARGET_LEAKAGE: constructing this readout calls SAT itself",
    }


def main():
    print("[finite_diagnostic] base collision")
    print(verify_base_collision())
    print()

    print("[finite_diagnostic] collision amplification")
    for row in verify_collision_amplification():
        print(row)
    print()

    print("[structural negative control] one-bit answer leakage")
    print(verify_answer_leakage_demo())
    print()

    print("VERDICT: coarse readout insufficiency is real, but readout-size lower bounds alone")
    print("cannot prove P != NP.  The next load-bearing object must be a lower bound on")
    print("the computational cost of constructing an exact decision-sufficient readout.")


if __name__ == "__main__":
    main()
