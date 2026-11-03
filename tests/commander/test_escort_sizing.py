"""Tests for sizing air-to-air escorts to the enemy fighter threat."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from dcs.mapping import Point

from game.ato.flighttype import FlightType
from game.commander.missionproposals import EscortType, ProposedFlight
from game.commander.packagefulfiller import PackageFulfiller
from game.utils import nautical_miles


def _squadron(tasks: set[FlightType], x_nm: float, aircraft: int) -> Any:
    return SimpleNamespace(
        capable_of=lambda task: task in tasks,
        location=SimpleNamespace(position=Point(x_nm * 1852, 0, None)),  # type: ignore[arg-type]
        owned_aircraft=aircraft,
    )


def _fulfiller(squadrons: list[Any], scale: bool = True) -> PackageFulfiller:
    fulfiller = PackageFulfiller.__new__(PackageFulfiller)
    fulfiller.scale_escorts = scale
    fulfiller.coalition = SimpleNamespace(  # type: ignore[assignment]
        opponent=SimpleNamespace(
            air_wing=SimpleNamespace(iter_squadrons=lambda: iter(squadrons)),
            doctrine=MagicMock(),
        )
    )
    return fulfiller


def _flights(package_size: int) -> Any:
    waypoint = SimpleNamespace(position=Point(0, 0, None))  # type: ignore[arg-type]
    flight = SimpleNamespace(
        count=package_size,
        flight_plan=SimpleNamespace(escorted_waypoints=lambda: iter([waypoint])),
    )
    return [flight]


ESCORT = ProposedFlight(FlightType.ESCORT, 2, EscortType.AirToAir)
FIGHTER_TASKS = {FlightType.BARCAP, FlightType.INTERCEPTION}


@pytest.fixture(autouse=True)
def _reach_100nm() -> Any:
    with patch(
        "game.commander.packagefulfiller.ThreatZones.barcap_threat_range",
        return_value=nautical_miles(100),
    ):
        yield


def test_big_enemy_fighter_force_gets_a_four_ship_escort() -> None:
    fulfiller = _fulfiller([_squadron(FIGHTER_TASKS, 50, 8)])

    assert fulfiller.escort_size_for_threat(_flights(2), ESCORT) == 4


def test_small_enemy_fighter_force_keeps_the_two_ship_escort() -> None:
    fulfiller = _fulfiller([_squadron(FIGHTER_TASKS, 50, 4)])

    assert fulfiller.escort_size_for_threat(_flights(2), ESCORT) == 2


def test_fighters_out_of_reach_do_not_count() -> None:
    fulfiller = _fulfiller([_squadron(FIGHTER_TASKS, 150, 20)])

    assert fulfiller.enemy_fighters_covering(_flights(2)) == 0
    assert fulfiller.escort_size_for_threat(_flights(2), ESCORT) == 2


def test_non_fighter_squadrons_do_not_count() -> None:
    fulfiller = _fulfiller([_squadron({FlightType.STRIKE}, 50, 20)])

    assert fulfiller.enemy_fighters_covering(_flights(2)) == 0


def test_threat_is_measured_against_the_package_size() -> None:
    # Eight fighters is a big threat to a two-ship, not to a ten-ship package.
    fulfiller = _fulfiller([_squadron(FIGHTER_TASKS, 50, 8)])

    assert fulfiller.escort_size_for_threat(_flights(10), ESCORT) == 2


def test_setting_off_keeps_the_proposed_size() -> None:
    fulfiller = _fulfiller([_squadron(FIGHTER_TASKS, 50, 20)], scale=False)

    assert fulfiller.escort_size_for_threat(_flights(2), ESCORT) == 2


def test_sead_escorts_are_not_resized() -> None:
    fulfiller = _fulfiller([_squadron(FIGHTER_TASKS, 50, 20)])
    sead = ProposedFlight(FlightType.SEAD_ESCORT, 2, EscortType.Sead)

    assert fulfiller.escort_size_for_threat(_flights(2), sead) == 2
