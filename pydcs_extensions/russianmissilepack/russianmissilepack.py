from pydcs_extensions.weapon_injector import inject_weapons


class WeaponsRussianMissilePack:
    """Weapons from the "Russian Missile Pack" tech mod.

    These share their real-world designations with the R-77/R-37 variants carried by
    the Su-30 and Su-35 mods, but the pack declares its own CLSIDs, so they need their
    own entries here. Names and weights are taken from the pack's
    Database/weapons.lua declare_loadout blocks (dual racks include the 160kg
    pylon_dual_mass).
    """

    R_77__AA_12_Adder_Early____Active_Rdr = {
        "clsid": "{Mk_R77}",
        "name": "R-77 (AA-12 Adder Early) - Active Rdr",
        "weight": 175,
    }
    R_77_1__AA_12_Adder_B____Active_Rdr = {
        "clsid": "{Mk_R771}",
        "name": "R-77-1 (AA-12 Adder B) - Active Rdr",
        "weight": 190,
    }
    R_77_1__AA_12_Adder_B__x_2 = {
        "clsid": "{DUAL_Mk_771}",
        "name": "R-77-1 (AA-12 Adder B) x 2",
        "weight": 540,
    }
    R_77M__AA_12_Adder_C____Active_Rdr = {
        "clsid": "{Mk_R77M}",
        "name": "R-77M (AA-12 Adder C) - Active Rdr",
        "weight": 190,
    }
    R_77M__AA_12_Adder_C____Active_Rdr_x_2 = {
        "clsid": "{DUAL_Mk_R77M}",
        "name": "R-77M (AA-12 Adder C) - Active Rdr x 2",
        "weight": 540,
    }
    R_37M__AA_13_Axehead____Active_Rdr = {
        "clsid": "{Mk_R37M}",
        "name": "R-37M (AA-13 Axehead) - Active Rdr",
        "weight": 600,
    }


inject_weapons(WeaponsRussianMissilePack)
