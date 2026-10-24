from __future__ import annotations

import random
from unittest.mock import MagicMock

from game.data.units import UnitClass
from game.dcs.groundunittype import GroundUnitType
from game.ground_forces.ai_ground_planner import CombatGroupRole
from game.ground_forces.combat_stance import CombatStance
from game.ground_forces.frontline_events import (
    FLANK_CLASSES,
    FrontLineEventKind,
    MAX_EVENT_GROUP_SIZE,
    draw_group,
    plan_events,
)


def _unit(unit_class: UnitClass) -> GroundUnitType:
    u = MagicMock(spec=GroundUnitType)
    u.unit_class = unit_class
    return u


class AlwaysRng(random.Random):
    """Every event roll succeeds."""

    def random(self) -> float:
        return 0.0


class NeverRng(random.Random):
    def random(self) -> float:
        return 0.99


def test_draw_group_takes_units_out_of_the_spares() -> None:
    tank = _unit(UnitClass.TANK)
    spares = {tank: 6}
    group = draw_group(spares, FLANK_CLASSES)
    assert group is not None
    assert group.unit_type is tank
    assert group.size == MAX_EVENT_GROUP_SIZE
    assert group.role == CombatGroupRole.TANK
    assert spares[tank] == 6 - MAX_EVENT_GROUP_SIZE


def test_draw_group_prefers_class_order_then_the_most_plentiful_type() -> None:
    ifv = _unit(UnitClass.IFV)
    rare_tank = _unit(UnitClass.TANK)
    common_tank = _unit(UnitClass.TANK)
    spares = {ifv: 10, rare_tank: 1, common_tank: 3}
    group = draw_group(spares, FLANK_CLASSES)
    assert group is not None
    assert group.unit_type is common_tank
    assert group.size == 3
    assert spares == {ifv: 10, rare_tank: 1, common_tank: 0}


def test_draw_group_never_uses_unsuitable_or_missing_units() -> None:
    artillery = _unit(UnitClass.ARTILLERY)
    spares = {artillery: 8}
    assert draw_group(spares, FLANK_CLASSES) is None
    assert draw_group({}, FLANK_CLASSES) is None
    assert spares == {artillery: 8}


def test_events_only_use_what_the_side_has() -> None:
    tank = _unit(UnitClass.TANK)
    spares = {tank: 5}
    events = plan_events(CombatStance.AGGRESSIVE, spares, AlwaysRng())

    used = sum(g.size for event in events for g in event.groups)
    assert used == 5
    assert spares[tank] == 0
    assert [e.kind for e in events] == [
        FrontLineEventKind.FLANK,
        FrontLineEventKind.COLUMN,
    ]


def test_no_spares_means_no_events() -> None:
    assert plan_events(CombatStance.BREAKTHROUGH, {}, AlwaysRng()) == []


def test_column_brings_an_air_defence_escort_when_available() -> None:
    ifv = _unit(UnitClass.IFV)
    sam = _unit(UnitClass.SHORAD)
    spares = {ifv: 12, sam: 2}
    events = plan_events(CombatStance.DEFENSIVE, spares, AlwaysRng())
    column = next(e for e in events if e.kind == FrontLineEventKind.COLUMN)
    roles = [g.role for g in column.groups]
    assert roles == [CombatGroupRole.IFV, CombatGroupRole.IFV, CombatGroupRole.SHORAD]
    assert column.groups[-1].size == 1
    assert spares[sam] == 1


def test_retreating_side_plans_nothing() -> None:
    spares = {_unit(UnitClass.TANK): 20}
    assert plan_events(CombatStance.RETREAT, spares, AlwaysRng()) == []
    assert list(spares.values()) == [20]


def test_failed_rolls_plan_nothing() -> None:
    spares = {_unit(UnitClass.TANK): 20}
    assert plan_events(CombatStance.AGGRESSIVE, spares, NeverRng()) == []
