"""Behaviour tests for the Tactical AI Lua plugin.

The plugin script is run in Lua 5.1 (the version DCS uses) against a small fake
of the DCS scripting API, so these tests pin what the script decides: who
commits on what, when a commit ends, who retreats, which strikes abort and when
strikers may jettison.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest

from game.plugins import LuaPluginManager

# DCS runs Lua 5.1. Imported dynamically so the type check passes whether or not
# the installed lupa ships type information.
lupa: Any = importlib.import_module("lupa.lua51")

SCRIPT = Path("resources/plugins/tacticalai/tacticalai.lua")
NM = 1852

# A minimal fake of the DCS mission scripting environment. Tests build the world
# with makeUnit/makeGroup and read back what the script did from each group's
# controller log.
FAKE_DCS = r"""
env = { info = function() end, error = function(message) error(message) end }
trigger = { action = { outText = function() end } }
timer = {
    getTime = function() return 0 end,
    scheduleFunction = function() end,
}
Weapon = { Category = { MISSILE = 1 }, MissileCategory = { AAM = 1 } }
Object = { Category = { UNIT = 1 } }
Group = { Category = { GROUND = 2 } }
Controller = { Detection = { VISUAL = 1, OPTIC = 2, RADAR = 4, IRST = 8, DLINK = 32 } }
AI = { Option = { Air = {
    id = { ROE = 0, REACTION_ON_THREAT = 1, PROHIBIT_JETTISON = 15 },
    val = {
        ROE = { RETURN_FIRE = 3 },
        REACTION_ON_THREAT = { BYPASS_AND_ESCAPE = 3 },
    },
} } }

units, groups, routes = {}, {}, {}
coalition = { getGroups = function() return {} end }
mist = {
    DBs = { unitsByName = {} },
    utils = { deepCopy = function(t)
        local copy = {}
        for k, v in pairs(t) do copy[k] = v end
        return copy
    end },
    getGroupRoute = function(name) return routes[name] end,
}

Unit = {
    Category = { AIRPLANE = 0, HELICOPTER = 1 },
    getByName = function(name) return units[name] end,
}
Group.getByName = function(name) return groups[name] end

function makeUnit(name, side, x, z, attributes, missiles)
    local unit = { name = name, side = side, x = x, z = z, alive = true,
                   attributes = attributes or {}, missiles = missiles or 0 }
    function unit:isExist() return self.alive end
    function unit:getLife() return self.alive and 10 or 0 end
    function unit:getPoint() return { x = self.x, y = 5000, z = self.z } end
    function unit:inAir() return true end
    function unit:getName() return self.name end
    function unit:getCoalition() return self.side end
    function unit:getCategory() return Object.Category.UNIT end
    function unit:getDesc() return { category = Unit.Category.AIRPLANE } end
    function unit:getGroup() return self.group end
    function unit:hasAttribute(attribute) return self.attributes[attribute] == true end
    function unit:getAmmo()
        return { { count = self.missiles,
                   desc = { category = 1, missileCategory = 1 } } }
    end
    units[name] = unit
    return unit
end

function makeGroup(name, id, unitList)
    local controller = { pushed = {}, popped = 0, tasks = {}, options = {}, detected = {} }
    function controller:pushTask(task) table.insert(self.pushed, task) end
    function controller:popTask() self.popped = self.popped + 1 end
    function controller:setTask(task) table.insert(self.tasks, task) end
    function controller:setOption(id, value) self.options[id] = value end
    function controller:getDetectedTargets() return self.detected end
    local group = { name = name, id = id, units = unitList, controller = controller }
    function group:isExist()
        for _, unit in ipairs(self.units) do if unit.alive then return true end end
        return false
    end
    function group:getUnits() return self.units end
    function group:getName() return self.name end
    function group:getID() return self.id end
    function group:getController() return self.controller end
    for _, unit in ipairs(unitList) do
        unit.group = group
        mist.DBs.unitsByName[unit.name] = { groupName = name }
    end
    groups[name] = group
    return group
end

-- Every group sees every unit of the other side.
function detectEverything()
    for _, group in pairs(groups) do
        local detected = {}
        for _, unit in pairs(units) do
            if unit.side ~= group.units[1].side then
                table.insert(detected, { object = unit })
            end
        end
        group.controller.detected = detected
    end
end

function kill(groupName)
    for _, unit in ipairs(groups[groupName].units) do unit.alive = false end
end
"""

FIGHTER = "{ Fighters = true }"


class World:
    def __init__(self) -> None:
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(FAKE_DCS)
        self.lua.execute(SCRIPT.read_text())
        self.flights: list[str] = []

    def group(
        self,
        name: str,
        side: int,
        gid: int,
        count: int,
        x_nm: float,
        z_nm: float = 0,
        missiles: int = 4,
        attributes: str = FIGHTER,
    ) -> None:
        unit_defs = ", ".join(
            f'makeUnit("{name}-{i}", {side}, {x_nm * NM}, {z_nm * NM}, '
            f"{attributes}, {missiles})"
            for i in range(count)
        )
        self.lua.execute(f'makeGroup("{name}", {gid}, {{ {unit_defs} }})')
        self.lua.execute(
            f'routes["{name}"] = {{ {{ name = "WP1", type = "Turning Point" }}, '
            f'{{ name = "LAND", type = "Land", airdromeId = 7 }} }}'
        )

    def flight(self, name: str, side: int, role: str, count: int, **extra: Any) -> None:
        units = ", ".join(f'"{name}-{i}"' for i in range(count))
        fields = [f"units = {{ {units} }}", f'side = "{side}"', f'role = "{role}"']
        for key, value in extra.items():
            fields.append(f'{key} = "{value}"')
        self.flights.append("{ " + ", ".join(fields) + " }")

    def start(self, **options: Any) -> None:
        opts = ", ".join(f"{k} = {str(v).lower()}" for k, v in options.items())
        self.lua.execute(
            "dcsRetribution = { TacticalAI = { flights = { "
            + ", ".join(self.flights)
            + f" }} }}, plugins = {{ tacticalai = {{ {opts} }} }} }}"
        )

    def update(self, now: float) -> None:
        self.lua.execute("detectEverything()")
        self.lua.eval("TacticalAI.update")(now)

    def controller(self, name: str) -> Any:
        return self.lua.eval(f'groups["{name}"].controller')

    def mode(self, name: str) -> str:
        return self.lua.eval(f"""(function()
                for i, f in ipairs(TacticalAI.flights) do
                    if f.groupName == "{name}" then return TacticalAI.state[i].mode end
                end
            end)()""")

    def pushed_targets(self, name: str) -> list[int]:
        pushed = self.controller(name).pushed
        return [pushed[i].params.groupId for i in range(1, len(pushed) + 1)]

    def landed_route(self, name: str) -> Any:
        tasks = self.controller(name).tasks
        if len(tasks) == 0:
            return None
        return tasks[len(tasks)].params.route.points[1]


def test_plugin_is_registered_and_loads_its_script() -> None:
    plugin = next(
        p for p in LuaPluginManager.plugins() if p.definition.identifier == "tacticalai"
    )
    assert [w.filename for w in plugin.definition.work_orders] == ["tacticalai.lua"]
    assert not plugin.definition.enabled_by_default


def test_cap_commits_on_contact_inside_commit_range() -> None:
    world = World()
    world.group("CAP", 2, 1, 2, x_nm=0)
    world.group("BANDIT", 1, 50, 2, x_nm=40)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start()

    world.update(100)

    assert world.pushed_targets("CAP") == [50]
    assert world.mode("CAP") == "committed"


def test_cap_ignores_contact_outside_commit_range() -> None:
    world = World()
    world.group("CAP", 2, 1, 2, x_nm=0)
    world.group("BANDIT", 1, 50, 2, x_nm=70)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start(commitRangeNm=60)

    world.update(100)

    assert world.pushed_targets("CAP") == []


def test_cap_does_not_chase_past_its_leash() -> None:
    world = World()
    # The CAP has drifted towards the contact, which is far from the station.
    world.group("CAP", 2, 1, 2, x_nm=50)
    world.group("BANDIT", 1, 50, 2, x_nm=95)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start(leashRangeNm=80)

    world.update(100)

    assert world.pushed_targets("CAP") == []


def test_contacts_are_shared_out_between_caps() -> None:
    world = World()
    world.group("CAP1", 2, 1, 2, x_nm=0)
    world.group("CAP2", 2, 2, 2, x_nm=0, z_nm=5)
    world.group("PAIR", 1, 50, 2, x_nm=30)
    world.group("FOUR", 1, 51, 4, x_nm=40)
    world.flight("CAP1", 2, "cap", 2, anchorX=0, anchorY=0)
    world.flight("CAP2", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start()

    world.update(100)

    # The pair gets one CAP; the second CAP goes after the four-ship rather
    # than piling onto the pair.
    targets = sorted(world.pushed_targets("CAP1") + world.pushed_targets("CAP2"))
    assert targets == [50, 51]


def test_commit_ends_when_target_is_destroyed() -> None:
    world = World()
    world.group("CAP", 2, 1, 2, x_nm=0)
    world.group("BANDIT", 1, 50, 2, x_nm=40)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start()
    world.update(100)

    world.lua.execute('kill("BANDIT")')
    world.update(115)

    # DCS drops a finished AttackGroup task by itself; popping again would
    # remove the CAP's patrol mission.
    assert world.controller("CAP").popped == 0
    assert world.mode("CAP") == "normal"


def test_commit_is_called_off_when_target_leaves_the_leash() -> None:
    world = World()
    world.group("CAP", 2, 1, 2, x_nm=0)
    world.group("BANDIT", 1, 50, 2, x_nm=40)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start(leashRangeNm=80)
    world.update(100)

    world.lua.execute('groups["BANDIT"].units[1].x = 120 * 1852')
    world.update(115)

    assert world.controller("CAP").popped == 1
    assert world.mode("CAP") == "normal"


def test_commit_times_out() -> None:
    world = World()
    world.group("CAP", 2, 1, 2, x_nm=0)
    world.group("BANDIT", 1, 50, 2, x_nm=40)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start(maxCommitMinutes=5)
    world.update(100)

    world.update(100 + 4 * 60)
    assert world.controller("CAP").popped == 0
    world.update(100 + 6 * 60)
    assert world.controller("CAP").popped == 1


def test_cap_without_missiles_does_not_commit() -> None:
    world = World()
    world.group("CAP", 2, 1, 2, x_nm=0, missiles=0)
    world.group("BANDIT", 1, 50, 2, x_nm=40)
    world.flight("CAP", 2, "cap", 2, anchorX=0, anchorY=0)
    world.start(enableRetreat=False)

    world.update(100)

    assert world.pushed_targets("CAP") == []


def test_outnumbered_fighters_low_on_missiles_go_home() -> None:
    world = World()
    world.group("ESCORT", 2, 1, 2, x_nm=0, missiles=1)
    world.group("BANDITS", 1, 50, 4, x_nm=15)
    world.flight("ESCORT", 2, "fighter", 2, escort="true")
    world.start()

    world.update(100)

    assert world.mode("ESCORT") == "retreating"
    landing = world.landed_route("ESCORT")
    assert landing.type == "Land"
    assert landing.airdromeId == 7
    options = world.controller("ESCORT").options
    assert options[1] == 3  # bypass and escape
    assert options[0] == 3  # return fire only


def test_outnumbered_fighters_with_missiles_keep_fighting() -> None:
    world = World()
    world.group("ESCORT", 2, 1, 2, x_nm=0, missiles=4)
    world.group("BANDITS", 1, 50, 4, x_nm=15)
    world.flight("ESCORT", 2, "fighter", 2, escort="true")
    world.start()

    world.update(100)

    assert world.mode("ESCORT") == "normal"
    assert world.landed_route("ESCORT") is None


def _strike_package(world: World, striker_x_nm: float) -> None:
    world.group("STRIKE", 2, 1, 2, x_nm=striker_x_nm, attributes="{}")
    world.group("ESCORT", 2, 2, 2, x_nm=striker_x_nm, missiles=4)
    world.group("BANDITS", 1, 50, 2, x_nm=striker_x_nm + 20)
    world.flight("STRIKE", 2, "striker", 2, package="p1", targetX=0, targetY=0)
    world.flight("ESCORT", 2, "fighter", 2, package="p1", escort="true")


def test_strike_aborts_when_its_escort_is_lost() -> None:
    world = World()
    _strike_package(world, striker_x_nm=-60)
    world.start()
    world.update(100)
    assert world.mode("STRIKE") == "normal"

    world.lua.execute('kill("ESCORT")')
    world.update(115)

    assert world.mode("STRIKE") == "aborted"
    assert world.landed_route("STRIKE").type == "Land"
    # Aborting strikers may drop their bombs.
    assert world.controller("STRIKE").options[15] is False


def test_strike_in_the_target_area_presses_on() -> None:
    world = World()
    _strike_package(world, striker_x_nm=-10)
    world.start()
    world.update(100)

    world.lua.execute('kill("ESCORT")')
    world.update(115)

    assert world.mode("STRIKE") == "normal"


def test_unescorted_strike_presses_on_by_default() -> None:
    world = World()
    world.group("STRIKE", 2, 1, 2, x_nm=-60, attributes="{}")
    world.group("BANDITS", 1, 50, 2, x_nm=-40)
    world.flight("STRIKE", 2, "striker", 2, package="p1", targetX=0, targetY=0)
    world.start()

    world.update(100)

    assert world.mode("STRIKE") == "normal"


@pytest.mark.parametrize("bandit_distance_nm,cleared", [(10, True), (25, False)])
def test_strikers_cleared_to_jettison_when_fighters_close(
    bandit_distance_nm: float, cleared: bool
) -> None:
    world = World()
    world.group("STRIKE", 2, 1, 2, x_nm=-60, attributes="{}")
    world.group("BANDITS", 1, 50, 1, x_nm=-60 + bandit_distance_nm)
    world.flight("STRIKE", 2, "striker", 2, package="p1", targetX=0, targetY=0)
    world.start(jettisonRangeNm=15)

    world.update(100)

    assert (world.controller("STRIKE").options[15] is False) == cleared


def test_escort_leash_leaves_managed_groups_alone() -> None:
    world = World()
    world.group("ESCORT", 2, 1, 2, x_nm=0, missiles=1)
    world.group("BANDITS", 1, 50, 4, x_nm=15)
    world.flight("ESCORT", 2, "fighter", 2, escort="true")
    world.start()
    world.update(100)

    assert world.lua.eval('TacticalAI.isManaged("ESCORT")') is True
    assert world.lua.eval('TacticalAI.isManaged("BANDITS")') is False
