#!/usr/bin/env python3
"""eng_readouts.py — a domain-spanning library of FINITE mathematical readouts.

Every function here is a pure mathematical operation on finite data — a formula, a finite transform, a
ratio. None of it is a physical claim: these are the *mathematics* that many domains happen to use
(spectral, response, spec/limits, relational, information, capacity), stated domain-neutrally. Whether a
readout is "for" signals, control, quality, or structures is not this module's concern and no domain is
privileged — it is all finite arithmetic.

On-philosophy: the transcendental helpers (exp, ln, sin, cos, π) are computed here as FINITE series
(the same finite readouts proven elsewhere in this repo), so no continuum library call ever produces a
value. `sqrt` is an algebraic finite operation. Run `python3 tools/eng_readouts.py` for the self-check.
"""
from fractions import Fraction as Q
import math   # reference column in the self-check ONLY

# ------------------------------------------------------------ finite primitives (no continuum call) --
def _exp(x, N=200):
    t = 1.0; s = 1.0
    for k in range(1, N + 1): t = t * x / k; s += t
    return s
def _atan(x, N=800):
    s = 0.0; p = x; x2 = x * x
    for k in range(N): s += ((-1) ** k) * p / (2 * k + 1); p *= x2
    return s
_PI = 16 * _atan(1 / 5) - 4 * _atan(1 / 239)
_TWO_PI = 2 * _PI
def _atanh(y, N=80):
    y2 = y * y; term = y; s = y
    for n in range(1, N): term *= y2; s += term / (2 * n + 1)
    return s
_LN2 = 2 * _atanh(1 / 3)                  # ln 2 as a finite series (full precision)
def _ln(x):                              # ln via 2·atanh((x-1)/(x+1)) with power-of-two mantissa reduction
    if x <= 0: raise ValueError("ln domain x>0")
    k = 0
    while x > 1.5: x /= 2; k += 1
    while x < 0.66: x *= 2; k -= 1
    y = (x - 1) / (x + 1); y2 = y * y; term = y; s = y; n = 1
    while abs(term) > 1e-18 and n < 400: term *= y2; s += term / (2 * n + 1); n += 1
    return 2 * s + k * _LN2
_LN10 = _ln(10)
def _log10(x): return _ln(x) / _LN10
def _cos(x):
    x = x - _TWO_PI * math.floor(x / _TWO_PI + 0.5)
    t = 1.0; s = 1.0; x2 = x * x; n = 1
    while abs(t) > 1e-18 and n < 100: t = -t * x2 / ((2 * n - 1) * (2 * n)); s += t; n += 1
    return s
def _sin(x):
    x = x - _TWO_PI * math.floor(x / _TWO_PI + 0.5)
    t = x; s = x; x2 = x * x; n = 1
    while abs(t) > 1e-18 and n < 100: t = -t * x2 / ((2 * n) * (2 * n + 1)); s += t; n += 1
    return s
_sqrt = math.sqrt                        # algebraic finite operation (allowed)

# ============================================================ discrete transforms ==================
def dft(xs):
    """discrete Fourier transform — a FINITE linear map; twiddles are finite readouts of cos/sin.
    Returns N complex bins as (re, im) pairs."""
    N = len(xs); out = []
    for k in range(N):
        re = im = 0.0
        for n in range(N):
            ang = -_TWO_PI * k * n / N
            re += xs[n] * _cos(ang); im += xs[n] * _sin(ang)
        out.append((re, im))
    return out
def magnitude_spectrum(xs): return [_sqrt(re * re + im * im) for re, im in dft(xs)]
def power_spectrum(xs):     return [(re * re + im * im) for re, im in dft(xs)]
def dominant_bin(xs):
    mags = magnitude_spectrum(xs)[1:len(xs) // 2 + 1]      # skip DC, up to Nyquist
    return 1 + max(range(len(mags)), key=lambda i: mags[i])
def thd(xs, fundamental_bin=1, n_harm=5):
    """total harmonic distortion = √(Σ harmonic powers)/fundamental amplitude (a pure ratio)."""
    mag = magnitude_spectrum(xs)
    f = mag[fundamental_bin]
    harm = sum(mag[fundamental_bin * h] ** 2 for h in range(2, n_harm + 1) if fundamental_bin * h < len(mag))
    return _sqrt(harm) / f if f else float("nan")
def autocorrelation(xs, lag):
    n = len(xs); return sum(xs[i] * xs[i + lag] for i in range(n - lag))
def cross_correlation(xs, ys, lag):
    n = min(len(xs), len(ys)); return sum(xs[i] * ys[i + lag] for i in range(n - lag))

# ============================================================ decibel ratios =======================
def db_power(ratio):      return 10 * _log10(ratio)        # power ratio → dB
def db_amplitude(ratio):  return 20 * _log10(ratio)        # amplitude ratio → dB
def snr_db(signal_power, noise_power):
    return 10 * _log10(signal_power / noise_power) if noise_power else float("inf")

# ============================================================ response-series readouts =============
def overshoot(series, final=None):
    """percent overshoot of a response relative to its final value: (peak − final)/final · 100."""
    f = series[-1] if final is None else final
    return (max(series) - f) / f * 100 if f else float("nan")
def peak_index(series):   return max(range(len(series)), key=lambda i: series[i])
def rise_indices(series, lo=0.1, hi=0.9, final=None):
    """(first index reaching lo·final, first reaching hi·final) — rise measured in discrete samples."""
    f = series[-1] if final is None else final
    i_lo = next((i for i, v in enumerate(series) if v >= lo * f), None)
    i_hi = next((i for i, v in enumerate(series) if v >= hi * f), None)
    return (i_lo, i_hi)
def settling_index(series, tol=0.02, final=None):
    """last sample index that is still OUTSIDE the ±tol band around final (settling in samples)."""
    f = series[-1] if final is None else final
    last = None
    for i, v in enumerate(series):
        if abs(v - f) > tol * abs(f): last = i
    return last
def steady_state_error(series, target): return target - series[-1]

# ============================================================ spec / limit readouts ================
def cp(data, lsl, usl, sigma=None):
    """process capability Cp = (USL − LSL)/(6σ) — arithmetic on the spec width and spread."""
    s = sigma if sigma is not None else _std(data)
    return (usl - lsl) / (6 * s) if s else float("inf")
def cpk(data, lsl, usl, sigma=None):
    m = float(_mean(data)); s = sigma if sigma is not None else _std(data)
    return min(usl - m, m - lsl) / (3 * s) if s else float("inf")
def in_spec_fraction(data, lsl, usl):
    return Q(sum(1 for x in data if lsl <= x <= usl), len(data))     # yield (exact ℚ)
def z_score(x, data):                    return (x - float(_mean(data))) / _std(data)
def standardize(data):                   m = float(_mean(data)); s = _std(data); return [(x - m) / s for x in data]
def histogram(data, bins):
    lo, hi = min(data), max(data); w = (hi - lo) / bins if hi > lo else 1
    counts = [0] * bins
    for x in data:
        b = min(bins - 1, int((x - lo) / w)); counts[b] += 1
    return counts

# ============================================================ relational / regression ==============
def covariance(xs, ys):
    mx, my = _mean(xs), _mean(ys)
    return sum((Q(x) - mx) * (Q(y) - my) for x, y in zip(xs, ys)) / len(xs)     # population (exact ℚ)
def correlation(xs, ys):
    c = float(covariance(xs, ys)); return c / (_std(xs) * _std(ys)) if _std(xs) and _std(ys) else float("nan")
def linear_regression(xs, ys):
    """least-squares slope & intercept, EXACT ℚ via the normal equations (no float)."""
    n = len(xs); Sx = sum(_q(xs), Q(0)); Sy = sum(_q(ys), Q(0))
    Sxx = sum(Q(x) * Q(x) for x in xs); Sxy = sum(Q(x) * Q(y) for x, y in zip(xs, ys))
    slope = (n * Sxy - Sx * Sy) / (n * Sxx - Sx * Sx)
    intercept = (Sy - slope * Sx) / n
    return slope, intercept
def r_squared(xs, ys):
    slope, b = linear_regression(xs, ys); my = _mean(ys)
    ss_res = sum((Q(y) - (slope * Q(x) + b)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((Q(y) - my) ** 2 for y in ys)
    return float(1 - ss_res / ss_tot) if ss_tot else float("nan")

# ============================================================ information ===========================
def shannon_entropy(probs, base=2):
    lg = _ln
    div = _ln(base)
    return -sum(float(p) * (lg(float(p)) / div) for p in probs if float(p) > 0)     # Σ −p·log_base p

# ============================================================ capacity / margin =====================
def safety_factor(capacity, demand): return capacity / demand if demand else float("inf")
def utilization(demand, capacity):   return demand / capacity if capacity else float("inf")
def margin(capacity, demand):        return capacity - demand

# ------------------------------------------------------------ small shared helpers -------------------
def _q(xs): return [Q(x) for x in xs]
def _mean(xs): return sum(_q(xs), Q(0)) / len(xs)
def _std(xs):
    m = _mean(xs); return _sqrt(float(sum((Q(x) - m) ** 2 for x in xs) / len(xs)))

# ============================================================ self-check ===========================
if __name__ == "__main__":
    ok = []
    # transforms: a pure cosine at bin 2 should peak at bin 2
    N = 16; sig = [math.cos(2 * math.pi * 2 * n / N) for n in range(N)]
    ok.append(("dominant_bin of a bin-2 cosine == 2", dominant_bin(sig) == 2))
    ok.append(("dft ≈ reference dft (bin 2 magnitude)",
               abs(magnitude_spectrum(sig)[2] - N / 2) < 1e-6))
    # decibels
    ok.append(("db_power(1000) == 30", abs(db_power(1000) - 30) < 1e-9))
    ok.append(("db_amplitude(10) == 20", abs(db_amplitude(10) - 20) < 1e-9))
    ok.append(("snr_db(100,1) == 20", abs(snr_db(100, 1) - 20) < 1e-9))
    # response metrics on a synthetic step response overshooting to 1.2 then settling to 1.0
    resp = [0, 0.5, 1.2, 1.05, 0.98, 1.01, 1.0, 1.0]
    ok.append(("overshoot ≈ 20%", abs(overshoot(resp, 1.0) - 20) < 1e-9))
    ok.append(("peak_index == 2", peak_index(resp) == 2))
    # spec / capability
    data = [9.8, 10.1, 10.0, 9.9, 10.2, 9.7, 10.0, 10.1, 9.9, 10.0]
    ok.append(("cp > 0", cp(data, 9.0, 11.0) > 0))
    ok.append(("in_spec all", in_spec_fraction(data, 9.0, 11.0) == 1))
    ok.append(("histogram sums to n", sum(histogram(data, 4)) == len(data)))
    # relational / regression: y = 2x + 1 exactly
    xs = [0, 1, 2, 3, 4]; ys = [1, 3, 5, 7, 9]
    sl, ic = linear_regression(xs, ys)
    ok.append(("regression slope==2, intercept==1", sl == 2 and ic == 1))
    ok.append(("r_squared == 1 (perfect fit)", abs(r_squared(xs, ys) - 1) < 1e-12))
    ok.append(("correlation(y=2x+1) == 1", abs(correlation(xs, ys) - 1) < 1e-9))
    ok.append(("covariance exact ℚ", isinstance(covariance(xs, ys), Q)))
    # information: fair coin = 1 bit; fair 4-way = 2 bits
    ok.append(("entropy(fair coin) == 1", abs(shannon_entropy([Q(1, 2), Q(1, 2)]) - 1) < 1e-9))
    ok.append(("entropy(uniform 4) == 2", abs(shannon_entropy([Q(1, 4)] * 4) - 2) < 1e-9))
    # capacity
    ok.append(("safety_factor(200,50) == 4", safety_factor(200, 50) == 4))
    ok.append(("finite ln/log/sin match reference",
               abs(_ln(7) - math.log(7)) < 1e-9 and abs(_log10(50) - math.log10(50)) < 1e-9
               and abs(_sin(3) - math.sin(3)) < 1e-9))
    npass = sum(b for _, b in ok)
    for name, b in ok:
        print(f"  {'ok ' if b else 'FAIL'} {name}")
    print(f"eng_readouts self-check: {'PASS' if npass == len(ok) else 'FAIL'} ({npass}/{len(ok)})")
    raise SystemExit(0 if npass == len(ok) else 1)
