from typing import Any
from unittest.mock import MagicMock

from dcs import Point
from dcs.terrain import Terrain

from game.campaignloader.campaignairwingconfig import CampaignAirWingConfig
from game.theater.controlpoint import (
    Carrier,
    ControlPoint,
    ControlPointType,
    Fob,
    Player,
)
from game.theater.invertedstart import InvertedStart


def base(
    name: str,
    x: float,
    owner: Player,
    captured_invert: bool,
    cptype: ControlPointType = ControlPointType.FOB,
) -> ControlPoint:
    cp = Fob(name, Point(x, 0, MagicMock(spec=Terrain)), MagicMock(), owner)
    cp.cptype = cptype
    cp.captured_invert = captured_invert
    return cp


def connect(*chain: ControlPoint) -> None:
    for a, b in zip(chain, chain[1:]):
        a.connected_points.append(b)
        b.connected_points.append(a)


def owners(control_points: list[ControlPoint]) -> dict[str, Player]:
    return {cp.name: cp.starting_coalition for cp in control_points}


def campaign() -> list[ControlPoint]:
    """A player foothold at the front and two rear airfields against a long
    enemy front with two rear airfields of its own, all marked to be captured
    when inverted.
    """
    airbase = ControlPointType.AIRBASE
    foothold = base("foothold", 0, Player.BLUE, False)
    blue_rear_1 = base("blue rear 1", -100_000, Player.BLUE, False, airbase)
    blue_rear_2 = base("blue rear 2", -120_000, Player.BLUE, False, airbase)
    front = [
        base(f"front {i}", i * 10_000, Player.RED, True, airbase) for i in range(1, 5)
    ]
    red_rear_1 = base("red rear 1", 100_000, Player.RED, True, airbase)
    red_rear_2 = base("red rear 2", 120_000, Player.RED, True, airbase)
    connect(foothold, *front)
    return [foothold, blue_rear_1, blue_rear_2, *front, red_rear_1, red_rear_2]


def test_player_takes_enemy_rear_with_normal_number_of_bases() -> None:
    control_points = campaign()
    InvertedStart(control_points).assign_bases()
    assert owners(control_points) == {
        "foothold": Player.RED,
        "blue rear 1": Player.RED,
        "blue rear 2": Player.RED,
        "front 1": Player.RED,
        "front 2": Player.RED,
        "front 3": Player.RED,
        "front 4": Player.BLUE,
        "red rear 1": Player.BLUE,
        "red rear 2": Player.BLUE,
    }


def test_designed_inversion_is_kept() -> None:
    control_points = campaign()
    for cp in control_points[3:]:
        cp.captured_invert = cp.name in ("front 4", "red rear 2")
    inverted = InvertedStart(control_points)
    inverted.assign_bases()
    assert [cp.name for cp in control_points if cp.starting_coalition.is_blue] == [
        "front 4",
        "red rear 2",
    ]

    squadrons: dict[ControlPoint, Any] = {control_points[1]: ["F-16"]}
    air_wing = CampaignAirWingConfig(squadrons)
    assert inverted.move_squadrons(air_wing, control_points) is air_wing


def test_squadrons_follow_their_side() -> None:
    control_points = campaign()
    foothold, blue_rear_1, blue_rear_2 = control_points[:3]
    front_3, front_4, red_rear_1, red_rear_2 = control_points[5:]
    position = Point(0, -50_000, MagicMock(spec=Terrain))
    carrier = Carrier("carrier", position, MagicMock(), Player.BLUE)
    carrier.captured_invert = False
    control_points.append(carrier)
    # Names stand in for the squadron configs, which are only moved around.
    squadrons: dict[ControlPoint, Any] = {
        foothold: ["UH-1H"],
        blue_rear_1: ["F-16"],
        blue_rear_2: ["B-1B"],
        carrier: ["F/A-18C"],
        front_4: ["Mi-24"],
        red_rear_1: ["Su-27"],
        red_rear_2: ["Tu-22"],
    }
    air_wing = CampaignAirWingConfig(squadrons)

    inverted = InvertedStart(control_points)
    inverted.assign_bases()
    by_location: dict[Any, Any] = inverted.move_squadrons(
        air_wing, control_points
    ).by_location

    player_squadrons = sorted(
        s
        for cp, squadrons in by_location.items()
        if cp.starting_coalition.is_blue
        for s in squadrons
    )
    enemy_squadrons = sorted(
        s
        for cp, squadrons in by_location.items()
        if cp.starting_coalition.is_red
        for s in squadrons
    )
    assert player_squadrons == ["B-1B", "F-16", "F/A-18C", "UH-1H"]
    assert enemy_squadrons == ["Mi-24", "Su-27", "Tu-22"]
    # Each set of squadrons gets its own base where there are enough.
    assert by_location[front_4] == ["UH-1H"]
    assert sorted(by_location[red_rear_1] + by_location[red_rear_2]) == [
        "B-1B",
        "F-16",
        "F/A-18C",
    ]
    # The enemy squadrons fall back to the nearest base the enemy holds.
    assert by_location[front_3] == ["Mi-24", "Su-27", "Tu-22"]


def test_player_keeps_an_airfield_for_their_jets() -> None:
    control_points = campaign()
    # The enemy's rear airfields are now FARPs too, so the deepest bases can't
    # take the player's jets.
    for cp in control_points[-2:]:
        cp.cptype = ControlPointType.FOB
    InvertedStart(control_points).assign_bases()
    player_bases = [cp for cp in control_points if cp.starting_coalition.is_blue]
    assert any(cp.cptype is ControlPointType.AIRBASE for cp in player_bases)
