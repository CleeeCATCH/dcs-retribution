"""Tests for putting idle ground units to sleep.

The Python side picks which groups the in-mission script may manage; the Lua side
(resources/plugins/base/dynamic_activation.lua) is run here under Lua 5.1, the
version DCS embeds, against a minimal fake of the DCS scripting API.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import lupa.lua51 as lupa
import pytest
from dcs.mapping import Point

from game.data.units import UnitClass
from game.missiongenerator.dynamicactivation import (
    group_is_eligible,
    ground_object_is_eligible,
    managed_groups,
)
from game.missiongenerator.luagenerator import LuaGenerator
from game.settings import Settings
from game.theater.player import Player
from game.theater.theatergroundobject import (
    BuildingGroundObject,
    CoastalSiteGroundObject,
    EwrGroundObject,
    IadsBuildingGroundObject,
    MissileSiteGroundObject,
    MotorpoolGroundObject,
    SamGroundObject,
    ShipGroundObject,
    VehicleGroupGroundObject,
)

SCRIPT = Path("resources/plugins/base/dynamic_activation.lua")


def _unit(
    unit_class: UnitClass = UnitClass.TANK,
    anti_air: bool = False,
    alive: bool = True,
    x: float = 0,
    y: float = 0,
) -> Any:
    return SimpleNamespace(
        is_vehicle=True,
        is_anti_air=anti_air,
        alive=alive,
        unit_type=SimpleNamespace(unit_class=unit_class),
        position=Point(x, y, None),  # type: ignore[arg-type]
    )


def _group(name: str, *units: Any) -> Any:
    return SimpleNamespace(
        group_name=name, units=list(units), max_threat_range=lambda: 0
    )


def _ground_object(cls: Any, *groups: Any) -> Any:
    ground_object = cls.__new__(cls)
    ground_object.groups = list(groups)
    return ground_object


@pytest.mark.parametrize(
    "cls", [VehicleGroupGroundObject, MotorpoolGroundObject, BuildingGroundObject]
)
def test_idle_ground_objects_are_eligible(cls: Any) -> None:
    assert ground_object_is_eligible(_ground_object(cls))


@pytest.mark.parametrize(
    "cls",
    [
        SamGroundObject,
        EwrGroundObject,
        IadsBuildingGroundObject,
        ShipGroundObject,
        MissileSiteGroundObject,
        CoastalSiteGroundObject,
    ],
)
def test_air_defence_ships_and_launchers_are_never_managed(cls: Any) -> None:
    assert not ground_object_is_eligible(_ground_object(cls))


def test_armour_group_is_eligible() -> None:
    assert group_is_eligible(_group("armour", _unit(), _unit(UnitClass.APC)))


def test_group_with_any_anti_air_unit_stays_awake() -> None:
    # Battle positions can carry SHORAD or MANPADS; those must keep searching.
    assert not group_is_eligible(
        _group("mixed", _unit(), _unit(UnitClass.MANPAD, anti_air=True))
    )


@pytest.mark.parametrize("unit_class", [UnitClass.ARTILLERY, UnitClass.MISSILE])
def test_script_tasked_groups_stay_awake(unit_class: UnitClass) -> None:
    assert not group_is_eligible(_group("fire support", _unit(unit_class)))


def test_dead_group_is_not_managed() -> None:
    assert not group_is_eligible(_group("dead", _unit(alive=False)))


def _game(*control_points: Any, culled: bool = False) -> Any:
    return SimpleNamespace(
        theater=SimpleNamespace(controlpoints=list(control_points)),
        iads_considerate_culling=lambda tgo: culled,
    )


def _control_point(captured: Player, *ground_objects: Any) -> Any:
    return SimpleNamespace(captured=captured, ground_objects=list(ground_objects))


def test_managed_groups_carry_coalition_and_position() -> None:
    armour = _ground_object(
        VehicleGroupGroundObject, _group("0001 | Armour", _unit(x=100, y=200))
    )
    sam = _ground_object(SamGroundObject, _group("0002 | SAM", _unit(anti_air=True)))
    game = _game(
        _control_point(Player.RED, armour, sam),
        _control_point(Player.NEUTRAL, armour),
    )

    groups = list(managed_groups(game))

    assert [(g.group_name, g.coalition, g.x, g.y) for g in groups] == [
        ("0001 | Armour", "red", 100, 200)
    ]


def test_culled_ground_objects_are_skipped() -> None:
    armour = _ground_object(VehicleGroupGroundObject, _group("0001 | Armour", _unit()))
    game = _game(_control_point(Player.BLUE, armour), culled=True)
    assert not list(managed_groups(game))


def _generated_lua(settings: Settings, *control_points: Any) -> str:
    game = SimpleNamespace(
        settings=settings,
        theater=SimpleNamespace(
            controlpoints=list(control_points),
            ground_objects=[go for cp in control_points for go in cp.ground_objects],
            iads_network=SimpleNamespace(skynet_nodes=lambda game: []),
        ),
        iads_considerate_culling=lambda tgo: False,
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
        player_frontline_groups=[],
        enemy_frontline_groups=[],
    )
    mission = SimpleNamespace(triggerrules=SimpleNamespace(triggers=[]))
    generator = LuaGenerator(game, mission, mission_data)  # type: ignore[arg-type]
    generator.generate_plugin_data()
    return str(mission.triggerrules.triggers[-1].actions[0].text.id)


def test_no_data_when_disabled() -> None:
    assert "DynamicActivation" not in _generated_lua(Settings())


def test_generated_data_is_valid_lua() -> None:
    settings = Settings()
    settings.perf_dynamic_activation = True
    settings.perf_dynamic_activation_radius = 15
    settings.perf_dynamic_activation_sleep_delay = 2
    armour = _ground_object(
        VehicleGroupGroundObject, _group("0001 | Armour", _unit(x=10, y=20))
    )
    sam = _ground_object(SamGroundObject, _group("0002 | SAM", _unit(anti_air=True)))

    lua = lupa.LuaRuntime()
    lua.execute(
        "env = {info = function() end}\n"
        + _generated_lua(settings, _control_point(Player.BLUE, armour, sam))
    )
    data = lua.eval("dcsRetribution.DynamicActivation")

    assert data.radiusMeters == "15000"
    assert data.sleepDelaySeconds == "120"
    assert data.debug == "false"
    assert list(data.fixedGroupNames.values()) == ["0001 | Armour", "0002 | SAM"]
    group = data.groups[1]
    assert (group.name, group.coalition, group.x, group.z) == (
        "0001 | Armour",
        "blue",
        "10",
        "20",
    )
    assert data.groups[2] is None


# A minimal fake of the DCS scripting API: ground/helicopter groups per coalition,
# players, controllers that record setOnOff, a manual timer and event dispatch.
FAKE_DCS = """
coalition = {side = {NEUTRAL = 0, RED = 1, BLUE = 2}, groups = {}, players = {[1] = {}, [2] = {}}}
Group = {Category = {AIRPLANE = 0, HELICOPTER = 1, GROUND = 2}}
world = {event = {S_EVENT_HIT = 2}, handlers = {}}
timer = {now = 0, scheduled = {}}
env = {info = function(message) end}
ai = {}
groupsByName = {}

function coalition.getGroups(side, category)
    local result = {}
    for _, g in ipairs(coalition.groups) do
        if g.side == side and g.category == category then
            result[#result + 1] = g
        end
    end
    return result
end

function coalition.getPlayers(side)
    return coalition.players[side]
end

function Group.getByName(name)
    return groupsByName[name]
end

function world.addEventHandler(handler)
    world.handlers[#world.handlers + 1] = handler
end

function timer.getTime()
    return timer.now
end

function timer.scheduleFunction(fn, arg, time)
    timer.scheduled[#timer.scheduled + 1] = {fn = fn, arg = arg, time = time}
end

function runTimers(untilTime)
    while true do
        local nextIndex = nil
        for i, s in ipairs(timer.scheduled) do
            if s.time <= untilTime and (nextIndex == nil or s.time < timer.scheduled[nextIndex].time) then
                nextIndex = i
            end
        end
        if nextIndex == nil then
            break
        end
        local s = table.remove(timer.scheduled, nextIndex)
        timer.now = s.time
        local again = s.fn(s.arg, s.time)
        if again then
            timer.scheduleFunction(s.fn, s.arg, again)
        end
    end
    timer.now = untilTime
end

function makeUnit(x, z)
    local unit = {point = {x = x, y = 0, z = z}}
    function unit:getPoint() return self.point end
    return unit
end

function addGroup(name, side, category, x, z)
    local unit = makeUnit(x, z)
    local group = {name = name, side = side, category = category, units = {unit}, exists = true}
    unit.group = group
    function unit:getGroup() return self.group end
    function group:getName() return self.name end
    function group:getUnit(i) return self.units[i] end
    function group:getUnits() return self.units end
    function group:isExist() return self.exists end
    function group:getController()
        local controller = {}
        function controller:setOnOff(on) ai[group.name] = on end
        return controller
    end
    coalition.groups[#coalition.groups + 1] = group
    groupsByName[name] = group
    return group
end

function removeGroup(name)
    local group = groupsByName[name]
    for i, g in ipairs(coalition.groups) do
        if g == group then
            table.remove(coalition.groups, i)
            break
        end
    end
    return group
end

function hit(unit)
    for _, handler in ipairs(world.handlers) do
        handler:onEvent({id = world.event.S_EVENT_HIT, target = unit})
    end
end
"""


class FakeDcs:
    def __init__(self, managed: list[tuple[str, str, float, float]], **config: Any):
        self.lua = lupa.LuaRuntime()
        self.lua.execute(FAKE_DCS)
        radius = config.get("radius", 20000)
        delay = config.get("delay", 180)
        fixed = config.get("fixed", [])
        entries = ", ".join(
            f'{{name = "{name}", coalition = "{side}", x = "{x}", z = "{z}"}}'
            for name, side, x, z in managed
        )
        fixed_names = ", ".join(f'"{name}"' for name in fixed)
        self.lua.execute(
            "dcsRetribution = {DynamicActivation = {"
            f'radiusMeters = "{radius}", sleepDelaySeconds = "{delay}", '
            f'debug = "true", fixedGroupNames = {{{fixed_names}}}, '
            f"groups = {{{entries}}}}}}}"
        )
        for name, side, x, z in managed:
            self.add_group(name, side, "ground", x, z)

    def start(self) -> None:
        self.lua.execute(SCRIPT.read_text())

    def add_group(self, name: str, side: str, category: str, x: float, z: float) -> Any:
        sides = {"red": 1, "blue": 2}
        categories = {"airplane": 0, "helicopter": 1, "ground": 2}
        return self.lua.globals().addGroup(
            name, sides[side], categories[category], x, z
        )

    def add_player(self, side: str, x: float, z: float) -> None:
        sides = {"red": 1, "blue": 2}
        players = self.lua.eval(f"coalition.players[{sides[side]}]")
        players[len(players) + 1] = self.lua.globals().makeUnit(x, z)

    def run_until(self, seconds: float) -> None:
        self.lua.globals().runTimers(seconds)

    def ai(self, name: str) -> Any:
        return self.lua.eval("ai")[name]


def test_idle_group_goes_to_sleep_at_mission_start() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)])
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is False


def test_nothing_happens_without_data() -> None:
    lua = lupa.LuaRuntime()
    lua.execute(FAKE_DCS)
    lua.execute(SCRIPT.read_text())
    assert len(lua.eval("timer.scheduled")) == 0
    assert len(lua.eval("world.handlers")) == 0


def test_mobile_enemy_ground_unit_wakes_group() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)])
    dcs.add_group("blue convoy", "blue", "ground", 5000, 0)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is None  # never switched off


def test_fixed_enemy_ground_objects_do_not_wake_group() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)], fixed=["blue sam"])
    dcs.add_group("blue sam", "blue", "ground", 5000, 0)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is False


def test_friendly_ground_units_do_not_wake_group() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)])
    dcs.add_group("red convoy", "red", "ground", 1000, 0)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is False


def test_enemy_helicopter_wakes_group_but_airplane_does_not() -> None:
    dcs = FakeDcs([("near helo", "red", 0, 0), ("near jet", "red", 100000, 0)])
    dcs.add_group("apache", "blue", "helicopter", 10000, 0)
    dcs.add_group("strike", "blue", "airplane", 100000, 1000)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("near helo") is None
    assert dcs.ai("near jet") is False


@pytest.mark.parametrize("side", ["red", "blue"])
def test_player_of_either_side_wakes_group(side: str) -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)])
    dcs.add_player(side, 0, 19000)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is None


def test_group_outside_radius_sleeps() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)], radius=20000)
    dcs.add_player("blue", 0, 21000)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is False


def test_group_wakes_when_enemy_arrives_and_sleeps_after_delay() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)], delay=60)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is False

    convoy = dcs.add_group("blue convoy", "blue", "ground", 5000, 0)
    dcs.run_until(15)
    assert dcs.ai("armour") is True

    convoy.units[1].point.x = 50000
    dcs.run_until(40)
    assert dcs.ai("armour") is True  # still inside the sleep delay
    dcs.run_until(90)
    assert dcs.ai("armour") is False


def test_hit_wakes_group_and_it_never_sleeps_again() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)], delay=0)
    dcs.start()
    dcs.run_until(2)
    assert dcs.ai("armour") is False

    dcs.lua.globals().hit(dcs.lua.eval('groupsByName["armour"].units[1]'))
    assert dcs.ai("armour") is True
    dcs.run_until(120)
    assert dcs.ai("armour") is True
    assert not dcs.lua.eval('DynamicActivation.isAsleep("armour")')


def test_hits_on_other_objects_are_ignored() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0)])
    dcs.start()
    dcs.run_until(2)
    static = dcs.lua.eval("{getGroup = function() error('statics have no group') end}")
    dcs.lua.globals().hit(static)
    dcs.lua.globals().hit(dcs.lua.eval("makeUnit(0, 0)"))
    assert dcs.ai("armour") is False


def test_destroyed_group_is_dropped_without_errors() -> None:
    dcs = FakeDcs([("armour", "red", 0, 0), ("gone", "red", 0, 0)])
    dcs.lua.eval('removeGroup("gone")').exists = False
    dcs.lua.execute('groupsByName["gone"] = nil')
    dcs.start()
    dcs.run_until(30)
    assert dcs.ai("armour") is False
    assert dcs.ai("gone") is None


def test_large_campaigns_are_evaluated_in_slices() -> None:
    managed = [(f"g{i}", "red", i * 1000.0, 0.0) for i in range(100)]
    dcs = FakeDcs(managed)
    dcs.start()
    dcs.run_until(2)  # the mission start pass handles everyone at once
    assert all(dcs.ai(f"g{i}") is False for i in range(100))

    dcs.add_group("blue convoy", "blue", "ground", 99000, 0)
    dcs.run_until(3)
    # One tick only covers a tenth of the groups; the last ones are not reached yet.
    assert dcs.ai("g99") is False
    # Enemy positions are refreshed once per cycle, so waking can take up to two.
    dcs.run_until(22)
    assert dcs.ai("g99") is True
    assert dcs.ai("g0") is False
