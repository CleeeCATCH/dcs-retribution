"""Tests for the TacticalAI table the Lua generator hands to the Tactical AI plugin."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from dcs.mapping import Point

from game.ato import FlightType
from game.ato.flightwaypointtype import FlightWaypointType
from game.missiongenerator.luagenerator import LuaGenerator, TACTICAL_AI_ROLES


def _waypoint(kind: FlightWaypointType, x: float, y: float) -> Any:
    return SimpleNamespace(waypoint_type=kind, position=SimpleNamespace(x=x, y=y))


def _flight(
    flight_type: FlightType,
    unit_names: list[str],
    clients: int = 0,
    blue: bool = True,
    waypoints: list[Any] | None = None,
    package: Any = None,
) -> Any:
    units = [SimpleNamespace(name=name) for name in unit_names]
    return SimpleNamespace(
        flight_type=flight_type,
        units=units,
        client_units=units[:clients],
        friendly=SimpleNamespace(is_blue=blue),
        waypoints=waypoints or [],
        package=package
        or SimpleNamespace(target=SimpleNamespace(position=Point(1000, 2000, None))),  # type: ignore[arg-type]
    )


def _generated_lua(flights: list[Any]) -> str:
    game = SimpleNamespace(
        settings=SimpleNamespace(perf_dynamic_activation=False),
        theater=SimpleNamespace(
            ground_objects=[],
            controlpoints=[],
            iads_network=SimpleNamespace(skynet_nodes=lambda game: []),
        ),
    )
    mission_data = SimpleNamespace(
        front_line_director=[],
        runways=[],
        carriers=[],
        tankers=[],
        awacs=[],
        jtacs=[],
        logistics=[],
        flights=flights,
        escorts=[],
        player_frontline_groups=[],
        enemy_frontline_groups=[],
    )
    mission = SimpleNamespace(triggerrules=SimpleNamespace(triggers=[]))
    generator = LuaGenerator(game, mission, mission_data)  # type: ignore[arg-type]
    generator.generate_plugin_data()
    return str(mission.triggerrules.triggers[-1].actions[0].text.id)


def test_ai_cap_is_exported_with_its_station() -> None:
    cap = _flight(
        FlightType.BARCAP,
        ["CAP-1", "CAP-2"],
        blue=False,
        waypoints=[
            _waypoint(FlightWaypointType.TAKEOFF, 0, 0),
            _waypoint(FlightWaypointType.PATROL_TRACK, 100, 300),
            _waypoint(FlightWaypointType.PATROL, 300, 500),
        ],
    )

    lua = _generated_lua([cap])

    assert 'units = {"CAP-1", "CAP-2"}' in lua
    assert 'role = "cap"' in lua
    assert 'side = "1"' in lua
    assert 'anchorX = "200.0"' in lua
    assert 'anchorY = "400.0"' in lua


def test_escort_is_flagged_and_shares_its_package_id() -> None:
    package = SimpleNamespace(target=SimpleNamespace(position=Point(0, 0, None)))  # type: ignore[arg-type]
    strike = _flight(FlightType.STRIKE, ["S-1"], package=package)
    escort = _flight(FlightType.ESCORT, ["E-1"], package=package)

    lua = _generated_lua([strike, escort])

    assert lua.count(f'package = "{id(package)}"') == 2
    assert 'escort = "true"' in lua
    assert 'role = "striker"' in lua
    # Only CAPs have a station to be leashed to.
    assert "anchorX" not in lua


def test_player_and_support_flights_are_left_out() -> None:
    player_cap = _flight(FlightType.BARCAP, ["PLAYER-1", "AI-WINGMAN"], clients=1)
    tanker = _flight(FlightType.REFUELING, ["TANKER-1"])

    lua = _generated_lua([player_cap, tanker])

    tactical_ai = lua[lua.index("TacticalAI = ") :]
    assert "PLAYER-1" not in tactical_ai
    assert "AI-WINGMAN" not in tactical_ai
    assert "TANKER-1" not in tactical_ai


def test_every_air_to_air_and_attack_role_is_mapped() -> None:
    assert TACTICAL_AI_ROLES[FlightType.ESCORT] == "fighter"
    assert TACTICAL_AI_ROLES[FlightType.SWEEP] == "fighter"
    assert FlightType.AEWC not in TACTICAL_AI_ROLES
    assert FlightType.TRANSPORT not in TACTICAL_AI_ROLES
