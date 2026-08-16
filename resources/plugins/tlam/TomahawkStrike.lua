----- Tomahawk Strike -----
-- Lets players direct BGM-109 cruise missile strikes from friendly VLS ships
-- onto positions marked on the F10 map.
----------------------------------------------------------------

-- Script control functions:
--AddTLAMPlatform(GroupName, Callsign)						--register a ship group that can launch cruise missiles; ignored if it carries none
--AddTLAMObserver(UnitName)									--register a unit that may call strikes

----------------------------------------------------------------

env.info("DCSRetribution|Tomahawk Strike plugin - Imported")

TLAM = {}
TLAM.Platforms = {}											--[groupName] = {callsign = ...}
TLAM.Observers = {}											--[unitName] = {id = groupID, active = true}
TLAM.Marks = {[1] = {}, [2] = {}}							--map markers, per coalition
TLAM.LastFired = {}											--[groupName] = mission time of the last launch

-- Tunables. The configuration script overrides these from the plugin options.
TLAM.MaxRangeMeters = 1250000								--BGM-109 has far more reach than any gun; range is a game balance knob
TLAM.MinRangeMeters = 5000
TLAM.CooldownSeconds = 300
TLAM.SalvoSizes = {1, 2, 4, 8}
TLAM.MaxMarksListed = 8										--keep the radio menu navigable
TLAM.WeaponFlag = 2097152									--Weapon.flag.CruiseMissile
TLAM.MenuName = "Tomahawk Strike"

----- Ammunition -----

-- DCS reports the round as "BGM-109C Tomahawk" but launches a weapon typed
-- BGM_109B, so match on either rather than on one spelling.
local function IsCruiseMissile(desc)
	if not desc then
		return false
	end
	local typeName = desc.typeName or ""
	local displayName = desc.displayName or ""
	return string.find(typeName, "BGM_109") ~= nil
		or string.find(displayName, "BGM%-109") ~= nil
		or string.find(string.lower(displayName), "tomahawk") ~= nil
end

local function CountCruiseMissiles(GroupName)
	local group = Group.getByName(GroupName)
	if not group then
		return 0
	end
	local total = 0
	for _, unit in pairs(group:getUnits()) do
		local ammo = unit:getAmmo()
		if ammo then
			for a = 1, #ammo do
				if IsCruiseMissile(ammo[a].desc) then
					total = total + ammo[a].count
				end
			end
		end
	end
	return total
end

----- Registration -----

function AddTLAMPlatform(GroupName, Callsign)
	local group = Group.getByName(GroupName)
	if not group then
		return false
	end
	if CountCruiseMissiles(GroupName) == 0 then				--most escorts carry none; leave them out of the menu entirely
		return false
	end
	TLAM.Platforms[GroupName] = {callsign = Callsign or GroupName}
	return true
end

function AddTLAMObserver(UnitName)
	if TLAM.Observers[UnitName] == nil then
		TLAM.Observers[UnitName] = {}
	end
end

----- Map markers -----

TLAMMarkHandler = {}
function TLAMMarkHandler:onEvent(event)
	if event.id == world.event.S_EVENT_MARK_ADDED then
		if event.coalition == 1 or event.coalition == 2 then
			table.insert(TLAM.Marks[event.coalition], event)
		else												--not coalition specific, visible to both
			table.insert(TLAM.Marks[1], event)
			table.insert(TLAM.Marks[2], event)
		end
	elseif event.id == world.event.S_EVENT_MARK_REMOVED then
		for c = 1, 2 do
			for i = #TLAM.Marks[c], 1, -1 do
				if TLAM.Marks[c][i].idx == event.idx then
					table.remove(TLAM.Marks[c], i)
				end
			end
		end
	end
end
world.addEventHandler(TLAMMarkHandler)

local function MarkLabel(mark)
	if mark.text and mark.text ~= "" then
		return string.sub(mark.text, 1, 20)
	end
	local lat, lon = coord.LOtoLL(mark.pos)
	local mgrs = coord.LLtoMGRS(lat, lon)
	return mgrs.MGRSDigraph .. " " .. math.floor(mgrs.Easting / 100) .. " " .. math.floor(mgrs.Northing / 100)
end

----- Fire mission -----

local function Distance(a, b)
	local dx = a.x - b.x
	local dz = a.z - b.z
	return math.sqrt(dx * dx + dz * dz)
end

local function Fire(arg)
	local unitName, groupName, markIdx, qty = arg[1], arg[2], arg[3], arg[4]

	local unit = Unit.getByName(unitName)
	if not unit then
		return
	end
	local coalitionId = unit:getCoalition()

	local group = Group.getByName(groupName)
	local platform = TLAM.Platforms[groupName]
	if not group or not platform then
		trigger.action.outTextForCoalition(coalitionId, "Strike request failed: launch platform is no longer on station.", 15)
		return
	end
	local callsign = platform.callsign

	-- The marker may have been dragged or deleted since the menu was built.
	local mark
	for _, m in pairs(TLAM.Marks[coalitionId] or {}) do
		if m.idx == markIdx then
			mark = m
		end
	end
	if not mark then
		trigger.action.outTextForCoalition(coalitionId, callsign .. ": that target marker no longer exists, out.", 15)
		TLAM.BuildMenu(unitName)
		return
	end

	local available = CountCruiseMissiles(groupName)
	if available == 0 then
		trigger.action.outTextForCoalition(coalitionId, callsign .. ": negative, no missiles remaining, out.", 15)
		TLAM.BuildMenu(unitName)
		return
	end
	if qty > available then
		qty = available
	end

	local lastFired = TLAM.LastFired[groupName]
	if lastFired and timer.getTime() - lastFired < TLAM.CooldownSeconds then
		local wait = math.floor(TLAM.CooldownSeconds - (timer.getTime() - lastFired))
		trigger.action.outTextForCoalition(coalitionId, callsign .. ": negative, reloading, ready in " .. wait .. " seconds, out.", 15)
		return
	end

	local range = Distance(group:getUnit(1):getPoint(), mark.pos)
	if range > TLAM.MaxRangeMeters then
		trigger.action.outTextForCoalition(coalitionId, callsign .. ": negative, target out of range at " .. math.floor(range / 1000) .. " km, out.", 15)
		return
	end
	if range < TLAM.MinRangeMeters then
		trigger.action.outTextForCoalition(coalitionId, callsign .. ": negative, target within minimum range, out.", 15)
		return
	end

	group:getController():pushTask({
		id = "FireAtPoint",
		params = {
			x = mark.pos.x,
			y = mark.pos.z,
			radius = 50,
			expendQty = qty,
			expendQtyEnabled = true,
			weaponType = TLAM.WeaponFlag,
		},
	})
	TLAM.LastFired[groupName] = timer.getTime()

	local minutes = math.max(1, math.floor(range / 1000 / 880 * 60 + 0.5))	--BGM-109 cruises around 880 km/h
	trigger.action.outTextForCoalition(coalitionId,
		callsign .. ": rounds away, " .. qty .. " missile(s) on " .. MarkLabel(mark)
		.. ", " .. math.floor(range / 1000) .. " km, impact in approximately " .. minutes .. " minute(s), out.", 20)

	TLAM.BuildMenu(unitName)
end

----- Radio menu -----

function TLAM.BuildMenu(unitName)
	local observer = TLAM.Observers[unitName]
	local unit = Unit.getByName(unitName)
	if not observer or not observer.id or not unit then
		return
	end
	local groupID = observer.id
	local coalitionId = unit:getCoalition()

	-- Remove by the path DCS handed back, never by name. A non-table path
	-- resolves to the menu root, which wipes every other script's items too.
	if observer.rootPath then
		missionCommands.removeItemForGroup(groupID, observer.rootPath)
	end
	local root = missionCommands.addSubMenuForGroup(groupID, TLAM.MenuName)
	observer.rootPath = root

	-- Rebuilding is how a player picks up markers placed since the menu was last drawn.
	missionCommands.addCommandForGroup(groupID, "Refresh target list", root, TLAM.BuildMenu, unitName)

	local marks = TLAM.Marks[coalitionId] or {}
	local first = math.max(1, #marks - TLAM.MaxMarksListed + 1)

	local platforms = 0
	for groupName, platform in pairs(TLAM.Platforms) do
		local group = Group.getByName(groupName)
		if group and group:getCoalition() == coalitionId then
			local available = CountCruiseMissiles(groupName)
			if available > 0 then
				platforms = platforms + 1
				-- Use the path returned by DCS rather than rebuilding it from the
				-- display name, so two platforms sharing a name cannot collide.
				local shipMenu = missionCommands.addSubMenuForGroup(groupID, platform.callsign .. " (" .. available .. ")", root)
				if #marks == 0 then
					missionCommands.addCommandForGroup(groupID, "Mark a target on the F10 map first", shipMenu, TLAM.BuildMenu, unitName)
				else
					for i = first, #marks do
						local mark = marks[i]
						local markMenu = missionCommands.addSubMenuForGroup(groupID, MarkLabel(mark), shipMenu)
						for _, qty in pairs(TLAM.SalvoSizes) do
							if qty <= available then
								missionCommands.addCommandForGroup(groupID, qty .. " missile(s)", markMenu, Fire, {unitName, groupName, mark.idx, qty})
							end
						end
					end
				end
			end
		end
	end

	if platforms == 0 then
		missionCommands.addCommandForGroup(groupID, "No launch platforms available", root, TLAM.BuildMenu, unitName)
	end
end

----- Observer tracking -----

-- A slot reports no unit until a player occupies it, so the menu has to be
-- built on a poll rather than once at mission start.
local function CheckObservers()
	for unitName, observer in pairs(TLAM.Observers) do
		local unit = Unit.getByName(unitName)
		if unit and observer.active == nil then
			observer.active = true
			observer.id = unit:getGroup():getID()
			TLAM.BuildMenu(unitName)
		elseif unit == nil then
			observer.active = nil
		end
	end
	return timer.getTime() + 5
end
timer.scheduleFunction(CheckObservers, nil, timer.getTime() + 2)
