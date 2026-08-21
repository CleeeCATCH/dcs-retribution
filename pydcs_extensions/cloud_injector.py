from typing import Any, Iterable, Mapping, Optional, Set

from dcs.cloud_presets import CLOUD_PRESETS

#: Names of injected presets that carry precipitation. pydcs' own rainy presets
#: are recognizable by their name ("RainyPresetN"), but modded presets keep the
#: preset keys DCS expects ("PresetN"), so mods register their rainy ones here
#: for the weather generator to find. See game.weather.clouds.
PRECIPITATION_PRESETS: Set[str] = set()


def inject_cloud_presets(
    presets: Mapping[str, Any], precipitation: Optional[Iterable[str]] = None
) -> None:
    """
    Inject custom cloud presets from mods into pydcs' cloud presets databases via introspection
    :param presets: The custom presets to be injected into pydcs' cloud presets
        database, keyed by the preset name DCS uses. The values are members of
        the mod's own preset enum, which pydcs' database is not aware of.
    :param precipitation: The subset of those presets which rain
    :return: None
    """
    CLOUD_PRESETS.update(presets)
    if precipitation is not None:
        PRECIPITATION_PRESETS.update(precipitation)


def eject_cloud_presets(
    presets: Mapping[str, Any], precipitation: Optional[Iterable[str]] = None
) -> None:
    for preset in presets:
        if preset in CLOUD_PRESETS:
            del CLOUD_PRESETS[preset]
    if precipitation is not None:
        PRECIPITATION_PRESETS.difference_update(precipitation)
