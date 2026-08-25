"""Tests for the "All flights never use ECM" setting.

Two halves have to hold together for the option to work in DCS: the group must get
`OptECMUsing(NeverUse)` at its first waypoint, and none of the later waypoint builders
may append an `OptECMUsing` that would override it from that waypoint onwards.
"""

from types import SimpleNamespace
from typing import Any

from dcs.task import OptECMUsing

from game.ato import FlightType
from game.missiongenerator.aircraft.aircraftbehavior import AircraftBehavior
from game.missiongenerator.aircraft.waypoints.pydcswaypointbuilder import (
    PydcsWaypointBuilder,
)


def _flight(never_use_ecm: bool) -> Any:
    settings = SimpleNamespace(
        ai_unlimited_fuel=False,
        ai_vertical_takoff_landing=False,
        ai_jettison_empty_tanks=False,
        ai_never_use_ecm=never_use_ecm,
    )
    coalition = SimpleNamespace(game=SimpleNamespace(settings=settings))
    return SimpleNamespace(
        squadron=SimpleNamespace(coalition=coalition),
        coalition=coalition,
        flight_plan=SimpleNamespace(layout=None),
        state=SimpleNamespace(is_at_ip=False, in_combat=False),
        is_helo=False,
        client_count=0,
        flight_type=FlightType.STRIKE,
    )


def _group() -> Any:
    return SimpleNamespace(points=[SimpleNamespace(tasks=[])], units=[])


def _ecm_tasks(tasks: list[Any]) -> list[Any]:
    return [t for t in tasks if isinstance(t, OptECMUsing)]


def _builder(never_use_ecm: bool) -> PydcsWaypointBuilder:
    builder = PydcsWaypointBuilder.__new__(PydcsWaypointBuilder)
    builder.flight = _flight(never_use_ecm)
    return builder


def test_never_use_ecm_sets_group_option() -> None:
    group = _group()
    AircraftBehavior(FlightType.STRIKE, None).configure_behavior(  # type: ignore[arg-type]
        _flight(never_use_ecm=True), group
    )

    ecm = _ecm_tasks(group.points[0].tasks)
    assert len(ecm) == 1
    assert ecm[0].value == OptECMUsing.Values.NeverUse


def test_group_option_absent_when_setting_disabled() -> None:
    group = _group()
    AircraftBehavior(FlightType.STRIKE, None).configure_behavior(  # type: ignore[arg-type]
        _flight(never_use_ecm=False), group
    )

    assert _ecm_tasks(group.points[0].tasks) == []


def test_set_ecm_using_suppressed_when_never_use_ecm() -> None:
    # Appending here would override the NeverUse set at the first waypoint.
    waypoint = SimpleNamespace(tasks=[])
    _builder(never_use_ecm=True).set_ecm_using(
        waypoint, OptECMUsing.Values.UseIfDetectedLockByRadar  # type: ignore[arg-type]
    )

    assert waypoint.tasks == []


def test_set_ecm_using_applies_requested_value_by_default() -> None:
    waypoint = SimpleNamespace(tasks=[])
    _builder(never_use_ecm=False).set_ecm_using(
        waypoint, OptECMUsing.Values.UseIfDetectedLockByRadar  # type: ignore[arg-type]
    )

    assert len(waypoint.tasks) == 1
    assert waypoint.tasks[0].value == OptECMUsing.Values.UseIfDetectedLockByRadar
