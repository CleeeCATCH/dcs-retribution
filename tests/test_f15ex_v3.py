"""Checks the F-15EX mod (V3) data: unit types, stations, stores and loadouts."""

from __future__ import annotations

from pathlib import Path

import pytest
from dcs.payloads import PayloadDirectories

from game import persistency
from game.ato.flighttype import FlightType
from game.ato.loadouts import Loadout
from game.data.weapons import Pylon, Weapon, WeaponType
from game.dcs.aircrafttype import AircraftType
from pydcs_extensions.f15ex.f15ex import F15EXWeapons

RESOURCES = Path(__file__).resolve().parents[1] / "resources"

TYPES = {
    "F15EX": "F-15EX Eagle II",
    "F15EX_CFT": "F-15EX Eagle II (CFT)",
    "F15IA": "F-15IA",
}
AIR_TO_AIR = [
    FlightType.BARCAP,
    FlightType.TARCAP,
    FlightType.ESCORT,
    FlightType.SWEEP,
    FlightType.INTERCEPTION,
]


@pytest.fixture(autouse=True)
def _setup(tmp_path: Path) -> None:
    persistency.setup(str(tmp_path), prefer_liberation_payloads=False, port=16885)
    PayloadDirectories.set_fallback(RESOURCES / "customized_payloads")


@pytest.mark.parametrize("dcs_id", TYPES)
def test_type_has_fifteen_stations(dcs_id: str) -> None:
    aircraft = AircraftType.named(TYPES[dcs_id])
    assert aircraft.dcs_id == dcs_id
    assert aircraft.dcs_unit_type.pylons == set(range(1, 16))


@pytest.mark.parametrize("dcs_id", TYPES)
@pytest.mark.parametrize("flight_type", AIR_TO_AIR)
def test_air_to_air_loadouts_fit_the_stations(
    dcs_id: str, flight_type: FlightType
) -> None:
    aircraft = AircraftType.named(TYPES[dcs_id])
    assert aircraft.capable_of(flight_type)
    loadout = Loadout.default_for_task_and_aircraft(flight_type, aircraft.dcs_unit_type)
    assert loadout.name == f"Retribution {flight_type.value}"
    missiles = 0
    for number, weapon in loadout.pylons.items():
        assert weapon is not None
        assert Pylon.for_aircraft(aircraft, number).can_equip(weapon)
        if weapon.weapon_group.type in (WeaponType.AAM_RADAR, WeaponType.AAM_IR):
            missiles += 1
    assert missiles >= 12


@pytest.mark.parametrize("dcs_id", TYPES)
def test_no_air_to_ground_tasks(dcs_id: str) -> None:
    # V3 has no air-to-ground stores, so the planner must not pick it for strikes.
    aircraft = AircraftType.named(TYPES[dcs_id])
    for flight_type in [FlightType.STRIKE, FlightType.CAS, FlightType.SEAD]:
        assert not aircraft.capable_of(flight_type)


def test_mod_missiles_belong_to_weapon_groups() -> None:
    for name, data in vars(F15EXWeapons).items():
        if name.startswith("_") or "Legion" in name:
            continue
        weapon = Weapon.with_clsid(data["clsid"])
        assert weapon is not None, data["clsid"]
        assert weapon.weapon_group.type in (
            WeaponType.AAM_RADAR,
            WeaponType.AAM_IR,
        ), data["clsid"]
