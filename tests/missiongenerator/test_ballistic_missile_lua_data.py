"""Tests for the ballisticMissiles table the Lua generator hands to plugins.

The Ballistic Missile Strike plugin reads
`dcsRetribution.artilleryGroups.ballisticMissiles`. Missile launchers are
UnitClass.MISSILE, not ARTILLERY, so they need their own collection; dropping
the branch in `LuaGenerator.generate_plugin_data` leaves the plugin with an
empty radio menu, which is exactly what these tests pin.
"""

from types import SimpleNamespace
from typing import Any

from game.data.units import UnitClass
from game.missiongenerator.luagenerator import LuaGenerator


def _unit_type(unit_class: UnitClass, threat_range: int) -> Any:
    return SimpleNamespace(
        unit_class=unit_class,
        display_name="Launcher",
        dcs_unit_type=SimpleNamespace(threat_range=threat_range),
    )


def _ground_object(name: str, unit_type: Any) -> Any:
    return SimpleNamespace(
        groups=[
            SimpleNamespace(
                group_name=f"0001 | {name}",
                name=name,
                units=[SimpleNamespace(unit_type=unit_type)],
            )
        ]
    )


def _generated_lua(ground_objects: list[Any], frontline_groups: list[Any]) -> str:
    game = SimpleNamespace(
        theater=SimpleNamespace(
            ground_objects=ground_objects,
            controlpoints=[],
            iads_network=SimpleNamespace(skynet_nodes=lambda game: []),
        )
    )
    mission_data = SimpleNamespace(
        runways=[],
        carriers=[],
        tankers=[],
        awacs=[],
        jtacs=[],
        logistics=[],
        flights=[],
        escorts=[],
        player_frontline_groups=frontline_groups,
        enemy_frontline_groups=[],
    )
    mission = SimpleNamespace(triggerrules=SimpleNamespace(triggers=[]))

    generator = LuaGenerator(game, mission, mission_data)  # type: ignore[arg-type]
    generator.generate_plugin_data()

    # String.__str__ is empty without a translation table; .id holds the raw script.
    return str(mission.triggerrules.triggers[-1].actions[0].text.id)


def test_missile_launcher_is_exported_with_its_range() -> None:
    lua = _generated_lua(
        [_ground_object("SCUD SITE", _unit_type(UnitClass.MISSILE, 285000))], []
    )

    assert 'groupName = "0001 | SCUD SITE"' in lua
    assert 'callsign = "SCUD SITE"' in lua
    assert 'maxRangeMeters = "285000"' in lua


def test_launcher_without_a_firing_range_is_skipped() -> None:
    # The V-1 ramp has threat_range 0 and cannot be tasked in DCS, so offering
    # it in the radio menu would only be a dead entry.
    lua = _generated_lua(
        [_ground_object("V-1 SITE", _unit_type(UnitClass.MISSILE, 0))], []
    )

    assert "V-1 SITE" not in lua
    assert "ballisticMissiles = {}" in lua


def test_artillery_does_not_land_in_the_ballistic_collection() -> None:
    lua = _generated_lua(
        [_ground_object("GUNS", _unit_type(UnitClass.ARTILLERY, 20000))], []
    )

    assert "ballisticMissiles = {}" in lua
    assert 'groupName = "0001 | GUNS"' in lua


def test_frontline_missile_group_is_exported() -> None:
    unit_type = _unit_type(UnitClass.MISSILE, 300000)
    frontline_group = SimpleNamespace(
        group_name="0042 | ATACMS", unit_type=unit_type, units=[]
    )

    lua = _generated_lua([], [frontline_group])

    assert 'groupName = "0042 | ATACMS"' in lua
    assert 'maxRangeMeters = "300000"' in lua
