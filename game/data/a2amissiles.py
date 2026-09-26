"""Campaign-wide preferences for the air-to-air missiles aircraft carry.

Default loadouts pin specific missiles to each aircraft (the F-16's BARCAP loadout
carries AIM-120Cs, for example). The preferences here let the player rank missiles of
each guidance type for their side and the enemy's. When a flight's loadout is
generated, each pylon that carries one of the ranked missiles is re-armed with the
highest ranked missile that the pylon can carry. Loadouts keep their layout (tanks,
pods, bombs and the number of missiles per pylon), only the missiles change.
"""

from __future__ import annotations

import datetime
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import cache
from typing import Optional, TYPE_CHECKING

from game.data.weapons import Pylon, Weapon, WeaponGroup, WeaponType

if TYPE_CHECKING:
    from game.factions.faction import Faction
    from game.settings import Settings

A2A_MISSILE_TYPES = (WeaponType.AAM_RADAR, WeaponType.AAM_IR)

A2A_MISSILE_TYPE_NAMES = {
    WeaponType.AAM_RADAR: "Radar guided",
    WeaponType.AAM_IR: "Infrared guided",
}

# Weapon groups for multi-rail launchers are named "2xAIM-9M" or "R-60 x 2".
_MULTI_RAIL_PREFIX = re.compile(r"^\d+x\s*")
_MULTI_RAIL_SUFFIX = re.compile(r"\s+x\s*\d+$")

# Missile counts in weapon names, e.g. "2x AIM-120C" or "LAU-115 with 2 x LAU-127". Numbers that are part of a designation ("R-60 x 2") are skipped.
_MISSILE_COUNT = re.compile(r"(?<![\w-])(\d+)\s*x(?=[\s/]|$)", re.IGNORECASE)

# Variants of a store that must not be traded for one another: losing an IRST pod or
# loading cargo instead of a missile would change what the loadout does.
_STORE_MARKERS = ("irst", "ammo")

# Variants that only work for the AI or with extra mods. Avoided unless the original
# store was one as well.
_RESTRICTED_MARKERS = ("ai only", "mod required")


@dataclass(frozen=True)
class MissileFamily:
    """A missile together with all of its launchers (single and multi-rail)."""

    name: str
    type: WeaponType
    groups: tuple[WeaponGroup, ...]

    @property
    def introduction_year(self) -> Optional[int]:
        years = [g.introduction_year for g in self.groups if g.introduction_year]
        return min(years, default=None)

    @property
    def weapons(self) -> Iterator[Weapon]:
        for group in self.groups:
            yield from group.weapons

    @property
    def display_name(self) -> str:
        if self.introduction_year is None:
            return self.name
        return f"{self.name} ({self.introduction_year})"


def family_name_for(group: WeaponGroup) -> str:
    name = _MULTI_RAIL_PREFIX.sub("", group.name.strip())
    return _MULTI_RAIL_SUFFIX.sub("", name)


@cache
def _families() -> dict[str, MissileFamily]:
    grouped: dict[str, list[WeaponGroup]] = {}
    types: dict[str, WeaponType] = {}
    for group in WeaponGroup.iter_all():
        if group.type not in A2A_MISSILE_TYPES:
            continue
        name = family_name_for(group)
        grouped.setdefault(name, []).append(group)
        types[name] = group.type
    return {
        name: MissileFamily(name, types[name], tuple(groups))
        for name, groups in sorted(grouped.items(), key=lambda i: i[0].lower())
    }


def missile_families(weapon_type: WeaponType) -> list[MissileFamily]:
    return [f for f in _families().values() if f.type is weapon_type]


def missile_family_named(name: str) -> Optional[MissileFamily]:
    return _families().get(name)


def missile_family_for(weapon: Weapon) -> Optional[MissileFamily]:
    if weapon.weapon_group.type not in A2A_MISSILE_TYPES:
        return None
    return missile_family_named(family_name_for(weapon.weapon_group))


def preferred_missiles(
    settings: Settings, player: bool
) -> dict[WeaponType, Sequence[str]]:
    """The ranked missile family names for one side, keyed by guidance type."""
    if player:
        return {
            WeaponType.AAM_RADAR: settings.player_preferred_radar_missiles,
            WeaponType.AAM_IR: settings.player_preferred_ir_missiles,
        }
    return {
        WeaponType.AAM_RADAR: settings.enemy_preferred_radar_missiles,
        WeaponType.AAM_IR: settings.enemy_preferred_ir_missiles,
    }


def missile_count(weapon: Weapon) -> int:
    # Racks are often named after both the rails and the missiles ("LAU-115: 2 x
    # LAU-127 - 2 x AIM-120C"), so the largest count is the closest guess. It is only
    # used to compare launchers against each other, so it need not be exact.
    return max((int(c) for c in _MISSILE_COUNT.findall(weapon.name)), default=1)


def _markers(weapon: Weapon, markers: Sequence[str]) -> tuple[bool, ...]:
    name = weapon.name.lower()
    return tuple(m in name for m in markers)


def replacement_for(
    weapon: Weapon,
    pylon: Pylon,
    preferences: Sequence[str],
    date: Optional[datetime.date],
    faction: Optional[Faction],
) -> Optional[Weapon]:
    """Returns the preferred missile to load on the pylon instead of weapon.

    Only missiles that are part of the ranking are replaced, and only by a missile
    ranked above them. Missiles that are not ranked are left alone so that, for
    example, ranking AIM-7s does not take the Phoenixes off an F-14.

    Returns None when the weapon should be kept: it is not a ranked air-to-air missile,
    it is already the best ranked missile the pylon can carry, or no better ranked
    missile fits.
    """
    current = missile_family_for(weapon)
    if current is None or current.name not in preferences:
        return None

    for name in preferences:
        if name == current.name:
            return None
        family = missile_family_named(name)
        if family is None or family.type is not current.type:
            continue
        candidates = [
            c
            for c in family.weapons
            if pylon.can_equip(c)
            and _markers(c, _STORE_MARKERS) == _markers(weapon, _STORE_MARKERS)
            and (date is None or faction is None or c.available_on(date, faction))
        ]
        if candidates:
            return max(candidates, key=lambda c: _similarity(weapon, c))
    return None


def _similarity(original: Weapon, candidate: Weapon) -> tuple[bool, bool, float]:
    return (
        missile_count(candidate) == missile_count(original),
        _markers(candidate, _RESTRICTED_MARKERS)
        == _markers(original, _RESTRICTED_MARKERS),
        # Prefer the launcher that looks most like the original one, e.g. keep a
        # LAU-127 when replacing a missile that was on a LAU-127.
        SequenceMatcher(None, original.clsid, candidate.clsid).ratio(),
    )
