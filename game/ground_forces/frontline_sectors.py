"""Sector planning for front-line ground battles.

Without sectors every combat group is spawned at a random spot along the whole
front line and drives straight at the enemy. With sectors the front is split
into a few focal areas, each with an objective the two sides fight over. Every
side picks a main effort sector when attacking, keeps part of its maneuver
force back as a reserve task force and spreads the rest over the sectors.

The plan is used by the FlotGenerator to place and route groups, and is handed
to the in-mission front line director script (the ``frontlinedirector``
plugin), which keeps fighting the battle by those rules while the mission runs.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional, Sequence

from .ai_ground_planner import CombatGroup, CombatGroupRole
from .combat_stance import CombatStance

# Sectors are focal areas, not a partition of the front: on wide fronts groups
# cluster around the sector centers instead of being spread over many km.
MAX_SECTOR_COUNT = 4
MIN_SECTOR_SPACING = 8000
MAX_SECTOR_WIDTH = 6000

# Groups fighting for a sector objective. Artillery and logistics support the
# whole front and are not assigned to a sector.
MANEUVER_ROLES = frozenset(
    {
        CombatGroupRole.TANK,
        CombatGroupRole.IFV,
        CombatGroupRole.APC,
        CombatGroupRole.ATGM,
        CombatGroupRole.RECON,
        CombatGroupRole.INFANTRY,
    }
)

OFFENSIVE_STANCES = frozenset(
    {CombatStance.AGGRESSIVE, CombatStance.BREAKTHROUGH, CombatStance.ELIMINATION}
)

# Share of the maneuver groups held back as reserve task force.
RESERVE_FRACTION = {
    CombatStance.DEFENSIVE: 0.3,
    CombatStance.AMBUSH: 0.25,
    CombatStance.AGGRESSIVE: 0.2,
    CombatStance.ELIMINATION: 0.15,
    CombatStance.BREAKTHROUGH: 0.1,
    CombatStance.RETREAT: 0.0,
}
MIN_GROUPS_FOR_RESERVE = 3

# Share of the committed maneuver groups sent to the main effort sector.
MAIN_EFFORT_FRACTION = 0.5

# Roles preferred for the reserve, best first.
RESERVE_ROLE_PREFERENCE = (
    CombatGroupRole.TANK,
    CombatGroupRole.IFV,
    CombatGroupRole.APC,
)


@dataclass(frozen=True)
class FrontLineSector:
    index: int
    # Distance along the front line from its left end, in meters.
    center_offset: int
    width: int

    @property
    def start_offset(self) -> int:
        return self.center_offset - self.width // 2

    @property
    def end_offset(self) -> int:
        return self.center_offset + self.width // 2


@dataclass(frozen=True)
class GroupAssignment:
    # None for groups supporting the whole front (artillery, logistics).
    sector: Optional[int]
    reserve: bool


@dataclass(frozen=True)
class SidePlan:
    stance: CombatStance
    main_effort: Optional[int]
    # Parallel to the planned combat groups.
    assignments: list[GroupAssignment]


def sector_count(front_width: int) -> int:
    if front_width < MIN_SECTOR_SPACING:
        return 1
    return max(2, min(MAX_SECTOR_COUNT, front_width // MIN_SECTOR_SPACING))


def build_sectors(front_width: int) -> list[FrontLineSector]:
    count = sector_count(front_width)
    spacing = front_width / count
    width = int(min(spacing * 0.8, MAX_SECTOR_WIDTH))
    return [FrontLineSector(i, int(spacing * (i + 0.5)), width) for i in range(count)]


def choose_main_effort(
    stance: CombatStance, count: int, rng: random.Random
) -> Optional[int]:
    if stance not in OFFENSIVE_STANCES:
        return None
    return rng.randrange(count)


def _pick_reserves(
    groups: Sequence[CombatGroup], maneuver: list[int], stance: CombatStance
) -> set[int]:
    if len(maneuver) < MIN_GROUPS_FOR_RESERVE:
        return set()
    reserve_count = int(len(maneuver) * RESERVE_FRACTION.get(stance, 0.0))
    if reserve_count == 0:
        return set()

    def preference(i: int) -> int:
        role = groups[i].role
        if role in RESERVE_ROLE_PREFERENCE:
            return RESERVE_ROLE_PREFERENCE.index(role)
        return len(RESERVE_ROLE_PREFERENCE)

    return set(sorted(maneuver, key=preference)[:reserve_count])


def plan_side(
    groups: Sequence[CombatGroup],
    stance: CombatStance,
    count: int,
    rng: random.Random,
) -> SidePlan:
    main_effort = choose_main_effort(stance, count, rng)
    maneuver = [i for i, g in enumerate(groups) if g.role in MANEUVER_ROLES]
    reserves = _pick_reserves(groups, maneuver, stance)
    committed = [i for i in maneuver if i not in reserves]
    rng.shuffle(committed)

    sectors: dict[int, int] = {}
    if main_effort is not None:
        main_count = math.ceil(len(committed) * MAIN_EFFORT_FRACTION)
        others = [s for s in range(count) if s != main_effort] or [main_effort]
        for n, i in enumerate(committed):
            sectors[i] = main_effort if n < main_count else others[n % len(others)]
    else:
        for n, i in enumerate(committed):
            sectors[i] = n % count

    # The reserve waits behind the main effort, or the middle of the front.
    reserve_sector = main_effort if main_effort is not None else count // 2
    for i in reserves:
        sectors[i] = reserve_sector

    # Air defence follows the heaviest concentrations of maneuver groups.
    load = [0] * count
    for sector in sectors.values():
        load[sector] += 1
    by_load = sorted(range(count), key=lambda s: -load[s])
    shorad = [i for i, g in enumerate(groups) if g.role == CombatGroupRole.SHORAD]
    for n, i in enumerate(shorad):
        sectors[i] = by_load[n % count]

    assignments = [
        GroupAssignment(sectors.get(i), i in reserves) for i in range(len(groups))
    ]
    return SidePlan(stance, main_effort, assignments)
