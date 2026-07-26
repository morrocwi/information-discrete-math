"""Executable contract tests for Retained Contraction Protocol 1.0."""

from tools.idm_discipline import ACCEPT, BLOCK, HOLD
from tools.retained_contraction_protocol import (
    PreflightCertificate,
    RCPDeclaration,
    RetainedFactor,
    certify_contraction,
    preflight_contraction,
)


FACTORS = (
    RetainedFactor("left", (0,)),
    RetainedFactor("coupling", (0, 1)),
    RetainedFactor("right", (1,)),
)


def declaration(**changes):
    values = {
        "resolution_lambda": "2 states per retained axis",
        "tolerance": 1e-12,
        "axis_sizes": ((0, 2), (1, 2)),
        "boundary_axes": (),
        "output_names": ("partition",),
        "max_work_tokens": 100,
        "max_peak_elements": 16,
    }
    values.update(changes)
    return RCPDeclaration(**values)


def test_rcp_accepts_admissible_path_and_preserved_readout():
    preflight = preflight_contraction(declaration(), FACTORS, (0, 1))
    assert preflight.status == ACCEPT
    plan = preflight.value
    assert isinstance(plan, PreflightCertificate)
    assert plan.plan.peak_retained_elements == 4
    verdict = certify_contraction(
        preflight,
        (0.75,),
        (0.75 + 1e-13,),
        measured_work_tokens=plan.planned_work_tokens,
        witness_method="independent finite enumeration",
    )
    assert verdict.status == ACCEPT
    assert verdict.value.maximum_absolute_difference < 1e-12


def test_rcp_blocks_path_that_eliminates_wrong_boundary():
    verdict = preflight_contraction(
        declaration(boundary_axes=(1,)),
        FACTORS,
        (0, 1),
    )
    assert verdict.status == BLOCK
    assert "forbidden" in verdict.reason


def test_rcp_blocks_over_budget_before_execution():
    verdict = preflight_contraction(
        declaration(max_work_tokens=1),
        FACTORS,
        (0, 1),
    )
    assert verdict.status == BLOCK
    assert "execution refused" in verdict.reason


def test_rcp_holds_disagreement_instead_of_claiming_preservation():
    preflight = preflight_contraction(declaration(), FACTORS, (0, 1))
    plan = preflight.value
    verdict = certify_contraction(
        preflight,
        (0.75,),
        (0.70,),
        measured_work_tokens=plan.planned_work_tokens,
        witness_method="alternate admissible path",
    )
    assert verdict.status == HOLD
    assert "exceeds tolerance" in verdict.reason


def test_rcp_holds_when_preservation_witness_is_missing():
    preflight = preflight_contraction(declaration(), FACTORS, (0, 1))
    plan = preflight.value
    verdict = certify_contraction(
        preflight,
        (0.75,),
        None,
        measured_work_tokens=plan.planned_work_tokens,
        witness_method="",
    )
    assert verdict.status == HOLD
    assert "no independent" in verdict.reason


def test_rcp_holds_when_operation_ledger_does_not_sum():
    preflight = preflight_contraction(declaration(), FACTORS, (0, 1))
    plan = preflight.value
    verdict = certify_contraction(
        preflight,
        (0.75,),
        (0.75,),
        measured_work_tokens=plan.planned_work_tokens,
        measured_work_by_op={"incomplete": 1},
        witness_method="independent finite enumeration",
    )
    assert verdict.status == HOLD
    assert "does not sum" in verdict.reason
