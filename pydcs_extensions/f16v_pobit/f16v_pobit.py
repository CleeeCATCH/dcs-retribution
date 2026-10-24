from typing import Any, Dict, Optional, Type

from dcs.planes import F_16C_50

from pydcs_extensions.pylon_injector import inject_pylon, eject_pylon
from pydcs_extensions.weapon_injector import inject_weapons


class WeaponsF16V:
    """Stores added to the stock F-16C_50 by the "F-16V" mod by Pobit.

    The mod installs into the core game (CoreMods/aircraft/F-16C bl.50 AI) and
    patches the stock F-16C_50 rather than adding a new airframe, so pydcs knows
    the aircraft but not these CLSIDs. They are declared in the mod's
    F16V_Weapons folder (GBU39.lua, GBU53.lua, SDB_Loadout.lua, CFT_Loadouts.lua,
    AUX_Loadouts.lua and AAQ13_Loadouts.lua) and wired to the pylons by
    F16V_Weapons/loadouts.lua.

    The mod gives its SDBs a mass of 130 kg and the BRU-61/A rack 145 kg. The CFT
    pair is 408.2 kg dry plus 3060 lb of fuel.
    """

    BRU_61_A_with_1_x_GBU_39_B_SDB = {
        "clsid": "{F16V_BRU61_1*GBU39}",
        "name": "BRU-61/A with 1 x GBU-39/B SDB",
        "weight": 275,
    }
    BRU_61_A_with_2_x_GBU_39_B_SDB = {
        "clsid": "{F16V_BRU61_2*GBU39}",
        "name": "BRU-61/A with 2 x GBU-39/B SDB",
        "weight": 405,
    }
    BRU_61_A_with_3_x_GBU_39_B_SDB = {
        "clsid": "{F16V_BRU61_3*GBU39}",
        "name": "BRU-61/A with 3 x GBU-39/B SDB",
        "weight": 535,
    }
    BRU_61_A_with_4_x_GBU_39_B_SDB = {
        "clsid": "{F16V_BRU61_4*GBU39}",
        "name": "BRU-61/A with 4 x GBU-39/B SDB",
        "weight": 665,
    }
    BRU_61_A_with_1_x_GBU_53_B_SDB_II = {
        "clsid": "{F16V_BRU61_1*GBU53}",
        "name": "BRU-61/A with 1 x GBU-53/B SDB II",
        "weight": 275,
    }
    BRU_61_A_with_2_x_GBU_53_B_SDB_II = {
        "clsid": "{F16V_BRU61_2*GBU53}",
        "name": "BRU-61/A with 2 x GBU-53/B SDB II",
        "weight": 405,
    }
    BRU_61_A_with_3_x_GBU_53_B_SDB_II = {
        "clsid": "{F16V_BRU61_3*GBU53}",
        "name": "BRU-61/A with 3 x GBU-53/B SDB II",
        "weight": 535,
    }
    BRU_61_A_with_4_x_GBU_53_B_SDB_II = {
        "clsid": "{F16V_BRU61_4*GBU53}",
        "name": "BRU-61/A with 4 x GBU-53/B SDB II",
        "weight": 665,
    }
    F_16V_CFT__3060_lb_FUEL = {
        "clsid": "{F16V_cft_03}",
        "name": "CFT - 3060 lb FUEL",
        "weight": 408.2 + 3060 * 0.45359237,
    }
    F_16V_AUX = {
        "clsid": "{F16V_aux_02}",
        "name": "AUX",
        "weight": 0,
    }
    AN_AAQ_13 = {
        "clsid": "{F16V_aaq13_pod}",
        "name": "AN/AAQ-13",
        "weight": 204.6,
    }


inject_weapons(WeaponsF16V)


class F16VPylon3:
    BRU_61_A_with_1_x_GBU_39_B_SDB = (3, WeaponsF16V.BRU_61_A_with_1_x_GBU_39_B_SDB)
    BRU_61_A_with_2_x_GBU_39_B_SDB = (3, WeaponsF16V.BRU_61_A_with_2_x_GBU_39_B_SDB)
    BRU_61_A_with_3_x_GBU_39_B_SDB = (3, WeaponsF16V.BRU_61_A_with_3_x_GBU_39_B_SDB)
    BRU_61_A_with_4_x_GBU_39_B_SDB = (3, WeaponsF16V.BRU_61_A_with_4_x_GBU_39_B_SDB)
    BRU_61_A_with_1_x_GBU_53_B_SDB_II = (
        3,
        WeaponsF16V.BRU_61_A_with_1_x_GBU_53_B_SDB_II,
    )
    BRU_61_A_with_2_x_GBU_53_B_SDB_II = (
        3,
        WeaponsF16V.BRU_61_A_with_2_x_GBU_53_B_SDB_II,
    )
    BRU_61_A_with_3_x_GBU_53_B_SDB_II = (
        3,
        WeaponsF16V.BRU_61_A_with_3_x_GBU_53_B_SDB_II,
    )
    BRU_61_A_with_4_x_GBU_53_B_SDB_II = (
        3,
        WeaponsF16V.BRU_61_A_with_4_x_GBU_53_B_SDB_II,
    )


class F16VPylon7:
    BRU_61_A_with_1_x_GBU_39_B_SDB = (7, WeaponsF16V.BRU_61_A_with_1_x_GBU_39_B_SDB)
    BRU_61_A_with_2_x_GBU_39_B_SDB = (7, WeaponsF16V.BRU_61_A_with_2_x_GBU_39_B_SDB)
    BRU_61_A_with_3_x_GBU_39_B_SDB = (7, WeaponsF16V.BRU_61_A_with_3_x_GBU_39_B_SDB)
    BRU_61_A_with_4_x_GBU_39_B_SDB = (7, WeaponsF16V.BRU_61_A_with_4_x_GBU_39_B_SDB)
    BRU_61_A_with_1_x_GBU_53_B_SDB_II = (
        7,
        WeaponsF16V.BRU_61_A_with_1_x_GBU_53_B_SDB_II,
    )
    BRU_61_A_with_2_x_GBU_53_B_SDB_II = (
        7,
        WeaponsF16V.BRU_61_A_with_2_x_GBU_53_B_SDB_II,
    )
    BRU_61_A_with_3_x_GBU_53_B_SDB_II = (
        7,
        WeaponsF16V.BRU_61_A_with_3_x_GBU_53_B_SDB_II,
    )
    BRU_61_A_with_4_x_GBU_53_B_SDB_II = (
        7,
        WeaponsF16V.BRU_61_A_with_4_x_GBU_53_B_SDB_II,
    )


class F16VPylon10:
    AN_AAQ_13 = (10, WeaponsF16V.AN_AAQ_13)


# Stations 13 (CFT) and 14 (AUX) do not exist on the stock F-16C_50. The mod
# only adds them when nothing else has claimed those station numbers, which the
# IDF Mods Project F-16I does, so the same check is made in inject_F16V().
# Unlike the classes above these are attached to the aircraft as they are, so
# they must be named PylonN: Retribution finds an aircraft's pylons by name.
class Pylon13:
    F_16V_CFT__3060_lb_FUEL = (13, WeaponsF16V.F_16V_CFT__3060_lb_FUEL)


class Pylon14:
    F_16V_AUX = (14, WeaponsF16V.F_16V_AUX)


_INJECTED_PYLONS: Dict[int, Type[Any]] = {
    3: F16VPylon3,
    7: F16VPylon7,
    10: F16VPylon10,
}

_ADDED_PYLONS: Dict[int, Type[Any]] = {
    13: Pylon13,
    14: Pylon14,
}


def inject_F16V() -> None:
    for number, pylon in _INJECTED_PYLONS.items():
        inject_pylon(getattr(F_16C_50, f"Pylon{number}"), pylon)

    for number, pylon in _ADDED_PYLONS.items():
        existing: Optional[Type[Any]] = getattr(F_16C_50, f"Pylon{number}", None)
        if existing is None or existing is pylon:
            setattr(F_16C_50, f"Pylon{number}", pylon)
            F_16C_50.pylons = F_16C_50.pylons | {number}


def eject_F16V() -> None:
    for number, pylon in _INJECTED_PYLONS.items():
        eject_pylon(getattr(F_16C_50, f"Pylon{number}"), pylon)

    for number, pylon in _ADDED_PYLONS.items():
        if getattr(F_16C_50, f"Pylon{number}", None) is pylon:
            delattr(F_16C_50, f"Pylon{number}")
            F_16C_50.pylons = F_16C_50.pylons - {number}
