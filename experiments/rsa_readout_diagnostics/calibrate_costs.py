"""Calibrate the REAL wall-clock cost of one division-op vs one modpow-squaring
(the two operation types collapsed into a naive '1 unit each' scalar sum in the
prior smoke tests -- flagged as an invalid comparison by the project reviewer).
Classical measurement technique, no novelty claimed. Reports a weight ratio to
use instead of treating #div and #cert as commensurable units.
"""
import timeit

# realistic operand sizes matching the smoke tests: N ~ 34-40 bits, factor-base
# primes < 300 (division operand), MR modpow on cofactors up to ~40 bits with
# exponent ~ up to 40 bits.
N = 9998000099
cofactor_example = 99990001  # ~27 bits, representative "large residual" case
prime_example = 293

def one_division():
    return cofactor_example % prime_example

def one_modpow_round():
    return pow(2, (cofactor_example - 1) // 2, cofactor_example)

REPS = 200_000
t_div = timeit.timeit(one_division, number=REPS)
t_mr = timeit.timeit(one_modpow_round, number=REPS)

w_div = t_div / REPS
w_mr = t_mr / REPS
ratio = w_mr / w_div

print(f"measured wall time per division op:  {w_div*1e9:.1f} ns  (n={REPS})")
print(f"measured wall time per modpow round:  {w_mr*1e9:.1f} ns  (n={REPS})")
print(f"CALIBRATED WEIGHT RATIO (1 modpow round costs this many division-op-units): {ratio:.2f}")
