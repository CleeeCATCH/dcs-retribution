"""Selects the ground groups the in-mission dynamic activation script may put to sleep.

Sleeping a group switches its DCS AI off (``Controller.setOnOff(false)``). The units
stay in the world, can be seen, targeted and killed, but stop running the target
search, line-of-sight and pathfinding logic that dominates the CPU cost of ground
units. The script in ``resources/plugins/base/dynamic_activation.lua`` wakes a group
when an enemy ground unit, enemy helicopter or any player comes within the wake
radius, or as soon as the group is hit.

Only groups whose AI does nothing useful while no enemy is close are eligible. Air
defence is never managed: SAMs, EWRs, AAA and MANPADS must keep searching for
aircraft, and SEAD packages need emitting radars to find their targets. Groups that
other scripts task (artillery and ballistic missile launchers) are left alone too.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from game.data.units import UnitClass
from game.theater.theatergroundobject import (
    BuildingGroundObject,
    IadsBuildingGroundObject,
    MotorpoolGroundObject,
    TheaterGroundObject,
    VehicleGroupGroundObject,
)
from game.theater.theatergroup import TheaterGroup

if TYPE_CHECKING:
    from game import Game

# Ground object types whose vehicle groups are passive until an enemy arrives:
# battle positions, motorpools and the vehicles placed around strike targets.
SLEEP_ELIGIBLE_GROUND_OBJECTS: tuple[type[TheaterGroundObject], ...] = (
    VehicleGroupGroundObject,
    MotorpoolGroundObject,
    BuildingGroundObject,
)

# Unit classes that fire-support scripts (artillery, ballistic missile strike)
# task during the mission. A sleeping group cannot execute those fire missions.
SCRIPT_TASKED_UNIT_CLASSES = {UnitClass.ARTILLERY, UnitClass.MISSILE}


@dataclass(frozen=True)
class ManagedGroup:
    group_name: str
    coalition: str
    x: float
    y: float


def ground_object_is_eligible(ground_object: TheaterGroundObject) -> bool:
    if isinstance(ground_object, IadsBuildingGroundObject):
        return False
    return isinstance(ground_object, SLEEP_ELIGIBLE_GROUND_OBJECTS)


def group_is_eligible(group: TheaterGroup) -> bool:
    vehicles = [u for u in group.units if u.is_vehicle]
    if not any(u.alive for u in vehicles):
        return False
    for unit in vehicles:
        if unit.is_anti_air:
            return False
        unit_type = unit.unit_type
        if unit_type is not None and unit_type.unit_class in SCRIPT_TASKED_UNIT_CLASSES:
            return False
    return True


def managed_groups(game: Game) -> Iterator[ManagedGroup]:
    for control_point in game.theater.controlpoints:
        if control_point.captured.is_neutral:
            continue
        coalition = "blue" if control_point.captured.is_blue else "red"
        for ground_object in control_point.ground_objects:
            if not ground_object_is_eligible(ground_object):
                continue
            if game.iads_considerate_culling(ground_object):
                # Culled ground objects are not generated at all.
                continue
            for group in ground_object.groups:
                if not group_is_eligible(group):
                    continue
                position = next(u.position for u in group.units if u.is_vehicle)
                yield ManagedGroup(group.group_name, coalition, position.x, position.y)
