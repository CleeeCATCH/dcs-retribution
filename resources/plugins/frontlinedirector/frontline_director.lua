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
--   * exploits a collapsed enemy sector by pushing toward the next high ground
--     or the enemy base,
--   * springs ambushes: ambushing groups hold fire until the enemy is close,
--   * runs the front line artillery: batteries fire on enemies friendly units
--     (or players' aircraft) actually see, by priority (counter-battery, air
--     defence, counter-attacks, contested objectives), never danger close, and
--     relocate after every fire mission because firing reveals them to the
--     enemy's counter-battery fire.
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
    commitCooldownSeconds = 180,
    -- Reserve groups committed together as one task force.
    taskForceSize = 2,
    -- A sector whose enemy strength drops below this share is exploited.
    exploitEnemyStrength = 0.3,
    -- Our strength share needed to exploit.
    exploitFriendlyStrength = 0.5,
    -- Distance pushed past the objective when exploiting.
    exploitDistance = 4000,
    -- The enemy base is the exploitation target when it is this close.
    exploitBaseDistance = 15000,
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

local function routePoint(x, z, speed)
    return {
        x = x,
        y = z,
        type = "Turning Point",
        action = "Off Road",
        speed = speed,
        ETA = 0,
        ETA_locked = false,
        speed_locked = true,
        task = { id = "ComboTask", params = { tasks = {} } },
    }
end

function FLD.routeTo(name, x, z, speed)
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
                points = { routePoint(fromX, fromZ, speed), routePoint(x, z, speed) },
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
            -- Enemy batteries located after they fired.
            located = {},
            recentTargets = {},
            lastArtilleryMessage = -math.huge,
        }
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

local function addStatusMenus()
    if not FLD.config.statusMenu then
        return
    end
    for _, sideName in ipairs({ "blue", "red" }) do
        missionCommands.addCommandForCoalition(coalitionOf(sideName), "Front line status", nil, FLD.showStatus, sideName)
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
            and (group.state == "IDLE" or group.state == "COUNTER")
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

-- How urgently a sector needs the reserve. 0 means it does not.
function FLD.sectorNeed(sector, sideName)
    local enemy = OTHER_SIDE[sideName]
    if sector.holder == enemy and not sector.contested then
        return 3
    end
    if sector.contested then
        return 2
    end
    if sector.initial[sideName] > 0 and strengthShare(sector, sideName) < FLD.config.reinforceStrength
        and sector.current[enemy] > 0 then
        return 1
    end
    return 0
end

function FLD.commitReserves(front, sideName, now)
    local side = front.sides[sideName]
    if now - side.lastCommit < FLD.config.commitCooldownSeconds then
        return
    end
    local best, bestNeed = nil, 0
    for _, sector in ipairs(front.sectors) do
        local need = FLD.sectorNeed(sector, sideName)
        if side.mainEffort == sector.index and need > 0 then
            need = need + 0.5
        end
        if need > bestNeed then
            best, bestNeed = sector, need
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

    local counterAttack = bestNeed >= 2
    local committed = 0
    for i = 1, math.min(FLD.config.taskForceSize, #reserves) do
        local group = reserves[i].group
        group.sector = best.index
        best.initial[sideName] = best.initial[sideName] + group.initialSize
        if counterAttack then
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
    if counterAttack then
        say(sideName, string.format("%s: reserve task force (%d groups) committed to counter-attack %s.",
            front.name, committed, best.label))
    else
        say(sideName, string.format("%s: reserve task force (%d groups) reinforcing %s.",
            front.name, committed, best.label))
    end
end

function FLD.exploitationTarget(front, sideName, sector)
    local side = front.sides[sideName]
    if side.enemyBaseX and distance(sector.objX, sector.objZ, side.enemyBaseX, side.enemyBaseZ)
        <= FLD.config.exploitBaseDistance then
        return side.enemyBaseX, side.enemyBaseZ, "the enemy base"
    end
    local x, z = T.offset(sector.objX, sector.objZ, side.heading, FLD.config.exploitDistance)
    local keyX, keyZ, keyH = T.findKeyTerrain(x, z, FLD.config.keyTerrainRadius)
    return keyX, keyZ, string.format("Hill %d", math.floor(keyH + 0.5))
end

function FLD.exploit(front, sideName)
    local side = front.sides[sideName]
    if not OFFENSIVE_STANCES[side.stance] then
        return
    end
    local enemy = OTHER_SIDE[sideName]
    for _, sector in ipairs(front.sectors) do
        if not side.exploited[sector.index] and sideHolding(sector) == sideName
            and sector.initial[enemy] > 0
            and strengthShare(sector, enemy) <= FLD.config.exploitEnemyStrength
            and strengthShare(sector, sideName) >= FLD.config.exploitFriendlyStrength then
            local x, z, targetName = FLD.exploitationTarget(front, sideName, sector)
            local count = 0
            for _, group in ipairs(front.groups) do
                if group.side == sideName and group.sector == sector.index and ASSAULT_ROLES[group.role]
                    and (group.state == "HOLDING" or group.state == "IDLE" or group.state == "COUNTER") then
                    if FLD.routeTo(group.name, x, z, SPEED_ASSAULT) then
                        group.state = "EXPLOITING"
                        count = count + 1
                    end
                end
            end
            if count > 0 then
                side.exploited[sector.index] = true
                say(sideName, string.format("%s: enemy collapsing at %s, task force exploiting toward %s.",
                    front.name, sector.label, targetName))
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
            table.insert(targets, { x = located.x, z = located.z, score = 8, name = located.name, kind = "battery" })
        end
    end

    for _, group in ipairs(front.groups) do
        if group.side == enemy and group.state ~= "DEAD" and group.role ~= "ARTILLERY" then
            local x, z = FLD.groupPosition(group.name)
            if x and FLD.isSpotted(front, sideName, x, z) then
                local score = TARGET_PRIORITY[group.role] or 2
                local kind = group.role == "SHORAD" and "air defence" or "armor"
                if group.state == "COUNTER" or group.state == "EXPLOITING" then
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
                    local hx, hz = T.findPosition(ax, az, side.heading, "hide")
                    FLD.routeTo(battery.name, hx, hz, SPEED_WITHDRAW)
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
                            if target.kind == "battery" then
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
    FLD.exploit(front, sideName)
end

function FLD.tickFront(front, now)
    for _, sector in ipairs(front.sectors) do
        FLD.updateSector(front, sector)
    end
    for _, sideName in ipairs({ "blue", "red" }) do
        FLD.decide(front, sideName, now)
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
    return now + FLD.config.tickSeconds
end

local function addShotHandler()
    if not world or not world.addEventHandler then
        return
    end
    local handler = {}
    function handler:onEvent(event)
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
        addShotHandler()
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
