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
    FrontLineEventInfo,
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
taskMarks = {}
effects = {}
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
    getClosestPointOnRoads = function(kind, x, z)
        if roadZ then return x, roadZ end
        return nil
    end,
}
coalition = {side = {RED = 1, BLUE = 2}, getPlayers = function(side)
    if side == 2 then return players.blue end
    return players.red
end}
buildings = {}
world = {
    event = {S_EVENT_SHOT = 1, S_EVENT_SHOOTING_START = 23},
    addEventHandler = function() end,
    VolumeType = {SPHERE = 2},
    searchObjects = function(category, volume, handler)
        local p = volume.params.point
        for _, b in ipairs(buildings) do
            if math.sqrt((b.x - p.x) ^ 2 + (b.z - p.z) ^ 2) <= volume.params.radius then
                handler()
            end
        end
    end,
}
Object = {Category = {SCENERY = 5}}
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
    markToCoalition = function(id, text, pos, side) taskMarks[id] = {text = text, x = pos.x, z = pos.z, side = side} end,
    removeMark = function(id) taskMarks[id] = nil end,
    effectSmokeBig = function(pos, preset, density, name)
        effects[name] = {x = pos.x, z = pos.z, preset = preset, density = density}
    end,
    effectSmokeStop = function(name) effects[name] = nil end,
}}
coord = {
    LOtoLL = function(p) return p.x / 1000, p.z / 1000, 0 end,
    LLtoMGRS = function(lat, lon) return {lat = lat, lon = lon} end,
}
mist = {tostringMGRS = function(m, acc) return string.format("GRID %.1f %.1f", m.lat, m.lon) end}
Unit = {Category = {GROUND_UNIT = 2, AIRPLANE = 0}}
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
        activate = function() g.active = true end,
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

function deadUnit(x, z, armored, category, infantry)
    return {
        getDesc = function() return {category = category or Unit.Category.GROUND_UNIT} end,
        hasAttribute = function(_, attribute)
            if attribute == "Infantry" then return infantry == true end
            return armored and attribute == "Armored vehicles"
        end,
        getName = function() return string.format("wreck %d %d", x, z) end,
        getPoint = function() return {x = x, y = 0, z = z} end,
    }
end

function effectCount()
    local n = 0
    for _ in pairs(effects) do n = n + 1 end
    return n
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

function countSaid(fragment)
    local n = 0
    for _, m in ipairs(messages) do
        if string.find(m.text, fragment, 1, true) then n = n + 1 end
    end
    return n
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
    assert lua.eval("countSaid('committed to counter-attack')") == 1


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


def test_undefended_sector_is_exploited(lua: Any) -> None:
    # Red keeps nothing in the sector: a gap blue drives through.
    lua.execute("""
        spawn("blue-tank", 1000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        local data = plan('AGGRESSIVE', 'DEFENSIVE')
        data.frontLines[1].groups[3].reserve = "true"
        FLD.start(data)
    """)
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")

    assert lua.eval("groupState('blue-tank')") == "EXPLOITING"
    x, _ = lua.eval("lastDestination('blue-tank')")
    assert x > 3000


def test_exploitation_keeps_pushing_without_resistance(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("kill('red-reserve', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    first_x, first_z = lua.eval("lastDestination('blue-tank')")

    # Not there yet: no new orders.
    lua.execute("FLD.tickFront(FLD.frontLines[1], 90)")
    assert lua.eval("lastDestination('blue-tank')") == (first_x, first_z)

    # The reserve followed the breakthrough up: the task force regroups.
    assert lua.eval("groupState('blue-reserve')") == "EXPLOITING"
    lua.execute(f"moveTo('blue-tank', {first_x}, {first_z})")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 120)")
    assert lua.eval("lastDestination('blue-tank')") == (first_x, first_z)

    # The straggler is not there after two minutes: the force pushes on.
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    x, _ = lua.eval("lastDestination('blue-tank')")
    assert x > first_x + 2000
    assert lua.eval("lastDestination('blue-reserve')")[0] > first_x + 2000
    assert lua.eval("groupState('blue-tank')") == "EXPLOITING"
    assert lua.eval("said('meets no resistance, pushing on toward')")


def test_exploiting_task_force_pushes_on_together_once_all_arrived(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("kill('red-reserve', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 90)")
    tank = lua.eval("lastDestination('blue-tank')")
    reserve = lua.eval("lastDestination('blue-reserve')")
    lua.execute(f"moveTo('blue-tank', {tank[0]}, {tank[1]})")
    lua.execute(f"moveTo('blue-reserve', {reserve[0]}, {reserve[1]})")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 120)")
    tank_x, tank_z = lua.eval("lastDestination('blue-tank')")
    reserve_x, reserve_z = lua.eval("lastDestination('blue-reserve')")
    assert tank_x > tank[0] + 2000 and reserve_x > reserve[0] + 2000
    # Side by side, not stacked on one point.
    assert tank_z != reserve_z


def test_exploitation_stops_at_enemy_contact(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    first = lua.eval("lastDestination('blue-tank')")

    # The red reserve still waits near the exploitation target.
    lua.execute(f"moveTo('blue-tank', {first[0]}, {first[1]})")
    lua.execute(f"moveTo('red-reserve', {first[0] + 1000}, {first[1]})")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 120)")
    assert lua.eval("lastDestination('blue-tank')") == first


def test_attacker_reserve_advances_into_a_gap(lua: Any) -> None:
    # Two sectors, nobody committed to the second one.
    lua.execute("""
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        local data = plan('AGGRESSIVE', 'DEFENSIVE')
        table.insert(data.frontLines[1].sectors, {x = "0", z = "10000", width = "6000"})
        FLD.start(data)
    """)
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")

    assert lua.eval("groupState('blue-reserve')") == "COUNTER"
    assert lua.eval("said('advancing into the gap at OBJ BRAVO')")
    _, z = lua.eval("lastDestination('blue-reserve')")
    assert z == pytest.approx(lua.eval("FLD.frontLines[1].sectors[2].objZ"))
    # Defenders keep their reserve back.
    assert lua.eval("groupState('red-reserve')") == "RESERVE"


def test_defensive_side_holds_against_a_dented_attack(lua: Any) -> None:
    lua.execute("setupBattle('DEFENSIVE', 'AGGRESSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 2)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    assert lua.eval("groupState('blue-tank')") != "EXPLOITING"


def test_defensive_side_counter_attacks_a_broken_attack(lua: Any) -> None:
    lua.execute("setupBattle('DEFENSIVE', 'AGGRESSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("kill('red-reserve', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    assert lua.eval("groupState('blue-tank')") == "EXPLOITING"
    assert lua.eval("said('counter-attacking toward')")

    # One bound only, then the defenders hold again.
    first = lua.eval("lastDestination('blue-tank')")
    lua.execute(f"moveTo('blue-tank', {first[0]}, {first[1]})")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 90)")
    assert lua.eval("lastDestination('blue-tank')") == first


def test_idle_attackers_go_looking_for_the_enemy(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    # Red falls back out of contact but is not beaten yet.
    lua.execute("moveTo('red-tank', 6000, 2000)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    assert lua.eval("groupState('blue-tank')") == "HOLDING"

    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    assert lua.eval("groupState('blue-tank')") == "ATTACKING"
    x, z = lua.eval("lastDestination('blue-tank')")
    assert x == 6000


def test_reserve_follows_up_a_breakthrough(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("kill('red-tank', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    target = lua.eval("lastDestination('blue-tank')")

    lua.execute("FLD.tickFront(FLD.frontLines[1], 200)")
    assert lua.eval("groupState('blue-reserve')") == "EXPLOITING"
    assert lua.eval("lastDestination('blue-reserve')") == target
    assert lua.eval("said('following up the breakthrough at OBJ ALPHA')")


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


EVENTS = """
function setupEvents(events, extraGroups)
    spawn("blue-tank", -3000, 0, 4)
    spawn("blue-reserve", -6000, 0, 4)
    spawn("red-tank", 3000, 0, 4)
    spawn("red-reserve", 6000, 0, 4)
    local data = plan('AGGRESSIVE', 'DEFENSIVE', extraGroups)
    data.frontLines[1].events = events
    FLD.start(data)
end

function taskFor(side, fragment)
    for _, task in ipairs(FLD.tasks[side]) do
        if string.find(task.title, fragment, 1, true) then return task end
    end
end
"""


@pytest.fixture
def events(arty: Any) -> Any:
    arty.execute(EVENTS)
    return arty


def test_flanking_raid_goes_for_the_enemy_guns(events: Any) -> None:
    events.execute("""
        spawn("blue-raid", -6000, 9000, 3)
        spawn("red-arty", 15000, 0, 4)
        setupEvents({{kind = "FLANK", side = "blue", destinationX = "0", destinationZ = "0",
                      groups = {{name = "blue-raid", role = "TANK"}}}},
                    {{name = "red-arty", side = "red", role = "ARTILLERY", reserve = "false", range = "30000"}})
        FLD.frontLines[1].events[1].fireAt = 100
        FLD.tickFront(FLD.frontLines[1], 50)
    """)
    # Not before its time, and inactive until then.
    assert events.eval("mockGroups['blue-raid'].active") is None
    assert events.eval("groupState('blue-raid')") is None

    events.execute("FLD.tickFront(FLD.frontLines[1], 120)")
    assert events.eval("mockGroups['blue-raid'].active") is True
    assert events.eval("groupState('blue-raid')") == "RAIDING"
    assert events.eval("lastDestination('blue-raid')") == pytest.approx((15000, 10))
    assert events.eval("said('flanking raid launched toward the enemy artillery')")
    # Red gets an urgent intercept tasking with a moving map mark.
    task = events.eval("taskFor('red', 'Enemy armor is flanking toward our artillery')")
    assert task is not None and task.kind == "DESTROY"
    assert events.eval(f"taskMarks[{task.markId}].side") == 1

    events.execute("kill('blue-raid', 3)")
    events.execute("FLD.updateTasks(150)")
    assert events.eval("taskFor('red', 'Enemy armor is flanking').status") == "COMPLETE"
    assert events.eval("said('TASKING COMPLETE')")


def test_reinforcement_column_joins_the_reserve(events: Any) -> None:
    events.execute("""
        spawn("red-column-1", 20000, 0, 4)
        spawn("red-column-2", 20300, 0, 4)
        setupEvents({{kind = "COLUMN", side = "red", destinationX = "8000", destinationZ = "0",
                      groups = {{name = "red-column-1", role = "TANK"}, {name = "red-column-2", role = "IFV"}}}})
        FLD.frontLines[1].events[1].fireAt = 10
        FLD.tickFront(FLD.frontLines[1], 30)
    """)
    assert events.eval("groupState('red-column-1')") == "ARRIVING"
    assert (
        events.eval("lastTask('red-column-1').params.route.points[2].action")
        == "On Road"
    )
    interdict = events.eval("taskFor('blue', 'reinforcement column on the road')")
    escort = events.eval("taskFor('red', 'keep it safe')")
    assert interdict is not None and escort is not None

    events.execute("""
        moveTo('red-column-1', 8100, 0)
        moveTo('red-column-2', 8200, 0)
        FLD.tickFront(FLD.frontLines[1], 60)
        FLD.updateTasks(60)
    """)
    assert events.eval("groupState('red-column-1')") == "RESERVE"
    assert events.eval("said('joins the reserve')")
    assert (
        events.eval("taskFor('blue', 'reinforcement column on the road').status")
        == "FAILED"
    )
    assert events.eval("taskFor('red', 'keep it safe').status") == "COMPLETE"
    # The new reserve can be committed like any other.
    assert "Reserve task force groups available: 3" in events.eval(
        "FLD.statusText('red')"
    )


def test_interdicted_column_completes_the_tasking(events: Any) -> None:
    events.execute("""
        spawn("red-column-1", 20000, 0, 4)
        setupEvents({{kind = "COLUMN", side = "red", destinationX = "8000", destinationZ = "0",
                      groups = {{name = "red-column-1", role = "TANK"}}}})
        FLD.frontLines[1].events[1].fireAt = 10
        FLD.tickFront(FLD.frontLines[1], 30)
        kill('red-column-1', 4)
        FLD.tickFront(FLD.frontLines[1], 60)
        FLD.updateTasks(60)
    """)
    assert events.eval("taskFor('blue', 'reinforcement column').status") == "COMPLETE"
    assert events.eval("taskFor('red', 'keep it safe').status") == "FAILED"


def test_events_respect_options_and_static_units(events: Any) -> None:
    events.execute("""
        spawn("blue-raid", -6000, 9000, 3)
        FLD.config.popupEvents = false
        setupEvents({{kind = "FLANK", side = "blue", destinationX = "0", destinationZ = "0",
                      groups = {{name = "blue-raid", role = "TANK"}}}})
        FLD.frontLines[1].events[1].fireAt = 10
        FLD.tickFront(FLD.frontLines[1], 30)
    """)
    assert events.eval("mockGroups['blue-raid'].active") is None
    assert events.eval("#FLD.tasks.red") == 0


def test_troops_in_contact_tasking(events: Any) -> None:
    events.execute("""
        setupEvents({})
        moveTo('blue-tank', 1000, 0)
        FLD.tickFront(FLD.frontLines[1], 30)
        kill('blue-tank', 2)
        moveTo('red-tank', 1100, 0)
        FLD.tickFront(FLD.frontLines[1], 60)
    """)
    task = events.eval("taskFor('blue', 'Troops in contact at OBJ ALPHA')")
    assert task is not None and task.kind == "DEFEND"
    assert events.eval("said('POP-UP TASKING')")
    assert "Troops in contact" in events.eval("FLD.tasksText('blue')")

    # The red tank is driven off: the objective holds.
    events.execute("kill('red-tank', 4)")
    events.execute("FLD.tickFront(FLD.frontLines[1], 90)")
    events.execute("FLD.updateTasks(90)")
    assert events.eval("taskFor('blue', 'Troops in contact').status") == "COMPLETE"
    assert events.eval(f"taskMarks[{task.id}]") is None


def test_battlefield_taskings_respect_the_cooldown(events: Any) -> None:
    events.execute("""
        spawn("red-shorad", 2500, 500, 1)
        spawn("red-arty", 15000, 0, 4)
        setupEvents({}, {
            {name = "red-shorad", side = "red", role = "SHORAD", sector = "1", reserve = "false"},
            {name = "red-arty", side = "red", role = "ARTILLERY", reserve = "false", range = "30000"},
        })
        FLD.batteryFired('red-arty', 0)
        FLD.tickFront(FLD.frontLines[1], 60)
    """)
    assert events.eval("#FLD.tasks.blue") == 1
    events.execute("FLD.tickFront(FLD.frontLines[1], 90)")
    assert events.eval("#FLD.tasks.blue") == 1
    events.execute("FLD.tickFront(FLD.frontLines[1], 400)")
    assert events.eval("#FLD.tasks.blue") == 2
    assert events.eval("taskFor('blue', 'artillery battery located')") is not None
    assert events.eval("taskFor('blue', 'air defence spotted')") is not None


def test_wrecks_burn_then_smoulder_then_go_out(events: Any) -> None:
    events.execute("""
        setupEvents({})
        FLD.onUnitDestroyed(deadUnit(500, 0, true), 100)
        FLD.onUnitDestroyed(deadUnit(500, 0, true), 101)
        FLD.onUnitDestroyed(deadUnit(400, 0, false), 100)
        FLD.onUnitDestroyed(deadUnit(90000, 0, true), 100)
        FLD.onUnitDestroyed(deadUnit(600, 0, true, Unit.Category.AIRPLANE), 100)
    """)
    # One fire per wreck near the fighting, nothing far away or for aircraft.
    assert events.eval("effectCount()") == 2
    assert events.eval("FLD.fires[1].phase") == "BURNING"
    assert events.eval("effects[FLD.fires[1].effect].preset") in (1, 2)

    events.execute("FLD.updateFires(100 + FLD.config.burnSecondsMax)")
    assert events.eval("effectCount()") == 2
    assert events.eval("FLD.fires[1].phase") == "SMOULDERING"
    assert events.eval("effects[FLD.fires[1].effect].preset") == 5

    events.execute(
        "FLD.updateFires(100 + FLD.config.burnSecondsMax + FLD.config.smoulderSecondsMax + 1)"
    )
    assert events.eval("effectCount()") == 0
    assert events.eval("#FLD.fires") == 0


def test_battle_fires_are_capped(events: Any) -> None:
    events.execute("""
        setupEvents({})
        FLD.config.maxBattleFires = 3
        for i = 1, 5 do FLD.onUnitDestroyed(deadUnit(i * 100, 0, true), 100) end
    """)
    assert events.eval("effectCount()") == 3
    assert events.eval("#FLD.fires") == 3


def test_generated_events_load_in_lua(lua: Any) -> None:
    mission_data = MissionData()
    mission_data.front_line_director.append(
        FrontLineDirectorInfo(
            name="A/B",
            sectors=[FrontLineSectorInfo(0.0, 0.0, 6000)],
            blue=FrontLineSideInfo("AGGRESSIVE", 0, 0, 30000.0, 0.0),
            red=FrontLineSideInfo("DEFENSIVE", None, 180, -30000.0, 0.0),
            groups=[],
            events=[
                FrontLineEventInfo(
                    kind="COLUMN",
                    side="red",
                    groups=[
                        FrontLineGroupInfo("red-col", "red", "TANK", None, False),
                        FrontLineGroupInfo("red-aa", "red", "SHORAD", None, False),
                    ],
                    destination_x=8000.0,
                    destination_y=-50.0,
                )
            ],
        )
    )
    game = cast(Game, SimpleNamespace(settings=Settings()))
    lua_data = LuaData("dcsRetribution")
    LuaGenerator(game, cast(Any, None), mission_data).generate_front_line_director_data(
        lua_data
    )
    lua.execute(lua_data.create_operations_lua())
    lua.execute("FLD.start(dcsRetribution.FrontLineDirector)")

    event = lua.eval("FLD.frontLines[1].events[1]")
    assert event.kind == "COLUMN" and event.side == "red"
    assert (event.destX, event.destZ) == (8000, -50)
    assert lua.eval("FLD.frontLines[1].events[1].groups[2].role") == "SHORAD"
    assert 480 <= event.fireAt <= 2400


def test_column_alive_when_time_runs_out_was_kept_safe(events: Any) -> None:
    events.execute("""
        spawn("red-column-1", 20000, 0, 4)
        setupEvents({{kind = "COLUMN", side = "red", destinationX = "8000", destinationZ = "0",
                      groups = {{name = "red-column-1", role = "TANK"}}}})
        FLD.frontLines[1].events[1].fireAt = 10
        FLD.tickFront(FLD.frontLines[1], 30)
        FLD.updateTasks(30 + FLD.config.taskDurationSeconds)
    """)
    assert events.eval("taskFor('red', 'keep it safe').status") == "COMPLETE"
    assert events.eval("taskFor('blue', 'reinforcement column').status") == "FAILED"


def test_located_battery_is_announced_once(arty: Any) -> None:
    arty.execute("""
        setupArtillery('AGGRESSIVE', 'DEFENSIVE')
        FLD.batteryFired('red-arty', 0)
        FLD.config.fireMissionSeconds = 0
        FLD.config.relocateSeconds = 0
        FLD.config.retargetSeconds = 0
        for t = 60, 600, 30 do
            FLD.runArtillery(FLD.frontLines[1], 'blue', t)
        end
        announced = 0
        for _, m in ipairs(messages) do
            if string.find(m.text, "counter-battery", 1, true) then announced = announced + 1 end
        end
    """)
    assert arty.eval("battery('blue-arty').missions") > 1
    assert arty.eval("announced") == 1


def start_with_battery(lua: Any, x: float, z: float) -> None:
    lua.execute(f"""
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        spawn("blue-arty", {x}, {z}, 4)
        FLD.start(plan('AGGRESSIVE', 'DEFENSIVE', {{
            {{name = "blue-arty", side = "blue", role = "ARTILLERY", reserve = "false", range = "30000"}},
        }}))
    """)


def test_battery_on_a_slope_moves_to_flat_ground(lua: Any) -> None:
    start_with_battery(lua, 1500, 0)
    x, z = lua.eval("lastDestination('blue-arty')")
    assert lua.eval(f"FLD.terrain.slope({x}, {z})") <= 0.1
    assert lua.eval("FLD.frontLines[1].groups[5].artyState") == "MOVING"


def test_battery_on_open_flat_ground_stays(lua: Any) -> None:
    start_with_battery(lua, -15000, 0)
    assert lua.eval("lastDestination('blue-arty')") is None


def test_battery_prefers_a_roadside_position(lua: Any) -> None:
    lua.execute("roadZ = 400")
    start_with_battery(lua, -15000, 0)
    assert lua.eval("lastDestination('blue-arty')") == (-15000, 400)


def test_battery_moves_away_from_buildings(lua: Any) -> None:
    lua.execute("table.insert(buildings, {x = -15000, z = 20})")
    start_with_battery(lua, -15000, 0)
    x, z = lua.eval("lastDestination('blue-arty')")
    assert ((x + 15000) ** 2 + (z - 20) ** 2) ** 0.5 > 60


def test_idle_attackers_without_enemy_in_reach_push_on(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    # Red is far away but not beaten: no exploitation, nothing to engage.
    lua.execute("moveTo('red-tank', 20000, 0)")
    lua.execute("moveTo('red-reserve', 20000, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    assert lua.eval("groupState('blue-tank')") == "EXPLOITING"
    x, _ = lua.eval("lastDestination('blue-tank')")
    assert x > 3000
    assert lua.eval("said('no enemy in sight')")


def test_moving_groups_are_not_idle(lua: Any) -> None:
    lua.execute("setupBattle('AGGRESSIVE', 'DEFENSIVE')")
    lua.execute("moveTo('blue-tank', 1000, 0)")
    lua.execute("moveTo('red-tank', 20000, 0)")
    lua.execute("moveTo('red-reserve', 20000, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    for t, z in ((120, 200), (210, 400), (300, 600)):
        lua.execute(f"moveTo('blue-tank', 1000, {z})")
        lua.execute(f"FLD.tickFront(FLD.frontLines[1], {t})")
    assert lua.eval("groupState('blue-tank')") == "HOLDING"


def test_support_weapons_follow_the_assault(lua: Any) -> None:
    lua.execute("""
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        spawn("blue-atgm", -8000, 0, 2)
        FLD.start(plan('AGGRESSIVE', 'DEFENSIVE', {
            {name = "blue-atgm", side = "blue", role = "ATGM", sector = "1", reserve = "false"},
        }))
    """)
    lua.execute("FLD.frontLines[1].groups[1].state = 'HOLDING'")
    lua.execute("FLD.frontLines[1].groups[5].state = 'HOLDING'")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    # The tank goes for the red tank, the ATGM team overwatches from behind.
    assert lua.eval("groupState('blue-tank')") == "ATTACKING"
    assert lua.eval("lastDestination('blue-tank')")[0] == 3000
    assert lua.eval("groupState('blue-atgm')") == "ATTACKING"
    x, _ = lua.eval("lastDestination('blue-atgm')")
    assert -3000 < x < 3000 - 1000


def test_idle_defenders_shift_to_a_threatened_sector(lua: Any) -> None:
    lua.execute("""
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 1000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        spawn("blue-tank2", -500, 10000, 4)
        local data = plan('DEFENSIVE', 'AGGRESSIVE', {
            {name = "blue-tank2", side = "blue", role = "TANK", sector = "2", reserve = "false"},
        })
        table.insert(data.frontLines[1].sectors, {x = "0", z = "10000", width = "6000"})
        FLD.start(data)
    """)
    # Red takes OBJ ALPHA, BRAVO stays quiet.
    lua.execute("kill('blue-tank', 4)")
    lua.execute("kill('red-reserve', 4)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    assert lua.eval("FLD.frontLines[1].groups[5].sector") == 1
    assert lua.eval("said('shifts to reinforce OBJ ALPHA')")


def test_quiet_defenders_push_a_screen_forward_once(lua: Any) -> None:
    lua.execute("setupBattle('DEFENSIVE', 'AGGRESSIVE')")
    lua.execute("moveTo('red-tank', 20000, 0)")
    lua.execute("moveTo('red-reserve', 20000, 0)")
    holding_x, holding_z = lua.eval("lastDestination('blue-tank')")
    lua.execute(f"moveTo('blue-tank', {holding_x}, {holding_z})")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    x, _ = lua.eval("lastDestination('blue-tank')")
    assert x > holding_x + 500
    tasks = lua.eval("#mockGroups['blue-tank'].tasks")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 500)")
    assert lua.eval("#mockGroups['blue-tank'].tasks") == tasks


def start_with_air_defence(lua: Any, x: float, z: float) -> None:
    lua.execute(f"""
        spawn("blue-tank", -3000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 3000, 0, 4)
        spawn("red-reserve", 6000, 0, 4)
        spawn("blue-sam", {x}, {z}, 1)
        FLD.start(plan('AGGRESSIVE', 'DEFENSIVE', {{
            {{name = "blue-sam", side = "blue", role = "SHORAD", sector = "1", reserve = "false"}},
        }}))
    """)


def test_air_defence_in_position_stays(lua: Any) -> None:
    start_with_air_defence(lua, -4500, 0)
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    assert lua.eval("lastDestination('blue-sam')") is None


def test_air_defence_follows_the_advance_a_bit_behind(lua: Any) -> None:
    start_with_air_defence(lua, -4500, 0)
    lua.execute("moveTo('red-tank', 12000, 0)")
    lua.execute("moveTo('red-reserve', 12000, 0)")
    lua.execute("moveTo('blue-tank', 4000, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    x, _ = lua.eval("lastDestination('blue-sam')")
    # Behind the tanks, but well forward of where it was.
    assert 1000 < x < 4000


def test_air_defence_keeps_away_from_the_enemy(lua: Any) -> None:
    start_with_air_defence(lua, -8000, 0)
    lua.execute("moveTo('blue-tank', 2000, 0)")
    lua.execute("moveTo('red-tank', 1500, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    x, _ = lua.eval("lastDestination('blue-sam')")
    assert x < 1500 - 2500 + 800


def test_air_defence_bounds_rather_than_moving_constantly(lua: Any) -> None:
    start_with_air_defence(lua, -4500, 0)
    lua.execute("moveTo('red-tank', 12000, 0)")
    lua.execute("moveTo('red-reserve', 12000, 0)")
    lua.execute("moveTo('blue-tank', 4000, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("moveTo('blue-tank', 7000, 0)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 60)")
    assert lua.eval("#mockGroups['blue-sam'].tasks") == 1
    lua.execute("FLD.tickFront(FLD.frontLines[1], 160)")
    assert lua.eval("#mockGroups['blue-sam'].tasks") == 2


def test_idle_task_force_moves_together(lua: Any) -> None:
    # Two groups reach the objective a few minutes apart.
    lua.execute("""
        spawn("blue-tank", 1000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 7000, 0, 4)
        spawn("red-reserve", 20000, 0, 4)
        spawn("blue-ifv", -2000, 0, 4)
        FLD.start(plan('AGGRESSIVE', 'DEFENSIVE', {
            {name = "blue-ifv", side = "blue", role = "IFV", sector = "1", reserve = "false"},
        }))
    """)
    lua.execute("FLD.tickFront(FLD.frontLines[1], 30)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 120)")
    lua.execute("moveTo('blue-ifv', 1000, 400)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 150)")
    # The tank waited long enough on its own, but the IFV just arrived.
    lua.execute("FLD.tickFront(FLD.frontLines[1], 240)")
    lua.execute("FLD.tickFront(FLD.frontLines[1], 330)")
    assert lua.eval("groupState('blue-tank')") != "ATTACKING"
    lua.execute("FLD.tickFront(FLD.frontLines[1], 420)")
    assert lua.eval("groupState('blue-tank')") == "ATTACKING"
    assert lua.eval("groupState('blue-ifv')") == "ATTACKING"
    assert lua.eval("countSaid('moves to engage')") == 1


def test_one_group_in_contact_holds_the_task_force(lua: Any) -> None:
    lua.execute("""
        spawn("blue-tank", 1000, 0, 4)
        spawn("blue-reserve", -6000, 0, 4)
        spawn("red-tank", 9000, 0, 4)
        spawn("red-reserve", 20000, 0, 4)
        spawn("blue-ifv", 7000, 0, 4)
        FLD.start(plan('AGGRESSIVE', 'DEFENSIVE', {
            {name = "blue-ifv", side = "blue", role = "IFV", sector = "1", reserve = "false"},
        }))
    """)
    for t in (30, 120, 240, 330):
        lua.execute(f"FLD.tickFront(FLD.frontLines[1], {t})")
    assert lua.eval("groupState('blue-tank')") == "HOLDING"


def test_dead_infantry_leaves_no_smoke(events: Any) -> None:
    events.execute("setupEvents({})")
    events.execute("FLD.onUnitDestroyed(deadUnit(500, 0, false, nil, true), 100)")
    assert events.eval("effectCount()") == 0
    events.execute("FLD.onUnitDestroyed(deadUnit(600, 0, false), 100)")
    assert events.eval("effectCount()") == 1
