from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import ceil, floor
from typing import Optional

from dcs.cloud_presets import CLOUD_PRESETS
from dcs.weather import Weather as PydcsWeather, CloudPreset

from pydcs_extensions.cloud_injector import PRECIPITATION_PRESETS


@dataclass(frozen=True)
class Clouds:
    base: int
    density: int
    thickness: int
    precipitation: PydcsWeather.Preceptions
    preset: Optional[CloudPreset] = field(default=None)

    @staticmethod
    def preset_has_precipitation(preset: CloudPreset) -> bool:
        # pydcs' own rainy presets are named "RainyPresetN"; modded ones keep the
        # preset keys DCS expects ("PresetN") and register themselves instead.
        return "Rain" in preset.name or preset.name in PRECIPITATION_PRESETS

    @classmethod
    def random_preset(cls, rain: bool) -> Clouds:
        clouds = (p.value for _, p in CLOUD_PRESETS.items())
        presets = [p for p in clouds if cls.preset_has_precipitation(p) == rain]
        preset = random.choice(presets)
        return Clouds(
            base=random.randint(ceil(preset.min_base), floor(preset.max_base)),
            density=0,
            thickness=0,
            precipitation=PydcsWeather.Preceptions.None_,
            preset=preset,
        )
