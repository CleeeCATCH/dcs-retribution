from __future__ import annotations

from collections import Counter
from types import SimpleNamespace
from typing import Any, cast

import pytest
from dcs import Mission
from dcs.coalition import Coalition
from dcs.countries import Switzerland
from dcs.mapping import Point

from game import Game
from game.missiongenerator.frontlineconflictdescription import (
    FrontLineBounds,
    FrontLineConflictDescription,
)
from game.missiongenerator.missiondata import (
    FrontLineDirectorInfo,
    FrontLineSectorInfo,
    FrontLineSideInfo,
    MissionData,
)
from game.missiongenerator.visualsgenerator import VisualsGenerator

FRONT_LENGTH = 80000


def _smokes(mission: Mission) -> list[Any]:
    return [
        unit
        for country in mission.coalition["neutrals"].countries.values()
        for group in country.static_group
        for unit in group.units
        if unit.type == "big_smoke"
    ]


@pytest.fixture
def setup(monkeypatch: pytest.MonkeyPatch) -> tuple[Mission, Game]:
    mission = Mission()
    mission.coalition["neutrals"] = Coalition("neutrals")
    mission.coalition["neutrals"].add_country(Switzerland())
    left = Point(0, 0, mission.terrain)
    right = Point(0, FRONT_LENGTH, mission.terrain)
    monkeypatch.setattr(
        FrontLineConflictDescription,
        "frontline_bounds",
        classmethod(lambda cls, front_line, theater: FrontLineBounds(left, right)),
    )
    front_line = SimpleNamespace(
        blue_cp=SimpleNamespace(name="A", is_global=False),
        red_cp=SimpleNamespace(name="B", is_global=False),
    )
    game = SimpleNamespace(
        settings=SimpleNamespace(perf_smoke_gen=True, perf_smoke_spacing=1600),
        theater=SimpleNamespace(
            conflicts=lambda: [front_line], is_on_land=lambda point: True
        ),
    )
    return mission, cast(Game, game)


def _director_plan(sector_offsets: list[int]) -> MissionData:
    side = FrontLineSideInfo("DEFENSIVE", None, 90, 0.0, 0.0)
    data = MissionData()
    data.front_line_director.append(
        FrontLineDirectorInfo(
            name="A/B",
            sectors=[FrontLineSectorInfo(0.0, y, 6000) for y in sector_offsets],
            blue=side,
            red=side,
            groups=[],
        )
    )
    return data


def test_smoke_is_concentrated_not_a_fence(setup: tuple[Mission, Game]) -> None:
    mission, game = setup
    VisualsGenerator(mission, game).generate()
    smokes = _smokes(mission)
    # The old generator put one plume every spacing step along the front.
    assert 0 < len(smokes) <= FRONT_LENGTH // 1600 // 3


def test_smoke_clusters_at_the_sectors(setup: tuple[Mission, Game]) -> None:
    mission, game = setup
    sectors = [20000, 60000]
    VisualsGenerator(mission, game, _director_plan(sectors)).generate()
    for smoke in _smokes(mission):
        nearest = min(abs(smoke.position.y - y) for y in sectors)
        # Lateral spread is gaussian with sigma 1250 m: well inside 4 sigma.
        assert nearest < 5000
        # Wrecks lie in no-man's land, close to the front line.
        assert abs(smoke.position.x) < 5000


def test_smoke_mostly_smoulders(setup: tuple[Mission, Game]) -> None:
    mission, game = setup
    # A tiny spacing gives a large sample of plumes.
    game.settings.perf_smoke_spacing = 20
    VisualsGenerator(mission, game).generate()
    presets = Counter(smoke.shape_name for smoke in _smokes(mission))
    total = sum(presets.values())
    assert total > 1000
    smoke_only = presets[5] + presets[6] + presets[7]
    assert smoke_only / total > 0.55
    # Never the large and huge fire presets of the old generator.
    assert presets[3] == 0 and presets[4] == 0
    for smoke in _smokes(mission):
        assert 0.4 <= smoke.rate <= 0.9


def test_no_smoke_when_disabled(setup: tuple[Mission, Game]) -> None:
    mission, game = setup
    game.settings.perf_smoke_gen = False
    VisualsGenerator(mission, game).generate()
    assert _smokes(mission) == []
