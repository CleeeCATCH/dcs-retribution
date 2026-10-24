"""Ownership of control points at the start of an inverted campaign.

Most campaigns start the player at a disadvantage: a few bases near the front
against a much larger enemy territory. Swapping the sides naively hands the
player that larger territory instead, which removes the challenge the campaign
was built around. Instead, the player takes over the enemy's rear with no more
bases than they would have had in the normal campaign, and the enemy holds
everything else. The squadrons each side would have had in the normal campaign
move with them, so the air war stays as balanced as the campaign intended.
"""

from __future__ import annotations

import logging
import math
from collections import deque
from dataclasses import replace
from typing import Iterable, Optional, TYPE_CHECKING

from game.theater.controlpoint import ControlPointType, OffMapSpawn
from game.theater.player import Player

if TYPE_CHECKING:
    from game.campaignloader.campaignairwingconfig import (
        CampaignAirWingConfig,
        SquadronConfig,
    )
    from game.theater.controlpoint import ControlPoint


#: The kinds of base that can take over the squadrons of each kind of base.
HOSTS = {
    ControlPointType.AIRBASE: {ControlPointType.AIRBASE},
    ControlPointType.AIRCRAFT_CARRIER_GROUP: {
        ControlPointType.AIRCRAFT_CARRIER_GROUP,
        ControlPointType.AIRBASE,
    },
    ControlPointType.LHA_GROUP: {
        ControlPointType.LHA_GROUP,
        ControlPointType.AIRCRAFT_CARRIER_GROUP,
        ControlPointType.AIRBASE,
    },
    ControlPointType.FARP: {ControlPointType.FARP, ControlPointType.AIRBASE},
    ControlPointType.FOB: {ControlPointType.FOB, ControlPointType.AIRBASE},
    ControlPointType.OFF_MAP: {ControlPointType.OFF_MAP, ControlPointType.AIRBASE},
}


def is_territory(cp: ControlPoint) -> bool:
    """Whether the control point is part of the land territory of a side.

    Fleets and off-map spawns move with their side rather than holding ground,
    so they are swapped as is and don't count toward the size of a territory.
    """
    return not cp.is_fleet and not isinstance(cp, OffMapSpawn)


class InvertedStart:
    def __init__(self, control_points: Iterable[ControlPoint]) -> None:
        self.control_points = list(control_points)
        self.original = {cp: cp.starting_coalition for cp in self.control_points}
        self.rebalanced = False

    def assign_bases(self) -> None:
        """Sets the starting coalitions of the control points.

        Bases marked by the campaign designer to be captured on inversion go to
        the player as before. If that leaves the player with more land bases
        than they had in the normal campaign, the extra bases nearest the front
        go back to the enemy, so the player keeps the same disadvantage.

        Bases connected to the ground network (which hold the front lines) and
        isolated rear airfields are limited separately, so the player gets the
        same mix of front-line and rear bases as before.
        """
        for cp in self.control_points:
            if not cp.starting_coalition.is_neutral:
                cp.starting_coalition = (
                    Player.BLUE if cp.captured_invert else Player.RED
                )

        territory = [
            cp
            for cp in self.control_points
            if is_territory(cp) and not self.original[cp].is_neutral
        ]
        player_bases = [cp for cp in territory if cp.starting_coalition.is_blue]
        original_player_bases = [cp for cp in territory if self.original[cp].is_blue]
        if len(player_bases) <= len(original_player_bases):
            # The campaign already gives the player no more ground than before.
            return
        self.rebalanced = True

        enemy_bases = [cp for cp in territory if not cp.starting_coalition.is_blue]
        depth = _depth_behind_front(player_bases, enemy_bases)

        networked = [cp for cp in player_bases if not cp.is_isolated]
        isolated = [cp for cp in player_bases if cp.is_isolated]
        networked_limit = sum(1 for cp in original_player_bases if not cp.is_isolated)
        isolated_limit = len(original_player_bases) - networked_limit
        # If the enemy's side has too few bases of one kind, make up the numbers
        # with the other kind.
        networked_limit, isolated_limit = (
            networked_limit + max(0, isolated_limit - len(isolated)),
            isolated_limit + max(0, networked_limit - len(networked)),
        )
        if networked_limit + isolated_limit == 0 and not any(
            cp.starting_coalition.is_blue and not is_territory(cp)
            for cp in self.control_points
        ):
            # The normal campaign starts the player at sea, but there is no
            # fleet for them when inverted, so they need somewhere to start.
            if networked:
                networked_limit = 1
            else:
                isolated_limit = 1

        keep = _grow_from_rear(networked, networked_limit, depth)
        isolated.sort(key=depth.__getitem__, reverse=True)
        keep.update(isolated[:isolated_limit])

        # Make sure the player has somewhere for the squadrons they would have
        # had in the normal campaign to operate from, such as an airfield for
        # their jets when the deepest bases are all FARPs.
        for cptype in sorted({cp.cptype for cp in original_player_bases}, key=str):
            if not any(cp.cptype in HOSTS[cptype] for cp in keep):
                hosts = [cp for cp in player_bases if cp.cptype in HOSTS[cptype]]
                if hosts:
                    keep.add(max(hosts, key=depth.__getitem__))

        for cp in player_bases:
            if cp not in keep:
                cp.starting_coalition = Player.RED

    def move_squadrons(
        self, air_wing: CampaignAirWingConfig, control_points: Iterable[ControlPoint]
    ) -> CampaignAirWingConfig:
        """Gives each side the squadrons it would have in the normal campaign.

        Only needed once the bases have been rebalanced. Without that the
        player takes over the enemy's whole territory and with it the enemy's
        squadrons, as the campaign designer intended.

        The squadrons at the bases the player normally starts with go to the
        player's new bases, and the squadrons at the enemy bases the player now
        holds fall back to the nearest base the enemy still holds.
        """
        if not self.rebalanced:
            return air_wing

        by_location: dict[ControlPoint, list[SquadronConfig]] = {
            cp: list(squadrons) for cp, squadrons in air_wing.by_location.items()
        }
        control_points = [
            cp for cp in control_points if not self.original[cp].is_neutral
        ]
        player_bases = [cp for cp in control_points if cp.starting_coalition.is_blue]
        enemy_bases = [cp for cp in control_points if cp.starting_coalition.is_red]

        moves: list[tuple[ControlPoint, Optional[ControlPoint]]] = []
        for cp in player_bases:
            if self.original[cp].is_red:
                moves.append((cp, _nearest_host(cp, enemy_bases)))
        used: set[ControlPoint] = set()
        rear = {
            cp: min(
                (cp.position.distance_to_point(e.position) for e in enemy_bases),
                default=0.0,
            )
            for cp in player_bases
        }
        for cp in enemy_bases:
            if self.original[cp].is_blue:
                hosts = [h for h in player_bases if _can_host(h, cp)]
                # Spread the squadrons out like they normally are, keeping them
                # at the same kind of base where possible, and otherwise as far
                # from the enemy as they can be.
                hosts.sort(
                    key=lambda h: (
                        h.cptype != cp.cptype,
                        h.is_isolated != cp.is_isolated,
                        h in used,
                        -rear[h],
                    )
                )
                host = hosts[0] if hosts else None
                if host is not None:
                    used.add(host)
                moves.append((cp, host))

        moved = {cp: by_location.pop(cp, []) for cp, _ in moves}
        for cp, host in moves:
            if host is None:
                if moved[cp]:
                    logging.warning(
                        f"No base can take over the squadrons at {cp} in the "
                        "inverted campaign"
                    )
                host = cp
            by_location.setdefault(host, []).extend(moved[cp])
        return replace(air_wing, by_location=by_location)


def _can_host(host: ControlPoint, origin: ControlPoint) -> bool:
    """Whether the squadrons based at origin can operate from host."""
    return host.cptype in HOSTS[origin.cptype]


def _nearest_host(
    origin: ControlPoint, bases: list[ControlPoint]
) -> Optional[ControlPoint]:
    hosts = [cp for cp in bases if _can_host(cp, origin)]
    # Prefer the same kind of base, then the nearest.
    return min(
        hosts,
        key=lambda cp: (
            cp.cptype != origin.cptype,
            cp.position.distance_to_point(origin.position),
        ),
        default=None,
    )


def _depth_behind_front(
    player_bases: list[ControlPoint], enemy_bases: list[ControlPoint]
) -> dict[ControlPoint, tuple[float, float]]:
    """How far behind the front each of the player's bases is.

    Depth is the number of ground network hops to the nearest enemy base, then
    the straight line distance to the nearest enemy base to break ties. Bases
    not linked to the enemy over the ground network are deepest of all.
    """
    hops: dict[ControlPoint, float] = {cp: 0 for cp in enemy_bases}
    queue = deque(enemy_bases)
    while queue:
        cp = queue.popleft()
        for neighbor in cp.connected_points:
            if neighbor not in hops:
                hops[neighbor] = hops[cp] + 1
                queue.append(neighbor)

    depth = {}
    for cp in player_bases:
        distance = min(
            (cp.position.distance_to_point(e.position) for e in enemy_bases),
            default=0.0,
        )
        depth[cp] = (hops.get(cp, math.inf), distance)
    return depth


def _grow_from_rear(
    bases: list[ControlPoint],
    limit: int,
    depth: dict[ControlPoint, tuple[float, float]],
) -> set[ControlPoint]:
    """Picks the deepest bases, kept connected to each other where possible."""
    remaining = list(bases)
    keep: set[ControlPoint] = set()
    while remaining and len(keep) < limit:
        adjacent = [
            cp for cp in remaining if any(n in keep for n in cp.connected_points)
        ]
        best = max(adjacent or remaining, key=depth.__getitem__)
        keep.add(best)
        remaining.remove(best)
    return keep
