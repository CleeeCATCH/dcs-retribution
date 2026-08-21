"""ATMOS X cloud presets, and the save-compat path from Bandit's clouds."""

from typing import Iterator

import pytest
from dcs.cloud_presets import CLOUD_PRESETS
from dcs.weather import CloudPreset

from game.settings.settings import Settings
from game.weather.clouds import Clouds
from pydcs_extensions.atmos_x.atmos_x import (
    ATMOS_X_CLOUDS,
    ATMOS_X_PRECIPITATION_PRESETS,
    AtmosXClouds,
)
from pydcs_extensions.cloud_injector import PRECIPITATION_PRESETS


@pytest.fixture
def atmos_x_enabled() -> Iterator[None]:
    AtmosXClouds.activate()
    yield
    AtmosXClouds.deactivate()


def _random_preset(rain: bool) -> CloudPreset:
    clouds = Clouds.random_preset(rain=rain)
    assert clouds.preset is not None
    # Raises if the generated base is outside the preset's declared range.
    clouds.preset.validate_base(clouds.base)
    return clouds.preset


def test_presets_are_keyed_by_their_dcs_name() -> None:
    # The key is what gets written to the .miz, so it has to match the preset
    # name in the mod's clouds.lua.
    for name, preset in ATMOS_X_CLOUDS.items():
        assert preset.value.name == name


def test_ui_names_are_unique() -> None:
    # The preset combo box in the weather editor selects by display name.
    ui_names = [preset.value.ui_name for preset in ATMOS_X_CLOUDS.values()]
    assert len(set(ui_names)) == len(ui_names)


def test_activate_and_deactivate_are_symmetric() -> None:
    before = dict(CLOUD_PRESETS)
    AtmosXClouds.activate()
    assert set(CLOUD_PRESETS) - set(before) == set(ATMOS_X_CLOUDS)
    assert ATMOS_X_PRECIPITATION_PRESETS <= PRECIPITATION_PRESETS
    AtmosXClouds.deactivate()
    assert CLOUD_PRESETS == before
    assert not ATMOS_X_PRECIPITATION_PRESETS & PRECIPITATION_PRESETS


def test_raining_weather_draws_only_rainy_presets(atmos_x_enabled: None) -> None:
    drawn = {_random_preset(rain=True).name for _ in range(500)}
    assert drawn & ATMOS_X_PRECIPITATION_PRESETS
    assert all(Clouds.preset_has_precipitation(CLOUD_PRESETS[n].value) for n in drawn)


def test_cloudy_weather_never_draws_rainy_presets(atmos_x_enabled: None) -> None:
    drawn = {_random_preset(rain=False).name for _ in range(500)}
    assert drawn
    assert not drawn & ATMOS_X_PRECIPITATION_PRESETS


def test_bandit_clouds_setting_is_migrated() -> None:
    state = Settings.deserialize_state_dict({"use_bandit_clouds": True})
    assert state["use_atmos_x_clouds"] is True
    assert "use_bandit_clouds" not in state


def test_disabled_bandit_clouds_setting_is_migrated() -> None:
    state = Settings.deserialize_state_dict({"use_bandit_clouds": False})
    assert state["use_atmos_x_clouds"] is False
