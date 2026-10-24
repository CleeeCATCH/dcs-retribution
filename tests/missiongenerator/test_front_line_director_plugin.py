"""Behaviour tests for resources/plugins/frontlinedirector under a mocked DCS."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import lupa.lua51 as lupa
import pytest

from game import Game
from game.missiongenerator.luagenerator import LuaData, LuaGenerator
from game.missiongenerator.missiondata import (
    FrontLineDirectorInfo,
    FrontLineGroupInfo,
    FrontLineSectorInfo,
    FrontLineSideInfo,
    MissionData,
)
from game.plugins import LuaPluginManager
from game.settings import Settings

SCRIPT = Path("resources/plugins/frontlinedirector/frontline_director.lua")

# Mocked DCS world. Terrain is flat at 100 m with a 300 m hill around HILL.
# Groups are plain tables: {units = {{x=, z=, life=}}, tasks = {}, options = {}}.
MOCK_DCS = """
HILL = {x = 1000, z = 0}
SURF = {LAND = 1, ROAD = 2, WATER = 3}
messages = {}
scheduled = {}
marks = {}
mockGroups = {}
visibleFn = function(a, b) return true end
players = {red = {}, blue = {}}

local function hillHeight(x, z)
    local d = math.sqrt((x - HILL.x) ^ 2 + (z - HILL.z) ^ 2)
    return 100 + math.max(0, 200 - d * 0.2)
end

env = {info = function() end, error = function(m) error(m) end}
land = {
    SurfaceType = SURF,
    getHeight = function(p) return hillHeight(p.x, p.y) end,
    getSurfaceType = function(p) return SURF.LAND end,
    isVisible = function(a, b) return visibleFn(a, b) end,
}
coalition = {side = {RED = 1, BLUE = 2}, getPlayers = function(side)
    if side == 2 then return players.blue end
    return players.red
end}
world = {event = {S_EVENT_SHOT = 1, S_EVENT_SHOOTING_START = 23}, addEventHandler = function() end}
AI = {Option = {Ground = {
    id = {ROE = "roe", ALARM_STATE = "alarm"},
    val = {ROE = {OPEN_FIRE = "open", WEAPON_HOLD = "hold"}, ALARM_STATE = {RED = "red"}},
}}}
trigger = {action = {
    outTextForCoalition = function(side, text) table.insert(messages, {side = side, text = text}) end,
    circleToAll = function(c, id) marks[id] = true end,
    textToAll = function(c, id) marks[id] = true end,
    setMarkupColor = function() end,
    setMarkupColorFill = function() end,
}}
missionCommands = {addCommandForCoalition = function() end}
timer = {
    getTime = function() return 0 end,
    scheduleFunction = function(fn, arg, t) table.insert(scheduled, {fn = fn, arg = arg, t = t}) end,
}

local function makeUnit(u)
    return {
        isExist = function() return u.life > 0 end,
        getLife = function() return u.life end,
        getPoint = function() return {x = u.x, y = 0, z = u.z} end,
    }
end

Group = {getByName = function(name)
    local g = mockGroups[name]
    if not g then return nil end
    return {
        isExist = function() return true end,
        getUnits = function()
            local units = {}
            for _, u in ipairs(g.units) do table.insert(units, makeUnit(u)) end
            return units
        end,
        getController = function()
            return {
                setTask = function(_, task) table.insert(g.tasks, task) end,
                setOption = function(_, id, value) g.options[id] = value end,
            }
        end,
    }
end}

function spawn(name, x, z, count)
    local units = {}
    for i = 1, count do table.insert(units, {x = x, z = z + i * 10, life = 1}) end
    mockGroups[name] = {units = units, tasks = {}, options = {}}
end

function addPlayer(side, x, alt, z)
    table.insert(players[side], {
        isExist = function() return true end,
        inAir = function() return true end,
        getPoint = function() return {x = x, y = alt, z = z} end,
    })
end

function moveTo(name, x, z)
    for _, u in ipairs(mockGroups[name].units) do u.x, u.z = x, z end
end

function kill(name, count)
    for i = 1, count do mockGroups[name].units[i].life = 0 end
end

function lastTask(name)
    return mockGroups[name].tasks[#mockGroups[name].tasks]
end

function lastDestination(name)
    local task = mockGroups[name].tasks[#mockGroups[name].tasks]
    if not task or task.id ~= "Mission" then return nil end
    local points = task.params.route.points
    return points[#points].x, points[#points].y
end

function said(fragment)
    for _, m in ipairs(messages) do
        if string.find(m.text, fragment, 1, true) then return true end
    end
    return false
end

function groupState(name)
    for _, g in ipairs(FLD.frontLines[1].groups) do
        if g.name == name then return g.state end
    end
end
"""

# One front line along the z axis at x = 0, blue south of it attacking north
# (heading 0), red north of it. One sector, centered next to the hill.
PLAN = """
function plan(blueStance, redStance, extraGroups)
    local groups = {
        {name = "blue-tank", side = "blue", role = "TANK", sector = "1", reserve = "false"},
        {name = "blue-reserve", side = "blue", role = "TANK", sector = "1", reserve = "true"},
        {name = "red-tank", side = "red", role = "TANK", sector = "1", reserve = "false"},
        {name = "red-reserve", side = "red", role = "TANK", sector = "1", reserve = "true"},
    }
    for _, g in ipairs(extraGroups or {}) do table.insert(groups, g) end
    return {
        movingUnits = "true",
        frontLines = {{
            name = "A/B",
            sectors = {{x = "0", z = "0", width = "6000"}},
            sides = {
                blue = {stance = blueStance, mainEffort = "1", forwardHeading = "0",
                        enemyBaseX = "30000", enemyBaseZ = "0"},
                red = {stance = redStance, forwardHeading = "180",
                       enemyBaseX = "-30000", enemyBaseZ = "0"},
            },
            groups = groups,
        }},
    }
end

function setupBattle(blueStance, redStance)
    spawn("blue-tank", -3000, 0, 4)
    spawn("blue-reserve", -6000, 0, 4)
    spawn("red-tank", 3000, 0, 4)
    spawn("red-reserve", 6000, 0, 4)
    FLD.start(plan(blueStance, redStance))
end
"""


@pytest.fixture
def lua() -> Any:
    runtime = lupa.LuaRuntime(unpack_returned_tuples=True)
    runtime.execute(MOCK_DCS)
    runtime.execute(SCRIPT.read_text())
    runtime.execute(PLAN)
    runtime.execute("math.randomseed(1)")
    return runtime


def test_objective_is_the_key_terrain(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    sector = lua.eval("FLD.frontLines[1].sectors[1]")
    assert abs(sector.objX - 1000) <= 500
    assert sector.label == "OBJ ALPHA (Hill 300)"
    assert lua.eval("#scheduled") >= 1


def test_defenders_occupy_battle_positions_and_reserves_hide(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    assert lua.eval("groupState('red-tank')") == "HOLDING"
    # Red defends facing south: its battle position is on its side of the hill.
    x, _ = lua.eval("lastDestination('red-tank')")
    assert x >= 1000
    # Both reserves moved to cover, the attacking blue tank kept its route.
    assert lua.eval("lastDestination('red-reserve')") is not None
    assert lua.eval("lastDestination('blue-reserve')") is not None
    assert lua.eval("lastDestination('blue-tank')") is None
    assert lua.eval("groupState('blue-reserve')") == "RESERVE"


def test_ambush_holds_fire_until_enemy_is_close(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'AMBUSH')")
    assert lua.eval("mockGroups['red-tank'].options.roe") == "hold"
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    assert lua.eval("mockGroups['red-tank'].options.roe") == "hold"
    # Blue walks into the kill zone.
    rx, rz = lua.eval("FLD.groupPosition('red-tank')")
    lua.execute(f"moveTo('blue-tank', {rx - 1000}, {rz})")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    assert lua.eval("mockGroups['red-tank'].options.roe") == "open"


def test_capture_and_counter_attack(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('red-tank', 2500, 0)")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")

    assert lua.eval("FLD.frontLines[1].sectors[1].holder") == "blue"
    assert lua.eval("said('we have taken OBJ ALPHA')")
    # Blue consolidates on the objective, red commits its reserve to retake it.
    assert lua.eval("groupState('blue-tank')") == "HOLDING"
    assert lua.eval("groupState('red-reserve')") == "COUNTER"
    assert lua.eval("said('committed to counter-attack OBJ ALPHA')")
    obj_x = lua.eval("FLD.frontLines[1].sectors[1].objX")
    x, _ = lua.eval("lastDestination('red-reserve')")
    assert x == pytest.approx(obj_x)

    # The reserve is spent: no second commitment, even after the cooldown.
    lua.execute("FLD.tickFront(FLD.frontLines[1], 1000)")
    assert lua.eval("#mockGroups['red-reserve'].tasks") == 2


def test_broken_group_withdraws_to_cover(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("kill('red-tank', 3)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")

    assert lua.eval("groupState('red-tank')") == "WITHDRAWN"
    x, _ = lua.eval("lastDestination('red-tank')")
    # Red falls back north, away from blue.
    assert x > 3000
    assert lua.eval("said('falls back from OBJ ALPHA')")


def test_collapsed_sector_is_exploited(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")

    assert lua.eval("groupState('blue-tank')") == "EXPLOITING"
    assert lua.eval("said('task force exploiting toward')")
    x, _ = lua.eval("lastDestination('blue-tank')")
    assert x > 3000


def test_defensive_side_does_not_exploit(lua: Any) -> None:
    lua.execute("setupBattle('DEFENSIVE', 'AGGRESSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    assert lua.eval("groupState('blue-tank')") != "EXPLOITING"


def test_static_units_are_never_moved(lua: Any) -> None:
    lua.execute("""
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        local data = plan('AGGRESSIVE', 'DEFENSIVE')
        data.movingUnits = "false"
        FLD.start(data)
        kill('red-tank', 3)
        moveTo('blue-tank', 1000, 0)
        FLD.tickFront(FLD.frontLines[1], 30)
    """)
    for name in ("blue-tank", "blue-reserve", "red-tank", "red-reserve"):
        assert lua.eval(f"#mockGroups['{name}'].tasks") == 0
    # Objectives are still tracked.
    assert lua.eval("FLD.frontLines[1].sectors[1].holder") == "blue"


def test_status_report(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    text = lua.eval("FLD.statusText('blue')")
    assert "OBJ ALPHA (Hill 300) [MAIN EFFORT]" in text
    assert "our strength 100%" in text
    assert "Reserve task force groups available: 1" in text


def test_missing_groups_do_not_break_the_director(lua: Any) -> None:
    lua.execute("FLD.start(plan('AGGRESSIVE', 'DEFENSIVE'))")
    lua.execute("FLD.tick(nil, 30)")
    assert lua.eval("FLD.frontLines[1].sectors[1].holder") is None


def test_generated_plan_loads_in_lua(lua: Any) -> None:
    mission_data = MissionData()
    mission_data.front_line_director.append(
        FrontLineDirectorInfo(
            name='Senaki "A"/Kutaisi',
            sectors=[FrontLineSectorInfo(0.0, 0.0, 6000)],
            blue=FrontLineSideInfo("AGGRESSIVE", 0, 0, 30000.0, 0.0),
            red=FrontLineSideInfo("DEFENSIVE", None, 180, -30000.0, 0.0),
            groups=[
                FrontLineGroupInfo("blue-tank", "blue", "TANK", 0, False),
                FrontLineGroupInfo("red-art", "red", "ARTILLERY", None, False, 25000),
            ],
        )
    )
    settings = Settings()
    settings.plugins["arty"] = True
    game = cast(Game, SimpleNamespace(settings=settings))
    generator = LuaGenerator(game, cast(Any, None), mission_data)
    lua_data = LuaData("dcsRetribution")
    generator.generate_front_line_director_data(lua_data)

    lua.execute(lua_data.create_operations_lua())
    lua.execute("spawn('blue-tank', -3000, 0, 2)")
    lua.execute("FLD.start(dcsRetribution.FrontLineDirector)")

    front = lua.eval("FLD.frontLines[1]")
    # Double quotes are escaped to single quotes for Lua.
    assert front.name == "Senaki 'A'/Kutaisi"
    assert front.sides.blue.mainEffort == 1
    assert front.sides.red.mainEffort is None
    assert lua.eval("FLD.frontLines[1].groups[1].sector") == 1
    assert lua.eval("FLD.frontLines[1].groups[2].sector") is None
    assert lua.eval("FLD.frontLines[1].sectors[1].initial.blue") == 2
    assert lua.eval("FLD.frontLines[1].groups[2].range") == 25000
    assert lua.eval("FLD.config.playerArtillery") is True
    assert lua.eval("FLD.config.artilleryStrikes") is True


def test_plugin_registered() -> None:
    plugin = next(
        p
        for p in LuaPluginManager.plugins()
        if p.definition.identifier == "frontlinedirector"
    )
    files = [work_order.filename for work_order in plugin.definition.work_orders]
    assert files == ["frontline_director.lua"]


ARTILLERY = """
function setupArtillery(blueStance, redStance, playerArtillery)
    spawn("blue-tank", -3000, 0, 4)
    spawn("blue-reserve", -6000, 0, 4)
    spawn("red-tank", 3000, 0, 4)
    spawn("red-reserve", 6000, 0, 4)
    spawn("blue-arty", -15000, 0, 4)
    spawn("red-arty", 15000, 0, 4)
    local data = plan(blueStance, redStance, {
        {name = "blue-arty", side = "blue", role = "ARTILLERY", reserve = "false", range = "30000"},
        {name = "red-arty", side = "red", role = "ARTILLERY", reserve = "false", range = "30000"},
    })
    data.playerArtillery = playerArtillery and "true" or "false"
    FLD.start(data)
end

function fireTarget(name)
    local task = lastTask(name)
    if not task or task.id ~= "FireAtPoint" then return nil end
    return task.params.point.x, task.params.point.y
end

function battery(name)
    for _, g in ipairs(FLD.frontLines[1].groups) do
        if g.name == name then return g end
    end
end
"""


@pytest.fixture
def arty(lua: Any) -> Any:
    lua.execute(ARTILLERY)
    return lua


def test_artillery_fires_on_spotted_enemy(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE')")
    rx, rz = arty.eval("FLD.groupPosition('red-tank')")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 30)")
    x, z = arty.eval("fireTarget('blue-arty')")
    assert (x, z) == pytest.approx((rx, rz))
    assert arty.eval("battery('blue-arty').artyState") == "FIRING"


def test_artillery_holds_fire_without_spotting(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE')")
    arty.execute("visibleFn = function() return false end")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 30)")
    assert arty.eval("fireTarget('blue-arty')") is None


def test_player_helicopter_spots_for_artillery(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE')")
    # Ground units are blind, a player helicopter sees from above.
    arty.execute("""
        visibleFn = function(a, b) return a.y > 1000 end
        addPlayer('blue', -2000, 1500, 0)
    """)
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 30)")
    assert arty.eval("fireTarget('blue-arty')") is not None


def test_artillery_never_fires_danger_close(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE')")
    rx, rz = arty.eval("FLD.groupPosition('red-tank')")
    arty.execute(f"moveTo('blue-tank', {rx + 100}, {rz})")
    # The red reserve is far behind and unseen by anyone but the blue tank.
    arty.execute("visibleFn = function(a, b) return math.abs(b.x - a.x) < 1000 end")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 30)")
    assert arty.eval("fireTarget('blue-arty')") is None


def test_air_defence_is_a_priority_target(arty: Any) -> None:
    arty.execute("""
        spawn("red-shorad", 2500, 500, 2)
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, -500, 4)
        spawn("red-reserve", 6000, 0, 4)
        spawn("blue-arty", -15000, 0, 4)
        FLD.start(plan('AGGRESSIVE', 'DEFENSIVE', {
            {name = "blue-arty", side = "blue", role = "ARTILLERY", reserve = "false", range = "30000"},
            {name = "red-shorad", side = "red", role = "SHORAD", sector = "1", reserve = "false"},
        }))
        FLD.runArtillery(FLD.frontLines[1], 'blue', 30)
    """)
    sx, sz = arty.eval("FLD.groupPosition('red-shorad')")
    assert arty.eval("fireTarget('blue-arty')") == pytest.approx((sx, sz))
    assert arty.eval("said('suppressing enemy air defence')")


def test_shoot_scoot_and_counter_battery(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE')")
    red_x, red_z = arty.eval("FLD.groupPosition('red-arty')")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'red', 30)")
    assert arty.eval("fireTarget('red-arty')") is not None

    # Blue locates the red battery only after the counter-battery delay.
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 31)")
    assert arty.eval("fireTarget('blue-arty')") != pytest.approx((red_x, red_z))
    arty.execute("battery('blue-arty').artyState = 'READY'")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 80)")
    assert arty.eval("fireTarget('blue-arty')") == pytest.approx((red_x, red_z))
    assert arty.eval("said('counter-battery fire')")

    # Red relocated once its fire mission was over.
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'red', 125)")
    assert arty.eval("battery('red-arty').artyState") == "MOVING"
    assert arty.eval("lastDestination('red-arty')") is not None
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'red', 280)")
    assert arty.eval("battery('red-arty').artyState") in ("READY", "FIRING")


def test_out_of_range_targets_are_skipped(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE')")
    arty.execute("battery('blue-arty').range = 5000")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 30)")
    assert arty.eval("fireTarget('blue-arty')") is None


def test_player_called_artillery_keeps_blue_batteries(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE', true)")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'blue', 30)")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'red', 30)")
    assert arty.eval("fireTarget('blue-arty')") is None
    assert arty.eval("fireTarget('red-arty')") is not None


def test_externally_fired_battery_is_located(arty: Any) -> None:
    arty.execute("setupArtillery('AGGRESSIVE', 'DEFENSIVE', true)")
    arty.execute("FLD.batteryFired('blue-arty', 10)")
    arty.execute("FLD.batteryFired('blue-arty', 12)")
    assert arty.eval("#FLD.frontLines[1].sides.red.located") == 1
    bx, bz = arty.eval("FLD.groupPosition('blue-arty')")
    arty.execute("FLD.runArtillery(FLD.frontLines[1], 'red', 60)")
    assert arty.eval("fireTarget('red-arty')") == pytest.approx((bx, bz))
