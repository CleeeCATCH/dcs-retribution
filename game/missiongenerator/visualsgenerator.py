from __future__ import annotations

import random
from typing import Any, Optional, TYPE_CHECKING

from dcs.mapping import Point
from dcs.mission import Mission
from dcs.unit import Static
from dcs.unittype import StaticType

if TYPE_CHECKING:
    from game import Game
    from game.theater import FrontLine

from .frontlineconflictdescription import (
    FrontLineBounds,
    FrontLineConflictDescription,
)
from .missiondata import MissionData


class MarkerSmoke(StaticType):
    id = "big_smoke"
    category = "Effects"
    name = "big_smoke"
    shape_name = 5  # type: ignore
    rate = 0.1  # type: ignore


class MediumSmokeAndFire(StaticType):
    id = "big_smoke"
    category = "Effects"
    name = "big_smoke"
    shape_name = 2  # type: ignore
    rate = 1


def __monkey_static_dict(self: Static) -> dict[str, Any]:
    global __original_static_dict

    d = __original_static_dict(self)
    if self.type == "big_smoke":
        d["effectPreset"] = self.shape_name
        d["effectTransparency"] = self.rate
    return d


__original_static_dict = Static.dict
Static.dict = __monkey_static_dict  # type: ignore


# Battle damage smoke. The effect presets of the DCS "big_smoke" static are:
# 1-4 small to huge smoke and fire, 5-8 small to huge smoke only.
class SmallSmokeAndFire(StaticType):
    id = "big_smoke"
    category = "Effects"
    name = "big_smoke"
    shape_name = 1  # type: ignore
    rate = 1


class SmallSmoke(StaticType):
    id = "big_smoke"
    category = "Effects"
    name = "big_smoke"
    shape_name = 5  # type: ignore
    rate = 1


class MediumSmoke(StaticType):
    id = "big_smoke"
    category = "Effects"
    name = "big_smoke"
    shape_name = 6  # type: ignore
    rate = 1


class LargeSmoke(StaticType):
    id = "big_smoke"
    category = "Effects"
    name = "big_smoke"
    shape_name = 7  # type: ignore
    rate = 1


# Most of the damage from earlier fighting smoulders. Open fires are rarer and
# big columns (fuel, a burning village) rarer still.
FRONT_SMOKE_TYPE_WEIGHTS: list[tuple[type[StaticType], int]] = [
    (SmallSmoke, 50),
    (SmallSmokeAndFire, 25),
    (MediumSmoke, 15),
    (MediumSmokeAndFire, 8),
    (LargeSmoke, 2),
]
# Smoke marks where the fighting is, not a fence along the whole front line.
FRONT_SMOKE_DENSITY_FACTOR = 3
FRONT_SMOKE_BATTLE_AREA_SPACING = 10000
# Wrecks pile up in no-man's land, within this distance of the front line.
FRONT_SMOKE_DEPTH_SPREAD = 2000
FRONT_SMOKE_LATERAL_SPREAD = 2500
FRONT_SMOKE_TRANSPARENCY = 0.4, 0.9


class VisualsGenerator:
    def __init__(
        self,
        mission: Mission,
        game: Game,
        mission_data: Optional[MissionData] = None,
    ) -> None:
        self.mission = mission
        self.game = game
        self.mission_data = mission_data

    def _battle_areas(
        self, front_line: FrontLine, bounds: FrontLineBounds
    ) -> list[Point]:
        """The front line sectors when planned, otherwise spots along the front."""
        name = f"{front_line.blue_cp.name}/{front_line.red_cp.name}"
        if self.mission_data is not None:
            for plan in self.mission_data.front_line_director:
                if plan.name == name and plan.sectors:
                    return [
                        bounds.left_position.new_in_same_map(sector.x, sector.y)
                        for sector in plan.sectors
                    ]
        count = max(1, bounds.length // FRONT_SMOKE_BATTLE_AREA_SPACING)
        return [
            bounds.left_position.point_from_heading(
                bounds.heading_from_left_to_right.degrees,
                random.randint(0, bounds.length),
            )
            for _ in range(count)
        ]

    def _generate_frontline_smokes(self) -> None:
        country = list(self.mission.coalition["neutrals"].countries.values())[0]
        types = [t for t, _ in FRONT_SMOKE_TYPE_WEIGHTS]
        weights = [w for _, w in FRONT_SMOKE_TYPE_WEIGHTS]
        for front_line in self.game.theater.conflicts():
            from_cp = front_line.blue_cp
            to_cp = front_line.red_cp
            if from_cp.is_global or to_cp.is_global:
                continue

            bounds = FrontLineConflictDescription.frontline_bounds(
                front_line, self.game.theater
            )
            areas = self._battle_areas(front_line, bounds)
            count = bounds.length // (
                self.game.settings.perf_smoke_spacing * FRONT_SMOKE_DENSITY_FACTOR
            )
            along = bounds.heading_from_left_to_right
            for _ in range(max(len(areas), count)):
                pos = (
                    random.choice(areas)
                    .point_from_heading(
                        along.degrees,
                        random.gauss(0, FRONT_SMOKE_LATERAL_SPREAD / 2),
                    )
                    .point_from_heading(
                        along.right.degrees,
                        random.gauss(0, FRONT_SMOKE_DEPTH_SPREAD / 2),
                    )
                )
                if not self.game.theater.is_on_land(pos):
                    continue

                group = self.mission.static_group(
                    country,
                    "",
                    _type=random.choices(types, weights)[0],
                    position=pos,
                )
                group.units[0].rate = round(
                    random.uniform(*FRONT_SMOKE_TRANSPARENCY), 2
                )

    def generate(self) -> None:
        if self.game.settings.perf_smoke_gen:
            self._generate_frontline_smokes()
