from __future__ import annotations

from typing import Optional
from unittest.mock import MagicMock, patch

from game.commander.tasks.primitive.barcap import PlanBarcap
from game.commander.tasks.primitive.recovery import MARGIN, PlanRecovery
from game.commander.theaterstate import TheaterState
from game.settings import Settings


def _state(packages_remaining: Optional[int]) -> TheaterState:
    context = MagicMock()
    context.settings = Settings()
    return TheaterState(
        context=context,
        barcaps_needed={},
        active_front_lines=[],
        front_line_stances={},
        vulnerable_front_lines=[],
        aewc_targets=[],
        refueling_targets=[],
        recovery_targets={},
        enemy_air_defenses=[],
        threatening_air_defenses=[],
        detecting_air_defenses=[],
        enemy_convoys=[],
        enemy_shipping=[],
        enemy_ships=[],
        enemy_battle_positions={},
        oca_targets=[],
        strike_targets=[],
        motorpool_targets=[],
        enemy_barcaps=[],
        threat_zones=MagicMock(),
        vulnerable_control_points=[],
        control_point_priority_queue=[],
        priority_cp=None,
        packages_remaining=packages_remaining,
    )


def test_unlimited_by_default() -> None:
    state = _state(None)
    for _ in range(1000):
        state.consume_package()
    assert state.can_plan_package()


def test_limit_is_consumed_and_cloned() -> None:
    state = _state(2)
    state.consume_package()
    clone = state.clone()
    assert clone.packages_remaining == 1
    clone.consume_package()
    assert not clone.can_plan_package()
    # Cloning must not share the counter, or HTN backtracking would leak it.
    assert state.can_plan_package()


def test_package_task_rejected_when_limit_reached() -> None:
    target = MagicMock()
    state = _state(0)
    state.barcaps_needed[target] = 1
    task = PlanBarcap(target, max_orders=1)
    with patch.object(PlanBarcap, "fulfill_mission", return_value=True) as fulfill:
        assert not task.preconditions_met(state)
        # No aircraft may be claimed for a package that will not be planned.
        fulfill.assert_not_called()


def test_package_task_allowed_and_consumes_budget() -> None:
    target = MagicMock()
    state = _state(1)
    state.barcaps_needed[target] = 2
    task = PlanBarcap(target, max_orders=1)
    with patch.object(PlanBarcap, "fulfill_mission", return_value=True):
        assert task.preconditions_met(state)
        task.package = MagicMock(flights=[])
        task.apply_effects(state)
        assert not task.preconditions_met(state)
    assert state.packages_remaining == 0


def test_recovery_tanker_counts_against_limit() -> None:
    target = MagicMock()
    state = _state(1)
    state.recovery_targets[target] = 100
    PlanRecovery(target).apply_effects(state)
    assert state.recovery_targets[target] == 100 - (
        state.context.settings.aircraft_per_recovery_tanker + MARGIN
    )
    assert not state.can_plan_package()
