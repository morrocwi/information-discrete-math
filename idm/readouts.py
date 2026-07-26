"""idm.readouts — the finite scalar readouts and transforms engineers read values with.

Central tendency, spread, peak/RMS, norms, differences, spectra, dB, regression, Cp/Cpk, entropy — all
finite retained aggregations. (Re-export of the verified `tools/aggregate.py` + `tools/eng_readouts.py`.)
"""
from . import _bridge  # noqa: F401
import aggregate as _agg
import eng_readouts as _eng

# scalar dashboard + full map
dashboard = _agg.dashboard
READOUTS = _agg.READOUTS
# common scalars, promoted to the namespace
(mean, median, mode, rms, peak, variance_pop, variance_samp, std_pop, std_samp, mad,
 norm_L1, norm_L2, norm_Linf, argmin, argmax, prefix_sum, running_min, running_max,
 moving_average, first_diff, second_diff, percentile, weighted_mean, geometric_mean, harmonic_mean,
 crest_factor, form_factor, energy, power) = (
    _agg.mean, _agg.median, _agg.mode, _agg.rms, _agg.peak, _agg.variance_pop, _agg.variance_samp,
    _agg.std_pop, _agg.std_samp, _agg.mad, _agg.norm_L1, _agg.norm_L2, _agg.norm_Linf, _agg.argmin,
    _agg.argmax, _agg.prefix_sum, _agg.running_min, _agg.running_max, _agg.moving_average,
    _agg.first_diff, _agg.second_diff, _agg.percentile, _agg.weighted_mean, _agg.geometric_mean,
    _agg.harmonic_mean, _agg.crest_factor, _agg.form_factor, _agg.energy, _agg.power)

# transforms / domain readouts
(dft, magnitude_spectrum, power_spectrum, dominant_bin, thd, autocorrelation, cross_correlation,
 db_power, db_amplitude, snr_db, overshoot, rise_indices, settling_index, steady_state_error,
 cp, cpk, in_spec_fraction, histogram, covariance, correlation, linear_regression, r_squared,
 shannon_entropy, safety_factor, utilization, margin) = (
    _eng.dft, _eng.magnitude_spectrum, _eng.power_spectrum, _eng.dominant_bin, _eng.thd,
    _eng.autocorrelation, _eng.cross_correlation, _eng.db_power, _eng.db_amplitude, _eng.snr_db,
    _eng.overshoot, _eng.rise_indices, _eng.settling_index, _eng.steady_state_error, _eng.cp, _eng.cpk,
    _eng.in_spec_fraction, _eng.histogram, _eng.covariance, _eng.correlation, _eng.linear_regression,
    _eng.r_squared, _eng.shannon_entropy, _eng.safety_factor, _eng.utilization, _eng.margin)
