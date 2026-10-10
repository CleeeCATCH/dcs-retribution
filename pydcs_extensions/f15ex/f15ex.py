"""F-15EX Eagle II (Spino's mod, V3 with the F15EX_FM EFM and standalone avionics).

The mod registers three types: "F15EX" (no CFTs), "F15EX_CFT" and "F15IA" (the
Israeli F-15IA, a CFT airframe with Python-5 on the wing rails). V3 rebuilt the
stations: 15 pylons, single-round AMRAAM / AIM-260A / AIM-200A / AIM-9X stores per
station (Weapons/Loadouts/EX_Stations.lua), AMBER racks and the AIM-174B. V3 has
no air-to-ground stores.

Generated from the mod's F15EX.lua, F15EX_CFT.lua and F15IA.lua (pylons) and
Weapons/*.lua (names and weights). The Python-5 stores and the three-round AIM-200A
rack are not in those files, so their weights are estimates; weights only affect
what Retribution displays, DCS uses the mod's own. The LAU-115 twin rails the mod
shares with the F-22A EFM mod are referenced from that extension.
"""

from typing import Set

from dcs import task
from dcs.planes import PlaneType
from dcs.weapons_data import Weapons

from game.modsupport import planemod
from pydcs_extensions.f22a_efm.f22a_efm import F22AEFMWeapons
from pydcs_extensions.weapon_injector import inject_weapons


class F15EXWeapons:
    AIM200_4XRACK = {
        "clsid": "{AIM200-4XRACK}",
        "name": "BRU-61C - 4 x AIM-200A - Active Radar AAM",
        "weight": 157.85 * 4 + 50,
    }
    AIM200_X3_F_15EX = {
        "clsid": "{AIM200_X3_F-15EX}",
        "name": "3 x AIM-200A - Active Radar AAM",
        "weight": 157.85 * 3 + 50,  # estimated: rack not in the weapon files
    }
    AMBER_2xAIM120C5 = {
        "clsid": "{AMBER_2xAIM120C5}",
        "name": "AMBER 2x AIM-120C-5 AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    AMBER_2xAIM120C7 = {
        "clsid": "{AMBER_2xAIM120C7}",
        "name": "AMBER 2x AIM-120C-7 AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    AMBER_2xAIM120C8 = {
        "clsid": "{AMBER_2xAIM120C8}",
        "name": "AMBER 2x AIM-120C-8 AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    AMBER_2xAIM120D = {
        "clsid": "{AMBER_2xAIM120D}",
        "name": "AMBER 2x AIM-120D-3 AMRAAM - Active Radar AAM",
        "weight": 165.31 * 2 + 50,
    }
    AMBER_2xAIM120D_P3I = {
        "clsid": "{AMBER_2xAIM120D_P3I}",
        "name": "AMBER 2x AIM-120D P3I AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    AMBER_2xAIM260A = {
        "clsid": "{AMBER_2xAIM260A}",
        "name": "AMBER 2x AIM-260A - Active Radar AAM",
        "weight": 177.8 * 2 + 50,
    }
    ASG_34_LegionPod = {
        "clsid": "{ASG-34_LegionPod}",
        "name": "AN/ASG-34 Legion Pod - IRST",
        "weight": 240,  # estimated
    }
    F15EX_2xAIM_120C_5 = {
        "clsid": "{F15EX_2xAIM-120C-5}",
        "name": "2x AIM-120C-5 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_2xAIM_120C_7 = {
        "clsid": "{F15EX_2xAIM-120C-7}",
        "name": "2x AIM-120C-7 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_2xAIM_120C_8 = {
        "clsid": "{F15EX_2xAIM-120C-8}",
        "name": "2x AIM-120C-8 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_2xAIM_120D = {
        "clsid": "{F15EX_2xAIM-120D}",
        "name": "2x AIM-120D P3I AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_2xAIM_120D_3 = {
        "clsid": "{F15EX_2xAIM-120D-3}",
        "name": "2x AIM-120D-3 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 165.31 * 2 + 50,
    }
    F15EX_2xAIM_260A = {
        "clsid": "{F15EX_2xAIM-260A}",
        "name": "2x AIM-260A - Active Radar AAM (Outer Rail)",
        "weight": 177.8 * 2 + 50,
    }
    F15EX_AIM_120C_5_CFT_A = {
        "clsid": "{F15EX_AIM-120C-5_CFT_A}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (CFT Aft)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_CFT_F = {
        "clsid": "{F15EX_AIM-120C-5_CFT_F}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (CFT Forward)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_FUS_LA = {
        "clsid": "{F15EX_AIM-120C-5_FUS_LA}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Fuselage LA)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_FUS_LF = {
        "clsid": "{F15EX_AIM-120C-5_FUS_LF}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Fuselage LF)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_FUS_RA = {
        "clsid": "{F15EX_AIM-120C-5_FUS_RA}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Fuselage RA)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_FUS_RF = {
        "clsid": "{F15EX_AIM-120C-5_FUS_RF}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Fuselage RF)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_STA11A = {
        "clsid": "{F15EX_AIM-120C-5_STA11A}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Station 11A)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_STA11B = {
        "clsid": "{F15EX_AIM-120C-5_STA11B}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Station 11B)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_STA2A = {
        "clsid": "{F15EX_AIM-120C-5_STA2A}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Station 2A)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_5_STA2B = {
        "clsid": "{F15EX_AIM-120C-5_STA2B}",
        "name": "AIM-120C-5 AMRAAM - Active Radar AAM (Station 2B)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_CFT_A = {
        "clsid": "{F15EX_AIM-120C-7_CFT_A}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (CFT Aft)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_CFT_F = {
        "clsid": "{F15EX_AIM-120C-7_CFT_F}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (CFT Forward)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_FUS_LA = {
        "clsid": "{F15EX_AIM-120C-7_FUS_LA}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Fuselage LA)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_FUS_LF = {
        "clsid": "{F15EX_AIM-120C-7_FUS_LF}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Fuselage LF)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_FUS_RA = {
        "clsid": "{F15EX_AIM-120C-7_FUS_RA}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Fuselage RA)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_FUS_RF = {
        "clsid": "{F15EX_AIM-120C-7_FUS_RF}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Fuselage RF)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_STA11A = {
        "clsid": "{F15EX_AIM-120C-7_STA11A}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Station 11A)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_STA11B = {
        "clsid": "{F15EX_AIM-120C-7_STA11B}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Station 11B)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_STA2A = {
        "clsid": "{F15EX_AIM-120C-7_STA2A}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Station 2A)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_7_STA2B = {
        "clsid": "{F15EX_AIM-120C-7_STA2B}",
        "name": "AIM-120C-7 AMRAAM - Active Radar AAM (Station 2B)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_CFT_A = {
        "clsid": "{F15EX_AIM-120C-8_CFT_A}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (CFT Aft)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_CFT_F = {
        "clsid": "{F15EX_AIM-120C-8_CFT_F}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (CFT Forward)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_FUS_LA = {
        "clsid": "{F15EX_AIM-120C-8_FUS_LA}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Fuselage LA)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_FUS_LF = {
        "clsid": "{F15EX_AIM-120C-8_FUS_LF}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Fuselage LF)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_FUS_RA = {
        "clsid": "{F15EX_AIM-120C-8_FUS_RA}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Fuselage RA)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_FUS_RF = {
        "clsid": "{F15EX_AIM-120C-8_FUS_RF}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Fuselage RF)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_STA11A = {
        "clsid": "{F15EX_AIM-120C-8_STA11A}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Station 11A)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_STA11B = {
        "clsid": "{F15EX_AIM-120C-8_STA11B}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Station 11B)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_STA2A = {
        "clsid": "{F15EX_AIM-120C-8_STA2A}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Station 2A)",
        "weight": 161.48,
    }
    F15EX_AIM_120C_8_STA2B = {
        "clsid": "{F15EX_AIM-120C-8_STA2B}",
        "name": "AIM-120C-8 AMRAAM - Active Radar AAM (Station 2B)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_3_CFT_A = {
        "clsid": "{F15EX_AIM-120D-3_CFT_A}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (CFT Aft)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_CFT_F = {
        "clsid": "{F15EX_AIM-120D-3_CFT_F}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (CFT Forward)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_FUS_LA = {
        "clsid": "{F15EX_AIM-120D-3_FUS_LA}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Fuselage LA)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_FUS_LF = {
        "clsid": "{F15EX_AIM-120D-3_FUS_LF}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Fuselage LF)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_FUS_RA = {
        "clsid": "{F15EX_AIM-120D-3_FUS_RA}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Fuselage RA)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_FUS_RF = {
        "clsid": "{F15EX_AIM-120D-3_FUS_RF}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Fuselage RF)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_STA11A = {
        "clsid": "{F15EX_AIM-120D-3_STA11A}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Station 11A)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_STA11B = {
        "clsid": "{F15EX_AIM-120D-3_STA11B}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Station 11B)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_STA2A = {
        "clsid": "{F15EX_AIM-120D-3_STA2A}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Station 2A)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_3_STA2B = {
        "clsid": "{F15EX_AIM-120D-3_STA2B}",
        "name": "AIM-120D-3 AMRAAM - Active Radar AAM (Station 2B)",
        "weight": 165.31,
    }
    F15EX_AIM_120D_CFT_A = {
        "clsid": "{F15EX_AIM-120D_CFT_A}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (CFT Aft)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_CFT_F = {
        "clsid": "{F15EX_AIM-120D_CFT_F}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (CFT Forward)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_FUS_LA = {
        "clsid": "{F15EX_AIM-120D_FUS_LA}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Fuselage LA)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_FUS_LF = {
        "clsid": "{F15EX_AIM-120D_FUS_LF}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Fuselage LF)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_FUS_RA = {
        "clsid": "{F15EX_AIM-120D_FUS_RA}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Fuselage RA)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_FUS_RF = {
        "clsid": "{F15EX_AIM-120D_FUS_RF}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Fuselage RF)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_STA11A = {
        "clsid": "{F15EX_AIM-120D_STA11A}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Station 11A)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_STA11B = {
        "clsid": "{F15EX_AIM-120D_STA11B}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Station 11B)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_STA2A = {
        "clsid": "{F15EX_AIM-120D_STA2A}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Station 2A)",
        "weight": 161.48,
    }
    F15EX_AIM_120D_STA2B = {
        "clsid": "{F15EX_AIM-120D_STA2B}",
        "name": "AIM-120D P3I AMRAAM - Active Radar AAM (Station 2B)",
        "weight": 161.48,
    }
    F15EX_AIM_174B = {
        "clsid": "{F15EX_AIM-174B}",
        "name": "AIM-174B Gunslinger - Active Radar ULRAAM",
        "weight": 860.0 + 50,
    }
    F15EX_AIM_174B_CFT = {
        "clsid": "{F15EX_AIM-174B_CFT}",
        "name": "AIM-174B Gunslinger - Active Radar ULRAAM (CFT)",
        "weight": 860.0,
    }
    F15EX_AIM_200A_CFT_A = {
        "clsid": "{F15EX_AIM-200A_CFT_A}",
        "name": "AIM-200A - Active Radar AAM (CFT Aft)",
        "weight": 157.85,
    }
    F15EX_AIM_200A_CFT_F = {
        "clsid": "{F15EX_AIM-200A_CFT_F}",
        "name": "AIM-200A - Active Radar AAM (CFT Forward)",
        "weight": 157.85,
    }
    F15EX_AIM_200A_FUS_LA = {
        "clsid": "{F15EX_AIM-200A_FUS_LA}",
        "name": "AIM-200A - Active Radar AAM (Fuselage LA)",
        "weight": 157.85,
    }
    F15EX_AIM_200A_FUS_LF = {
        "clsid": "{F15EX_AIM-200A_FUS_LF}",
        "name": "AIM-200A - Active Radar AAM (Fuselage LF)",
        "weight": 157.85,
    }
    F15EX_AIM_200A_FUS_RA = {
        "clsid": "{F15EX_AIM-200A_FUS_RA}",
        "name": "AIM-200A - Active Radar AAM (Fuselage RA)",
        "weight": 157.85,
    }
    F15EX_AIM_200A_FUS_RF = {
        "clsid": "{F15EX_AIM-200A_FUS_RF}",
        "name": "AIM-200A - Active Radar AAM (Fuselage RF)",
        "weight": 157.85,
    }
    F15EX_AIM_260A_CFT_A = {
        "clsid": "{F15EX_AIM-260A_CFT_A}",
        "name": "AIM-260A - Active Radar AAM (CFT Aft)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_CFT_F = {
        "clsid": "{F15EX_AIM-260A_CFT_F}",
        "name": "AIM-260A - Active Radar AAM (CFT Forward)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_FUS_LA = {
        "clsid": "{F15EX_AIM-260A_FUS_LA}",
        "name": "AIM-260A - Active Radar AAM (Fuselage LA)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_FUS_LF = {
        "clsid": "{F15EX_AIM-260A_FUS_LF}",
        "name": "AIM-260A - Active Radar AAM (Fuselage LF)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_FUS_RA = {
        "clsid": "{F15EX_AIM-260A_FUS_RA}",
        "name": "AIM-260A - Active Radar AAM (Fuselage RA)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_FUS_RF = {
        "clsid": "{F15EX_AIM-260A_FUS_RF}",
        "name": "AIM-260A - Active Radar AAM (Fuselage RF)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_STA11A = {
        "clsid": "{F15EX_AIM-260A_STA11A}",
        "name": "AIM-260A - Active Radar AAM (Station 11A)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_STA11B = {
        "clsid": "{F15EX_AIM-260A_STA11B}",
        "name": "AIM-260A - Active Radar AAM (Station 11B)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_STA2A = {
        "clsid": "{F15EX_AIM-260A_STA2A}",
        "name": "AIM-260A - Active Radar AAM (Station 2A)",
        "weight": 177.8,
    }
    F15EX_AIM_260A_STA2B = {
        "clsid": "{F15EX_AIM-260A_STA2B}",
        "name": "AIM-260A - Active Radar AAM (Station 2B)",
        "weight": 177.8,
    }
    F15EX_AIM_9X_ED_STA11A = {
        "clsid": "{F15EX_AIM-9X-ED_STA11A}",
        "name": "AIM-9X Sidewinder IR AAM (ED) (Station 11A)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_ED_STA11B = {
        "clsid": "{F15EX_AIM-9X-ED_STA11B}",
        "name": "AIM-9X Sidewinder IR AAM (ED) (Station 11B)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_ED_STA2A = {
        "clsid": "{F15EX_AIM-9X-ED_STA2A}",
        "name": "AIM-9X Sidewinder IR AAM (ED) (Station 2A)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_ED_STA2B = {
        "clsid": "{F15EX_AIM-9X-ED_STA2B}",
        "name": "AIM-9X Sidewinder IR AAM (ED) (Station 2B)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_STA11A = {
        "clsid": "{F15EX_AIM-9X_STA11A}",
        "name": "AIM-9X-2 Sidewinder IR AAM (Station 11A)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_STA11B = {
        "clsid": "{F15EX_AIM-9X_STA11B}",
        "name": "AIM-9X-2 Sidewinder IR AAM (Station 11B)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_STA2A = {
        "clsid": "{F15EX_AIM-9X_STA2A}",
        "name": "AIM-9X-2 Sidewinder IR AAM (Station 2A)",
        "weight": 85.5,
    }
    F15EX_AIM_9X_STA2B = {
        "clsid": "{F15EX_AIM-9X_STA2B}",
        "name": "AIM-9X-2 Sidewinder IR AAM (Station 2B)",
        "weight": 85.5,
    }
    F15EX_LAU_115_2xAIM_120C_5 = {
        "clsid": "{F15EX_LAU_115_2xAIM-120C-5}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120C-5 AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_LAU_115_2xAIM_120C_8 = {
        "clsid": "{F15EX_LAU_115_2xAIM-120C-8}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120C-8 AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_LAU_115_2xAIM_120D = {
        "clsid": "{F15EX_LAU_115_2xAIM-120D}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120D P3I AMRAAM - Active Radar AAM",
        "weight": 161.48 * 2 + 50,
    }
    F15EX_PYTHON_5_STA11A = {
        "clsid": "{F15EX_PYTHON-5_STA11A}",
        "name": "Python-5 IR AAM (Station 11A)",
        "weight": 105,
    }
    F15EX_PYTHON_5_STA11B = {
        "clsid": "{F15EX_PYTHON-5_STA11B}",
        "name": "Python-5 IR AAM (Station 11B)",
        "weight": 105,
    }
    F15EX_PYTHON_5_STA2A = {
        "clsid": "{F15EX_PYTHON-5_STA2A}",
        "name": "Python-5 IR AAM (Station 2A)",
        "weight": 105,
    }
    F15EX_PYTHON_5_STA2B = {
        "clsid": "{F15EX_PYTHON-5_STA2B}",
        "name": "Python-5 IR AAM (Station 2B)",
        "weight": 105,
    }
    F15IA_PYTHON_5 = {
        "clsid": "{F15IA_PYTHON-5}",
        "name": "2x Python-5 IR AAM (Outer Rail)",
        "weight": 105 * 2 + 150,  # estimated: Python-5 not in the weapon files
    }
    F_15EX_AIM_9X_O = {
        "clsid": "{F-15EX_AIM-9X_O}",
        "name": "2x AIM-9X-2 Sidewinder IR AAM (Outer Rail)",
        "weight": 85.5 * 2 + 150,
    }


inject_weapons(F15EXWeapons)


@planemod
class F_15EX(PlaneType):
    """Plain jet: AMRAAM rails on the fuselage stations."""

    id = "F15EX"
    flyable = True
    height = 5.63
    width = 13.05
    length = 19.43
    fuel_max = 6146
    max_speed = 2873.196
    chaff = 120
    flare = 120
    charge_total = 360
    chaff_charge_size = 1
    flare_charge_size = 2
    category = "Interceptor"  # {78EFB7A2-FD52-4b57-A6A6-3BF0E1D6555F}
    radio_frequency = 127.5

    livery_name = "F-15EX"  # from livery_entry

    class Pylon1:
        F15EX_2xAIM_260A = (1, F15EXWeapons.F15EX_2xAIM_260A)
        F15EX_2xAIM_120D_3 = (1, F15EXWeapons.F15EX_2xAIM_120D_3)
        F15EX_2xAIM_120D = (1, F15EXWeapons.F15EX_2xAIM_120D)
        F15EX_2xAIM_120C_8 = (1, F15EXWeapons.F15EX_2xAIM_120C_8)
        F15EX_2xAIM_120C_7 = (1, F15EXWeapons.F15EX_2xAIM_120C_7)
        F15EX_2xAIM_120C_5 = (1, F15EXWeapons.F15EX_2xAIM_120C_5)
        F_15EX_AIM_9X_O = (1, F15EXWeapons.F_15EX_AIM_9X_O)

    class Pylon2:
        Fuel_tank_610_gal_ = (2, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (2, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120C_8 = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_8)
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120D = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120D)
        F15EX_LAU_115_2xAIM_120C_5 = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_5)
        AIM200_4XRACK = (2, F15EXWeapons.AIM200_4XRACK)
        F15EX_AIM_174B = (2, F15EXWeapons.F15EX_AIM_174B)

    class Pylon3:
        F15EX_AIM_120C_8_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_8_STA2A)
        F15EX_AIM_120C_7_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_7_STA2A)
        F15EX_AIM_120C_5_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_5_STA2A)
        F15EX_AIM_120D_3_STA2A = (3, F15EXWeapons.F15EX_AIM_120D_3_STA2A)
        F15EX_AIM_120D_STA2A = (3, F15EXWeapons.F15EX_AIM_120D_STA2A)
        F15EX_AIM_260A_STA2A = (3, F15EXWeapons.F15EX_AIM_260A_STA2A)
        F15EX_AIM_9X_STA2A = (3, F15EXWeapons.F15EX_AIM_9X_STA2A)
        F15EX_AIM_9X_ED_STA2A = (3, F15EXWeapons.F15EX_AIM_9X_ED_STA2A)

    class Pylon4:
        F15EX_AIM_120C_8_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_8_STA2B)
        F15EX_AIM_120C_7_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_7_STA2B)
        F15EX_AIM_120C_5_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_5_STA2B)
        F15EX_AIM_120D_3_STA2B = (4, F15EXWeapons.F15EX_AIM_120D_3_STA2B)
        F15EX_AIM_120D_STA2B = (4, F15EXWeapons.F15EX_AIM_120D_STA2B)
        F15EX_AIM_260A_STA2B = (4, F15EXWeapons.F15EX_AIM_260A_STA2B)
        F15EX_AIM_9X_STA2B = (4, F15EXWeapons.F15EX_AIM_9X_STA2B)
        F15EX_AIM_9X_ED_STA2B = (4, F15EXWeapons.F15EX_AIM_9X_ED_STA2B)

    class Pylon5:
        F15EX_AIM_120C_8_FUS_LF = (5, F15EXWeapons.F15EX_AIM_120C_8_FUS_LF)
        F15EX_AIM_120C_7_FUS_LF = (5, F15EXWeapons.F15EX_AIM_120C_7_FUS_LF)
        F15EX_AIM_120C_5_FUS_LF = (5, F15EXWeapons.F15EX_AIM_120C_5_FUS_LF)
        F15EX_AIM_120D_3_FUS_LF = (5, F15EXWeapons.F15EX_AIM_120D_3_FUS_LF)
        F15EX_AIM_120D_FUS_LF = (5, F15EXWeapons.F15EX_AIM_120D_FUS_LF)
        F15EX_AIM_260A_FUS_LF = (5, F15EXWeapons.F15EX_AIM_260A_FUS_LF)
        F15EX_AIM_200A_FUS_LF = (5, F15EXWeapons.F15EX_AIM_200A_FUS_LF)

    class Pylon6:
        F15EX_AIM_120C_8_FUS_LA = (6, F15EXWeapons.F15EX_AIM_120C_8_FUS_LA)
        F15EX_AIM_120C_7_FUS_LA = (6, F15EXWeapons.F15EX_AIM_120C_7_FUS_LA)
        F15EX_AIM_120C_5_FUS_LA = (6, F15EXWeapons.F15EX_AIM_120C_5_FUS_LA)
        F15EX_AIM_120D_3_FUS_LA = (6, F15EXWeapons.F15EX_AIM_120D_3_FUS_LA)
        F15EX_AIM_120D_FUS_LA = (6, F15EXWeapons.F15EX_AIM_120D_FUS_LA)
        F15EX_AIM_260A_FUS_LA = (6, F15EXWeapons.F15EX_AIM_260A_FUS_LA)
        F15EX_AIM_200A_FUS_LA = (6, F15EXWeapons.F15EX_AIM_200A_FUS_LA)

    class Pylon7:
        AN_AAQ_28_LITENING___Targeting_Pod_ = (
            7,
            Weapons.AN_AAQ_28_LITENING___Targeting_Pod_,
        )
        AN_AAQ_33___Advanced_Targeting_Pod = (
            7,
            Weapons.AN_AAQ_33___Advanced_Targeting_Pod,
        )
        AN_AAQ_14_LANTIRN_TGT_Pod = (7, Weapons.AN_AAQ_14_LANTIRN_TGT_Pod)

    class Pylon8:
        AIM200_4XRACK = (8, F15EXWeapons.AIM200_4XRACK)
        Fuel_tank_610_gal_ = (8, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (8, Weapons.Fuel_tank_610_gal__Empty_)
        ASG_34_LegionPod = (8, F15EXWeapons.ASG_34_LegionPod)
        AN_AAQ_33___Advanced_Targeting_Pod = (
            8,
            Weapons.AN_AAQ_33___Advanced_Targeting_Pod,
        )

    class Pylon9:
        AN_AAQ_13_LANTIRN_NAV_POD = (9, Weapons.AN_AAQ_13_LANTIRN_NAV_POD)

    class Pylon10:
        F15EX_AIM_120C_8_FUS_RA = (10, F15EXWeapons.F15EX_AIM_120C_8_FUS_RA)
        F15EX_AIM_120C_7_FUS_RA = (10, F15EXWeapons.F15EX_AIM_120C_7_FUS_RA)
        F15EX_AIM_120C_5_FUS_RA = (10, F15EXWeapons.F15EX_AIM_120C_5_FUS_RA)
        F15EX_AIM_120D_3_FUS_RA = (10, F15EXWeapons.F15EX_AIM_120D_3_FUS_RA)
        F15EX_AIM_120D_FUS_RA = (10, F15EXWeapons.F15EX_AIM_120D_FUS_RA)
        F15EX_AIM_260A_FUS_RA = (10, F15EXWeapons.F15EX_AIM_260A_FUS_RA)
        F15EX_AIM_200A_FUS_RA = (10, F15EXWeapons.F15EX_AIM_200A_FUS_RA)

    class Pylon11:
        F15EX_AIM_120C_8_FUS_RF = (11, F15EXWeapons.F15EX_AIM_120C_8_FUS_RF)
        F15EX_AIM_120C_7_FUS_RF = (11, F15EXWeapons.F15EX_AIM_120C_7_FUS_RF)
        F15EX_AIM_120C_5_FUS_RF = (11, F15EXWeapons.F15EX_AIM_120C_5_FUS_RF)
        F15EX_AIM_120D_3_FUS_RF = (11, F15EXWeapons.F15EX_AIM_120D_3_FUS_RF)
        F15EX_AIM_120D_FUS_RF = (11, F15EXWeapons.F15EX_AIM_120D_FUS_RF)
        F15EX_AIM_260A_FUS_RF = (11, F15EXWeapons.F15EX_AIM_260A_FUS_RF)
        F15EX_AIM_200A_FUS_RF = (11, F15EXWeapons.F15EX_AIM_200A_FUS_RF)

    class Pylon12:
        F15EX_AIM_120C_8_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_8_STA11B)
        F15EX_AIM_120C_7_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_7_STA11B)
        F15EX_AIM_120C_5_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_5_STA11B)
        F15EX_AIM_120D_3_STA11B = (12, F15EXWeapons.F15EX_AIM_120D_3_STA11B)
        F15EX_AIM_120D_STA11B = (12, F15EXWeapons.F15EX_AIM_120D_STA11B)
        F15EX_AIM_260A_STA11B = (12, F15EXWeapons.F15EX_AIM_260A_STA11B)
        F15EX_AIM_9X_STA11B = (12, F15EXWeapons.F15EX_AIM_9X_STA11B)
        F15EX_AIM_9X_ED_STA11B = (12, F15EXWeapons.F15EX_AIM_9X_ED_STA11B)

    class Pylon13:
        F15EX_AIM_120C_8_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_8_STA11A)
        F15EX_AIM_120C_7_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_7_STA11A)
        F15EX_AIM_120C_5_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_5_STA11A)
        F15EX_AIM_120D_3_STA11A = (13, F15EXWeapons.F15EX_AIM_120D_3_STA11A)
        F15EX_AIM_120D_STA11A = (13, F15EXWeapons.F15EX_AIM_120D_STA11A)
        F15EX_AIM_260A_STA11A = (13, F15EXWeapons.F15EX_AIM_260A_STA11A)
        F15EX_AIM_9X_STA11A = (13, F15EXWeapons.F15EX_AIM_9X_STA11A)
        F15EX_AIM_9X_ED_STA11A = (13, F15EXWeapons.F15EX_AIM_9X_ED_STA11A)

    class Pylon14:
        Fuel_tank_610_gal_ = (14, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (14, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120C_8 = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_8)
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120D = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120D)
        F15EX_LAU_115_2xAIM_120C_5 = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_5)
        AIM200_4XRACK = (14, F15EXWeapons.AIM200_4XRACK)
        F15EX_AIM_174B = (14, F15EXWeapons.F15EX_AIM_174B)

    class Pylon15:
        F_15EX_AIM_9X_O = (15, F15EXWeapons.F_15EX_AIM_9X_O)
        F15EX_2xAIM_260A = (15, F15EXWeapons.F15EX_2xAIM_260A)
        F15EX_2xAIM_120D_3 = (15, F15EXWeapons.F15EX_2xAIM_120D_3)
        F15EX_2xAIM_120D = (15, F15EXWeapons.F15EX_2xAIM_120D)
        F15EX_2xAIM_120C_8 = (15, F15EXWeapons.F15EX_2xAIM_120C_8)
        F15EX_2xAIM_120C_7 = (15, F15EXWeapons.F15EX_2xAIM_120C_7)
        F15EX_2xAIM_120C_5 = (15, F15EXWeapons.F15EX_2xAIM_120C_5)

    pylons: Set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}

    tasks = [
        task.CAP,
        task.Escort,
        task.FighterSweep,
        task.Intercept,
        task.Reconnaissance,
        task.GroundAttack,
        task.CAS,
        task.SEAD,
        task.RunwayAttack,
        task.AntishipStrike,
    ]
    task_default = task.CAP


@planemod
class F_15EX_CFT(PlaneType):
    """Conformal fuel tanks: CFT and AMBER stations."""

    id = "F15EX_CFT"
    flyable = True
    height = 5.63
    width = 13.05
    length = 19.43
    fuel_max = 10571
    max_speed = 2873.196
    chaff = 120
    flare = 120
    charge_total = 360
    chaff_charge_size = 1
    flare_charge_size = 2
    category = "Interceptor"  # {78EFB7A2-FD52-4b57-A6A6-3BF0E1D6555F}
    radio_frequency = 127.5

    livery_name = "F-15EX_CFT"  # from livery_entry

    class Pylon1:
        F15EX_2xAIM_260A = (1, F15EXWeapons.F15EX_2xAIM_260A)
        F15EX_2xAIM_120D_3 = (1, F15EXWeapons.F15EX_2xAIM_120D_3)
        F15EX_2xAIM_120D = (1, F15EXWeapons.F15EX_2xAIM_120D)
        F15EX_2xAIM_120C_8 = (1, F15EXWeapons.F15EX_2xAIM_120C_8)
        F15EX_2xAIM_120C_7 = (1, F15EXWeapons.F15EX_2xAIM_120C_7)
        F15EX_2xAIM_120C_5 = (1, F15EXWeapons.F15EX_2xAIM_120C_5)
        F_15EX_AIM_9X_O = (1, F15EXWeapons.F_15EX_AIM_9X_O)

    class Pylon2:
        Fuel_tank_610_gal_ = (2, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (2, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120C_8 = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_8)
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120D = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120D)
        F15EX_LAU_115_2xAIM_120C_5 = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_5)
        AIM200_4XRACK = (2, F15EXWeapons.AIM200_4XRACK)
        F15EX_AIM_174B = (2, F15EXWeapons.F15EX_AIM_174B)

    class Pylon3:
        F15EX_AIM_120C_8_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_8_STA2A)
        F15EX_AIM_120C_7_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_7_STA2A)
        F15EX_AIM_120C_5_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_5_STA2A)
        F15EX_AIM_120D_3_STA2A = (3, F15EXWeapons.F15EX_AIM_120D_3_STA2A)
        F15EX_AIM_120D_STA2A = (3, F15EXWeapons.F15EX_AIM_120D_STA2A)
        F15EX_AIM_260A_STA2A = (3, F15EXWeapons.F15EX_AIM_260A_STA2A)
        F15EX_AIM_9X_STA2A = (3, F15EXWeapons.F15EX_AIM_9X_STA2A)
        F15EX_AIM_9X_ED_STA2A = (3, F15EXWeapons.F15EX_AIM_9X_ED_STA2A)

    class Pylon4:
        F15EX_AIM_120C_8_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_8_STA2B)
        F15EX_AIM_120C_7_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_7_STA2B)
        F15EX_AIM_120C_5_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_5_STA2B)
        F15EX_AIM_120D_3_STA2B = (4, F15EXWeapons.F15EX_AIM_120D_3_STA2B)
        F15EX_AIM_120D_STA2B = (4, F15EXWeapons.F15EX_AIM_120D_STA2B)
        F15EX_AIM_260A_STA2B = (4, F15EXWeapons.F15EX_AIM_260A_STA2B)
        F15EX_AIM_9X_STA2B = (4, F15EXWeapons.F15EX_AIM_9X_STA2B)
        F15EX_AIM_9X_ED_STA2B = (4, F15EXWeapons.F15EX_AIM_9X_ED_STA2B)

    class Pylon5:
        AMBER_2xAIM120C8 = (5, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (5, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (5, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (5, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (5, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (5, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_F = (5, F15EXWeapons.F15EX_AIM_120C_8_CFT_F)
        F15EX_AIM_120C_7_CFT_F = (5, F15EXWeapons.F15EX_AIM_120C_7_CFT_F)
        F15EX_AIM_120C_5_CFT_F = (5, F15EXWeapons.F15EX_AIM_120C_5_CFT_F)
        F15EX_AIM_120D_3_CFT_F = (5, F15EXWeapons.F15EX_AIM_120D_3_CFT_F)
        F15EX_AIM_120D_CFT_F = (5, F15EXWeapons.F15EX_AIM_120D_CFT_F)
        F15EX_AIM_260A_CFT_F = (5, F15EXWeapons.F15EX_AIM_260A_CFT_F)
        F15EX_AIM_200A_CFT_F = (5, F15EXWeapons.F15EX_AIM_200A_CFT_F)
        AIM200_4XRACK = (5, F15EXWeapons.AIM200_4XRACK)
        AIM200_X3_F_15EX = (5, F15EXWeapons.AIM200_X3_F_15EX)
        F15EX_AIM_174B_CFT = (5, F15EXWeapons.F15EX_AIM_174B_CFT)

    class Pylon6:
        AMBER_2xAIM120C8 = (6, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (6, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (6, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (6, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (6, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (6, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_A = (6, F15EXWeapons.F15EX_AIM_120C_8_CFT_A)
        F15EX_AIM_120C_7_CFT_A = (6, F15EXWeapons.F15EX_AIM_120C_7_CFT_A)
        F15EX_AIM_120C_5_CFT_A = (6, F15EXWeapons.F15EX_AIM_120C_5_CFT_A)
        F15EX_AIM_120D_3_CFT_A = (6, F15EXWeapons.F15EX_AIM_120D_3_CFT_A)
        F15EX_AIM_120D_CFT_A = (6, F15EXWeapons.F15EX_AIM_120D_CFT_A)
        F15EX_AIM_260A_CFT_A = (6, F15EXWeapons.F15EX_AIM_260A_CFT_A)
        F15EX_AIM_200A_CFT_A = (6, F15EXWeapons.F15EX_AIM_200A_CFT_A)

    class Pylon7:
        AMBER_2xAIM120C8 = (7, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (7, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (7, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (7, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (7, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (7, F15EXWeapons.AMBER_2xAIM260A)
        AN_AAQ_28_LITENING___Targeting_Pod_ = (
            7,
            Weapons.AN_AAQ_28_LITENING___Targeting_Pod_,
        )
        AN_AAQ_33___Advanced_Targeting_Pod = (
            7,
            Weapons.AN_AAQ_33___Advanced_Targeting_Pod,
        )
        AN_AAQ_14_LANTIRN_TGT_Pod = (7, Weapons.AN_AAQ_14_LANTIRN_TGT_Pod)

    class Pylon8:
        AMBER_2xAIM120C8 = (8, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (8, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (8, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (8, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (8, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (8, F15EXWeapons.AMBER_2xAIM260A)
        AIM200_4XRACK = (8, F15EXWeapons.AIM200_4XRACK)
        Fuel_tank_610_gal_ = (8, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (8, Weapons.Fuel_tank_610_gal__Empty_)
        ASG_34_LegionPod = (8, F15EXWeapons.ASG_34_LegionPod)

    class Pylon9:
        AMBER_2xAIM120C8 = (9, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (9, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (9, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (9, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (9, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (9, F15EXWeapons.AMBER_2xAIM260A)
        AN_AAQ_13_LANTIRN_NAV_POD = (9, Weapons.AN_AAQ_13_LANTIRN_NAV_POD)

    class Pylon10:
        AMBER_2xAIM120C8 = (10, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (10, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (10, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (10, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (10, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (10, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_A = (10, F15EXWeapons.F15EX_AIM_120C_8_CFT_A)
        F15EX_AIM_120C_7_CFT_A = (10, F15EXWeapons.F15EX_AIM_120C_7_CFT_A)
        F15EX_AIM_120C_5_CFT_A = (10, F15EXWeapons.F15EX_AIM_120C_5_CFT_A)
        F15EX_AIM_120D_3_CFT_A = (10, F15EXWeapons.F15EX_AIM_120D_3_CFT_A)
        F15EX_AIM_120D_CFT_A = (10, F15EXWeapons.F15EX_AIM_120D_CFT_A)
        F15EX_AIM_260A_CFT_A = (10, F15EXWeapons.F15EX_AIM_260A_CFT_A)
        F15EX_AIM_200A_CFT_A = (10, F15EXWeapons.F15EX_AIM_200A_CFT_A)

    class Pylon11:
        AMBER_2xAIM120C8 = (11, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (11, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (11, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (11, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (11, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (11, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_F = (11, F15EXWeapons.F15EX_AIM_120C_8_CFT_F)
        F15EX_AIM_120C_7_CFT_F = (11, F15EXWeapons.F15EX_AIM_120C_7_CFT_F)
        F15EX_AIM_120C_5_CFT_F = (11, F15EXWeapons.F15EX_AIM_120C_5_CFT_F)
        F15EX_AIM_120D_3_CFT_F = (11, F15EXWeapons.F15EX_AIM_120D_3_CFT_F)
        F15EX_AIM_120D_CFT_F = (11, F15EXWeapons.F15EX_AIM_120D_CFT_F)
        F15EX_AIM_260A_CFT_F = (11, F15EXWeapons.F15EX_AIM_260A_CFT_F)
        F15EX_AIM_200A_CFT_F = (11, F15EXWeapons.F15EX_AIM_200A_CFT_F)
        AIM200_4XRACK = (11, F15EXWeapons.AIM200_4XRACK)
        AIM200_X3_F_15EX = (11, F15EXWeapons.AIM200_X3_F_15EX)
        F15EX_AIM_174B_CFT = (11, F15EXWeapons.F15EX_AIM_174B_CFT)

    class Pylon12:
        F15EX_AIM_120C_8_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_8_STA11B)
        F15EX_AIM_120C_7_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_7_STA11B)
        F15EX_AIM_120C_5_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_5_STA11B)
        F15EX_AIM_120D_3_STA11B = (12, F15EXWeapons.F15EX_AIM_120D_3_STA11B)
        F15EX_AIM_120D_STA11B = (12, F15EXWeapons.F15EX_AIM_120D_STA11B)
        F15EX_AIM_260A_STA11B = (12, F15EXWeapons.F15EX_AIM_260A_STA11B)
        F15EX_AIM_9X_STA11B = (12, F15EXWeapons.F15EX_AIM_9X_STA11B)
        F15EX_AIM_9X_ED_STA11B = (12, F15EXWeapons.F15EX_AIM_9X_ED_STA11B)

    class Pylon13:
        F15EX_AIM_120C_8_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_8_STA11A)
        F15EX_AIM_120C_7_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_7_STA11A)
        F15EX_AIM_120C_5_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_5_STA11A)
        F15EX_AIM_120D_3_STA11A = (13, F15EXWeapons.F15EX_AIM_120D_3_STA11A)
        F15EX_AIM_120D_STA11A = (13, F15EXWeapons.F15EX_AIM_120D_STA11A)
        F15EX_AIM_260A_STA11A = (13, F15EXWeapons.F15EX_AIM_260A_STA11A)
        F15EX_AIM_9X_STA11A = (13, F15EXWeapons.F15EX_AIM_9X_STA11A)
        F15EX_AIM_9X_ED_STA11A = (13, F15EXWeapons.F15EX_AIM_9X_ED_STA11A)

    class Pylon14:
        Fuel_tank_610_gal_ = (14, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (14, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120C_8 = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_8)
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120D = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120D)
        F15EX_LAU_115_2xAIM_120C_5 = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_5)
        AIM200_4XRACK = (14, F15EXWeapons.AIM200_4XRACK)
        F15EX_AIM_174B = (14, F15EXWeapons.F15EX_AIM_174B)

    class Pylon15:
        F_15EX_AIM_9X_O = (15, F15EXWeapons.F_15EX_AIM_9X_O)
        F15EX_2xAIM_260A = (15, F15EXWeapons.F15EX_2xAIM_260A)
        F15EX_2xAIM_120D_3 = (15, F15EXWeapons.F15EX_2xAIM_120D_3)
        F15EX_2xAIM_120D = (15, F15EXWeapons.F15EX_2xAIM_120D)
        F15EX_2xAIM_120C_8 = (15, F15EXWeapons.F15EX_2xAIM_120C_8)
        F15EX_2xAIM_120C_7 = (15, F15EXWeapons.F15EX_2xAIM_120C_7)
        F15EX_2xAIM_120C_5 = (15, F15EXWeapons.F15EX_2xAIM_120C_5)

    pylons: Set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}

    tasks = [
        task.CAP,
        task.Escort,
        task.FighterSweep,
        task.Intercept,
        task.Reconnaissance,
        task.GroundAttack,
        task.CAS,
        task.SEAD,
        task.RunwayAttack,
        task.AntishipStrike,
    ]
    task_default = task.CAP


@planemod
class F_15IA(PlaneType):
    """F-15IA: the CFT airframe with Python-5 on the wing rails."""

    id = "F15IA"
    flyable = True
    height = 5.63
    width = 13.05
    length = 19.43
    fuel_max = 10571
    max_speed = 2873.196
    chaff = 120
    flare = 120
    charge_total = 360
    chaff_charge_size = 1
    flare_charge_size = 2
    category = "Interceptor"  # {78EFB7A2-FD52-4b57-A6A6-3BF0E1D6555F}
    radio_frequency = 127.5

    livery_name = "F-15IA"  # from livery_entry

    class Pylon1:
        F15EX_2xAIM_260A = (1, F15EXWeapons.F15EX_2xAIM_260A)
        F15EX_2xAIM_120D_3 = (1, F15EXWeapons.F15EX_2xAIM_120D_3)
        F15EX_2xAIM_120D = (1, F15EXWeapons.F15EX_2xAIM_120D)
        F15EX_2xAIM_120C_8 = (1, F15EXWeapons.F15EX_2xAIM_120C_8)
        F15EX_2xAIM_120C_7 = (1, F15EXWeapons.F15EX_2xAIM_120C_7)
        F15EX_2xAIM_120C_5 = (1, F15EXWeapons.F15EX_2xAIM_120C_5)
        F15IA_PYTHON_5 = (1, F15EXWeapons.F15IA_PYTHON_5)

    class Pylon2:
        Fuel_tank_610_gal_ = (2, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (2, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120C_8 = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_8)
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120D = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120D)
        F15EX_LAU_115_2xAIM_120C_5 = (2, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_5)
        AIM200_4XRACK = (2, F15EXWeapons.AIM200_4XRACK)
        F15EX_AIM_174B = (2, F15EXWeapons.F15EX_AIM_174B)

    class Pylon3:
        F15EX_AIM_120C_8_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_8_STA2A)
        F15EX_AIM_120C_7_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_7_STA2A)
        F15EX_AIM_120C_5_STA2A = (3, F15EXWeapons.F15EX_AIM_120C_5_STA2A)
        F15EX_AIM_120D_3_STA2A = (3, F15EXWeapons.F15EX_AIM_120D_3_STA2A)
        F15EX_AIM_120D_STA2A = (3, F15EXWeapons.F15EX_AIM_120D_STA2A)
        F15EX_AIM_260A_STA2A = (3, F15EXWeapons.F15EX_AIM_260A_STA2A)
        F15EX_PYTHON_5_STA2A = (3, F15EXWeapons.F15EX_PYTHON_5_STA2A)
        F15EX_AIM_9X_ED_STA2A = (3, F15EXWeapons.F15EX_AIM_9X_ED_STA2A)

    class Pylon4:
        F15EX_AIM_120C_8_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_8_STA2B)
        F15EX_AIM_120C_7_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_7_STA2B)
        F15EX_AIM_120C_5_STA2B = (4, F15EXWeapons.F15EX_AIM_120C_5_STA2B)
        F15EX_AIM_120D_3_STA2B = (4, F15EXWeapons.F15EX_AIM_120D_3_STA2B)
        F15EX_AIM_120D_STA2B = (4, F15EXWeapons.F15EX_AIM_120D_STA2B)
        F15EX_AIM_260A_STA2B = (4, F15EXWeapons.F15EX_AIM_260A_STA2B)
        F15EX_PYTHON_5_STA2B = (4, F15EXWeapons.F15EX_PYTHON_5_STA2B)
        F15EX_AIM_9X_ED_STA2B = (4, F15EXWeapons.F15EX_AIM_9X_ED_STA2B)

    class Pylon5:
        AMBER_2xAIM120C8 = (5, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (5, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (5, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (5, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (5, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (5, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_F = (5, F15EXWeapons.F15EX_AIM_120C_8_CFT_F)
        F15EX_AIM_120C_7_CFT_F = (5, F15EXWeapons.F15EX_AIM_120C_7_CFT_F)
        F15EX_AIM_120C_5_CFT_F = (5, F15EXWeapons.F15EX_AIM_120C_5_CFT_F)
        F15EX_AIM_120D_3_CFT_F = (5, F15EXWeapons.F15EX_AIM_120D_3_CFT_F)
        F15EX_AIM_120D_CFT_F = (5, F15EXWeapons.F15EX_AIM_120D_CFT_F)
        F15EX_AIM_260A_CFT_F = (5, F15EXWeapons.F15EX_AIM_260A_CFT_F)
        F15EX_AIM_200A_CFT_F = (5, F15EXWeapons.F15EX_AIM_200A_CFT_F)
        AIM200_4XRACK = (5, F15EXWeapons.AIM200_4XRACK)
        AIM200_X3_F_15EX = (5, F15EXWeapons.AIM200_X3_F_15EX)
        F15EX_AIM_174B_CFT = (5, F15EXWeapons.F15EX_AIM_174B_CFT)

    class Pylon6:
        AMBER_2xAIM120C8 = (6, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (6, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (6, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (6, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (6, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (6, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_A = (6, F15EXWeapons.F15EX_AIM_120C_8_CFT_A)
        F15EX_AIM_120C_7_CFT_A = (6, F15EXWeapons.F15EX_AIM_120C_7_CFT_A)
        F15EX_AIM_120C_5_CFT_A = (6, F15EXWeapons.F15EX_AIM_120C_5_CFT_A)
        F15EX_AIM_120D_3_CFT_A = (6, F15EXWeapons.F15EX_AIM_120D_3_CFT_A)
        F15EX_AIM_120D_CFT_A = (6, F15EXWeapons.F15EX_AIM_120D_CFT_A)
        F15EX_AIM_260A_CFT_A = (6, F15EXWeapons.F15EX_AIM_260A_CFT_A)
        F15EX_AIM_200A_CFT_A = (6, F15EXWeapons.F15EX_AIM_200A_CFT_A)

    class Pylon7:
        AMBER_2xAIM120C8 = (7, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (7, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (7, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (7, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (7, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (7, F15EXWeapons.AMBER_2xAIM260A)
        AN_AAQ_28_LITENING___Targeting_Pod_ = (
            7,
            Weapons.AN_AAQ_28_LITENING___Targeting_Pod_,
        )
        AN_AAQ_14_LANTIRN_TGT_Pod = (7, Weapons.AN_AAQ_14_LANTIRN_TGT_Pod)

    class Pylon8:
        AMBER_2xAIM120C8 = (8, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (8, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (8, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (8, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (8, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (8, F15EXWeapons.AMBER_2xAIM260A)
        AIM200_4XRACK = (8, F15EXWeapons.AIM200_4XRACK)
        Fuel_tank_610_gal_ = (8, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (8, Weapons.Fuel_tank_610_gal__Empty_)
        ASG_34_LegionPod = (8, F15EXWeapons.ASG_34_LegionPod)

    class Pylon9:
        AMBER_2xAIM120C8 = (9, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (9, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (9, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (9, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (9, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (9, F15EXWeapons.AMBER_2xAIM260A)
        AN_AAQ_13_LANTIRN_NAV_POD = (9, Weapons.AN_AAQ_13_LANTIRN_NAV_POD)

    class Pylon10:
        AMBER_2xAIM120C8 = (10, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (10, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (10, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (10, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (10, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (10, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_A = (10, F15EXWeapons.F15EX_AIM_120C_8_CFT_A)
        F15EX_AIM_120C_7_CFT_A = (10, F15EXWeapons.F15EX_AIM_120C_7_CFT_A)
        F15EX_AIM_120C_5_CFT_A = (10, F15EXWeapons.F15EX_AIM_120C_5_CFT_A)
        F15EX_AIM_120D_3_CFT_A = (10, F15EXWeapons.F15EX_AIM_120D_3_CFT_A)
        F15EX_AIM_120D_CFT_A = (10, F15EXWeapons.F15EX_AIM_120D_CFT_A)
        F15EX_AIM_260A_CFT_A = (10, F15EXWeapons.F15EX_AIM_260A_CFT_A)
        F15EX_AIM_200A_CFT_A = (10, F15EXWeapons.F15EX_AIM_200A_CFT_A)

    class Pylon11:
        AMBER_2xAIM120C8 = (11, F15EXWeapons.AMBER_2xAIM120C8)
        AMBER_2xAIM120C7 = (11, F15EXWeapons.AMBER_2xAIM120C7)
        AMBER_2xAIM120C5 = (11, F15EXWeapons.AMBER_2xAIM120C5)
        AMBER_2xAIM120D = (11, F15EXWeapons.AMBER_2xAIM120D)
        AMBER_2xAIM120D_P3I = (11, F15EXWeapons.AMBER_2xAIM120D_P3I)
        AMBER_2xAIM260A = (11, F15EXWeapons.AMBER_2xAIM260A)
        F15EX_AIM_120C_8_CFT_F = (11, F15EXWeapons.F15EX_AIM_120C_8_CFT_F)
        F15EX_AIM_120C_7_CFT_F = (11, F15EXWeapons.F15EX_AIM_120C_7_CFT_F)
        F15EX_AIM_120C_5_CFT_F = (11, F15EXWeapons.F15EX_AIM_120C_5_CFT_F)
        F15EX_AIM_120D_3_CFT_F = (11, F15EXWeapons.F15EX_AIM_120D_3_CFT_F)
        F15EX_AIM_120D_CFT_F = (11, F15EXWeapons.F15EX_AIM_120D_CFT_F)
        F15EX_AIM_260A_CFT_F = (11, F15EXWeapons.F15EX_AIM_260A_CFT_F)
        F15EX_AIM_200A_CFT_F = (11, F15EXWeapons.F15EX_AIM_200A_CFT_F)
        AIM200_4XRACK = (11, F15EXWeapons.AIM200_4XRACK)
        AIM200_X3_F_15EX = (11, F15EXWeapons.AIM200_X3_F_15EX)
        F15EX_AIM_174B_CFT = (11, F15EXWeapons.F15EX_AIM_174B_CFT)

    class Pylon12:
        F15EX_AIM_120C_8_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_8_STA11B)
        F15EX_AIM_120C_7_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_7_STA11B)
        F15EX_AIM_120C_5_STA11B = (12, F15EXWeapons.F15EX_AIM_120C_5_STA11B)
        F15EX_AIM_120D_3_STA11B = (12, F15EXWeapons.F15EX_AIM_120D_3_STA11B)
        F15EX_AIM_120D_STA11B = (12, F15EXWeapons.F15EX_AIM_120D_STA11B)
        F15EX_AIM_260A_STA11B = (12, F15EXWeapons.F15EX_AIM_260A_STA11B)
        F15EX_PYTHON_5_STA11B = (12, F15EXWeapons.F15EX_PYTHON_5_STA11B)
        F15EX_AIM_9X_ED_STA11B = (12, F15EXWeapons.F15EX_AIM_9X_ED_STA11B)

    class Pylon13:
        F15EX_AIM_120C_8_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_8_STA11A)
        F15EX_AIM_120C_7_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_7_STA11A)
        F15EX_AIM_120C_5_STA11A = (13, F15EXWeapons.F15EX_AIM_120C_5_STA11A)
        F15EX_AIM_120D_3_STA11A = (13, F15EXWeapons.F15EX_AIM_120D_3_STA11A)
        F15EX_AIM_120D_STA11A = (13, F15EXWeapons.F15EX_AIM_120D_STA11A)
        F15EX_AIM_260A_STA11A = (13, F15EXWeapons.F15EX_AIM_260A_STA11A)
        F15EX_PYTHON_5_STA11A = (13, F15EXWeapons.F15EX_PYTHON_5_STA11A)
        F15EX_AIM_9X_ED_STA11A = (13, F15EXWeapons.F15EX_AIM_9X_ED_STA11A)

    class Pylon14:
        Fuel_tank_610_gal_ = (14, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (14, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120C_8 = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_8)
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            14,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2xAIM_120D = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120D)
        F15EX_LAU_115_2xAIM_120C_5 = (14, F15EXWeapons.F15EX_LAU_115_2xAIM_120C_5)
        AIM200_4XRACK = (14, F15EXWeapons.AIM200_4XRACK)
        F15EX_AIM_174B = (14, F15EXWeapons.F15EX_AIM_174B)

    class Pylon15:
        F15IA_PYTHON_5 = (15, F15EXWeapons.F15IA_PYTHON_5)
        F15EX_2xAIM_260A = (15, F15EXWeapons.F15EX_2xAIM_260A)
        F15EX_2xAIM_120D_3 = (15, F15EXWeapons.F15EX_2xAIM_120D_3)
        F15EX_2xAIM_120D = (15, F15EXWeapons.F15EX_2xAIM_120D)
        F15EX_2xAIM_120C_8 = (15, F15EXWeapons.F15EX_2xAIM_120C_8)
        F15EX_2xAIM_120C_7 = (15, F15EXWeapons.F15EX_2xAIM_120C_7)
        F15EX_2xAIM_120C_5 = (15, F15EXWeapons.F15EX_2xAIM_120C_5)

    pylons: Set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}

    tasks = [
        task.CAP,
        task.Escort,
        task.FighterSweep,
        task.Intercept,
        task.Reconnaissance,
        task.GroundAttack,
        task.CAS,
        task.SEAD,
        task.RunwayAttack,
        task.AntishipStrike,
    ]
    task_default = task.CAP
