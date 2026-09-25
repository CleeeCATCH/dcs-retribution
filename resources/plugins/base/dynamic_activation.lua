-------------------------------------------------------------------------------------------------
-- Dynamic activation of idle ground units
--
-- Switches the AI of idle ground groups off while nothing that could interact with them is
-- close, and back on when something arrives. A sleeping group keeps its units in the world: they
-- can be seen, attacked and destroyed, but stop running the target search, line-of-sight and
-- pathfinding logic that makes ground units expensive.
--
-- The groups to manage are selected by the mission generator (see
-- game/missiongenerator/dynamicactivation.py) and passed in dcsRetribution.DynamicActivation.
-- Air defences, ships, artillery and missile launchers are never included.
--
-- A group is woken when any of these is within the wake radius:
--   * a ground unit of the enemy coalition that is not part of a fixed ground object
--     (front line units, convoys, units spawned during the mission, Combined Arms players)
--   * a helicopter of the enemy coalition
--   * a player of either coalition
-- Enemy airplanes do not wake a group: the units cannot engage them anyway, and waking every
-- group under an AI strike package would undo the savings at peak activity. A group that is hit
-- wakes immediately and is never put back to sleep, so it can react and so that damage scripts
-- that switch off crippled units are not overridden.
-------------------------------------------------------------------------------------------------

DynamicActivation = DynamicActivation or {}

do
    local data = dcsRetribution and dcsRetribution.DynamicActivation
    if data then
        local RADIUS = tonumber(data.radiusMeters) or 20000
        local RADIUS_SQUARED = RADIUS * RADIUS
        local SLEEP_DELAY = tonumber(data.sleepDelaySeconds) or 180
        local DEBUG = data.debug == "true"
        -- Every group is evaluated once per cycle. The work is spread over one tick per second
        -- so that large campaigns do not stutter every cycle.
        local CYCLE_SECONDS = 10
        local TICK_SECONDS = 1

        local managed = {}
        local byName = {}
        local fixedGroups = {}

        for _, name in ipairs(data.fixedGroupNames or {}) do
            fixedGroups[name] = true
        end

        for _, entry in ipairs(data.groups or {}) do
            local side = coalition.side.RED
            if entry.coalition == "blue" then
                side = coalition.side.BLUE
            end
            local group = {
                name = entry.name,
                side = side,
                x = tonumber(entry.x),
                z = tonumber(entry.z),
                asleep = false,
                released = false,
                -- Never seen anything: groups start asleep unless something is already close.
                lastNear = nil,
            }
            managed[#managed + 1] = group
            byName[group.name] = group
        end

        local function log(message)
            env.info("DCSRetribution|DynamicActivation: " .. message)
        end

        local function setAi(group, on)
            local dcsGroup = Group.getByName(group.name)
            if dcsGroup == nil or not dcsGroup:isExist() then
                -- Destroyed, or never generated. Nothing left to manage.
                group.released = true
                return
            end
            local controller = dcsGroup:getController()
            if controller then
                controller:setOnOff(on)
            end
            group.asleep = not on
        end

        local function release(group)
            if group.released then
                return
            end
            if group.asleep then
                setAi(group, true)
            end
            group.released = true
            if DEBUG then
                log("released " .. group.name)
            end
        end

        -- Lets other scripts take a group out of management, waking it if needed.
        function DynamicActivation.release(groupName)
            local group = byName[groupName]
            if group then
                release(group)
            end
        end

        function DynamicActivation.isAsleep(groupName)
            local group = byName[groupName]
            return group ~= nil and group.asleep
        end

        local function addPoint(list, object)
            local ok, point = pcall(function()
                return object:getPoint()
            end)
            if ok and point then
                list[#list + 1] = point
            end
        end

        local function otherSide(side)
            if side == coalition.side.RED then
                return coalition.side.BLUE
            end
            return coalition.side.RED
        end

        -- Positions that wake groups of the given coalition.
        local function collectObservers(side)
            local points = {}
            local enemy = otherSide(side)
            for _, group in ipairs(coalition.getGroups(enemy, Group.Category.GROUND) or {}) do
                if not fixedGroups[group:getName()] then
                    local lead = group:getUnit(1)
                    if lead then
                        addPoint(points, lead)
                    end
                end
            end
            for _, group in ipairs(coalition.getGroups(enemy, Group.Category.HELICOPTER) or {}) do
                for _, unit in ipairs(group:getUnits() or {}) do
                    addPoint(points, unit)
                end
            end
            for _, playerSide in ipairs({ coalition.side.RED, coalition.side.BLUE }) do
                for _, unit in ipairs(coalition.getPlayers(playerSide) or {}) do
                    addPoint(points, unit)
                end
            end
            return points
        end

        local function anyObserverNear(group, points)
            for i = 1, #points do
                local dx = points[i].x - group.x
                local dz = points[i].z - group.z
                if dx * dx + dz * dz <= RADIUS_SQUARED then
                    return true
                end
            end
            return false
        end

        local function evaluate(group, observers, now)
            if group.released then
                return
            end
            if anyObserverNear(group, observers[group.side]) then
                group.lastNear = now
                if group.asleep then
                    setAi(group, true)
                    if DEBUG then
                        log("woke " .. group.name)
                    end
                end
            elseif not group.asleep then
                if group.lastNear == nil or now - group.lastNear >= SLEEP_DELAY then
                    setAi(group, false)
                    if DEBUG and group.asleep then
                        log("put to sleep " .. group.name)
                    end
                end
            end
        end

        local observers = nil
        local nextIndex = 1
        local batchSize = math.max(1, math.ceil(#managed * TICK_SECONDS / CYCLE_SECONDS))

        local function logSummary()
            local asleep = 0
            local released = 0
            for _, group in ipairs(managed) do
                if group.released then
                    released = released + 1
                elseif group.asleep then
                    asleep = asleep + 1
                end
            end
            log(string.format("%d of %d managed groups asleep, %d released", asleep, #managed, released))
        end

        -- Evaluates the next slice of groups. Returns true when a full cycle completed.
        function DynamicActivation.step(now)
            if nextIndex == 1 or observers == nil then
                observers = {
                    [coalition.side.RED] = collectObservers(coalition.side.RED),
                    [coalition.side.BLUE] = collectObservers(coalition.side.BLUE),
                }
            end
            local last = math.min(#managed, nextIndex + batchSize - 1)
            for i = nextIndex, last do
                evaluate(managed[i], observers, now)
            end
            if last >= #managed then
                nextIndex = 1
                if DEBUG then
                    logSummary()
                end
                return true
            end
            nextIndex = last + 1
            return false
        end

        -- Runs a complete cycle at once. Used at mission start so idle groups go to sleep
        -- straight away.
        function DynamicActivation.fullCycle(now)
            nextIndex = 1
            while not DynamicActivation.step(now) do
            end
        end

        local function tick(_, time)
            local ok, err = pcall(DynamicActivation.step, time)
            if not ok then
                log("error: " .. tostring(err))
            end
            return time + TICK_SECONDS
        end

        local hitHandler = {}
        function hitHandler:onEvent(event)
            if event.id ~= world.event.S_EVENT_HIT or event.target == nil then
                return
            end
            local ok, group = pcall(function()
                return event.target:getGroup()
            end)
            if not ok or group == nil then
                return
            end
            local nameOk, name = pcall(function()
                return group:getName()
            end)
            if nameOk and byName[name] then
                release(byName[name])
            end
        end

        DynamicActivation.hitHandler = hitHandler

        if #managed > 0 then
            world.addEventHandler(hitHandler)
            timer.scheduleFunction(function(_, time)
                local ok, err = pcall(DynamicActivation.fullCycle, time)
                if not ok then
                    log("error: " .. tostring(err))
                end
                timer.scheduleFunction(tick, nil, time + TICK_SECONDS)
                return nil
            end, nil, timer.getTime() + 1)
            log(string.format("managing %d ground groups, wake radius %d m", #managed, RADIUS))
        end
    end
end
