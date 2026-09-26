import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml
from dcs.planes import F_14B, F_15C, FA_18C_hornet, MiG_21Bis

from game.ato.loadouts import Loadout
from game.data.a2amissiles import (
    missile_count,
    missile_family_for,
    missile_family_named,
    preferred_missiles,
)
from game.data.weapons import Weapon, WeaponType
from game.settings import Settings

AIM_120C = "{40EF17B7-F508-45de-8566-6FFECC0C1AB8}"
AIM_120C_2X = "LAU-115_2*LAU-127_AIM-120C"
AIM_9X = "{5CE2FF2A-645A-4197-B48D-8720AC69394F}"
AIM_54C = "{AIM_54C_Mk60}"
AIM_7MH_SHOULDER = "{SHOULDER AIM-7MH}"
R_60M_2X = "{R-60M 2L}"
FUEL_TANK = "{FPU_8A_FUEL_TANK}"


def _weapon(clsid: str) -> Weapon:
    weapon = Weapon.with_clsid(clsid)
    assert weapon is not None
    return weapon


def _aircraft(dcs_type: Any) -> Any:
    return SimpleNamespace(dcs_unit_type=dcs_type)


def _prefs(
    radar: list[str] | None = None, ir: list[str] | None = None
) -> dict[WeaponType, list[str]]:
    return {WeaponType.AAM_RADAR: radar or [], WeaponType.AAM_IR: ir or []}


def test_every_a2a_missile_has_a_guidance_type() -> None:
    for path in Path("resources/weapons/a2a-missiles").glob("*.yaml"):
        with path.open(encoding="utf8") as f:
            data = yaml.safe_load(f)
        assert data.get("type") in ("AAM_RADAR", "AAM_IR"), path


def test_multi_rail_launchers_belong_to_the_missile_family() -> None:
    family = missile_family_named("AIM-120C")
    assert family is not None
    assert family.type is WeaponType.AAM_RADAR
    assert {g.name for g in family.groups} == {"AIM-120C", "2xAIM-120C"}
    assert missile_family_for(_weapon(AIM_120C_2X)) == family
    r60 = missile_family_for(_weapon(R_60M_2X))
    assert r60 is not None and r60.name == "R-60M"
    assert missile_family_for(_weapon(FUEL_TANK)) is None


def test_missile_count() -> None:
    assert missile_count(_weapon(AIM_120C)) == 1
    assert missile_count(_weapon(AIM_120C_2X)) == 2
    assert missile_count(_weapon(R_60M_2X)) == 2


def test_ranked_missile_replaces_lower_ranked_missile() -> None:
    loadout = Loadout(
        "BARCAP",
        {1: _weapon(AIM_9X), 2: _weapon(AIM_120C_2X), 3: _weapon(FUEL_TANK)},
        date=None,
    )
    new = loadout.with_preferred_a2a_missiles(
        _aircraft(FA_18C_hornet),
        _prefs(radar=["AIM-120B", "AIM-120C"], ir=["AIM-9M", "AIM-9X"]),
    )

    assert new.pylons[1].weapon_group.name == "AIM-9M"  # type: ignore[union-attr]
    # The double rack stays a double rack.
    assert new.pylons[2].weapon_group.name == "2xAIM-120B"  # type: ignore[union-attr]
    assert missile_count(new.pylons[2]) == 2  # type: ignore[arg-type]
    assert new.pylons[3] == _weapon(FUEL_TANK)
    # The original loadout is not modified.
    assert loadout.pylons[2] == _weapon(AIM_120C_2X)


def test_missile_ranked_above_the_best_fit_is_skipped() -> None:
    # The F-15C cannot carry the Meteor, so the AIM-120C it already has is kept.
    loadout = Loadout("CAP", {3: _weapon(AIM_120C)}, date=None)
    new = loadout.with_preferred_a2a_missiles(
        _aircraft(F_15C), _prefs(radar=["Meteor", "AIM-120C", "AIM-120B"])
    )
    assert new.pylons[3] == _weapon(AIM_120C)


def test_unranked_missiles_are_never_replaced() -> None:
    # The F-14's Phoenix stations can carry AIM-7s. Ranking AIM-7s must not take the
    # Phoenixes away.
    loadout = Loadout(
        "CAP", {2: _weapon(AIM_7MH_SHOULDER), 4: _weapon(AIM_54C)}, date=None
    )
    new = loadout.with_preferred_a2a_missiles(
        _aircraft(F_14B), _prefs(radar=["AIM-7P", "AIM-7MH"])
    )
    assert new.pylons[4] == _weapon(AIM_54C)


def test_custom_loadouts_are_not_changed() -> None:
    loadout = Loadout("Custom", {2: _weapon(AIM_120C_2X)}, date=None, is_custom=True)
    new = loadout.with_preferred_a2a_missiles(
        _aircraft(FA_18C_hornet), _prefs(radar=["AIM-120B", "AIM-120C"])
    )
    assert new.pylons[2] == _weapon(AIM_120C_2X)


def test_missiles_not_in_service_are_skipped() -> None:
    faction = SimpleNamespace(weapons_introduction_year_overrides={})
    loadout = Loadout("CAP", {1: _weapon(R_60M_2X)}, date=None)
    prefs = _prefs(ir=["R-73 (AA-11 Archer) - Infra Red", "R-60", "R-60M"])

    # The R-73 does not fit the MiG-21, so the R-60 is the best fit.
    new = loadout.with_preferred_a2a_missiles(_aircraft(MiG_21Bis), prefs)
    assert new.pylons[1].weapon_group.name == "R-60 x 2"  # type: ignore[union-attr]

    # Ranking only a missile that is not in service yet keeps the original.
    newer_first = _prefs(ir=["R-60M", "R-60"])
    r60m_year = missile_family_named("R-60M").introduction_year  # type: ignore[union-attr]
    assert r60m_year is not None
    older = Loadout("CAP", {1: _weapon("{R-60 2L}")}, date=None)
    new = older.with_preferred_a2a_missiles(
        _aircraft(MiG_21Bis),
        newer_first,
        date(r60m_year - 1, 1, 1),
        faction,  # type: ignore[arg-type]
    )
    assert new.pylons[1] == _weapon("{R-60 2L}")
    new = older.with_preferred_a2a_missiles(
        _aircraft(MiG_21Bis),
        newer_first,
        date(r60m_year, 1, 1),
        faction,  # type: ignore[arg-type]
    )
    assert new.pylons[1].weapon_group.name == "R-60M x 2"  # type: ignore[union-attr]


def test_preferences_are_per_coalition() -> None:
    settings = Settings()
    settings.player_preferred_radar_missiles = ["AIM-120C"]
    settings.enemy_preferred_ir_missiles = ["R-73 (AA-11 Archer) - Infra Red"]
    assert preferred_missiles(settings, player=True) == _prefs(radar=["AIM-120C"])
    assert preferred_missiles(settings, player=False) == _prefs(
        ir=["R-73 (AA-11 Archer) - Infra Red"]
    )


def test_preferences_survive_settings_save_and_load() -> None:
    settings = Settings()
    settings.player_preferred_radar_missiles = ["AIM-120C", "AIM-120B"]
    data = json.loads(
        json.dumps(settings.__dict__, default=settings.default_json),
        object_hook=settings.obj_hook,
    )
    loaded = Settings()
    loaded.__setstate__(data)
    assert loaded.player_preferred_radar_missiles == ["AIM-120C", "AIM-120B"]


def test_old_settings_default_to_no_preferences() -> None:
    state = Settings().__dict__.copy()
    for key in (
        "player_preferred_radar_missiles",
        "player_preferred_ir_missiles",
        "enemy_preferred_radar_missiles",
        "enemy_preferred_ir_missiles",
    ):
        del state[key]
    loaded = Settings()
    loaded.__setstate__(state)
    assert loaded.player_preferred_radar_missiles == []
    assert loaded.enemy_preferred_ir_missiles == []
