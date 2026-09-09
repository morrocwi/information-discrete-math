import idm
from idm import physics
from idm.physics import PhysicsAdapter


def test_physics_surface_is_public():
    assert hasattr(idm, "physics")
    assert callable(idm.physics.solve)
    assert "navier_stokes" in physics.models()
    assert set(physics.models()["navier_stokes"]) == {
        "fourier_mode",
        "point_velocity",
        "plane_average_velocity",
        "harmonic_probe",
    }


def test_every_physics_adapter_has_mandatory_lineage_and_is_discrete_native():
    rows = physics.adapters()
    assert rows
    for row in rows:
        assert row["toledo_root"]
        assert row["equation_parent"]
        assert row["derivation_tier"]
        assert row["continuum_primitive"] is False
        assert row["computation_semantics"] == "finite_discrete"


def test_adapter_registration_rejects_missing_lineage():
    try:
        PhysicsAdapter(
            model="dummy",
            readout="q",
            kind="dummy_kind",
            toledo_root="",
            equation_parent="PARENT",
            derivation_tier="derived",
            source_equation="dummy",
        )
    except ValueError as ex:
        assert "toledo_root" in str(ex)
    else:
        raise AssertionError("missing Toledo lineage must be rejected")


def test_adapter_registration_rejects_continuum_primitive():
    try:
        PhysicsAdapter(
            model="dummy",
            readout="q",
            kind="dummy_kind",
            toledo_root="root/EQ-008",
            equation_parent="PARENT",
            derivation_tier="derived",
            source_equation="dummy",
            continuum_primitive=True,
        )
    except ValueError as ex:
        assert "continuum" in str(ex).lower()
    else:
        raise AssertionError("continuum primitive must be rejected")


def test_navier_stokes_fourier_mode_dispatch_and_lineage():
    r = physics.solve(
        model="navier_stokes",
        readout="fourier_mode",
        K=1,
        nu=0.005,
        dt=0.0025,
        horizon=1,
        target_mode=[1, 0, 0],
        verify=True,
    )
    assert r.status == "ok"
    assert r["physics_model"] == "navier_stokes"
    assert r["physics_readout"] == "fourier_mode"
    assert r["physics_adapter_kind"] == "ns_retained_rk4"
    assert r["toledo_root"] == "root/EQ-008"
    assert r["equation_parent"] == "PROP-URCF-01"
    assert r["equation_parent_alias"] == "EQ-URCF-TURB-004"
    assert r["derivation_tier"] == "derived_finite_galerkin"
    assert r["continuum_primitive"] is False
    assert r["computation_semantics"] == "finite_discrete"
    assert r["equation_lineage"]["toledo_root"] == "root/EQ-008"


def test_harmonic_alias_dispatches_to_same_registered_adapter():
    r = physics.solve({
        "model": "ns",
        "readout": "harmonic",
        "K": 1,
        "nu": 0.005,
        "dt": 0.0025,
        "horizon": 1,
        "wavevector": [1, 1, 1],
        "phase": 0.3,
        "verify": True,
    })
    assert r.status == "ok"
    assert r["physics_readout"] == "harmonic_probe"
    assert r["physics_adapter_kind"] == "ns_retained_harmonic_probe"
    assert r["continuum_primitive"] is False


def test_unknown_physics_adapter_holds():
    r = physics.solve(model="maxwell", readout="field", horizon=1)
    assert r.status == "HOLD"
    assert "unknown physics adapter" in r.reason


def test_describe_exposes_lineage_before_execution():
    d = physics.describe("navier_stokes", "plane_average")
    assert d["status"] == "ok"
    assert d["toledo_root"] == "root/EQ-008"
    assert d["equation_parent"] == "PROP-URCF-01"
    assert d["derivation_tier"] == "derived_finite_galerkin"
    assert d["continuum_primitive"] is False
