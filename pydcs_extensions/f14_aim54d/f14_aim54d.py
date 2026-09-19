from pydcs_extensions.weapon_injector import inject_weapons


class WeaponsF14AIM54D:
    """AIM-54D Phoenix ER added to the Heatblur F-14 by the "AIM-54D" mod.

    The airframe is stock, so pydcs knows the F-14B and F-14BU but not these
    CLSIDs. The mod declares them in CoreMods/aircraft/F14/Entry/Weapons.lua: a
    bare {AIM_54D_Mk47} for the tunnel pallet stations, and
    {SHOULDER AIM_54D_Mk47 L/R} for the shoulder stations, which add 45.36 kg for
    the Phoenix adapter with LAU-93B/A on top of the missile.

    Launch mass is 694.0 kg: 291.0 kg C airframe + 163.0 kg Mk47 Mod 1 sustainer
    propellant + 240.0 kg boost motor (160.0 propellant + 80.0 inert), which is
    what make_aim_54_boosted sums into weapon.M and what the loadout's Weight
    field reports. The booster is jettisoned after its 4 s burn.

    Pylon membership is wired up in resources/units/aircraft/F-14B.yaml and
    F-14BU.yaml via weapon_injections, since the pylon classes live in pydcs
    rather than here. The mod gates the stations with b_and_bu_only, so the
    F-14B and F-14B(U) both get them and the F-14A files are untouched.
    """

    AIM_54D_Phoenix_ER = {
        "clsid": "{AIM_54D_Mk47}",
        "name": "AIM-54D Phoenix ER",
        "weight": 694.0,
    }

    AIM_54D_Phoenix_ER_SHOULDER_L = {
        "clsid": "{SHOULDER AIM_54D_Mk47 L}",
        "name": "AIM-54D Phoenix ER",
        "weight": 739.36,
    }

    AIM_54D_Phoenix_ER_SHOULDER_R = {
        "clsid": "{SHOULDER AIM_54D_Mk47 R}",
        "name": "AIM-54D Phoenix ER",
        "weight": 739.36,
    }


inject_weapons(WeaponsF14AIM54D)
