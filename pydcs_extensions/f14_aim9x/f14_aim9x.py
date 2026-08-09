from pydcs_extensions.weapon_injector import inject_weapons


class WeaponsF14AIM9X:
    """AIM-9X wingtip rail added to the Heatblur F-14 by the "AIM-54C+ AND AIM-9X" mod.

    The airframe itself is stock, so pydcs knows the F-14B/F-14BU but not this CLSID.
    Name and weight come from the mod's own declare_loadout: CoreMods/aircraft/F14/
    Entry/Weapons.lua builds it via modern_aim_9_without_adapter("{LAU-138 wtip -
    AIM-9X}", "AIM-9X", "LAU-138 "), and modern_aim9_variants["AIM-9X"] gives
    mass = 84.46.

    Pylon membership is wired up in resources/units/aircraft/F-14B*.yaml via
    weapon_injections, since the pylon classes live in pydcs rather than here.
    """

    LAU_138_AIM_9X = {
        "clsid": "{LAU-138 wtip - AIM-9X}",
        "name": "LAU-138 AIM-9X",
        "weight": 84.46,
    }


inject_weapons(WeaponsF14AIM9X)
