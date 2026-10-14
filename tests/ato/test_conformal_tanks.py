"""Tests for flying an airframe with or without conformal fuel tanks.

Some airframes (the F-15EX mod) exist in DCS as two unit types, one with CFTs and
one without. Retribution lists only the plain one; a flight switches to the CFT
unit type through `Flight.set_conformal_tanks`, and `Flight.unit_type` then reports
the CFT type so that loadouts, fuel and mission generation all follow it.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from dcs.payloads import PayloadDirectories

from game import persistency
from game.ato.flight import Flight
from game.ato.flightmember import FlightMember
from game.ato.flightmembers import FlightMembers
from game.ato.flighttype import FlightType
from game.ato.loadouts import Loadout
from game.dcs.aircrafttype import AircraftType

RESOURCES = Path(__file__).resolve().parents[2] / "resources"


@pytest.fixture(autouse=True)
def _setup(tmp_path: Path) -> None:
    persistency.setup(str(tmp_path), prefer_liberation_payloads=False, port=16885)
    PayloadDirectories.set_fallback(RESOURCES / "customized_payloads")


def _flight(flight_type: FlightType, members: int = 2) -> Flight:
    """A Flight with just the state the CFT switch touches."""
    flight = Flight.__new__(Flight)
    flight.squadron = SimpleNamespace(  # type: ignore[assignment]
        aircraft=AircraftType.named("F-15EX Eagle II")
    )
    flight.package = SimpleNamespace(target=None)  # type: ignore[assignment]
    flight.flight_type = flight_type
    flight.use_conformal_tanks = False
    flight.use_same_loadout_for_all_members = True
    roster = FlightMembers.__new__(FlightMembers)
    roster.flight = flight
    roster.members = [
        FlightMember(None, Loadout.default_for(flight)) for _ in range(members)
    ]
    flight.roster = roster
    flight.initialize_fuel()
    return flight


def test_every_conformal_tanks_variant_resolves() -> None:
    for aircraft in AircraftType.iter_all():
        if aircraft.conformal_tanks_variant is not None:
            cft = aircraft.conformal_tanks_type
            assert cft is not None
            assert cft.dcs_unit_type is not aircraft.dcs_unit_type


def test_switching_on_changes_unit_type_loadout_and_fuel() -> None:
    flight = _flight(FlightType.BARCAP)
    assert flight.unit_type.dcs_id == "F15EX"
    assert flight.can_use_conformal_tanks

    flight.set_conformal_tanks(True)

    assert flight.unit_type.dcs_id == "F15EX_CFT"
    assert flight.squadron.aircraft.dcs_id == "F15EX"
    assert flight.fuel == flight.unit_type.dcs_unit_type.fuel_max
    for member in flight.iter_members():
        # Station 5 holds an AMBER pair only on the CFT type.
        weapon = member.loadout.pylons[5]
        assert weapon is not None and weapon.clsid == "{AMBER_2xAIM120D}"
        assert not member.loadout.is_custom

    flight.set_conformal_tanks(False)
    assert flight.unit_type.dcs_id == "F15EX"
    weapon = flight.roster.members[0].loadout.pylons[5]
    assert weapon is not None and weapon.clsid == "{F15EX_AIM-120D-3_FUS_LF}"


def test_custom_loadouts_are_replaced_on_switch() -> None:
    flight = _flight(FlightType.BARCAP)
    member = flight.roster.members[0]
    member.loadout = member.loadout.derive_custom("Custom")
    member.use_custom_loadout = True

    flight.set_conformal_tanks(True)

    assert not member.loadout.is_custom
    assert not member.use_custom_loadout


def test_cft_not_offered_for_tasks_the_cft_jet_lacks() -> None:
    # The mod's V3 carries no air-to-ground stores.
    flight = _flight(FlightType.STRIKE)
    assert not flight.can_use_conformal_tanks


def test_task_change_drops_cfts_the_new_task_cannot_use() -> None:
    flight = _flight(FlightType.BARCAP)
    flight.set_conformal_tanks(True)
    flight.coalition = SimpleNamespace(  # type: ignore[assignment]
        game=SimpleNamespace(settings=None)
    )

    flight.set_flight_type(FlightType.STRIKE)

    assert not flight.use_conformal_tanks
    assert flight.unit_type.dcs_id == "F15EX"


def test_old_saves_default_to_no_cfts() -> None:
    flight = _flight(FlightType.BARCAP)
    state = flight.__dict__.copy()
    del state["use_conformal_tanks"]
    state["squadron"] = SimpleNamespace(
        aircraft=flight.squadron.aircraft, settings=None
    )
    restored = Flight.__new__(Flight)
    restored.__setstate__(state)
    assert restored.use_conformal_tanks is False


def test_switch_clears_liveries_of_the_other_unit_type() -> None:
    flight = _flight(FlightType.BARCAP)
    for member in flight.iter_members():
        member.livery = "plain f-15ex livery"

    flight.set_conformal_tanks(True)

    assert all(member.livery is None for member in flight.iter_members())


def test_squadron_liveries_are_not_painted_on_the_cft_jet() -> None:
    from game.missiongenerator.aircraft.aircraftpainter import AircraftPainter

    flight = _flight(FlightType.BARCAP)
    flight.squadron.livery = "plain f-15ex livery"  # type: ignore[attr-defined]
    flight.squadron.livery_set = ["plain f-15ex livery"]  # type: ignore[attr-defined]
    flight.squadron.use_livery_set = True  # type: ignore[attr-defined]
    painter = AircraftPainter(flight, None)  # type: ignore[arg-type]
    assert painter.livery_from_squadron() == "plain f-15ex livery"

    flight.set_conformal_tanks(True)

    assert painter.livery_from_squadron() is None
    assert painter.livery_from_squadron_set(member_uses_livery_set=True) is None
