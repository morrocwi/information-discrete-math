"""Exact finite checker for a standard parity -> CNF-SAT reduction.

Purpose: establish a nontrivial restricted-model baseline for the readout lane.
The script checks the reduction exhaustively for small n.  The asymptotic
AC0 lower-bound conclusion relies on the classical PARITY not-in-AC0 theorem;
this file itself is only a finite diagnostic.
"""

from itertools import product


def parity_to_2cnf(bits):
    """Return a 2-CNF satisfiable iff XOR(bits)=1.

    Auxiliary variables y_0,...,y_n are numbered 1,...,n+1.
      y_0 = 0
      y_i = y_{i-1} xor bits[i-1]
      y_n = 1

    Each input bit selects one of two constant-size local clause patterns.
    """
    n = len(bits)
    clauses = [(-1,)]  # y_0 = false

    for i, bit in enumerate(bits, start=1):
        prev_y = i
        next_y = i + 1
        if bit == 0:  # next_y <-> prev_y
            clauses.append((-prev_y, next_y))
            clauses.append((prev_y, -next_y))
        else:  # next_y <-> not prev_y
            clauses.append((prev_y, next_y))
            clauses.append((-prev_y, -next_y))

    clauses.append((n + 1,))  # y_n = true
    return tuple(clauses), n + 1


def brute_sat(clauses, n_vars):
    for assignment in product((False, True), repeat=n_vars):
        if all(
            any(
                assignment[abs(lit) - 1] if lit > 0 else not assignment[abs(lit) - 1]
                for lit in clause
            )
            for clause in clauses
        ):
            return True
    return False


def verify(max_n=7):
    checked = 0
    for n in range(1, max_n + 1):
        for bits in product((0, 1), repeat=n):
            formula, n_vars = parity_to_2cnf(bits)
            observed = brute_sat(formula, n_vars)
            expected = (sum(bits) % 2) == 1
            assert observed == expected, (bits, observed, expected)
            checked += 1
    return checked


if __name__ == "__main__":
    total = verify()
    print(f"[finite_diagnostic] PASS: {total} parity inputs checked exactly")
    print("Structural reduction: each input bit selects a constant-size local CNF gadget.")
    print("External theorem needed for asymptotic conclusion: PARITY is not in AC0.")
    print("Therefore this is a baseline restricted lower bound, NOT P != NP.")
