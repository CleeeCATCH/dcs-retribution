"""Pop-up front line events backed by real inventory.

Events give the front line director surprises to spring during the mission: a
flanking raid, or a reinforcement column driving up from the rear. Their units
are drawn from the armor a control point did not deploy to the front this turn
(see reserve_armor_for), so no side ever fields units it does not own. The
groups are generated late-activated and registered as front line units, so
losses come off the base like any other front line loss, and a group whose
event never fires loses nothing.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

from game.data.units import UnitClass
from game.dcs.groundunittype import GroundUnitType
from .ai_ground_planner import CombatGroupRole
from .combat_stance import CombatStance
from .frontline_sectors import OFFENSIVE_STANCES


class FrontLineEventKind(Enum):
    # Armor hooks around a flank to hit the enemy's rear or a weak sector.
    FLANK = "FLANK"
    # Reinforcements drive up from the rear and join the reserve.
    COLUMN = "COLUMN"


FLANK_CLASSES = (UnitClass.TANK, UnitClass.IFV, UnitClass.RECON, UnitClass.APC)
COLUMN_CLASSES = (UnitClass.TANK, UnitClass.IFV, UnitClass.APC, UnitClass.ATGM)
ESCORT_CLASSES = (UnitClass.SHORAD, UnitClass.AAA)

ROLE_FOR_CLASS = {
    UnitClass.TANK: CombatGroupRole.TANK,
    UnitClass.IFV: CombatGroupRole.IFV,
    UnitClass.APC: CombatGroupRole.APC,
    UnitClass.ATGM: CombatGroupRole.ATGM,
    UnitClass.RECON: CombatGroupRole.RECON,
    UnitClass.SHORAD: CombatGroupRole.SHORAD,
    UnitClass.AAA: CombatGroupRole.SHORAD,
}

MAX_EVENT_GROUP_SIZE = 4
COLUMN_MANEUVER_GROUPS = 2

# Chance of an event per side and front line. Defenders occasionally launch a
# spoiling attack around a flank.
FLANK_CHANCE_ATTACKING = 0.6
FLANK_CHANCE_DEFENDING = 0.3
COLUMN_CHANCE = 0.7


@dataclass(frozen=True)
class EventGroup:
    unit_type: GroundUnitType
    size: int
    role: CombatGroupRole


@dataclass(frozen=True)
class PlannedEvent:
    kind: FrontLineEventKind
    groups: list[EventGroup]


def draw_group(
    spares: dict[GroundUnitType, int],
    classes: Sequence[UnitClass],
    max_size: int = MAX_EVENT_GROUP_SIZE,
) -> Optional[EventGroup]:
    """Takes one group out of the spare inventory, best class first.

    Within a class the most plentiful type is used, so events don't strip the
    last unit of a rare type. Returns None when nothing suitable is left.
    """
    for unit_class in classes:
        candidates = [
            (count, unit_type)
            for unit_type, count in spares.items()
            if count > 0 and unit_type.unit_class == unit_class
        ]
        if not candidates:
            continue
        count, unit_type = max(candidates, key=lambda c: c[0])
        size = min(count, max_size)
        spares[unit_type] = count - size
        return EventGroup(unit_type, size, ROLE_FOR_CLASS[unit_class])
    return None


def plan_events(
    stance: CombatStance,
    spares: dict[GroundUnitType, int],
    rng: random.Random,
) -> list[PlannedEvent]:
    """Plans the events of one side of a front line, consuming spares."""
    if stance == CombatStance.RETREAT:
        return []

    events = []
    flank_chance = (
        FLANK_CHANCE_ATTACKING
        if stance in OFFENSIVE_STANCES
        else FLANK_CHANCE_DEFENDING
    )
    if rng.random() < flank_chance:
        group = draw_group(spares, FLANK_CLASSES)
        if group is not None:
            events.append(PlannedEvent(FrontLineEventKind.FLANK, [group]))

    if rng.random() < COLUMN_CHANCE:
        groups = []
        for _ in range(COLUMN_MANEUVER_GROUPS):
            group = draw_group(spares, COLUMN_CLASSES)
            if group is not None:
                groups.append(group)
        if groups:
            escort = draw_group(spares, ESCORT_CLASSES, max_size=1)
            if escort is not None:
                groups.append(escort)
            events.append(PlannedEvent(FrontLineEventKind.COLUMN, groups))
    return events
