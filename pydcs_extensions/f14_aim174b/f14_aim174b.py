from pydcs_extensions.weapon_injector import inject_weapons


class WeaponsF14AIM174B:
    """AIM-174B Gunslinger added to the Heatblur F-14 by the "F-14 AIM-174B" mod.

    The airframe is stock, so pydcs knows the F-14BU but not these CLSIDs. The mod
    declares them in CoreMods/aircraft/F14/Entry/Weapons.lua: a bare {AIM_174B} for
    the tunnel pallet stations, and {SHOULDER AIM_174B L/R} for the shoulder
    stations, which add 45.36 kg for the LAU-93 adapter on top of the 860 kg
    missile.

    The missile shape and textures come from the separate "Definitive AMRAAM"
    (AIM-120D-3 and AIM-174B) mod, which must also be enabled.

    Pylon membership is wired up in resources/units/aircraft/F-14BU.yaml via
    weapon_injections, since the pylon classes live in pydcs rather than here.
    Only the F-14B(U) gets them -- the stock F-14B/F-14A yaml files are untouched.
    """

    AIM_174B = {
        "clsid": "{AIM_174B}",
        "name": "AIM-174B Gunslinger",
        "weight": 860.0,
    }

    AIM_174B_SHOULDER_L = {
        "clsid": "{SHOULDER AIM_174B L}",
        "name": "AIM-174B Gunslinger",
        "weight": 905.36,
    }

    AIM_174B_SHOULDER_R = {
        "clsid": "{SHOULDER AIM_174B R}",
        "name": "AIM-174B Gunslinger",
        "weight": 905.36,
    }


inject_weapons(WeaponsF14AIM174B)
