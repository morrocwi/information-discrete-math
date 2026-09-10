import math

from idm.ns_observable_to_continuum import (
    observable_to_continuum_radius,
    observable_to_continuum_verdict,
    scalar_energy_min_depth,
    scalar_energy_rank_ceiling,
    shell_count,
    shell_energy_min_depth,
    shell_energy_rank_ceiling,
    state_dimension,
)


def test_recorded_observability_dimensions_and_depths():
    assert state_dimension(1) == 52
    assert state_dimension(2) == 248
    assert state_dimension(3) == 684
    assert shell_count(1) == 3
    assert shell_count(2) == 9
    assert shell_count(3) == 18
    assert scalar_energy_min_depth(1) == 48
    assert scalar_energy_min_depth(2) == 244
    assert scalar_energy_min_depth(3) == 680
    assert shell_energy_min_depth(1) == 23
    assert shell_energy_min_depth(3) == 39


def test_recorded_saturation_rows_hit_structural_ceiling():
    assert scalar_energy_rank_ceiling(1, 48) == 49
    assert shell_energy_rank_ceiling(1, 23) == 49
    assert scalar_energy_rank_ceiling(2, 244) == 245
    assert shell_energy_rank_ceiling(3, 39) == 681


def test_orthogonal_composition_is_pythagorean():
    r = observable_to_continuum_radius(retained_radius=3.0, tail_beta=4.0)
    assert r == 5.0


def test_gate_fails_closed_without_either_certificate():
    assert observable_to_continuum_verdict(
        retained_radius=None, tail_beta=0.1, epsilon=1.0
    )["status"] == "HOLD"
    assert observable_to_continuum_verdict(
        retained_radius=0.1, tail_beta=None, epsilon=1.0
    )["status"] == "HOLD"


def test_gate_certifies_only_inside_requested_tolerance():
    yes = observable_to_continuum_verdict(
        retained_radius=0.06, tail_beta=0.08, epsilon=0.1
    )
    assert yes["status"] == "CERTIFIED"
    assert math.isclose(yes["radius"], 0.1, rel_tol=0.0, abs_tol=1e-15)

    no = observable_to_continuum_verdict(
        retained_radius=0.06, tail_beta=0.08, epsilon=0.099
    )
    assert no["status"] == "HOLD"
