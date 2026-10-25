-------------------------------------------------------------------------------
-- Front line director for DCS Retribution
--
-- Fights the front line battle while the mission runs. DCS Retribution plans
-- each front line in sectors (see game/ground_forces/frontline_sectors.py):
-- every sector has an objective both sides fight over, an attacking side has a
-- main effort sector and both sides keep part of their armor back as a reserve
-- task force. This script:
--
--   * picks the key terrain (high ground) of every sector as its objective,
--   * puts defenders and consolidating attackers in hull-down battle positions
--     that can see the enemy approach, and hides reserves in dead ground,
--   * tracks who holds each objective and how strong each side is per sector,
--   * withdraws broken groups to cover,
--   * commits reserve task forces to counter-attack lost objectives or
--     reinforce failing sectors,
--   * exploits a collapsed or undefended enemy sector by pushing from high
--     ground to high ground toward the enemy base while nothing stops it,
--     follows a breakthrough up with the reserve and sends attackers into
--     gaps in the line; attackers out of contact go looking for the enemy and
--     defenders counter-attack an attack that broke,
--   * pursues an enemy falling back all the way to its base in one push,
--   * moves air defence with the groups it covers, a bit behind them,
--   * moves the groups of a sector as one task force: it waits for its
--     stragglers before bounding on and keeps busy when idle: attackers
--     hunt the enemy or push on,
--     support weapons follow them up, defenders shift to threatened sectors
--     or push a screen forward,
--   * springs ambushes: ambushing groups hold fire until the enemy is close,
--   * runs the front line artillery: batteries deploy on flat, open ground
--     (beside a road where possible, away from buildings) and fire on enemies friendly units
--     (or players' aircraft) actually see, by priority (counter-battery, air
--     defence, counter-attacks, contested objectives), never danger close, and
--     relocate after every fire mission because firing reveals them to the
--     enemy's counter-battery fire,
--   * springs pop-up events with forces the mission generator drew from each
--     side's undeployed inventory: flanking raids and reinforcement columns,
--   * raises pop-up taskings from what happens on the battlefield (troops in
--     contact, located batteries, breakthroughs, raids, columns, air defence)
--     with a grid, an F10 mark and a completed or failed outcome,
--   * sets destroyed vehicles burning where they died; fires die down to
--     smouldering smoke and then go out.
--
-- The plan is read from dcsRetribution.FrontLineDirector, set by the mission
-- generator. Configuration is set by frontline-director-config.lua, which
-- also starts the director by calling FLD.init().
-------------------------------------------------------------------------------

FLD = FLD or {}

FLD.config = {
    -- Seconds between two director decisions.
    tickSeconds = 30,
    -- Delay before the first positioning orders, so groups exist and reformed.
    startDelaySeconds = 5,
    -- Radius around an objective a side must hold to control it.
    objectiveRadius = 800,
    -- Radius around the sector center searched for key terrain.
    keyTerrainRadius = 1500,
    -- Seconds between two reserve commitments of one side on one front.
    commitCooldownSeconds = 120,
    -- Reserve groups committed together as one task force.
    taskForceSize = 2,
    -- A sector whose enemy strength drops below this share is exploited.
    exploitEnemyStrength = 0.5,
    -- Our strength share needed to exploit.
    exploitFriendlyStrength = 0.4,
    -- Defenders go over to the counter-attack when the attackers in front of
    -- them drop below this share.
    counterOffensiveEnemyStrength = 0.25,
    -- Distance pushed past the objective when exploiting.
    exploitDistance = 4000,
    -- The enemy base is the exploitation target when it is this close.
    exploitBaseDistance = 15000,
    -- An exploiting group this close to its target pushes on to the next one.
    exploitArrivalDistance = 600,
    -- Exploiting groups stop to fight enemies this close before pushing on.
    exploitContactDistance = 3000,
    -- A group that moved less than idleMoveDistance in idleSeconds while out
    -- of contact is idle and is given something to do.
    idleSeconds = 180,
    idleMoveDistance = 100,
    -- How far idle attackers look for an enemy to engage.
    seekContactRange = 8000,
    -- How far idle defenders push a screen ahead of their objective.
    screenDistance = 1500,
    -- Seconds an exploiting task force waits for its stragglers before the
    -- groups that arrived push on to the next bound.
    regroupSeconds = 120,
    -- Lateral spacing of the groups of a task force on the move.
    taskForceSpacing = 300,
    -- How far behind the assault the support weapons of a task force follow.
    supportStandoff = 2000,
    -- Air defence follows the groups it covers this far behind them, never
    -- closer than airDefenceEnemyDistance to the enemy. It bounds forward
    -- when its position is airDefenceMoveDistance off, at most once per
    -- airDefenceMoveCooldown seconds, so it spends most of its time ready.
    airDefenceStandoff = 1500,
    airDefenceEnemyDistance = 2500,
    airDefenceMoveDistance = 1000,
    airDefenceMoveCooldown = 120,
    -- Artillery firing positions: searched this far around the battery, at
    -- most this steep (rise over run), and preferably this close to a road,
    -- where no trees cover the guns.
    firingPositionRadius = 800,
    maxFiringSlope = 0.1,
    firingRoadDistance = 30,
    -- A friendly sector below this strength share asks for reinforcement.
    reinforceStrength = 0.5,
    -- Group strength share at which a group breaks, randomized in this range.
    breakPointMin = 0.3,
    breakPointMax = 0.5,
    -- Distance a broken group falls back.
    withdrawDistance = 2500,
    -- Ambushing groups open fire on enemies closer than this.
    ambushRange = 1500,
    -- Front line artillery fire missions.
    artilleryStrikes = true,
    -- Blue batteries are left to the players when a player-called artillery
    -- plugin is enabled.
    playerArtillery = false,
    -- Ground units spot enemies with line of sight this close.
    spotRange = 6000,
    -- Players' aircraft spot enemies with line of sight this close.
    aircraftSpotRange = 10000,
    -- Batteries never fire this close to friendly units.
    dangerCloseDistance = 400,
    -- Seconds a battery spends on one fire mission.
    fireMissionSeconds = 90,
    -- Seconds a battery needs to relocate after firing.
    relocateSeconds = 150,
    relocateDistance = 800,
    -- Seconds until the enemy locates a battery that fired.
    counterBatteryDelay = 45,
    -- Seconds a located battery stays a counter-battery target.
    counterBatteryMemory = 300,
    -- Seconds before a target is fired on again by another battery.
    retargetSeconds = 120,
    maxFireMissions = 6,
    fireMissionRadius = 150,
    -- Pop-up events and taskings.
    popupEvents = true,
    -- Seconds into the mission when events may fire.
    eventWindowMin = 480,
    eventWindowMax = 2400,
    -- Seconds between two new battlefield taskings of one side.
    taskCooldownSeconds = 240,
    maxActiveTasks = 3,
    taskDurationSeconds = 1200,
    -- A column within this distance of its destination has arrived.
    columnArrivalDistance = 500,
    -- Burning wrecks.
    battleSmoke = true,
    maxBattleFires = 30,
    -- Only vehicles destroyed this close to an objective are set burning.
    battleSmokeRange = 15000,
    burnSecondsMin = 360,
    burnSecondsMax = 720,
    smoulderSecondsMin = 900,
    smoulderSecondsMax = 1500,
    showMarks = true,
    messages = true,
    statusMenu = true,
    debug = false,
}

local SPEED_REPOSITION = 8
local SPEED_ASSAULT = 12
local SPEED_WITHDRAW = 15

local MARK_ID_BASE = 7300000

local MANEUVER_ROLES = {
    TANK = true,
    IFV = true,
    APC = true,
    ATGM = true,
    RECON = true,
    INFANTRY = true,
}

-- Roles that take part in counter-attacks and exploitation.
local ASSAULT_ROLES = { TANK = true, IFV = true, APC = true, RECON = true }

local OFFENSIVE_STANCES = { AGGRESSIVE = true, ELIMINATION = true, BREAKTHROUGH = true }

local PHONETIC = { "ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO", "FOXTROT" }

local OTHER_SIDE = { blue = "red", red = "blue" }

local MARK_COLORS = {
    blue = { line = { 0.1, 0.3, 1, 0.9 }, fill = { 0.1, 0.3, 1, 0.15 } },
    red = { line = { 1, 0.1, 0.1, 0.9 }, fill = { 1, 0.1, 0.1, 0.15 } },
    contested = { line = { 1, 0.8, 0, 0.9 }, fill = { 1, 0.8, 0, 0.15 } },
    neutral = { line = { 0.6, 0.6, 0.6, 0.9 }, fill = { 0.6, 0.6, 0.6, 0.1 } },
}

FLD.frontLines = {}
FLD.movingUnits = true
FLD.nextMarkId = MARK_ID_BASE

local function log(message)
    env.info("DCSRetribution|Front line director: " .. message)
end

local function debug(message)
    if FLD.config.debug then
        log(message)
    end
end

local function coalitionOf(sideName)
    if sideName == "blue" then
        return coalition.side.BLUE
    end
    return coalition.side.RED
end

local function say(sideName, text)
    if FLD.config.messages then
        trigger.action.outTextForCoalition(coalitionOf(sideName), text, 15)
    end
end

local function distance(x1, z1, x2, z2)
    local dx = x1 - x2
    local dz = z1 - z2
    return math.sqrt(dx * dx + dz * dz)
end

local function toBool(value)
    return value == true or value == "true"
end

-------------------------------------------------------------------------------
-- Terrain analysis
-------------------------------------------------------------------------------

FLD.terrain = {}
local T = FLD.terrain

-- Headings follow DCS: 0 is north (+x), 90 is east (+z).
function T.offset(x, z, headingDeg, dist)
    local r = math.rad(headingDeg)
    return x + dist * math.cos(r), z + dist * math.sin(r)
end

function T.height(x, z)
    return land.getHeight({ x = x, y = z })
end

function T.isGround(x, z)
    local surface = land.getSurfaceType({ x = x, y = z })
    return surface == land.SurfaceType.LAND or surface == land.SurfaceType.ROAD
end

function T.isRoad(x, z)
    return land.getSurfaceType({ x = x, y = z }) == land.SurfaceType.ROAD
end

-- Line of sight between two points, eyes the given heights above ground.
function T.visible(x1, z1, eye1, x2, z2, eye2)
    return land.isVisible(
        { x = x1, y = T.height(x1, z1) + eye1, z = z1 },
        { x = x2, y = T.height(x2, z2) + eye2, z = z2 }
    )
end

-- The highest ground near a point, preferring close ground on ties.
function T.findKeyTerrain(cx, cz, radius)
    local bestX, bestZ, bestScore, bestH = cx, cz, nil, T.height(cx, cz)
    local rings = { 0, radius / 3, radius * 2 / 3, radius }
    for _, r in ipairs(rings) do
        local steps = r == 0 and 1 or 12
        for i = 0, steps - 1 do
            local x, z = T.offset(cx, cz, i * 360 / steps, r)
            if T.isGround(x, z) then
                local h = T.height(x, z)
                local score = h - r * 0.005
                if bestScore == nil or score > bestScore then
                    bestX, bestZ, bestScore, bestH = x, z, score, h
                end
            end
        end
    end
    return bestX, bestZ, bestH
end

-- Points the enemy will come from, as seen from a position near the anchor.
local function approachPoints(ax, az, facing)
    local points = {}
    for _, spread in ipairs({ -25, 0, 25 }) do
        local x, z = T.offset(ax, az, facing + spread, 1500)
        table.insert(points, { x = x, z = z })
    end
    return points
end

-- Scores one candidate position. "overwatch" wants a hull-down spot just
-- behind a crest that still sees the enemy approach. "hide" wants dead ground
-- the enemy approach cannot see.
function T.scorePosition(x, z, mode, approach, facing, anchorH)
    local h = T.height(x, z)
    local crestX, crestZ = T.offset(x, z, facing, 100)
    local rise = T.height(crestX, crestZ) - h
    local seen = 0
    for _, p in ipairs(approach) do
        if T.visible(x, z, 2.5, p.x, p.z, 2) then
            seen = seen + 1
        end
    end
    local score = 0
    if mode == "hide" then
        if seen == 0 then
            score = score + 15
        else
            score = score - seen * 5
        end
        if rise > 3 then
            score = score + 4
        end
        score = score + (anchorH - h) * 0.1
    else
        score = score + seen * 10
        if rise >= 1 and rise <= 8 then
            -- Hull-down: the crest covers the hull, the turret sees over it.
            score = score + 6
        elseif rise > 8 then
            score = score - 4
        end
    end
    if T.isRoad(x, z) then
        score = score - 2
    end
    return score
end

-- Steepest rise over run to the ground 25 m around a point.
function T.slope(x, z)
    local h = T.height(x, z)
    local steepest = 0
    for i = 0, 3 do
        local px, pz = T.offset(x, z, i * 90, 25)
        steepest = math.max(steepest, math.abs(T.height(px, pz) - h) / 25)
    end
    return steepest
end

-- The closest point on a road, nil when the map has none.
function T.nearestRoad(x, z)
    if not land.getClosestPointOnRoads then
        return nil
    end
    local ok, rx, rz = pcall(land.getClosestPointOnRoads, "roads", x, z)
    if not ok or not rx or not rz then
        return nil
    end
    return rx, rz
end

-- Whether buildings or other map objects stand this close to a point.
-- Scripts cannot see trees; roads are the one place known to be clear of them.
function T.obstructed(x, z, radius)
    if not (world.searchObjects and world.VolumeType and Object and Object.Category) then
        return false
    end
    local found = false
    local volume = {
        id = world.VolumeType.SPHERE,
        params = { point = { x = x, y = T.height(x, z), z = z }, radius = radius },
    }
    pcall(world.searchObjects, Object.Category.SCENERY, volume, function()
        found = true
        return false
    end)
    return found
end

local function scoreFiringPosition(x, z, ax, az)
    if not T.isGround(x, z) then
        return nil
    end
    local slope = T.slope(x, z)
    local score = -slope * 100 - distance(x, z, ax, az) * 0.005
    if slope > FLD.config.maxFiringSlope then
        score = score - 50
    end
    local rx, rz = T.nearestRoad(x, z)
    if T.isRoad(x, z) or (rx and distance(x, z, rx, rz) <= FLD.config.firingRoadDistance) then
        score = score + 8
    end
    if T.obstructed(x, z, 60) then
        score = score - 20
    end
    return score
end

-- A flat, open spot near the anchor where a battery can fire: no steep
-- ground, no buildings, preferably beside a road so no trees cover the guns.
function T.findFiringPosition(ax, az)
    local radius = FLD.config.firingPositionRadius
    local candidates = { { x = ax, z = az } }
    for _, r in ipairs({ radius / 4, radius / 2, radius * 3 / 4, radius }) do
        for i = 0, 7 do
            local x, z = T.offset(ax, az, i * 45, r)
            table.insert(candidates, { x = x, z = z })
        end
    end
    local rx, rz = T.nearestRoad(ax, az)
    if rx and distance(ax, az, rx, rz) <= radius then
        table.insert(candidates, { x = rx, z = rz })
    end
    local bestX, bestZ, bestScore = ax, az, nil
    for _, c in ipairs(candidates) do
        local score = scoreFiringPosition(c.x, c.z, ax, az)
        if score and (bestScore == nil or score > bestScore) then
            bestX, bestZ, bestScore = c.x, c.z, score
        end
    end
    return bestX, bestZ
end

-- Finds a position near the anchor, on our side of it.
function T.findPosition(ax, az, facing, mode)
    local approach = approachPoints(ax, az, facing)
    local anchorH = T.height(ax, az)
    local bestX, bestZ, bestScore = ax, az, nil
    for _, back in ipairs({ 0, 150, 300, 500, 800 }) do
        for _, lateral in ipairs({ -600, -300, 0, 300, 600 }) do
            local x, z = T.offset(ax, az, facing + 180, back)
            x, z = T.offset(x, z, facing + 90, lateral)
            if T.isGround(x, z) then
                local score = T.scorePosition(x, z, mode, approach, facing, anchorH)
                    - back * 0.004
                    - math.abs(lateral) * 0.002
                if bestScore == nil or score > bestScore then
                    bestX, bestZ, bestScore = x, z, score
                end
            end
        end
    end
    return bestX, bestZ
end

-------------------------------------------------------------------------------
-- Groups
-------------------------------------------------------------------------------

function FLD.aliveUnits(name)
    local group = Group.getByName(name)
    local result = {}
    if not group or not group:isExist() then
        return result
    end
    for _, unit in ipairs(group:getUnits() or {}) do
        if unit and unit:isExist() and unit:getLife() >= 1 then
            table.insert(result, unit)
        end
    end
    return result
end

function FLD.groupPosition(name)
    local units = FLD.aliveUnits(name)
    if #units == 0 then
        return nil
    end
    local p = units[1]:getPoint()
    return p.x, p.z
end

local function routePoint(x, z, speed, action)
    return {
        x = x,
        y = z,
        type = "Turning Point",
        action = action or "Off Road",
        speed = speed,
        ETA = 0,
        ETA_locked = false,
        speed_locked = true,
        task = { id = "ComboTask", params = { tasks = {} } },
    }
end

function FLD.routeTo(name, x, z, speed, action)
    if not FLD.movingUnits then
        return false
    end
    local group = Group.getByName(name)
    local fromX, fromZ = FLD.groupPosition(name)
    if not group or not fromX then
        return false
    end
    local mission = {
        id = "Mission",
        params = {
            route = {
                points = { routePoint(fromX, fromZ, speed, action), routePoint(x, z, speed, action) },
            },
        },
    }
    group:getController():setTask(mission)
    return true
end

function FLD.setFireAtWill(name, fireAtWill)
    local group = Group.getByName(name)
    if not group or not group:isExist() then
        return
    end
    local controller = group:getController()
    local roe = AI.Option.Ground.val.ROE.OPEN_FIRE
    if not fireAtWill then
        roe = AI.Option.Ground.val.ROE.WEAPON_HOLD
    end
    controller:setOption(AI.Option.Ground.id.ROE, roe)
    controller:setOption(AI.Option.Ground.id.ALARM_STATE, AI.Option.Ground.val.ALARM_STATE.RED)
end

local function groupStrength(group)
    if group.state == "DEAD" then
        return 0
    end
    local alive = #FLD.aliveUnits(group.name)
    if alive == 0 then
        group.state = "DEAD"
    end
    return alive
end

-------------------------------------------------------------------------------
-- Plan loading
-------------------------------------------------------------------------------

local function sectorLabel(sector)
    local label = "OBJ " .. (PHONETIC[sector.index] or tostring(sector.index))
    if sector.prominence >= 15 then
        label = label .. string.format(" (Hill %d)", sector.objH)
    end
    return label
end

function FLD.loadFrontLine(data)
    local front = { name = data.name, sectors = {}, sides = {}, groups = {} }
    for i, s in ipairs(data.sectors or {}) do
        local x, z = tonumber(s.x), tonumber(s.z)
        local objX, objZ, objH = T.findKeyTerrain(x, z, FLD.config.keyTerrainRadius)
        local sector = {
            index = i,
            x = x,
            z = z,
            width = tonumber(s.width),
            objX = objX,
            objZ = objZ,
            objH = math.floor(objH + 0.5),
            prominence = objH - T.height(x, z),
            holder = nil,
            contested = false,
            initial = { blue = 0, red = 0 },
            current = { blue = 0, red = 0 },
            presence = { blue = 0, red = 0 },
        }
        sector.label = sectorLabel(sector)
        front.sectors[i] = sector
    end
    for _, sideName in ipairs({ "blue", "red" }) do
        local s = (data.sides or {})[sideName] or {}
        front.sides[sideName] = {
            stance = s.stance or "DEFENSIVE",
            mainEffort = tonumber(s.mainEffort),
            heading = tonumber(s.forwardHeading) or 0,
            enemyBaseX = tonumber(s.enemyBaseX),
            enemyBaseZ = tonumber(s.enemyBaseZ),
            lastCommit = -math.huge,
            exploited = {},
            -- By sector: since when its task force sits idle, when its
            -- exploiting groups started arriving, whether it pushed a screen.
            idleSince = {},
            exploitArrivals = {},
            screened = {},
            followed = {},
            -- Enemy batteries located after they fired.
            located = {},
            recentTargets = {},
            lastArtilleryMessage = -math.huge,
        }
    end
    front.events = {}
    for _, e in ipairs(data.events or {}) do
        local event = {
            kind = e.kind,
            side = e.side,
            destX = tonumber(e.destinationX),
            destZ = tonumber(e.destinationZ),
            groups = {},
            fireAt = FLD.config.eventWindowMin
                + math.random() * (FLD.config.eventWindowMax - FLD.config.eventWindowMin),
            fired = false,
        }
        for _, g in ipairs(e.groups or {}) do
            table.insert(event.groups, { name = g.name, role = g.role })
        end
        table.insert(front.events, event)
    end
    for _, g in ipairs(data.groups or {}) do
        local reserve = toBool(g.reserve)
        local group = {
            name = g.name,
            side = g.side,
            role = g.role,
            sector = tonumber(g.sector),
            reserve = reserve,
            state = reserve and "RESERVE" or "IDLE",
            breakPoint = FLD.config.breakPointMin
                + math.random() * (FLD.config.breakPointMax - FLD.config.breakPointMin),
            initialSize = #FLD.aliveUnits(g.name),
            weaponHold = false,
            range = tonumber(g.range) or 0,
            artyState = "READY",
            artyUntil = 0,
            missions = 0,
        }
        table.insert(front.groups, group)
        local sector = front.sectors[group.sector or 0]
        if sector and MANEUVER_ROLES[group.role] and not reserve then
            sector.initial[group.side] = sector.initial[group.side] + group.initialSize
        end
    end
    return front
end

-------------------------------------------------------------------------------
-- Map marks and status
-------------------------------------------------------------------------------

local function markState(sector)
    if sector.contested then
        return "contested"
    end
    return sector.holder or "neutral"
end

function FLD.drawSector(sector)
    if not FLD.config.showMarks then
        return
    end
    local colors = MARK_COLORS[markState(sector)]
    local center = { x = sector.objX, y = 0, z = sector.objZ }
    sector.circleId = FLD.nextMarkId
    sector.textId = FLD.nextMarkId + 1
    FLD.nextMarkId = FLD.nextMarkId + 2
    trigger.action.circleToAll(
        -1, sector.circleId, center, FLD.config.objectiveRadius, colors.line, colors.fill, 1, true, ""
    )
    local textX, textZ = T.offset(sector.objX, sector.objZ, 0, FLD.config.objectiveRadius + 200)
    trigger.action.textToAll(
        -1, sector.textId, { x = textX, y = 0, z = textZ }, colors.line, { 0, 0, 0, 0 }, 12, true, sector.label
    )
end

function FLD.recolorSector(sector)
    if not FLD.config.showMarks or not sector.circleId then
        return
    end
    local colors = MARK_COLORS[markState(sector)]
    trigger.action.setMarkupColor(sector.circleId, colors.line)
    trigger.action.setMarkupColorFill(sector.circleId, colors.fill)
    trigger.action.setMarkupColor(sector.textId, colors.line)
end

local function enemyEstimate(units)
    if units == 0 then
        return "none seen"
    elseif units <= 4 then
        return "light"
    elseif units <= 10 then
        return "moderate"
    end
    return "heavy"
end

function FLD.statusText(sideName)
    local lines = {}
    for _, front in ipairs(FLD.frontLines) do
        local side = front.sides[sideName]
        table.insert(lines, string.format("Front %s - our stance: %s", front.name, side.stance))
        for _, sector in ipairs(front.sectors) do
            local holder = "nobody"
            if sector.contested then
                holder = "CONTESTED"
            elseif sector.holder == sideName then
                holder = "friendly"
            elseif sector.holder then
                holder = "ENEMY"
            end
            local ours = 0
            if sector.initial[sideName] > 0 then
                ours = math.floor(100 * sector.current[sideName] / sector.initial[sideName] + 0.5)
            end
            local main = ""
            if side.mainEffort == sector.index then
                main = " [MAIN EFFORT]"
            end
            table.insert(
                lines,
                string.format(
                    "  %d. %s%s: held by %s, our strength %d%%, enemy %s",
                    sector.index,
                    sector.label,
                    main,
                    holder,
                    ours,
                    enemyEstimate(sector.current[OTHER_SIDE[sideName]])
                )
            )
        end
        local reserves = 0
        for _, group in ipairs(front.groups) do
            if group.side == sideName and group.state == "RESERVE" then
                reserves = reserves + 1
            end
        end
        table.insert(lines, string.format("  Reserve task force groups available: %d", reserves))
    end
    return table.concat(lines, "\n")
end

function FLD.showStatus(sideName)
    trigger.action.outTextForCoalition(coalitionOf(sideName), FLD.statusText(sideName), 30)
end

function FLD.tasksText(sideName)
    local lines = {}
    for _, task in ipairs(FLD.tasks[sideName]) do
        if task.status == "ACTIVE" then
            table.insert(lines, string.format("- %s: %s. Grid %s", task.front.name, task.title, FLD.grid(task.x, task.z)))
        end
    end
    if #lines == 0 then
        return "No active pop-up taskings."
    end
    return "Active pop-up taskings:\n" .. table.concat(lines, "\n")
end

function FLD.showTasks(sideName)
    trigger.action.outTextForCoalition(coalitionOf(sideName), FLD.tasksText(sideName), 30)
end

local function addStatusMenus()
    if not FLD.config.statusMenu then
        return
    end
    for _, sideName in ipairs({ "blue", "red" }) do
        missionCommands.addCommandForCoalition(coalitionOf(sideName), "Front line status", nil, FLD.showStatus, sideName)
        if FLD.config.popupEvents then
            missionCommands.addCommandForCoalition(coalitionOf(sideName), "Pop-up taskings", nil, FLD.showTasks, sideName)
        end
    end
end

-------------------------------------------------------------------------------
-- Initial positioning
-------------------------------------------------------------------------------

-- Spreads the groups positioned in one sector so they do not stack up.
local function lateralSlot(slots, key)
    local n = slots[key] or 0
    slots[key] = n + 1
    local offset = math.ceil(n / 2) * 400
    if n % 2 == 1 then
        offset = -offset
    end
    return offset
end

function FLD.occupy(front, group, mode, anchorX, anchorZ, slots)
    local side = front.sides[group.side]
    local ax, az = anchorX, anchorZ
    if slots then
        ax, az = T.offset(ax, az, side.heading + 90, lateralSlot(slots, group.side .. (group.sector or 0)))
    end
    local x, z = T.findPosition(ax, az, side.heading, mode)
    FLD.routeTo(group.name, x, z, SPEED_REPOSITION)
    group.positionX, group.positionZ = x, z
end

function FLD.setup(front)
    local slots = {}
    for _, group in ipairs(front.groups) do
        local side = front.sides[group.side]
        local sector = front.sectors[group.sector or 0]
        if group.state == "RESERVE" then
            -- Reserves wait in dead ground where the enemy cannot see them.
            local x, z = FLD.groupPosition(group.name)
            if x then
                FLD.occupy(front, group, "hide", x, z, nil)
            end
        elseif group.role == "ARTILLERY" then
            -- Batteries spawn wherever the generator put them, often on a
            -- slope or under cover: move them to ground they can fire from.
            local x, z = FLD.groupPosition(group.name)
            if x then
                local fx, fz = T.findFiringPosition(x, z)
                if distance(x, z, fx, fz) > 50 and FLD.routeTo(group.name, fx, fz, SPEED_REPOSITION) then
                    group.artyState = "MOVING"
                    group.artyUntil = timer.getTime() + FLD.config.relocateSeconds
                end
            end
        elseif sector and MANEUVER_ROLES[group.role] then
            if side.stance == "DEFENSIVE" then
                local depth = group.role == "ATGM" and 1500 or 200
                local ax, az = T.offset(sector.objX, sector.objZ, side.heading + 180, depth)
                FLD.occupy(front, group, "overwatch", ax, az, slots)
                group.state = "HOLDING"
            elseif side.stance == "AMBUSH" then
                -- Let the enemy walk onto the objective, fire from the flanks.
                local ax, az = T.offset(sector.objX, sector.objZ, side.heading + 180, 1200)
                FLD.occupy(front, group, "overwatch", ax, az, slots)
                FLD.setFireAtWill(group.name, false)
                group.weaponHold = true
                group.state = "HOLDING"
            end
        end
    end
    for _, sector in ipairs(front.sectors) do
        FLD.drawSector(sector)
    end
end

-------------------------------------------------------------------------------
-- Battle tracking
-------------------------------------------------------------------------------

local function sideHolding(sector)
    if sector.contested then
        return nil
    end
    return sector.holder
end

function FLD.updateSector(front, sector)
    local presence = { blue = 0, red = 0 }
    local current = { blue = 0, red = 0 }
    for _, group in ipairs(front.groups) do
        if MANEUVER_ROLES[group.role] and group.state ~= "DEAD" then
            local units = FLD.aliveUnits(group.name)
            if #units == 0 then
                group.state = "DEAD"
            else
                if group.sector == sector.index and group.state ~= "RESERVE" and group.state ~= "WITHDRAWN" then
                    current[group.side] = current[group.side] + #units
                end
                for _, unit in ipairs(units) do
                    local p = unit:getPoint()
                    if distance(p.x, p.z, sector.objX, sector.objZ) <= FLD.config.objectiveRadius then
                        presence[group.side] = presence[group.side] + 1
                    end
                end
            end
        end
    end
    sector.presence = presence
    sector.current = current

    local previousHolder, wasContested = sector.holder, sector.contested
    if presence.blue > 0 and presence.red > 0 then
        sector.contested = true
    else
        sector.contested = false
        if presence.blue > 0 then
            sector.holder = "blue"
        elseif presence.red > 0 then
            sector.holder = "red"
        end
    end

    if sector.holder ~= previousHolder and sector.holder then
        say(sector.holder, string.format("%s: we have taken %s.", front.name, sector.label))
        if previousHolder then
            say(previousHolder, string.format("%s: we have lost %s!", front.name, sector.label))
        end
    elseif sector.contested and not wasContested and sector.holder then
        say(sector.holder, string.format("%s: %s is under attack!", front.name, sector.label))
    end
    if sector.holder ~= previousHolder or sector.contested ~= wasContested then
        FLD.recolorSector(sector)
    end
end

local function strengthShare(sector, sideName)
    local initial = sector.initial[sideName]
    if initial <= 0 then
        return 0
    end
    return sector.current[sideName] / initial
end

-------------------------------------------------------------------------------
-- Decisions
-------------------------------------------------------------------------------

function FLD.withdrawBroken(front, sideName)
    local side = front.sides[sideName]
    for _, group in ipairs(front.groups) do
        if group.side == sideName and MANEUVER_ROLES[group.role] and group.initialSize > 1
            and group.state ~= "DEAD" and group.state ~= "WITHDRAWN" and group.state ~= "RESERVE" then
            local alive = groupStrength(group)
            if alive > 0 and alive / group.initialSize <= group.breakPoint then
                local x, z = FLD.groupPosition(group.name)
                if x then
                    local backX, backZ = T.offset(x, z, side.heading + 180, FLD.config.withdrawDistance)
                    local hideX, hideZ = T.findPosition(backX, backZ, side.heading, "hide")
                    FLD.routeTo(group.name, hideX, hideZ, SPEED_WITHDRAW)
                    group.state = "WITHDRAWN"
                    debug(group.name .. " broke and withdraws")
                    local sector = front.sectors[group.sector or 0]
                    if sector then
                        say(sideName, string.format("%s: %s took heavy losses and falls back from %s.",
                            front.name, group.name, sector.label))
                    end
                end
            end
        end
    end
end

function FLD.consolidate(front, sideName)
    local side = front.sides[sideName]
    if side.stance == "BREAKTHROUGH" then
        return
    end
    for _, group in ipairs(front.groups) do
        local sector = front.sectors[group.sector or 0]
        if sector and group.side == sideName and MANEUVER_ROLES[group.role]
            and (group.state == "IDLE" or group.state == "COUNTER" or group.state == "RAIDING")
            and sideHolding(sector) == sideName then
            local x, z = FLD.groupPosition(group.name)
            if x and distance(x, z, sector.objX, sector.objZ) <= FLD.config.objectiveRadius * 1.5 then
                FLD.occupy(front, group, "overwatch", sector.objX, sector.objZ, front.consolidationSlots)
                group.state = "HOLDING"
                debug(group.name .. " consolidates on " .. sector.label)
            end
        end
    end
end

-- A group still exploiting the breakthrough at a sector, if any.
local function exploitingGroup(front, sideName, sectorIndex)
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.sector == sectorIndex and group.state == "EXPLOITING"
            and groupStrength(group) > 0 then
            return group
        end
    end
    return nil
end

-- How urgently a sector needs the reserve, 0 when it does not, and what for.
function FLD.sectorNeed(front, sector, sideName)
    local side = front.sides[sideName]
    local enemy = OTHER_SIDE[sideName]
    if sector.holder == enemy and not sector.contested then
        return 3, "counter"
    end
    if sector.contested then
        return 2, "counter"
    end
    -- Reinforce success: the reserve follows a breakthrough.
    if OFFENSIVE_STANCES[side.stance] and side.exploited[sector.index] and not side.followed[sector.index]
        and exploitingGroup(front, sideName, sector.index) then
        return 1.5, "follow"
    end
    if sector.initial[sideName] > 0 and strengthShare(sector, sideName) < FLD.config.reinforceStrength
        and sector.current[enemy] > 0 then
        return 1, "reinforce"
    end
    -- A gap in the line: nobody fights for this objective. Attackers seize it.
    if OFFENSIVE_STANCES[side.stance] and sector.holder ~= sideName
        and sector.current[sideName] == 0 and sector.current[enemy] == 0 then
        return 0.5, "seize"
    end
    return 0, nil
end

function FLD.commitReserves(front, sideName, now)
    local side = front.sides[sideName]
    if now - side.lastCommit < FLD.config.commitCooldownSeconds then
        return
    end
    local best, bestNeed, kind = nil, 0, nil
    for _, sector in ipairs(front.sectors) do
        local need, needKind = FLD.sectorNeed(front, sector, sideName)
        if side.mainEffort == sector.index and need >= 1 then
            need = need + 0.5
        end
        if need > bestNeed then
            best, bestNeed, kind = sector, need, needKind
        end
    end
    if not best then
        return
    end

    local reserves = {}
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.state == "RESERVE" and groupStrength(group) > 0 then
            local x, z = FLD.groupPosition(group.name)
            if x then
                table.insert(reserves, { group = group, dist = distance(x, z, best.objX, best.objZ) })
            end
        end
    end
    if #reserves == 0 then
        return
    end
    table.sort(reserves, function(a, b)
        return a.dist < b.dist
    end)

    local leader = exploitingGroup(front, sideName, best.index)
    local committed = 0
    for i = 1, math.min(FLD.config.taskForceSize, #reserves) do
        local group = reserves[i].group
        group.sector = best.index
        best.initial[sideName] = best.initial[sideName] + group.initialSize
        if kind == "follow" then
            FLD.setFireAtWill(group.name, true)
            FLD.routeTo(group.name, leader.exploitX, leader.exploitZ, SPEED_ASSAULT)
            group.state = "EXPLOITING"
            group.exploitX, group.exploitZ = leader.exploitX, leader.exploitZ
            group.exploitBase = leader.exploitBase
        elseif kind == "counter" or kind == "seize" then
            FLD.setFireAtWill(group.name, true)
            FLD.routeTo(group.name, best.objX, best.objZ, SPEED_ASSAULT)
            group.state = "COUNTER"
        else
            local ax, az = T.offset(best.objX, best.objZ, side.heading + 180, 300)
            FLD.occupy(front, group, "overwatch", ax, az, front.consolidationSlots)
            group.state = "HOLDING"
        end
        committed = committed + 1
    end
    side.lastCommit = now
    if kind == "follow" then
        side.followed[best.index] = true
        say(sideName, string.format("%s: reserve task force (%d groups) following up the breakthrough at %s.",
            front.name, committed, best.label))
    elseif kind == "seize" then
        say(sideName, string.format("%s: reserve task force (%d groups) advancing into the gap at %s.",
            front.name, committed, best.label))
    elseif kind == "counter" then
        say(sideName, string.format("%s: reserve task force (%d groups) committed to counter-attack %s.",
            front.name, committed, best.label))
    else
        say(sideName, string.format("%s: reserve task force (%d groups) reinforcing %s.",
            front.name, committed, best.label))
    end
end

-- Whether the enemy is falling back: retreating, or every enemy group still
-- fighting on this front has broken and pulled back.
function FLD.enemyFallingBack(front, sideName)
    local enemy = OTHER_SIDE[sideName]
    if front.sides[enemy].stance == "RETREAT" then
        return true
    end
    local any = false
    for _, group in ipairs(front.groups) do
        if group.side == enemy and MANEUVER_ROLES[group.role] and group.state ~= "DEAD" then
            if group.state ~= "WITHDRAWN" then
                return false
            end
            any = true
        end
    end
    return any
end

-- The next exploitation target pushing on from a point: the next high
-- ground toward the enemy, or the enemy base once it is close. An enemy
-- falling back is pursued all the way to its base in one push.
function FLD.exploitationTarget(front, sideName, fromX, fromZ)
    local side = front.sides[sideName]
    if side.enemyBaseX and (FLD.enemyFallingBack(front, sideName)
        or distance(fromX, fromZ, side.enemyBaseX, side.enemyBaseZ) <= FLD.config.exploitBaseDistance) then
        return side.enemyBaseX, side.enemyBaseZ, "the enemy base"
    end
    local x, z = T.offset(fromX, fromZ, side.heading, FLD.config.exploitDistance)
    local keyX, keyZ, keyH = T.findKeyTerrain(x, z, FLD.config.keyTerrainRadius)
    return keyX, keyZ, string.format("Hill %d", math.floor(keyH + 0.5))
end

local function enemyNear(front, sideName, x, z, radius)
    local enemy = OTHER_SIDE[sideName]
    for _, group in ipairs(front.groups) do
        if group.side == enemy and MANEUVER_ROLES[group.role] and group.state ~= "DEAD"
            and group.state ~= "WITHDRAWN" then
            for _, unit in ipairs(FLD.aliveUnits(group.name)) do
                local p = unit:getPoint()
                if distance(p.x, p.z, x, z) <= radius then
                    return true
                end
            end
        end
    end
    return false
end

-- Average position of a task force's members.
local function forceCenter(members)
    local sx, sz = 0, 0
    for _, m in ipairs(members) do
        sx, sz = sx + m.x, sz + m.z
    end
    return sx / #members, sz / #members
end

-- Routes a task force's members side by side to a target.
local function routeTaskForce(front, sideName, members, tx, tz, state)
    local side = front.sides[sideName]
    local slots = {}
    local count = 0
    for _, m in ipairs(members) do
        local offset = lateralSlot(slots, "force") * FLD.config.taskForceSpacing / 400
        local x, z = T.offset(tx, tz, side.heading + 90, offset)
        if FLD.routeTo(m.group.name, x, z, SPEED_ASSAULT) then
            FLD.setFireAtWill(m.group.name, true)
            m.group.state = state
            m.group.exploitX, m.group.exploitZ = x, z
            count = count + 1
        end
    end
    return count
end

local function taskForceName(front, key)
    local sector = front.sectors[key]
    if sector then
        return "task force " .. sector.label
    end
    return "task force"
end

-- Exploiting task forces keep pushing toward the enemy base while nothing
-- stops them. A task force bounds together: once its first groups reach the
-- target it waits for the rest, or for regroupSeconds, and then all of its
-- groups push on to the next bound side by side.
function FLD.continueExploitation(front, sideName, now)
    local side = front.sides[sideName]
    local forces = {}
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.state == "EXPLOITING" and group.exploitX
            and not group.exploitBase and not group.counterOffensive then
            local x, z = FLD.groupPosition(group.name)
            if x then
                local key = group.sector or 0
                forces[key] = forces[key] or {}
                table.insert(forces[key], { group = group, x = x, z = z })
            end
        end
    end
    for key, members in pairs(forces) do
        local arrived, allArrived, contact = {}, true, false
        for _, m in ipairs(members) do
            if distance(m.x, m.z, m.group.exploitX, m.group.exploitZ) <= FLD.config.exploitArrivalDistance then
                table.insert(arrived, m)
            else
                allArrived = false
            end
            if enemyNear(front, sideName, m.x, m.z, FLD.config.exploitContactDistance) then
                contact = true
            end
        end
        if #arrived == 0 or contact then
            side.exploitArrivals[key] = nil
        else
            side.exploitArrivals[key] = side.exploitArrivals[key] or now
            if allArrived or now - side.exploitArrivals[key] >= FLD.config.regroupSeconds then
                -- The next bound is measured from the groups that made it.
                local cx, cz = forceCenter(arrived)
                local tx, tz, targetName = FLD.exploitationTarget(front, sideName, cx, cz)
                if routeTaskForce(front, sideName, members, tx, tz, "EXPLOITING") > 0 then
                    for _, m in ipairs(members) do
                        m.group.exploitBase = targetName == "the enemy base"
                    end
                    say(sideName, string.format("%s: %s meets no resistance, pushing on toward %s.",
                        front.name, taskForceName(front, key), targetName))
                end
                side.exploitArrivals[key] = nil
            end
        end
    end
end

local function nearestEnemyGroup(front, sideName, x, z, radius)
    local enemy = OTHER_SIDE[sideName]
    local best, bestX, bestZ, bestDist = nil, nil, nil, radius
    for _, group in ipairs(front.groups) do
        if group.side == enemy and MANEUVER_ROLES[group.role] and group.state ~= "DEAD"
            and group.state ~= "RESERVE" then
            local gx, gz = FLD.groupPosition(group.name)
            if gx and distance(x, z, gx, gz) <= bestDist then
                best, bestX, bestZ, bestDist = group, gx, gz, distance(x, z, gx, gz)
            end
        end
    end
    return best, bestX, bestZ
end

-- The most threatened sector other than the given one, if any needs help.
local function threatenedSector(front, sideName, exceptIndex)
    local best, bestNeed = nil, 0
    for _, sector in ipairs(front.sectors) do
        if sector.index ~= exceptIndex then
            local need, kind = FLD.sectorNeed(front, sector, sideName)
            if kind ~= "seize" and kind ~= "follow" and need > bestNeed then
                best, bestNeed = sector, need
            end
        end
    end
    return best
end

local function moveToSector(front, group, sector)
    local old = front.sectors[group.sector or 0]
    if old and old.initial[group.side] >= group.initialSize then
        old.initial[group.side] = old.initial[group.side] - group.initialSize
    end
    sector.initial[group.side] = sector.initial[group.side] + group.initialSize
    group.sector = sector.index
end

-- Gives an idle task force something to do, all of its groups together.
-- Attackers go for the nearest enemy, or push on toward the enemy base when
-- none is in reach, with their support weapons overwatching from behind.
-- Defenders shift to a threatened sector, or push a screen ahead of their
-- objective once.
function FLD.taskForceWork(front, sideName, key, members)
    local side = front.sides[sideName]
    local sector = front.sectors[key]
    local assault, support = {}, {}
    for _, m in ipairs(members) do
        if ASSAULT_ROLES[m.group.role] then
            table.insert(assault, m)
        else
            table.insert(support, m)
        end
    end
    if #assault == 0 then
        -- Support weapons do not attack on their own.
        return false
    end

    if OFFENSIVE_STANCES[side.stance] then
        local cx, cz = forceCenter(assault)
        local target, tx, tz = nearestEnemyGroup(front, sideName, cx, cz, FLD.config.seekContactRange)
        local state, targetName = "ATTACKING", nil
        if target then
            targetName = "the enemy near " .. FLD.grid(tx, tz)
        else
            state = "EXPLOITING"
            tx, tz, targetName = FLD.exploitationTarget(front, sideName, cx, cz)
        end
        if routeTaskForce(front, sideName, assault, tx, tz, state) == 0 then
            return false
        end
        for _, m in ipairs(assault) do
            m.group.exploitBase = targetName == "the enemy base"
        end
        local bx, bz = T.offset(tx, tz, side.heading + 180, FLD.config.supportStandoff)
        local slots = {}
        for _, m in ipairs(support) do
            local ax, az = T.offset(bx, bz, side.heading + 90, lateralSlot(slots, "support"))
            local px, pz = T.findPosition(ax, az, side.heading, "overwatch")
            if FLD.routeTo(m.group.name, px, pz, SPEED_ASSAULT) then
                m.group.state = "ATTACKING"
            end
        end
        if target then
            say(sideName, string.format("%s: %s moves to engage %s.", front.name, taskForceName(front, key), targetName))
        else
            say(sideName, string.format("%s: no enemy in sight, %s advancing toward %s.",
                front.name, taskForceName(front, key), targetName))
        end
        return true
    end

    if side.stance ~= "DEFENSIVE" then
        return false
    end
    local ownQuiet = not sector
        or (FLD.sectorNeed(front, sector, sideName) == 0 and sector.current[OTHER_SIDE[sideName]] == 0)
    local threatened = ownQuiet and threatenedSector(front, sideName, key)
    if threatened then
        for _, m in ipairs(assault) do
            moveToSector(front, m.group, threatened)
            local ax, az = T.offset(threatened.objX, threatened.objZ, side.heading + 180, 300)
            FLD.occupy(front, m.group, "overwatch", ax, az, front.consolidationSlots)
            m.group.state = "HOLDING"
        end
        say(sideName, string.format("%s: %s shifts to reinforce %s.",
            front.name, taskForceName(front, key), threatened.label))
        return true
    end
    if sector and not side.screened[key] then
        side.screened[key] = true
        local ax, az = T.offset(sector.objX, sector.objZ, side.heading, FLD.config.screenDistance)
        for _, m in ipairs(assault) do
            FLD.occupy(front, m.group, "overwatch", ax, az, front.consolidationSlots)
            m.group.state = "HOLDING"
        end
        debug(taskForceName(front, key) .. " pushes a screen ahead of " .. sector.label)
        return true
    end
    return false
end

local IDLE_STATES = { IDLE = true, HOLDING = true, ATTACKING = true }

-- Nobody sits idle. The groups of a sector form one task force: once none of
-- them has moved or been in contact for a while, the whole task force is
-- given something to do together, however long each group has waited.
function FLD.keepBusy(front, sideName, now)
    local side = front.sides[sideName]
    local forces = {}
    for _, group in ipairs(front.groups) do
        if group.side == sideName and MANEUVER_ROLES[group.role] and IDLE_STATES[group.state]
            and not group.weaponHold then
            local x, z = FLD.groupPosition(group.name)
            if x then
                local key = group.sector or 0
                forces[key] = forces[key] or {}
                table.insert(forces[key], { group = group, x = x, z = z })
            end
        end
    end
    for key, members in pairs(forces) do
        local busy = false
        for _, m in ipairs(members) do
            local group = m.group
            if enemyNear(front, sideName, m.x, m.z, FLD.config.exploitContactDistance)
                or (group.lastX and distance(m.x, m.z, group.lastX, group.lastZ) >= FLD.config.idleMoveDistance) then
                busy = true
            end
            group.lastX, group.lastZ = m.x, m.z
        end
        if busy then
            side.idleSince[key] = nil
        elseif not side.idleSince[key] then
            side.idleSince[key] = now
        elseif now - side.idleSince[key] >= FLD.config.idleSeconds then
            FLD.taskForceWork(front, sideName, key, members)
            -- Give the new orders, or the next look, time to play out.
            side.idleSince[key] = now
        end
    end
end

-- The center of the friendly maneuver groups an air defence group covers:
-- those of its sector, or of the whole front when its sector has none.
local function coveredForce(front, group)
    for _, wholeFront in ipairs({ false, true }) do
        local sx, sz, n = 0, 0, 0
        for _, other in ipairs(front.groups) do
            if other.side == group.side and MANEUVER_ROLES[other.role]
                and other.state ~= "DEAD" and other.state ~= "RESERVE" and other.state ~= "WITHDRAWN"
                and (wholeFront or other.sector == group.sector) then
                local x, z = FLD.groupPosition(other.name)
                if x then
                    sx, sz, n = sx + x, sz + z, n + 1
                end
            end
        end
        if n > 0 then
            return sx / n, sz / n
        end
    end
    return nil
end

-- Air defence keeps up with the front: a bit behind the groups it covers,
-- out of reach of the enemy's direct fire, on ground that sees the sky
-- over the battle.
function FLD.coverAirDefence(front, sideName, now)
    local side = front.sides[sideName]
    local slots = {}
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.role == "SHORAD" and groupStrength(group) > 0
            and now >= (group.airDefenceMoveAt or 0) then
            local x, z = FLD.groupPosition(group.name)
            local cx, cz = coveredForce(front, group)
            if x and cx then
                local tx, tz = T.offset(cx, cz, side.heading + 180, FLD.config.airDefenceStandoff)
                tx, tz = T.offset(tx, tz, side.heading + 90, lateralSlot(slots, group.sector or 0))
                for _ = 1, 3 do
                    if not enemyNear(front, sideName, tx, tz, FLD.config.airDefenceEnemyDistance) then
                        break
                    end
                    tx, tz = T.offset(tx, tz, side.heading + 180, 1000)
                end
                if distance(x, z, tx, tz) >= FLD.config.airDefenceMoveDistance then
                    local px, pz = T.findPosition(tx, tz, side.heading, "overwatch")
                    if FLD.routeTo(group.name, px, pz, SPEED_REPOSITION) then
                        group.airDefenceMoveAt = now + FLD.config.airDefenceMoveCooldown
                        debug(group.name .. " bounds to keep up with the front")
                    end
                end
            end
        end
    end
end

function FLD.exploit(front, sideName)
    local side = front.sides[sideName]
    local offensive = OFFENSIVE_STANCES[side.stance]
    -- Defenders seize the moment too: once the attack in front of them breaks
    -- they counter-attack one bound, then hold again.
    if not offensive and side.stance ~= "DEFENSIVE" then
        return
    end
    local enemyLimit = FLD.config.exploitEnemyStrength
    if not offensive then
        enemyLimit = FLD.config.counterOffensiveEnemyStrength
    end
    local enemy = OTHER_SIDE[sideName]
    for _, sector in ipairs(front.sectors) do
        -- Gaps the enemy never defended have no enemy strength and are
        -- exploited by attackers as soon as they hold them.
        if not side.exploited[sector.index] and sideHolding(sector) == sideName
            and (offensive or sector.initial[enemy] > 0)
            and strengthShare(sector, enemy) <= enemyLimit
            and strengthShare(sector, sideName) >= FLD.config.exploitFriendlyStrength then
            local x, z, targetName = FLD.exploitationTarget(front, sideName, sector.objX, sector.objZ)
            local count = 0
            for _, group in ipairs(front.groups) do
                if group.side == sideName and group.sector == sector.index and ASSAULT_ROLES[group.role]
                    and (group.state == "HOLDING" or group.state == "IDLE" or group.state == "COUNTER"
                        or group.state == "ATTACKING") then
                    if FLD.routeTo(group.name, x, z, SPEED_ASSAULT) then
                        group.state = "EXPLOITING"
                        group.exploitX, group.exploitZ = x, z
                        group.exploitBase = targetName == "the enemy base"
                        group.counterOffensive = not offensive
                        count = count + 1
                    end
                end
            end
            if count > 0 then
                side.exploited[sector.index] = true
                if offensive then
                    say(sideName, string.format("%s: enemy collapsing at %s, task force exploiting toward %s.",
                        front.name, sector.label, targetName))
                else
                    say(sideName, string.format("%s: attack broken at %s, counter-attacking toward %s.",
                        front.name, sector.label, targetName))
                end
                say(enemy, string.format("%s: enemy armor breaking through at %s!", front.name, sector.label))
            end
        end
    end
end

function FLD.springAmbushes(front, sideName)
    local enemy = OTHER_SIDE[sideName]
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.weaponHold then
            local x, z = FLD.groupPosition(group.name)
            if not x then
                group.weaponHold = false
            else
                for _, other in ipairs(front.groups) do
                    if other.side == enemy and other.state ~= "DEAD" then
                        local ox, oz = FLD.groupPosition(other.name)
                        if ox and distance(x, z, ox, oz) <= FLD.config.ambushRange then
                            FLD.setFireAtWill(group.name, true)
                            group.weaponHold = false
                            debug(group.name .. " springs the ambush")
                            break
                        end
                    end
                end
            end
        end
    end
end

-------------------------------------------------------------------------------
-- Artillery
-------------------------------------------------------------------------------

local function sayArtillery(front, sideName, now, text)
    local side = front.sides[sideName]
    if now - side.lastArtilleryMessage >= 60 then
        side.lastArtilleryMessage = now
        say(sideName, string.format("%s: %s", front.name, text))
    end
end

-- Whether units of a side see a point: ground units with line of sight, or
-- the side's players in the air (helicopters make great forward observers).
function FLD.isSpotted(front, sideName, x, z)
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.state ~= "DEAD" and group.role ~= "ARTILLERY" then
            for _, unit in ipairs(FLD.aliveUnits(group.name)) do
                local p = unit:getPoint()
                if distance(p.x, p.z, x, z) <= FLD.config.spotRange and T.visible(p.x, p.z, 2.5, x, z, 2) then
                    return true
                end
            end
        end
    end
    for _, player in ipairs(coalition.getPlayers(coalitionOf(sideName)) or {}) do
        if player and player:isExist() and player:inAir() then
            local p = player:getPoint()
            if distance(p.x, p.z, x, z) <= FLD.config.aircraftSpotRange
                and land.isVisible({ x = p.x, y = p.y, z = p.z }, { x = x, y = T.height(x, z) + 2, z = z }) then
                return true
            end
        end
    end
    return false
end

function FLD.dangerClose(front, sideName, x, z)
    for _, group in ipairs(front.groups) do
        if group.side == sideName and group.state ~= "DEAD" then
            for _, unit in ipairs(FLD.aliveUnits(group.name)) do
                local p = unit:getPoint()
                if distance(p.x, p.z, x, z) <= FLD.config.dangerCloseDistance then
                    return true
                end
            end
        end
    end
    return false
end

local TARGET_PRIORITY = { SHORAD = 6, TANK = 3, IFV = 3, ATGM = 3 }

-- Fire mission candidates for one side, best first.
function FLD.artilleryTargets(front, sideName, now)
    local side = front.sides[sideName]
    local enemy = OTHER_SIDE[sideName]
    local targets = {}

    for _, located in ipairs(side.located) do
        if located.knownAt <= now and now - located.knownAt <= FLD.config.counterBatteryMemory then
            table.insert(targets, { x = located.x, z = located.z, score = 8, name = located.name, kind = "battery", located = located })
        end
    end

    for _, group in ipairs(front.groups) do
        if group.side == enemy and group.state ~= "DEAD" and group.role ~= "ARTILLERY" then
            local x, z = FLD.groupPosition(group.name)
            if x and FLD.isSpotted(front, sideName, x, z) then
                local score = TARGET_PRIORITY[group.role] or 2
                local kind = group.role == "SHORAD" and "air defence" or "armor"
                if group.state == "COUNTER" or group.state == "EXPLOITING" or group.state == "ATTACKING" then
                    score = math.max(score, 5)
                end
                for _, sector in ipairs(front.sectors) do
                    if distance(x, z, sector.objX, sector.objZ) <= FLD.config.objectiveRadius * 2 then
                        if sector.contested or sector.holder ~= sideName then
                            score = score + 3
                        end
                        if side.mainEffort == sector.index then
                            score = score + 1
                        end
                        break
                    end
                end
                table.insert(targets, { x = x, z = z, score = score, name = group.name, kind = kind })
            end
        end
    end

    for _, target in ipairs(targets) do
        local last = side.recentTargets[target.name]
        if last and now - last < FLD.config.retargetSeconds then
            target.score = target.score - 3
        end
    end
    table.sort(targets, function(a, b)
        return a.score > b.score
    end)
    return targets
end

function FLD.fireMission(front, battery, target, now)
    local group = Group.getByName(battery.name)
    if not group then
        return false
    end
    local alive = #FLD.aliveUnits(battery.name)
    group:getController():setTask({
        id = "FireAtPoint",
        params = {
            point = { x = target.x, y = target.z },
            radius = FLD.config.fireMissionRadius,
            expendQty = math.max(4, alive * 3),
            expendQtyEnabled = true,
        },
    })
    battery.artyState = "FIRING"
    battery.artyUntil = now + FLD.config.fireMissionSeconds
    battery.missions = battery.missions + 1

    -- Firing gives the battery away to the enemy's counter-battery radar.
    local x, z = FLD.groupPosition(battery.name)
    local enemy = front.sides[OTHER_SIDE[battery.side]]
    table.insert(enemy.located, { x = x, z = z, name = battery.name, knownAt = now + FLD.config.counterBatteryDelay })
    front.sides[battery.side].recentTargets[target.name] = now
    debug(string.format("%s fires on %s (%s)", battery.name, target.name, target.kind))
    return true
end

-- Records batteries fired by other scripts (player-called artillery).
function FLD.batteryFired(groupName, now)
    for _, front in ipairs(FLD.frontLines) do
        for _, group in ipairs(front.groups) do
            if group.name == groupName and group.role == "ARTILLERY" then
                local x, z = FLD.groupPosition(groupName)
                local enemy = front.sides[OTHER_SIDE[group.side]]
                local known = false
                for _, located in ipairs(enemy.located) do
                    if located.name == groupName and located.knownAt > now - FLD.config.fireMissionSeconds then
                        known = true
                    end
                end
                if x and not known then
                    table.insert(enemy.located, { x = x, z = z, name = groupName, knownAt = now + FLD.config.counterBatteryDelay })
                end
            end
        end
    end
end

local function inRange(battery, x, z)
    local bx, bz = FLD.groupPosition(battery.name)
    if not bx then
        return false
    end
    local d = distance(bx, bz, x, z)
    return d <= battery.range and d >= math.max(1000, battery.range * 0.1)
end

function FLD.runArtillery(front, sideName, now)
    if not FLD.config.artilleryStrikes then
        return
    end
    if sideName == "blue" and FLD.config.playerArtillery then
        return
    end
    local side = front.sides[sideName]
    local targets = nil
    for _, battery in ipairs(front.groups) do
        if battery.side == sideName and battery.role == "ARTILLERY" and groupStrength(battery) > 0 then
            if battery.artyState == "FIRING" and now >= battery.artyUntil then
                -- Shoot and scoot before the counter-battery fire arrives.
                local x, z = FLD.groupPosition(battery.name)
                if FLD.movingUnits and x then
                    local ax, az = T.offset(x, z, side.heading + 180 + math.random(-60, 60), FLD.config.relocateDistance)
                    local fx, fz = T.findFiringPosition(ax, az)
                    FLD.routeTo(battery.name, fx, fz, SPEED_WITHDRAW)
                    battery.artyState = "MOVING"
                    battery.artyUntil = now + FLD.config.relocateSeconds
                else
                    battery.artyState = "READY"
                end
            elseif battery.artyState == "MOVING" and now >= battery.artyUntil then
                battery.artyState = "READY"
            end

            if battery.artyState == "READY" and battery.missions < FLD.config.maxFireMissions and battery.range > 0 then
                targets = targets or FLD.artilleryTargets(front, sideName, now)
                for _, target in ipairs(targets) do
                    if inRange(battery, target.x, target.z) and not FLD.dangerClose(front, sideName, target.x, target.z) then
                        if FLD.fireMission(front, battery, target, now) then
                            -- The next battery should prefer another target.
                            target.score = target.score - 3
                            table.sort(targets, function(a, b)
                                return a.score > b.score
                            end)
                            if target.kind == "battery" and not target.located.announced then
                                target.located.announced = true
                                sayArtillery(front, sideName, now, "enemy artillery located, counter-battery fire.")
                            elseif target.kind == "air defence" then
                                sayArtillery(front, sideName, now, "artillery suppressing enemy air defence at the front.")
                            end
                        end
                        break
                    end
                end
            end
        end
    end
end

function FLD.decide(front, sideName, now)
    FLD.runArtillery(front, sideName, now)
    if front.sides[sideName].stance == "RETREAT" then
        return
    end
    FLD.springAmbushes(front, sideName)
    if not FLD.movingUnits then
        return
    end
    FLD.withdrawBroken(front, sideName)
    FLD.consolidate(front, sideName)
    FLD.commitReserves(front, sideName, now)
    FLD.continueExploitation(front, sideName, now)
    FLD.exploit(front, sideName)
    FLD.keepBusy(front, sideName, now)
    FLD.coverAirDefence(front, sideName, now)
end

function FLD.tickFront(front, now)
    FLD.runEvents(front, now)
    for _, sector in ipairs(front.sectors) do
        FLD.updateSector(front, sector)
    end
    for _, sideName in ipairs({ "blue", "red" }) do
        FLD.decide(front, sideName, now)
        if FLD.config.popupEvents then
            FLD.battlefieldTasks(front, sideName, now)
        end
    end
end

function FLD.updateTasks(now)
    for _, sideName in ipairs({ "blue", "red" }) do
        for _, task in ipairs(FLD.tasks[sideName]) do
            FLD.updateTask(task, now)
        end
    end
end

-------------------------------------------------------------------------------
-- Pop-up taskings
-------------------------------------------------------------------------------

FLD.tasks = { blue = {}, red = {} }
FLD.lastTask = { blue = -math.huge, red = -math.huge }
FLD.nextTaskId = 1

function FLD.grid(x, z)
    local ok, text = pcall(function()
        local lat, lon = coord.LOtoLL({ x = x, y = 0, z = z })
        if mist and mist.tostringMGRS then
            return mist.tostringMGRS(coord.LLtoMGRS(lat, lon), 4)
        end
        return string.format("%.4f %.4f", lat, lon)
    end)
    if ok and text then
        return text
    end
    return string.format("x %d z %d", x, z)
end

local function activeTasks(sideName)
    local count = 0
    for _, task in ipairs(FLD.tasks[sideName]) do
        if task.status == "ACTIVE" then
            count = count + 1
        end
    end
    return count
end

local function hasTask(sideName, key)
    for _, task in ipairs(FLD.tasks[sideName]) do
        if task.key == key and task.status == "ACTIVE" then
            return true
        end
    end
    return false
end

function FLD.placeTaskMark(task)
    if task.markId then
        trigger.action.removeMark(task.markId)
    end
    task.markId = FLD.nextMarkId
    FLD.nextMarkId = FLD.nextMarkId + 1
    trigger.action.markToCoalition(
        task.markId, "TASKING: " .. task.title, { x = task.x, y = 0, z = task.z }, coalitionOf(task.side), true
    )
end

-- Raises a pop-up tasking. kind is DESTROY (kill or break the target groups),
-- DEFEND (hold the sector objective) or ESCORT (get the column through).
-- Event taskings bypass the cooldown, battlefield taskings respect it.
function FLD.raiseTask(front, sideName, now, spec, urgent)
    if not FLD.config.popupEvents or hasTask(sideName, spec.key) then
        return nil
    end
    if not urgent and (now - FLD.lastTask[sideName] < FLD.config.taskCooldownSeconds
        or activeTasks(sideName) >= FLD.config.maxActiveTasks) then
        return nil
    end
    local task = {
        id = FLD.nextTaskId,
        side = sideName,
        front = front,
        key = spec.key,
        kind = spec.kind,
        title = spec.title,
        targets = spec.targets or {},
        sector = spec.sector,
        x = spec.x,
        z = spec.z,
        expires = now + (spec.duration or FLD.config.taskDurationSeconds),
        failWhen = spec.failWhen,
        status = "ACTIVE",
        follow = spec.follow,
    }
    FLD.nextTaskId = FLD.nextTaskId + 1
    FLD.lastTask[sideName] = now
    table.insert(FLD.tasks[sideName], task)
    FLD.placeTaskMark(task)
    if FLD.config.messages then
        trigger.action.outTextForCoalition(
            coalitionOf(sideName),
            string.format("POP-UP TASKING - %s\n%s. Grid %s (marked on the F10 map).", front.name, task.title, FLD.grid(task.x, task.z)),
            30
        )
    end
    return task
end

local function finishTask(task, status)
    task.status = status
    if task.markId then
        trigger.action.removeMark(task.markId)
        task.markId = nil
    end
    local label = status == "COMPLETE" and "TASKING COMPLETE" or "TASKING FAILED"
    say(task.side, string.format("%s - %s: %s.", label, task.front.name, task.title))
end

local function findGroup(front, name)
    for _, group in ipairs(front.groups) do
        if group.name == name then
            return group
        end
    end
    return nil
end

-- A column has arrived when no group is still on the road and at least one
-- made it to the front. A destroyed column never arrives.
local function columnArrived(front, names)
    local any = false
    for _, name in ipairs(names) do
        local group = findGroup(front, name)
        if group and group.state == "ARRIVING" then
            return false
        end
        if group and group.state ~= "DEAD" and group.state ~= "WITHDRAWN" then
            any = true
        end
    end
    return any
end

-- Share of the targets' units still alive and fighting.
local function targetStrength(task)
    local alive, initial = 0, 0
    for _, name in ipairs(task.targets) do
        local group = findGroup(task.front, name)
        local units = #FLD.aliveUnits(name)
        initial = initial + math.max(group and group.initialSize or units, 1)
        if not (group and group.state == "WITHDRAWN") then
            alive = alive + units
        end
    end
    if initial == 0 then
        return 0
    end
    return alive / initial
end

function FLD.updateTask(task, now)
    if task.status ~= "ACTIVE" then
        return
    end
    if task.failWhen and task.failWhen(task) then
        finishTask(task, "FAILED")
        return
    end
    if task.kind == "DESTROY" then
        if targetStrength(task) == 0 then
            finishTask(task, "COMPLETE")
            return
        end
    elseif task.kind == "DEFEND" then
        local sector = task.front.sectors[task.sector]
        if sector.holder == OTHER_SIDE[task.side] and not sector.contested then
            finishTask(task, "FAILED")
            return
        end
        if sector.holder == task.side and not sector.contested then
            finishTask(task, "COMPLETE")
            return
        end
    elseif task.kind == "ESCORT" then
        if targetStrength(task) < 0.5 then
            finishTask(task, "FAILED")
            return
        end
        if columnArrived(task.front, task.targets) then
            finishTask(task, "COMPLETE")
            return
        end
    end
    if now >= task.expires then
        -- Holding out, or keeping the column alive, until the time is up is a
        -- success. Targets still standing at the end are a failure.
        finishTask(task, (task.kind == "DEFEND" or task.kind == "ESCORT") and "COMPLETE" or "FAILED")
        return
    end
    -- Keep the mark on moving targets.
    if task.follow and task.targets[1] then
        for _, name in ipairs(task.targets) do
            local x, z = FLD.groupPosition(name)
            if x then
                if distance(x, z, task.x, task.z) > 300 then
                    task.x, task.z = x, z
                    FLD.placeTaskMark(task)
                end
                break
            end
        end
    end
end

local function groupNames(groups)
    local names = {}
    for _, group in ipairs(groups) do
        table.insert(names, group.name)
    end
    return names
end

local function nearestSector(front, x, z)
    local best, bestDistance = nil, math.huge
    for _, sector in ipairs(front.sectors) do
        local d = distance(x, z, sector.objX, sector.objZ)
        if d < bestDistance then
            best, bestDistance = sector, d
        end
    end
    return best
end

-- Battlefield taskings: raised from what the director sees happening.
function FLD.battlefieldTasks(front, sideName, now)
    local enemy = OTHER_SIDE[sideName]
    local side = front.sides[sideName]

    for _, sector in ipairs(front.sectors) do
        if sector.contested and sector.holder == sideName and sector.current[sideName] > 0
            and strengthShare(sector, sideName) < 0.7 then
            FLD.raiseTask(front, sideName, now, {
                key = "defend" .. sector.index,
                kind = "DEFEND",
                sector = sector.index,
                title = string.format("Troops in contact at %s, CAS requested to hold it", sector.label),
                x = sector.objX,
                z = sector.objZ,
                duration = 900,
            })
        end
    end

    for _, located in ipairs(side.located) do
        local group = findGroup(front, located.name)
        if located.knownAt <= now and group and group.state ~= "DEAD" then
            FLD.raiseTask(front, sideName, now, {
                key = "battery" .. located.name,
                kind = "DESTROY",
                targets = { located.name },
                title = "Enemy artillery battery located, destroy it",
                x = located.x,
                z = located.z,
            })
        end
    end

    for _, group in ipairs(front.groups) do
        if group.side == enemy and group.state ~= "DEAD" then
            local x, z = FLD.groupPosition(group.name)
            if x then
                local sector = nearestSector(front, x, z)
                local where = sector and sector.label or "the front"
                if group.state == "EXPLOITING" then
                    FLD.raiseTask(front, sideName, now, {
                        key = "breakthrough" .. (group.sector or 0),
                        kind = "DESTROY",
                        targets = { group.name },
                        title = string.format("Stop the enemy breakthrough at %s", where),
                        x = x,
                        z = z,
                        follow = true,
                    })
                elseif group.state == "COUNTER" and FLD.isSpotted(front, sideName, x, z) then
                    FLD.raiseTask(front, sideName, now, {
                        key = "counter" .. group.name,
                        kind = "DESTROY",
                        targets = { group.name },
                        title = string.format("Enemy counter-attack moving on %s, hit it before it arrives", where),
                        x = x,
                        z = z,
                        follow = true,
                    })
                elseif group.role == "SHORAD" and FLD.isSpotted(front, sideName, x, z) then
                    FLD.raiseTask(front, sideName, now, {
                        key = "shorad" .. group.name,
                        kind = "DESTROY",
                        targets = { group.name },
                        title = string.format("Enemy air defence spotted near %s, clear it for the helicopters", where),
                        x = x,
                        z = z,
                    })
                end
            end
        end
    end
end

-------------------------------------------------------------------------------
-- Pop-up events
-------------------------------------------------------------------------------

-- Where a flanking raid goes: the enemy guns if any are left, otherwise the
-- weakest objective the enemy holds, otherwise the planned sector.
function FLD.raidTarget(front, event)
    local enemy = OTHER_SIDE[event.side]
    local x, z = FLD.groupPosition(event.groups[1].name)
    local best, bestDistance = nil, math.huge
    for _, group in ipairs(front.groups) do
        if group.side == enemy and group.role == "ARTILLERY" and groupStrength(group) > 0 then
            local gx, gz = FLD.groupPosition(group.name)
            local d = distance(x, z, gx, gz)
            if d < bestDistance then
                best, bestDistance = { x = gx, z = gz, name = "the enemy artillery", theirName = "our artillery" }, d
            end
        end
    end
    if best and bestDistance <= 25000 then
        return best, nil
    end
    local weakest, weakestStrength = nil, math.huge
    for _, sector in ipairs(front.sectors) do
        if sector.holder == enemy and sector.current[enemy] < weakestStrength then
            weakest, weakestStrength = sector, sector.current[enemy]
        end
    end
    local sector = weakest or nearestSector(front, event.destX, event.destZ)
    return { x = sector.objX, z = sector.objZ, name = sector.label, theirName = sector.label }, sector.index
end

function FLD.fireEvent(front, event, now)
    event.fired = true
    local activated = {}
    for _, g in ipairs(event.groups) do
        local dcsGroup = Group.getByName(g.name)
        if dcsGroup then
            dcsGroup:activate()
            local group = {
                name = g.name,
                side = event.side,
                role = g.role,
                reserve = false,
                state = event.kind == "FLANK" and "RAIDING" or "ARRIVING",
                breakPoint = FLD.config.breakPointMin
                    + math.random() * (FLD.config.breakPointMax - FLD.config.breakPointMin),
                initialSize = #FLD.aliveUnits(g.name),
                weaponHold = false,
                range = 0,
                artyState = "READY",
                artyUntil = 0,
                missions = 0,
            }
            table.insert(front.groups, group)
            table.insert(activated, group)
        end
    end
    if #activated == 0 then
        return
    end
    local enemy = OTHER_SIDE[event.side]
    local x, z = FLD.groupPosition(activated[1].name)
    local names = groupNames(activated)

    if event.kind == "FLANK" then
        local target, sectorIndex = FLD.raidTarget(front, event)
        for _, group in ipairs(activated) do
            group.sector = sectorIndex
            FLD.setFireAtWill(group.name, true)
            FLD.routeTo(group.name, target.x, target.z, SPEED_ASSAULT)
        end
        local sector = front.sectors[sectorIndex or 0]
        if sector then
            sector.initial[event.side] = sector.initial[event.side] + activated[1].initialSize
        end
        say(event.side, string.format("%s: flanking raid launched toward %s.", front.name, target.name))
        FLD.raiseTask(front, enemy, now, {
            key = "raid" .. names[1],
            kind = "DESTROY",
            targets = names,
            title = string.format("Enemy armor is flanking toward %s, intercept it", target.theirName),
            x = x,
            z = z,
            follow = true,
        }, true)
    else
        for _, group in ipairs(activated) do
            FLD.routeTo(group.name, event.destX, event.destZ, SPEED_ASSAULT, "On Road")
        end
        local arrived = function()
            return columnArrived(front, names)
        end
        say(event.side, string.format("%s: reinforcement column (%d groups) on the road to the front.", front.name, #activated))
        FLD.raiseTask(front, enemy, now, {
            key = "column" .. names[1],
            kind = "DESTROY",
            targets = names,
            title = "Enemy reinforcement column on the road, interdict it before it reaches the front",
            x = x,
            z = z,
            follow = true,
            failWhen = arrived,
        }, true)
        FLD.raiseTask(front, event.side, now, {
            key = "escort" .. names[1],
            kind = "ESCORT",
            targets = names,
            title = "Friendly reinforcement column moving up, keep it safe until it reaches the front",
            x = x,
            z = z,
            follow = true,
        }, true)
    end
end

function FLD.updateColumns(front)
    for _, group in ipairs(front.groups) do
        if group.state == "ARRIVING" then
            local event = nil
            for _, e in ipairs(front.events) do
                for _, g in ipairs(e.groups) do
                    if g.name == group.name then
                        event = e
                    end
                end
            end
            local x, z = FLD.groupPosition(group.name)
            if event and x and distance(x, z, event.destX, event.destZ) <= FLD.config.columnArrivalDistance then
                local sector = nearestSector(front, x, z)
                group.sector = sector and sector.index
                group.state = "RESERVE"
                group.reserve = true
                local side = front.sides[group.side]
                local hx, hz = T.findPosition(x, z, side.heading, "hide")
                FLD.routeTo(group.name, hx, hz, SPEED_REPOSITION)
                say(group.side, string.format("%s: reinforcements arrived, %s joins the reserve.", front.name, group.name))
            end
        end
    end
end

function FLD.runEvents(front, now)
    if not FLD.config.popupEvents or not FLD.movingUnits then
        return
    end
    for _, event in ipairs(front.events) do
        if not event.fired and now >= event.fireAt and front.sides[event.side].stance ~= "RETREAT" then
            FLD.fireEvent(front, event, now)
        end
    end
    FLD.updateColumns(front)
end

-------------------------------------------------------------------------------
-- Battle smoke
-------------------------------------------------------------------------------

FLD.fires = {}
FLD.nextFireId = 1
FLD.burned = {}

local function startEffect(fire, preset, density)
    fire.effect = string.format("fld-fire-%d", FLD.nextFireId)
    FLD.nextFireId = FLD.nextFireId + 1
    trigger.action.effectSmokeBig({ x = fire.x, y = fire.y, z = fire.z }, preset, density, fire.effect)
end

local function nearAnyObjective(x, z)
    for _, front in ipairs(FLD.frontLines) do
        for _, sector in ipairs(front.sectors) do
            if distance(x, z, sector.objX, sector.objZ) <= FLD.config.battleSmokeRange then
                return true
            end
        end
    end
    return false
end

-- A destroyed vehicle burns where it died. Armor burns hotter and tanks
-- sometimes cook off, soft vehicles mostly just smoke.
function FLD.burnWreck(unitName, point, armored, now)
    if not FLD.config.battleSmoke or FLD.burned[unitName] or not nearAnyObjective(point.x, point.z) then
        return
    end
    FLD.burned[unitName] = true
    if #FLD.fires >= FLD.config.maxBattleFires then
        local oldest = table.remove(FLD.fires, 1)
        trigger.action.effectSmokeStop(oldest.effect)
    end
    local fire = { x = point.x, y = T.height(point.x, point.z), z = point.z, phase = "BURNING" }
    local preset = 5
    if armored then
        preset = math.random() < 0.3 and 2 or 1
    elseif math.random() < 0.4 then
        preset = 1
    end
    startEffect(fire, preset, 0.5 + math.random() * 0.4)
    fire.untilTime = now + FLD.config.burnSecondsMin
        + math.random() * (FLD.config.burnSecondsMax - FLD.config.burnSecondsMin)
    table.insert(FLD.fires, fire)
end

function FLD.updateFires(now)
    local remaining = {}
    for _, fire in ipairs(FLD.fires) do
        if now >= fire.untilTime then
            trigger.action.effectSmokeStop(fire.effect)
            if fire.phase == "BURNING" then
                -- The fire dies down, the wreck smoulders for a while.
                fire.phase = "SMOULDERING"
                startEffect(fire, 5, 0.3 + math.random() * 0.2)
                fire.untilTime = now + FLD.config.smoulderSecondsMin
                    + math.random() * (FLD.config.smoulderSecondsMax - FLD.config.smoulderSecondsMin)
                table.insert(remaining, fire)
            end
        else
            table.insert(remaining, fire)
        end
    end
    FLD.fires = remaining
end

function FLD.onUnitDestroyed(unit, now)
    local ok, err = pcall(function()
        local desc = unit:getDesc()
        if not desc or desc.category ~= Unit.Category.GROUND_UNIT then
            return
        end
        -- Soldiers leave no burning wreck.
        if unit:hasAttribute("Infantry") then
            return
        end
        local armored = unit:hasAttribute("Armored vehicles") or unit:hasAttribute("Tanks")
        FLD.burnWreck(unit:getName(), unit:getPoint(), armored, now)
    end)
    if not ok then
        debug("could not set wreck burning: " .. tostring(err))
    end
end

-------------------------------------------------------------------------------
-- Scheduling
-------------------------------------------------------------------------------

function FLD.tick(_, now)
    for _, front in ipairs(FLD.frontLines) do
        local ok, err = pcall(FLD.tickFront, front, now)
        if not ok then
            env.error("DCSRetribution|Front line director tick failed on " .. tostring(front.name) .. ": " .. tostring(err))
        end
    end
    for _, update in ipairs({ FLD.updateTasks, FLD.updateFires }) do
        local ok, err = pcall(update, now)
        if not ok then
            env.error("DCSRetribution|Front line director update failed: " .. tostring(err))
        end
    end
    return now + FLD.config.tickSeconds
end

local function addWorldEventHandler()
    if not world or not world.addEventHandler then
        return
    end
    local handler = {}
    function handler:onEvent(event)
        if event.id == world.event.S_EVENT_DEAD or event.id == world.event.S_EVENT_UNIT_LOST then
            if event.initiator then
                FLD.onUnitDestroyed(event.initiator, timer.getTime())
            end
            return
        end
        if event.id ~= world.event.S_EVENT_SHOT and event.id ~= world.event.S_EVENT_SHOOTING_START then
            return
        end
        local ok, groupName = pcall(function()
            return event.initiator:getGroup():getName()
        end)
        if ok and groupName then
            FLD.batteryFired(groupName, timer.getTime())
        end
    end
    world.addEventHandler(handler)
end

function FLD.start(data)
    FLD.movingUnits = data.movingUnits ~= "false"
    if data.artilleryStrikes == "false" then
        FLD.config.artilleryStrikes = false
    end
    if data.playerArtillery == "true" then
        FLD.config.playerArtillery = true
    end
    for _, frontData in ipairs(data.frontLines or {}) do
        local ok, result = pcall(function()
            local front = FLD.loadFrontLine(frontData)
            front.consolidationSlots = {}
            FLD.setup(front)
            return front
        end)
        if ok then
            table.insert(FLD.frontLines, result)
            log(string.format("directing front line %s with %d sectors", result.name, #result.sectors))
        else
            env.error("DCSRetribution|Front line director failed to set up " .. tostring(frontData.name) .. ": " .. tostring(result))
        end
    end
    if #FLD.frontLines > 0 then
        addStatusMenus()
        addWorldEventHandler()
        timer.scheduleFunction(FLD.tick, nil, timer.getTime() + FLD.config.tickSeconds)
    end
end

function FLD.init(data)
    if not data then
        log("no front line plan, nothing to direct")
        return
    end
    timer.scheduleFunction(function()
        FLD.start(data)
        return nil
    end, nil, timer.getTime() + FLD.config.startDelaySeconds)
end
