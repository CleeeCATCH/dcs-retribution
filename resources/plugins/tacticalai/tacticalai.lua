-------------------------------------------------------------------------------
-- Tactical AI for DCS Retribution
--
-- Gives the AI flights Retribution generates some judgement while the mission
-- is running. DCS does the flying and the fighting; this script only decides
-- *what* each flight should be doing:
--
--   * GCI commit: CAP flights are sent after enemy aircraft that their side's
--     AWACS, EWRs or other fighters can see, instead of waiting for targets to
--     wander into their own radar. Contacts are shared out so two CAPs don't
--     pile onto one pair while another pair goes unchallenged. A committed CAP
--     goes back to its station when the target dies, leaves the leash, the CAP
--     runs out of missiles, or the commit takes too long.
--   * Retreat: fighters that are badly outnumbered and short of missiles break
--     off and head home instead of dying.
--   * Strike abort: strike flights whose fighter escort has been destroyed or
--     has gone home turn back when enemy fighters show up, rather than pressing
--     on alone.
--   * Jettison: strike flights are allowed to drop their bombs to defend
--     themselves when enemy fighters get close.
--
-- Mission data comes from dcsRetribution.TacticalAI, written by the
-- Retribution mission generator. Options come from
-- dcsRetribution.plugins.tacticalai (the plugin's settings page).
-------------------------------------------------------------------------------

TacticalAI = TacticalAI or {}
local TAI = TacticalAI

local NM = 1852

TAI.defaults = {
    enableCommit = true,
    commitRangeNm = 60,
    leashRangeNm = 80,
    maxCommitMinutes = 10,
    enableRetreat = true,
    outnumberedRatio = 2,
    lowMissilesPerAircraft = 2,
    enableStrikeAbort = true,
    abortUnescorted = false,
    fighterThreatRangeNm = 30,
    enableJettison = true,
    jettisonRangeNm = 15,
    updateIntervalSecs = 15,
    debug = false,
}

-- Per-flight runtime state, keyed by the flight's index in the exported list.
TAI.state = {}
TAI.ewrCache = { [1] = {}, [2] = {} }
TAI.ewrCacheTime = -math.huge

-------------------------------------------------------------------------------
-- Helpers
-------------------------------------------------------------------------------

function TAI.option(name)
    local plugins = dcsRetribution and dcsRetribution.plugins
    local options = plugins and plugins.tacticalai
    if options and options[name] ~= nil then
        return options[name]
    end
    return TAI.defaults[name]
end

local function log(message)
    env.info("DCSRetribution|TacticalAI: " .. message)
    if TAI.option("debug") then
        trigger.action.outText("TacticalAI: " .. message, 10)
    end
end

local function dist2d(a, b)
    local dx = a.x - b.x
    local dz = a.z - b.z
    return math.sqrt(dx * dx + dz * dz)
end

local function aliveUnits(group)
    local alive = {}
    if not group or not group:isExist() then
        return alive
    end
    for _, unit in ipairs(group:getUnits() or {}) do
        if unit and unit:isExist() and unit:getLife() > 1 then
            table.insert(alive, unit)
        end
    end
    return alive
end

local function leadPosition(group)
    local unit = aliveUnits(group)[1]
    return unit and unit:getPoint() or nil
end

local function isAirborne(group)
    local unit = aliveUnits(group)[1]
    return unit ~= nil and unit:inAir()
end

-- Air-to-air missiles left in the whole flight.
function TAI.aamCount(group)
    local total = 0
    for _, unit in ipairs(aliveUnits(group)) do
        for _, ammo in ipairs(unit:getAmmo() or {}) do
            local desc = ammo.desc
            if desc
                and desc.category == Weapon.Category.MISSILE
                and desc.missileCategory == Weapon.MissileCategory.AAM
            then
                total = total + (ammo.count or 0)
            end
        end
    end
    return total
end

local function isFighter(unit)
    return unit:hasAttribute("Fighters")
        or unit:hasAttribute("Multirole fighters")
        or unit:hasAttribute("Interceptors")
end

local function isHighValue(unit)
    return unit:hasAttribute("AWACS")
        or unit:hasAttribute("Tankers")
        or unit:hasAttribute("Bombers")
        or unit:hasAttribute("Strategic bombers")
end

-- The DCS group of an exported flight, or nil if it hasn't spawned or is dead.
function TAI.flightGroup(flight)
    for _, name in ipairs(flight.units or {}) do
        local unit = Unit.getByName(name)
        if unit and unit:isExist() then
            local group = unit:getGroup()
            if group and group:isExist() then
                flight.groupName = group:getName()
                return group
            end
        end
    end
    return nil
end

-- The mission-editor group name, known even before the group spawns.
local function flightGroupName(flight)
    if flight.groupName then
        return flight.groupName
    end
    local units = mist and mist.DBs and mist.DBs.unitsByName
    for _, name in ipairs(flight.units or {}) do
        local data = units and units[name]
        if data and data.groupName then
            flight.groupName = data.groupName
            return data.groupName
        end
    end
    return nil
end

local function stateFor(index)
    local state = TAI.state[index]
    if not state then
        state = { mode = "normal", cooldownUntil = 0, seenAlive = false }
        TAI.state[index] = state
    end
    return state
end

-- True while this script has taken a group off its planned mission. Other
-- scripts (the escort leash in dcs_retribution.lua) leave such groups alone.
function TAI.isManaged(groupName)
    for index, flight in ipairs(TAI.flights or {}) do
        if flight.groupName == groupName then
            local mode = stateFor(index).mode
            return mode == "retreating" or mode == "aborted"
        end
    end
    return false
end

-------------------------------------------------------------------------------
-- Air picture
-------------------------------------------------------------------------------

local function refreshEwrCache(now)
    if now - TAI.ewrCacheTime < 300 then
        return
    end
    TAI.ewrCacheTime = now
    for _, side in ipairs({ 1, 2 }) do
        local names = {}
        for _, group in ipairs(coalition.getGroups(side, Group.Category.GROUND) or {}) do
            for _, unit in ipairs(group:getUnits() or {}) do
                if unit:hasAttribute("EWR") then
                    table.insert(names, group:getName())
                    break
                end
            end
        end
        TAI.ewrCache[side] = names
    end
end

local function sensorGroups(side)
    local sensors = {}
    -- AWACS and every managed flight on this side.
    for _, flight in ipairs(TAI.flights or {}) do
        if flight.side == side then
            local group = TAI.flightGroup(flight)
            if group then
                table.insert(sensors, group)
            end
        end
    end
    for _, name in ipairs(TAI.ewrCache[side] or {}) do
        local group = Group.getByName(name)
        if group and group:isExist() then
            table.insert(sensors, group)
        end
    end
    return sensors
end

-- Enemy aircraft the given side can currently see, grouped by DCS group.
-- Each contact: { group, groupName, units = {unit...}, position, fighters,
-- highValue }.
function TAI.buildPicture(side)
    local contacts = {}
    local seenUnits = {}
    for _, sensor in ipairs(sensorGroups(side)) do
        local controller = sensor:getController()
        local ok, detected = pcall(
            controller.getDetectedTargets,
            controller,
            Controller.Detection.RADAR,
            Controller.Detection.DLINK,
            Controller.Detection.VISUAL,
            Controller.Detection.OPTIC,
            Controller.Detection.IRST
        )
        if ok and detected then
            for _, contact in ipairs(detected) do
                local object = contact.object
                local okUnit, isAircraft = pcall(function()
                    if not object or not object:isExist() then
                        return false
                    end
                    if object:getCategory() ~= Object.Category.UNIT then
                        return false
                    end
                    local category = object:getDesc().category
                    return (category == Unit.Category.AIRPLANE
                        or category == Unit.Category.HELICOPTER)
                        and object:getCoalition() ~= side
                end)
                if okUnit and isAircraft then
                    local unitName = object:getName()
                    if not seenUnits[unitName] then
                        seenUnits[unitName] = true
                        local group = object:getGroup()
                        local groupName = group:getName()
                        local entry = contacts[groupName]
                        if not entry then
                            entry = {
                                group = group,
                                groupName = groupName,
                                units = {},
                                fighters = 0,
                                highValue = false,
                            }
                            contacts[groupName] = entry
                        end
                        table.insert(entry.units, object)
                        if isFighter(object) then
                            entry.fighters = entry.fighters + 1
                        end
                        if isHighValue(object) then
                            entry.highValue = true
                        end
                        entry.position = entry.position or object:getPoint()
                    end
                end
            end
        end
    end
    return contacts
end

-- Number of enemy fighter aircraft within range of a position.
function TAI.fightersNear(picture, position, range)
    local count = 0
    for _, contact in pairs(picture) do
        for _, unit in ipairs(contact.units) do
            if isFighter(unit) and unit:isExist() and dist2d(unit:getPoint(), position) <= range then
                count = count + 1
            end
        end
    end
    return count
end

-------------------------------------------------------------------------------
-- Sending a flight home
-------------------------------------------------------------------------------

-- The landing leg of the flight's planned route, so it lands where it was
-- going to land anyway (airfield, FARP or carrier).
function TAI.homeRoute(flight)
    local groupName = flightGroupName(flight)
    if not groupName then
        return nil
    end
    local ok, route = pcall(mist.getGroupRoute, groupName, true)
    if not ok or type(route) ~= "table" or #route == 0 then
        return nil
    end
    local landing = #route
    for i = #route, 1, -1 do
        if route[i].type == "Land" then
            landing = i
            break
        end
    end
    local point = mist.utils.deepCopy(route[landing])
    point.ETA_locked = false
    point.speed_locked = true
    return { point }
end

function TAI.sendHome(index, flight, group, mode, reason)
    local state = stateFor(index)
    local route = TAI.homeRoute(flight)
    local controller = group:getController()
    controller:setOption(
        AI.Option.Air.id.REACTION_ON_THREAT,
        AI.Option.Air.val.REACTION_ON_THREAT.BYPASS_AND_ESCAPE
    )
    controller:setOption(AI.Option.Air.id.ROE, AI.Option.Air.val.ROE.RETURN_FIRE)
    if flight.role == "striker" then
        controller:setOption(AI.Option.Air.id.PROHIBIT_JETTISON, false)
    end
    if route then
        controller:setTask({ id = "Mission", params = { route = { points = route } } })
    end
    state.mode = mode
    state.target = nil
    log(string.format("%s %s (%s)", group:getName(), mode, reason))
end

-------------------------------------------------------------------------------
-- Behaviours
-------------------------------------------------------------------------------

-- Ends a commit. Only pop the attack task when it is still running (the
-- target is alive): DCS removes a finished AttackGroup task itself, and a
-- second pop would throw away the CAP's patrol mission underneath it. When the
-- flight is out of missiles DCS's own RTB-on-winchester takes over.
local function releaseCommit(state, group, now, reason, popAttack)
    if popAttack then
        local controller = group:getController()
        pcall(controller.popTask, controller)
    end
    log(string.format("%s back on station (%s)", group:getName(), reason))
    state.mode = "normal"
    state.target = nil
    state.cooldownUntil = now + 60
end

-- Ends commits that are finished; returns how many of our aircraft are
-- assigned to each enemy group.
local function updateCommitted(side, now)
    local assigned = {}
    local leash = TAI.option("leashRangeNm") * NM
    local maxTime = TAI.option("maxCommitMinutes") * 60
    for index, flight in ipairs(TAI.flights) do
        local state = stateFor(index)
        if flight.side == side and state.mode == "committed" then
            local group = TAI.flightGroup(flight)
            if not group then
                state.mode = "dead"
            else
                local target = Group.getByName(state.target)
                local targetPosition = target and leadPosition(target)
                if not targetPosition then
                    releaseCommit(state, group, now, "target destroyed", false)
                elseif flight.anchor and dist2d(targetPosition, flight.anchor) > leash then
                    releaseCommit(state, group, now, "target left the leash", true)
                elseif now - state.since > maxTime then
                    releaseCommit(state, group, now, "commit timed out", true)
                elseif TAI.aamCount(group) == 0 then
                    releaseCommit(state, group, now, "out of missiles", false)
                else
                    assigned[state.target] = (assigned[state.target] or 0) + #aliveUnits(group)
                end
            end
        end
    end
    return assigned
end

local function commitNewTargets(side, picture, assigned, now)
    local commitRange = TAI.option("commitRangeNm") * NM
    local leash = TAI.option("leashRangeNm") * NM
    for index, flight in ipairs(TAI.flights) do
        local state = stateFor(index)
        if flight.side == side and flight.role == "cap"
            and state.mode == "normal" and now >= state.cooldownUntil
        then
            local group = TAI.flightGroup(flight)
            local position = group and leadPosition(group)
            if position and isAirborne(group) and TAI.aamCount(group) > 0
                and (not flight.anchor or dist2d(position, flight.anchor) <= leash)
            then
                local best, bestScore
                for name, contact in pairs(picture) do
                    local contactPosition = leadPosition(contact.group)
                    if contactPosition
                        and (assigned[name] or 0) < #contact.units
                        and (not flight.anchor or dist2d(contactPosition, flight.anchor) <= leash)
                    then
                        local range = dist2d(position, contactPosition)
                        if range <= commitRange then
                            -- Closest first, but bombers and support aircraft
                            -- are worth a detour.
                            local score = range - (contact.highValue and 20 * NM or 0)
                            if not bestScore or score < bestScore then
                                best, bestScore = contact, score
                            end
                        end
                    end
                end
                if best then
                    local controller = group:getController()
                    local ok = pcall(controller.pushTask, controller, {
                        id = "AttackGroup",
                        params = { groupId = best.group:getID() },
                    })
                    if ok then
                        state.mode = "committed"
                        state.target = best.groupName
                        state.since = now
                        assigned[best.groupName] = (assigned[best.groupName] or 0) + #aliveUnits(group)
                        log(string.format("%s committing on %s", group:getName(), best.groupName))
                    end
                end
            end
        end
    end
end

local function updateRetreats(side, picture)
    local ratio = TAI.option("outnumberedRatio")
    local lowMissiles = TAI.option("lowMissilesPerAircraft")
    local range = TAI.option("fighterThreatRangeNm") * NM
    for index, flight in ipairs(TAI.flights) do
        local state = stateFor(index)
        if flight.side == side and (flight.role == "fighter" or flight.role == "cap") then
            if state.mode == "normal" or state.mode == "committed" then
                local group = TAI.flightGroup(flight)
                local position = group and leadPosition(group)
                if position and isAirborne(group) then
                    local own = #aliveUnits(group)
                    local enemies = TAI.fightersNear(picture, position, range)
                    if own > 0 and enemies >= own * ratio
                        and TAI.aamCount(group) < own * lowMissiles
                    then
                        TAI.sendHome(index, flight, group, "retreating",
                            string.format("%d enemy fighters vs %d, low on missiles", enemies, own))
                    end
                end
            end
        end
    end
end

-- Whether the package still has a fighter escort that is doing its job.
local function escortStatus(package)
    local planned, alive = false, false
    for index, flight in ipairs(TAI.flights) do
        if flight.package == package and flight.role == "fighter" and flight.escort then
            planned = true
            local state = stateFor(index)
            local group = TAI.flightGroup(flight)
            if group then
                state.seenAlive = true
                if state.mode ~= "retreating" then
                    alive = true
                end
            elseif not state.seenAlive then
                -- Hasn't spawned yet; give it the benefit of the doubt.
                alive = true
            end
        end
    end
    return planned, alive
end

local function updateStrikers(side, picture)
    local threatRange = TAI.option("fighterThreatRangeNm") * NM
    local jettisonRange = TAI.option("jettisonRangeNm") * NM
    for index, flight in ipairs(TAI.flights) do
        local state = stateFor(index)
        if flight.side == side and flight.role == "striker" and state.mode == "normal" then
            local group = TAI.flightGroup(flight)
            local position = group and leadPosition(group)
            if position and isAirborne(group) then
                if TAI.option("enableJettison") and not state.jettisonAllowed
                    and TAI.fightersNear(picture, position, jettisonRange) > 0
                then
                    group:getController():setOption(AI.Option.Air.id.PROHIBIT_JETTISON, false)
                    state.jettisonAllowed = true
                    log(group:getName() .. " cleared to jettison")
                end

                if flight.target then
                    local toTarget = dist2d(position, flight.target)
                    -- Once a flight is in the target area it's committed.
                    if toTarget < 15 * NM then
                        state.reachedTarget = true
                    end
                    if TAI.option("enableStrikeAbort") and not state.reachedTarget then
                        local planned, alive = escortStatus(flight.package)
                        local exposed = (planned and not alive)
                            or (not planned and TAI.option("abortUnescorted"))
                        local enemies = TAI.fightersNear(picture, position, threatRange)
                        if exposed and enemies > 0 and enemies >= #aliveUnits(group) then
                            TAI.sendHome(index, flight, group, "aborted",
                                string.format("no escort, %d enemy fighters", enemies))
                        end
                    end
                end
            end
        end
    end
end

-------------------------------------------------------------------------------
-- Main loop
-------------------------------------------------------------------------------

local function loadFlights()
    local data = dcsRetribution and dcsRetribution.TacticalAI
    if type(data) ~= "table" or type(data.flights) ~= "table" then
        return nil
    end
    local flights = {}
    for _, raw in ipairs(data.flights) do
        local flight = {
            units = raw.units or {},
            side = tonumber(raw.side),
            role = raw.role,
            flightType = raw.flightType,
            package = raw.package,
            escort = raw.escort == "true",
        }
        if raw.anchorX and raw.anchorY then
            flight.anchor = { x = tonumber(raw.anchorX), z = tonumber(raw.anchorY) }
        end
        if raw.targetX and raw.targetY then
            flight.target = { x = tonumber(raw.targetX), z = tonumber(raw.targetY) }
        end
        table.insert(flights, flight)
    end
    return flights
end

function TAI.update(now)
    if not TAI.flights then
        TAI.flights = loadFlights()
        if not TAI.flights then
            return
        end
        log(string.format("managing %d AI flights", #TAI.flights))
    end

    refreshEwrCache(now)
    for _, side in ipairs({ 1, 2 }) do
        local picture = TAI.buildPicture(side)
        if TAI.option("enableCommit") then
            local assigned = updateCommitted(side, now)
            commitNewTargets(side, picture, assigned, now)
        end
        if TAI.option("enableRetreat") then
            updateRetreats(side, picture)
        end
        updateStrikers(side, picture)
    end
end

function TAI.tick(_, now)
    local ok, err = pcall(TAI.update, now)
    if not ok then
        env.error("DCSRetribution|TacticalAI: " .. tostring(err))
    end
    return now + TAI.option("updateIntervalSecs")
end

timer.scheduleFunction(TAI.tick, nil, timer.getTime() + 10)
