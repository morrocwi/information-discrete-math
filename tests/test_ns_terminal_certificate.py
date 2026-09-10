import math

import pytest

from idm.ns_terminal_certificate import (
    energy_defect_floor,
    leray_terminal_energy_budget_beta,
)


def test_terminal_energy_budget_beta_from_certified_lower_records():
    r = leray_terminal_energy_budget_beta(
        K=7,
        initial_l2_norm_upper=2.0,
        retained_terminal_l2_norm_lower=1.5,
        resolved_viscous_dissipation_lower=0.5,
    )
    assert r["status"] == "CERTIFIED_BOUND"
    assert math.isclose(r["tail_squared_upper"], 0.75, rel_tol=1e-14)
    assert math.isclose(r["beta"], math.sqrt(0.75), rel_tol=1e-14)


def test_terminal_energy_budget_certificate_fails_closed_on_inconsistent_inputs():
    r = leray_terminal_energy_budget_beta(
        K=3,
        initial_l2_norm_upper=1.0,
        retained_terminal_l2_norm_lower=1.0,
        resolved_viscous_dissipation_lower=0.1,
    )
    assert r["status"] == "HOLD"
    assert r["beta"] is None


def test_energy_defect_floor_is_zero_under_energy_equality():
    # 4 = 3 + 2*0.5
    assert energy_defect_floor(
        initial_l2_norm=2.0,
        terminal_l2_norm=math.sqrt(3.0),
        total_viscous_dissipation=0.5,
    ) == 0.0


def test_energy_defect_floor_detects_positive_slack():
    # 4 - 2 - 1 = 1
    d = energy_defect_floor(
        initial_l2_norm=2.0,
        terminal_l2_norm=math.sqrt(2.0),
        total_viscous_dissipation=0.5,
    )
    assert math.isclose(d, 1.0, rel_tol=1e-14)


def test_energy_defect_floor_rejects_budget_violation():
    with pytest.raises(ValueError):
        energy_defect_floor(
            initial_l2_norm=1.0,
            terminal_l2_norm=1.0,
            total_viscous_dissipation=1.0,
        )
