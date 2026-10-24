from __future__ import annotations

import random
from unittest.mock import MagicMock

import pytest

from game.dcs.groundunittype import GroundUnitType
from game.ground_forces.ai_ground_planner import CombatGroup, CombatGroupRole
from game.ground_forces.combat_stance import CombatStance
from game.ground_forces.frontline_sectors import (
    MAX_SECTOR_COUNT,
    MAX_SECTOR_WIDTH,
    build_sectors,
    plan_side,
    sector_count,
)


def _group(role: CombatGroupRole) -> CombatGroup:
    return CombatGroup(role, MagicMock(spec=GroundUnitType), 4)


def _groups(*roles: CombatGroupRole) -> list[CombatGroup]:
    return [_group(role) for role in roles]


MANEUVER_FORCE = (
    [CombatGroupRole.TANK] * 4
    + [CombatGroupRole.IFV] * 3
    + [CombatGroupRole.APC] * 2
    + [CombatGroupRole.ATGM]
)


def test_narrow_front_has_one_sector() -> None:
    assert sector_count(5000) == 1


def test_wide_front_sector_count_is_capped() -> None:
    assert sector_count(80000) == MAX_SECTOR_COUNT
    assert sector_count(16000) == 2


def test_sectors_are_focal_areas_inside_the_front() -> None:
    sectors = build_sectors(80000)
    assert len(sectors) == MAX_SECTOR_COUNT
    for sector in sectors:
        assert sector.width <= MAX_SECTOR_WIDTH
        assert 0 <= sector.start_offset < sector.end_offset <= 80000
    offsets = [s.center_offset for s in sectors]
    assert offsets == sorted(offsets)


@pytest.mark.parametrize(
    "stance",
    [CombatStance.AGGRESSIVE, CombatStance.BREAKTHROUGH, CombatStance.ELIMINATION],
)
def test_attacker_concentrates_on_main_effort(stance: CombatStance) -> None:
    groups = _groups(*MANEUVER_FORCE)
    plan = plan_side(groups, stance, 4, random.Random(1))

    assert plan.main_effort is not None
    committed = [a for a in plan.assignments if not a.reserve]
    on_main = [a for a in committed if a.sector == plan.main_effort]
    assert len(on_main) >= len(committed) / 2
    # Every other sector still gets someone.
    assert {a.sector for a in committed} == set(range(4))


def test_defender_spreads_evenly_without_main_effort() -> None:
    groups = _groups(*MANEUVER_FORCE)
    plan = plan_side(groups, CombatStance.DEFENSIVE, 3, random.Random(2))

    assert plan.main_effort is None
    committed = [a.sector for a in plan.assignments if not a.reserve]
    counts = [committed.count(s) for s in range(3)]
    assert max(counts) - min(counts) <= 1


def test_reserve_prefers_tanks() -> None:
    groups = _groups(*MANEUVER_FORCE)
    plan = plan_side(groups, CombatStance.DEFENSIVE, 2, random.Random(3))

    reserves = [g for g, a in zip(groups, plan.assignments) if a.reserve]
    assert len(reserves) == 3
    assert all(g.role == CombatGroupRole.TANK for g in reserves)


def test_reserve_waits_behind_main_effort() -> None:
    groups = _groups(*MANEUVER_FORCE)
    plan = plan_side(groups, CombatStance.AGGRESSIVE, 4, random.Random(4))

    reserve_sectors = {a.sector for a in plan.assignments if a.reserve}
    assert reserve_sectors == {plan.main_effort}


def test_small_or_retreating_force_keeps_no_reserve() -> None:
    small = plan_side(
        _groups(CombatGroupRole.TANK, CombatGroupRole.IFV),
        CombatStance.DEFENSIVE,
        2,
        random.Random(5),
    )
    retreating = plan_side(
        _groups(*MANEUVER_FORCE), CombatStance.RETREAT, 2, random.Random(5)
    )
    assert not any(a.reserve for a in small.assignments)
    assert not any(a.reserve for a in retreating.assignments)


def test_support_roles() -> None:
    groups = _groups(
        *MANEUVER_FORCE,
        CombatGroupRole.ARTILLERY,
        CombatGroupRole.LOGI,
        CombatGroupRole.SHORAD,
    )
    plan = plan_side(groups, CombatStance.AGGRESSIVE, 4, random.Random(6))

    artillery, logistics, shorad = plan.assignments[-3:]
    assert artillery.sector is None and not artillery.reserve
    assert logistics.sector is None and not logistics.reserve
    # Air defence covers the heaviest concentration: the main effort.
    assert shorad.sector == plan.main_effort


def test_single_sector_front() -> None:
    groups = _groups(*MANEUVER_FORCE)
    plan = plan_side(groups, CombatStance.BREAKTHROUGH, 1, random.Random(7))

    assert plan.main_effort == 0
    assert {a.sector for a in plan.assignments} == {0}
