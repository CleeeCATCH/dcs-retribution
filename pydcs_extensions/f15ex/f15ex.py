"""F-15EX Eagle II (v2.33 by Spino, with the F15EX_FM EFM), with and without CFTs.

The mod registers two AI/flyable types, "F15EX" and "F15EX_CFT", which differ in
fuel load and in the fuselage stations: the plain jet has AMRAAM tandem rails on
FUS-L/FUS-R, while the CFT build carries conformal stores (bomb rows, AMRAAM and
AIM-200 racks) on LCFT/RCFT. The mod's third type, the F-15IA, is not covered.
Fuel figures follow the EFM build's F15EX.lua and F15EX_CFT.lua.

Pylon tables are generated from those two files. Stores the mod defines itself
are declared below from their CLSIDs: the AMRAAM racks in
Weapons/Loadouts/SP_AIM120C.lua carry the mod's own names and weights, the rest
are named from the pylon comments with estimated weights, which only affect what
Retribution displays -- DCS takes the real values from the mod. {MSM} is listed
on the mod's pylons but left out here: Weapons/Loadout.lua does not load
F15_MSM.lua, so DCS has no such store.
A few stores the mod shares with other mods (the F-22A EFM LAU-115 twin rails, the
Ukraine pack's MALD and JDAM-ER, the A-7E's BRU-41A) are referenced from the
extensions that already declare them.
"""

from typing import Set

from dcs import task
from dcs.planes import PlaneType
from dcs.weapons_data import Weapons

from game.modsupport import planemod
from pydcs_extensions.a7e.a7e import WeaponsA7E
from pydcs_extensions.f22a_efm.f22a_efm import F22AEFMWeapons
from pydcs_extensions.ukrainemilitaryassetspack.ukrainemilitaryassetspack import (
    WeaponsUKR,
)
from pydcs_extensions.weapon_injector import inject_weapons


class F15EXWeapons:
    F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail = {
        "clsid": "{F15EX_2xAIM-120C-5}",
        "name": "2 x AIM-120C AMRAAM - Active Radar AAM",
        "weight": 162.40 * 2 + 50,
    }
    F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail = {
        "clsid": "{F15EX_2xAIM-120C-7}",
        "name": "2 x AIM-120C-7 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 334,
    }
    F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail = {
        "clsid": "{F15EX_2xAIM-120C-8}",
        "name": "2 x AIM-120C-8 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 334,
    }
    F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail = {
        "clsid": "{F15EX_2xAIM-120D-3}",
        "name": "2 x AIM-120D-3 AMRAAM - Active Radar AAM (Outer Rail)",
        "weight": 334,
    }
    F15EX_2_x_AIM_260A_JATM_Outer_Rail = {
        "clsid": "{F15EX_2xAIM-260A}",
        "name": "2 x AIM-260A JATM - Active Radar AAM (Outer Rail)",
        "weight": 330,
    }
    F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail = {
        "clsid": "{F-15EX_AIM-9X_O}",
        "name": "2 x AIM-9X Sidewinder IR AAM (Outer Rail)",
        "weight": 180,
    }
    F15EX_AGM_88F_HCSM_Outer_Rail = {
        "clsid": "{AGM-88F_F15EX}",
        "name": "AGM-88F HCSM - Anti-Radiation AGM (Outer Rail)",
        "weight": 361,
    }
    F15EX_AGM_88G_AARGM_ER_Outer_Rail = {
        "clsid": "{AGM88G_F-15EX}",
        "name": "AGM-88G AARGM-ER - Anti-Radiation AGM (Outer Rail)",
        "weight": 411,
    }
    F15EX_2_x_Mako_A2G_Outer_Rail = {
        "clsid": "{F-15EX_MAKO_A2G_C}",
        "name": "2 x Mako Multi-Mission Hypersonic Missile - Anti-Radiation AGM (Outer Rail)",
        "weight": 1150,
    }
    F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Outboard = {
        "clsid": "{F-15EX_AIM-120C5_IN_O}",
        "name": "2 x AIM-120C AMRAAM - Active Radar AAM",
        "weight": 162.40 * 2,
    }
    F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Outboard = {
        "clsid": "{F-15EX_AIM-120C7_IN_O}",
        "name": "2 x AIM-120C-7 AMRAAM - Active Radar AAM (Stations 3/11)",
        "weight": 323,
    }
    F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Outboard = {
        "clsid": "{F-15EX_AIM-120C8_IN_O}",
        "name": "2 x AIM-120C-8 AMRAAM - Active Radar AAM (Stations 3/11)",
        "weight": 323,
    }
    F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Outboard = {
        "clsid": "{F-15EX_AIM-120D3_IN_O}",
        "name": "2 x AIM-120D-3 AMRAAM - Active Radar AAM (Stations 3/11)",
        "weight": 324,
    }
    F15EX_2_x_AIM_260A_JATM_Shoulder_Outboard = {
        "clsid": "{F-15EX_AIM-260A_IN_O}",
        "name": "2 x AIM-260A JATM - Active Radar AAM (Stations 3/11)",
        "weight": 320,
    }
    F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Outboard = {
        "clsid": "{F-15EX_AIM-9X_IN_O}",
        "name": "2 x AIM-9X Sidewinder IR AAM (Stations 3/11)",
        "weight": 170,
    }
    F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Inboard = {
        "clsid": "{F-15EX_AIM-120C5_IN}",
        "name": "2 x AIM-120C AMRAAM - Active Radar AAM",
        "weight": 162.40 * 2,
    }
    F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Inboard = {
        "clsid": "{F-15EX_AIM-120C7_IN}",
        "name": "2 x AIM-120C-7 AMRAAM - Active Radar AAM (Stations 4/10)",
        "weight": 323,
    }
    F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Inboard = {
        "clsid": "{F-15EX_AIM-120C8_IN}",
        "name": "2 x AIM-120C-8 AMRAAM - Active Radar AAM (Stations 4/10)",
        "weight": 323,
    }
    F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Inboard = {
        "clsid": "{F-15EX_AIM-120D3_IN}",
        "name": "2 x AIM-120D-3 AMRAAM - Active Radar AAM (Stations 4/10)",
        "weight": 324,
    }
    F15EX_2_x_AIM_260A_JATM_Shoulder_Inboard = {
        "clsid": "{F-15EX_AIM-260A_IN}",
        "name": "2 x AIM-260A JATM - Active Radar AAM (Stations 4/10)",
        "weight": 320,
    }
    F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Inboard = {
        "clsid": "{F-15EX_AIM-9X_IN}",
        "name": "2 x AIM-9X Sidewinder IR AAM (Stations 4/10)",
        "weight": 170,
    }
    F15EX_2_x_AIM_120C_AMRAAM_Tandem_Left = {
        "clsid": "{F-15EX_AIM120C_TANDEM_L}",
        "name": "2 x AIM-120C AMRAAM - Active Radar AAM",
        "weight": 162.40 * 2,
    }
    F15EX_2_x_AIM_120C_AMRAAM_Tandem_Right = {
        "clsid": "{F-15EX_AIM120C_TANDEM_R}",
        "name": "2 x AIM-120C AMRAAM - Active Radar AAM",
        "weight": 162.40 * 2,
    }
    F15EX_2_x_AIM_120C_AMRAAM_CFT = {
        "clsid": "{F-15EX_AIM120C_CFT}",
        "name": "2 x AIM-120C AMRAAM - Active Radar AAM",
        "weight": 162.40 * 2,
    }
    F15EX_2_x_AIM_200A_Peregrine_Tandem = {
        "clsid": "{F-15EX_AIM200_TANDEM}",
        "name": "2 x AIM-200A Peregrine Active Radar AAM (Tandem)",
        "weight": 323,
    }
    F15EX_3_x_AIM_200A_Peregrine = {
        "clsid": "{AIM200_X3_F-15EX}",
        "name": "3 x AIM-200A Peregrine Active Radar AAM",
        "weight": 510,
    }
    F15EX_4_x_AIM_200A_Peregrine = {
        "clsid": "{AIM200-4XRACK}",
        "name": "4 x AIM-200A Peregrine Active Radar AAM",
        "weight": 696,
    }
    F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM = {
        "clsid": "{F15EX_LAU_115_2xAIM-120C-8}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120C-8 AMRAAM - Active Radar AAM",
        "weight": 372.96,
    }
    F15EX_AGM_88F_HCSM = {
        "clsid": "{harmF-15ex}",
        "name": "AGM-88F HCSM - Anti-Radiation AGM",
        "weight": 361,
    }
    F15EX_AGM_88G_AARGM_ER = {
        "clsid": "{aargm_er}",
        "name": "AGM-88G AARGM-ER - Anti-Radiation AGM",
        "weight": 411,
    }
    F15EX_AGM_183A_ARRW = {
        "clsid": "{AGM183A}",
        "name": "AGM-183A ARRW - Hypersonic Strike Missile",
        "weight": 2268,
    }
    F15EX_AGM_158B_JASSM_ER = {
        "clsid": "{B21_AGM-158B}",
        "name": "AGM-158B JASSM-ER ALCM",
        "weight": 1021,
    }
    F15EX_AGM_158C_LRASM = {
        "clsid": "{B21_AGM-158C}",
        "name": "AGM-158C LRASM AShM",
        "weight": 1100,
    }
    F15EX_Mako_A2G = {
        "clsid": "{MAKO_A2G_C}",
        "name": "Mako Multi-Mission Hypersonic Missile - Anti-Radiation AGM",
        "weight": 575,
    }
    F15EX_BRU_57_2_x_Mako_A2G = {
        "clsid": "{BRU_57_MAKO_A2G_C}",
        "name": "BRU-57 with 2 x Mako Multi-Mission Hypersonic Missile - Anti-Radiation AGM",
        "weight": 1230,
    }
    F15EX_APKWS_II_M151_x21 = {
        "clsid": "{APKWS_II_IRx21}",
        "name": "BRU-42 with 3 x LAU-131 - 21 x APKWS II M151 HE",
        "weight": 485,
    }
    F15EX_APKWS_II_M282_x21 = {
        "clsid": "{APKWS_II_IR_x21}",
        "name": "BRU-42 with 3 x LAU-131 - 21 x APKWS II M282 MPP",
        "weight": 510,
    }
    F15EX_AN_ASG_34_Legion_Pod = {
        "clsid": "{ASG-34_LegionPod}",
        "name": "AN/ASG-34 Legion Pod - IRST",
        "weight": 240,
    }


inject_weapons(F15EXWeapons)


@planemod
class F_15EX(PlaneType):
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
        F15EX_2_x_AIM_260A_JATM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Outer_Rail,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail,
        )
        F15EX_AGM_88F_HCSM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_AGM_88F_HCSM_Outer_Rail,
        )
        F15EX_AGM_88G_AARGM_ER_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_AGM_88G_AARGM_ER_Outer_Rail,
        )
        F15EX_2_x_Mako_A2G_Outer_Rail = (1, F15EXWeapons.F15EX_2_x_Mako_A2G_Outer_Rail)

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
        F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM = (
            2,
            F15EXWeapons.F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_2_LAU_127_AIM_120C = (2, Weapons.LAU_115_2_LAU_127_AIM_120C)
        F15EX_4_x_AIM_200A_Peregrine = (2, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            2,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        F15EX_APKWS_II_M151_x21 = (2, F15EXWeapons.F15EX_APKWS_II_M151_x21)
        F15EX_APKWS_II_M282_x21 = (2, F15EXWeapons.F15EX_APKWS_II_M282_x21)
        F15EX_AGM_88F_HCSM = (2, F15EXWeapons.F15EX_AGM_88F_HCSM)
        F15EX_AGM_88G_AARGM_ER = (2, F15EXWeapons.F15EX_AGM_88G_AARGM_ER)
        F15EX_AGM_158B_JASSM_ER = (2, F15EXWeapons.F15EX_AGM_158B_JASSM_ER)
        F15EX_AGM_158C_LRASM = (2, F15EXWeapons.F15EX_AGM_158C_LRASM)
        F15EX_AGM_183A_ARRW = (2, F15EXWeapons.F15EX_AGM_183A_ARRW)
        AGM_84H_SLAM_ER__Expanded_Response_ = (
            2,
            Weapons.AGM_84H_SLAM_ER__Expanded_Response_,
        )
        AGM_88C_HARM___High_Speed_Anti_Radiation_Missile_ = (
            2,
            Weapons.AGM_88C_HARM___High_Speed_Anti_Radiation_Missile_,
        )
        F15EX_Mako_A2G = (2, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_BRU_57_2_x_Mako_A2G = (2, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        AGM_154A___JSOW_CEB__CBU_type_ = (2, Weapons.AGM_154A___JSOW_CEB__CBU_type_)
        BRU_57_with_2_x_AGM_154A___JSOW_CEB__CBU_type_ = (
            2,
            Weapons.BRU_57_with_2_x_AGM_154A___JSOW_CEB__CBU_type_,
        )
        AGM_154B___JSOW_Anti_Armour = (2, Weapons.AGM_154B___JSOW_Anti_Armour)
        BRU_57_with_2_x_AGM_154B___JSOW_Anti_Armour = (
            2,
            Weapons.BRU_57_with_2_x_AGM_154B___JSOW_Anti_Armour,
        )
        AGM_154C___JSOW_Unitary_BROACH = (2, Weapons.AGM_154C___JSOW_Unitary_BROACH)
        BRU_55_with_2_x_AGM_154C___JSOW_Unitary_BROACH = (
            2,
            Weapons.BRU_55_with_2_x_AGM_154C___JSOW_Unitary_BROACH,
        )
        ADM_160B_MALD___Miniature_Air_Launched_Decoy = (
            2,
            WeaponsUKR.ADM_160B_MALD___Miniature_Air_Launched_Decoy,
        )
        JDAM_ER___450_kg_GPS_Guided_Mk_83_GP_bomb = (
            2,
            WeaponsUKR.JDAM_ER___450_kg_GPS_Guided_Mk_83_GP_bomb,
        )
        BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD = (
            2,
            Weapons.BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            2,
            Weapons.BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD = (
            2,
            Weapons.BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD,
        )
        BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            2,
            Weapons.BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        Mk_84___2000lb_GP_Bomb_LD = (2, Weapons.Mk_84___2000lb_GP_Bomb_LD)
        Mk_82___500lb_GP_Bomb_LD = (2, Weapons.Mk_82___500lb_GP_Bomb_LD)
        BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            2,
            Weapons.BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            2,
            Weapons.BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        _6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_ = (
            2,
            Weapons._6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_,
        )
        BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD = (
            2,
            WeaponsA7E.BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD = (
            2,
            Weapons.BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD,
        )

    class Pylon3:
        F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_260A_JATM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Outboard,
        )

    class Pylon4:
        F15EX_2_x_AIM_120C_AMRAAM_Tandem_Left = (
            4,
            F15EXWeapons.F15EX_2_x_AIM_120C_AMRAAM_Tandem_Left,
        )
        F15EX_2_x_AIM_200A_Peregrine_Tandem = (
            4,
            F15EXWeapons.F15EX_2_x_AIM_200A_Peregrine_Tandem,
        )

    class Pylon5:
        AN_AAQ_28_LITENING___Targeting_Pod_ = (
            5,
            Weapons.AN_AAQ_28_LITENING___Targeting_Pod_,
        )
        AN_AAQ_33___Advanced_Targeting_Pod = (
            5,
            Weapons.AN_AAQ_33___Advanced_Targeting_Pod,
        )
        AN_AAQ_14_LANTIRN_TGT_Pod = (5, Weapons.AN_AAQ_14_LANTIRN_TGT_Pod)

    class Pylon6:
        F15EX_4_x_AIM_200A_Peregrine = (6, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        F15EX_Mako_A2G = (6, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_AGM_183A_ARRW = (6, F15EXWeapons.F15EX_AGM_183A_ARRW)
        F15EX_BRU_57_2_x_Mako_A2G = (6, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        Fuel_tank_610_gal_ = (6, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (6, Weapons.Fuel_tank_610_gal__Empty_)
        F15EX_AN_ASG_34_Legion_Pod = (6, F15EXWeapons.F15EX_AN_ASG_34_Legion_Pod)
        AN_AAQ_33___Advanced_Targeting_Pod = (
            6,
            Weapons.AN_AAQ_33___Advanced_Targeting_Pod,
        )

    class Pylon7:
        AN_AAQ_13_LANTIRN_NAV_POD = (7, Weapons.AN_AAQ_13_LANTIRN_NAV_POD)

    class Pylon8:
        F15EX_2_x_AIM_120C_AMRAAM_Tandem_Right = (
            8,
            F15EXWeapons.F15EX_2_x_AIM_120C_AMRAAM_Tandem_Right,
        )
        F15EX_2_x_AIM_200A_Peregrine_Tandem = (
            8,
            F15EXWeapons.F15EX_2_x_AIM_200A_Peregrine_Tandem,
        )

    class Pylon9:
        F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_260A_JATM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Inboard,
        )

    class Pylon10:
        Fuel_tank_610_gal_ = (10, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (10, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM = (
            10,
            F15EXWeapons.F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_2_LAU_127_AIM_120C = (10, Weapons.LAU_115_2_LAU_127_AIM_120C)
        F15EX_4_x_AIM_200A_Peregrine = (10, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            10,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        F15EX_APKWS_II_M151_x21 = (10, F15EXWeapons.F15EX_APKWS_II_M151_x21)
        F15EX_APKWS_II_M282_x21 = (10, F15EXWeapons.F15EX_APKWS_II_M282_x21)
        F15EX_AGM_88F_HCSM = (10, F15EXWeapons.F15EX_AGM_88F_HCSM)
        F15EX_AGM_88G_AARGM_ER = (10, F15EXWeapons.F15EX_AGM_88G_AARGM_ER)
        F15EX_AGM_183A_ARRW = (10, F15EXWeapons.F15EX_AGM_183A_ARRW)
        AGM_88C_HARM___High_Speed_Anti_Radiation_Missile_ = (
            10,
            Weapons.AGM_88C_HARM___High_Speed_Anti_Radiation_Missile_,
        )
        F15EX_Mako_A2G = (10, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_BRU_57_2_x_Mako_A2G = (10, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD = (
            10,
            Weapons.BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            10,
            Weapons.BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD = (
            10,
            Weapons.BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD,
        )
        BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            10,
            Weapons.BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        Mk_84___2000lb_GP_Bomb_LD = (10, Weapons.Mk_84___2000lb_GP_Bomb_LD)
        Mk_82___500lb_GP_Bomb_LD = (10, Weapons.Mk_82___500lb_GP_Bomb_LD)
        BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            10,
            Weapons.BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            10,
            Weapons.BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        _6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_ = (
            10,
            Weapons._6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_,
        )
        BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD = (
            10,
            WeaponsA7E.BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD = (
            10,
            Weapons.BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD,
        )

    class Pylon11:
        F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail,
        )
        F15EX_2_x_AIM_260A_JATM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Outer_Rail,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail,
        )
        F15EX_AGM_88F_HCSM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_AGM_88F_HCSM_Outer_Rail,
        )
        F15EX_AGM_88G_AARGM_ER_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_AGM_88G_AARGM_ER_Outer_Rail,
        )
        F15EX_2_x_Mako_A2G_Outer_Rail = (11, F15EXWeapons.F15EX_2_x_Mako_A2G_Outer_Rail)

    pylons: Set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

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
        F15EX_2_x_AIM_260A_JATM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Outer_Rail,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail,
        )
        F15EX_AGM_88F_HCSM_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_AGM_88F_HCSM_Outer_Rail,
        )
        F15EX_AGM_88G_AARGM_ER_Outer_Rail = (
            1,
            F15EXWeapons.F15EX_AGM_88G_AARGM_ER_Outer_Rail,
        )
        F15EX_2_x_Mako_A2G_Outer_Rail = (1, F15EXWeapons.F15EX_2_x_Mako_A2G_Outer_Rail)

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
        F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM = (
            2,
            F15EXWeapons.F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_2_LAU_127_AIM_120C = (2, Weapons.LAU_115_2_LAU_127_AIM_120C)
        F15EX_4_x_AIM_200A_Peregrine = (2, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            2,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        F15EX_APKWS_II_M151_x21 = (2, F15EXWeapons.F15EX_APKWS_II_M151_x21)
        F15EX_APKWS_II_M282_x21 = (2, F15EXWeapons.F15EX_APKWS_II_M282_x21)
        F15EX_AGM_88F_HCSM = (2, F15EXWeapons.F15EX_AGM_88F_HCSM)
        F15EX_AGM_88G_AARGM_ER = (2, F15EXWeapons.F15EX_AGM_88G_AARGM_ER)
        F15EX_AGM_183A_ARRW = (2, F15EXWeapons.F15EX_AGM_183A_ARRW)
        AGM_88C_HARM___High_Speed_Anti_Radiation_Missile_ = (
            2,
            Weapons.AGM_88C_HARM___High_Speed_Anti_Radiation_Missile_,
        )
        F15EX_Mako_A2G = (2, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_BRU_57_2_x_Mako_A2G = (2, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD = (
            2,
            Weapons.BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            2,
            Weapons.BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD = (
            2,
            Weapons.BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD,
        )
        BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            2,
            Weapons.BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        Mk_84___2000lb_GP_Bomb_LD = (2, Weapons.Mk_84___2000lb_GP_Bomb_LD)
        Mk_82___500lb_GP_Bomb_LD = (2, Weapons.Mk_82___500lb_GP_Bomb_LD)
        BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            2,
            Weapons.BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            2,
            Weapons.BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        _6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_ = (
            2,
            Weapons._6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_,
        )
        BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD = (
            2,
            WeaponsA7E.BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD = (
            2,
            Weapons.BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD,
        )

    class Pylon3:
        F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_260A_JATM_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Shoulder_Outboard,
        )
        F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Outboard = (
            3,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Outboard,
        )

    class Pylon4:
        F15EX_4_x_AIM_200A_Peregrine = (4, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        F15EX_3_x_AIM_200A_Peregrine = (4, F15EXWeapons.F15EX_3_x_AIM_200A_Peregrine)
        F15EX_2_x_AIM_120C_AMRAAM_CFT = (4, F15EXWeapons.F15EX_2_x_AIM_120C_AMRAAM_CFT)
        F15EX_2_x_AIM_200A_Peregrine_Tandem = (
            4,
            F15EXWeapons.F15EX_2_x_AIM_200A_Peregrine_Tandem,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            4,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        F15EX_Mako_A2G = (4, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_BRU_57_2_x_Mako_A2G = (4, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        BLU_107___6 = (4, Weapons.BLU_107___6)
        CBU_87___6 = (4, Weapons.CBU_87___6)
        CBU_97___6 = (4, Weapons.CBU_97___6)
        Mk_20_Rockeye___6 = (4, Weapons.Mk_20_Rockeye___6)
        Mk_82_AIR___6 = (4, Weapons.Mk_82_AIR___6)
        Mk_82___6 = (4, Weapons.Mk_82___6)

    class Pylon5:
        AN_AAQ_28_LITENING___Targeting_Pod_ = (
            5,
            Weapons.AN_AAQ_28_LITENING___Targeting_Pod_,
        )
        AN_AAQ_33___Advanced_Targeting_Pod = (
            5,
            Weapons.AN_AAQ_33___Advanced_Targeting_Pod,
        )
        AN_AAQ_14_LANTIRN_TGT_Pod = (5, Weapons.AN_AAQ_14_LANTIRN_TGT_Pod)

    class Pylon6:
        F15EX_4_x_AIM_200A_Peregrine = (6, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        F15EX_Mako_A2G = (6, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_AGM_183A_ARRW = (6, F15EXWeapons.F15EX_AGM_183A_ARRW)
        F15EX_BRU_57_2_x_Mako_A2G = (6, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        Fuel_tank_610_gal_ = (6, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (6, Weapons.Fuel_tank_610_gal__Empty_)
        F15EX_AN_ASG_34_Legion_Pod = (6, F15EXWeapons.F15EX_AN_ASG_34_Legion_Pod)

    class Pylon7:
        AN_AAQ_13_LANTIRN_NAV_POD = (7, Weapons.AN_AAQ_13_LANTIRN_NAV_POD)

    class Pylon8:
        F15EX_4_x_AIM_200A_Peregrine = (8, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        F15EX_3_x_AIM_200A_Peregrine = (8, F15EXWeapons.F15EX_3_x_AIM_200A_Peregrine)
        F15EX_2_x_AIM_120C_AMRAAM_CFT = (8, F15EXWeapons.F15EX_2_x_AIM_120C_AMRAAM_CFT)
        F15EX_2_x_AIM_200A_Peregrine_Tandem = (
            8,
            F15EXWeapons.F15EX_2_x_AIM_200A_Peregrine_Tandem,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            8,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        F15EX_Mako_A2G = (8, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_BRU_57_2_x_Mako_A2G = (8, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        BLU_107___6_ = (8, Weapons.BLU_107___6_)
        CBU_87___6_ = (8, Weapons.CBU_87___6_)
        CBU_97___6_ = (8, Weapons.CBU_97___6_)
        Mk_20_Rockeye___6_ = (8, Weapons.Mk_20_Rockeye___6_)
        Mk_82_AIR___6_ = (8, Weapons.Mk_82_AIR___6_)
        Mk_82___6_ = (8, Weapons.Mk_82___6_)

    class Pylon9:
        F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_260A_JATM_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Shoulder_Inboard,
        )
        F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Inboard = (
            9,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Shoulder_Inboard,
        )

    class Pylon10:
        Fuel_tank_610_gal_ = (10, Weapons.Fuel_tank_610_gal_)
        Fuel_tank_610_gal__Empty_ = (10, Weapons.Fuel_tank_610_gal__Empty_)
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM = (
            10,
            F15EXWeapons.F15EX_LAU_115_2_x_AIM_120C_8_AMRAAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_2_LAU_127_AIM_120C = (10, Weapons.LAU_115_2_LAU_127_AIM_120C)
        F15EX_4_x_AIM_200A_Peregrine = (10, F15EXWeapons.F15EX_4_x_AIM_200A_Peregrine)
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            10,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        F15EX_APKWS_II_M151_x21 = (10, F15EXWeapons.F15EX_APKWS_II_M151_x21)
        F15EX_APKWS_II_M282_x21 = (10, F15EXWeapons.F15EX_APKWS_II_M282_x21)
        F15EX_AGM_88F_HCSM = (10, F15EXWeapons.F15EX_AGM_88F_HCSM)
        F15EX_AGM_88G_AARGM_ER = (10, F15EXWeapons.F15EX_AGM_88G_AARGM_ER)
        F15EX_AGM_183A_ARRW = (10, F15EXWeapons.F15EX_AGM_183A_ARRW)
        F15EX_Mako_A2G = (10, F15EXWeapons.F15EX_Mako_A2G)
        F15EX_BRU_57_2_x_Mako_A2G = (10, F15EXWeapons.F15EX_BRU_57_2_x_Mako_A2G)
        BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD = (
            10,
            Weapons.BRU_42___3_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            10,
            Weapons.BRU_33_with_2_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD = (
            10,
            Weapons.BRU_42___3_x_Mk_82_AIR_Ballute___500lb_GP_Bomb_HD,
        )
        BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets = (
            10,
            Weapons.BRU_42___3_x_Mk_20_Rockeye___490lbs_CBU__247_x_HEAT_Bomblets,
        )
        Mk_84___2000lb_GP_Bomb_LD = (10, Weapons.Mk_84___2000lb_GP_Bomb_LD)
        Mk_82___500lb_GP_Bomb_LD = (10, Weapons.Mk_82___500lb_GP_Bomb_LD)
        BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            10,
            Weapons.BRU_42_3_x_LAU_68___7_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE = (
            10,
            Weapons.BRU_33_2_x_LAU_61___19_x_UnGd_Rkts__70_mm_Hydra_70_M151_HE,
        )
        _6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_ = (
            10,
            Weapons._6x_BLU_107_B_Durandal___219kg_Concrete_Piercing_Chute_Retarded_Bomb_w_Booster__MER_,
        )
        BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD = (
            10,
            WeaponsA7E.BRU_41A_with_6_x_Mk_82___500lb_GP_Bomb_LD,
        )
        BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD = (
            10,
            Weapons.BRU_33_with_2_x_Mk_83___1000lb_GP_Bomb_LD,
        )

    class Pylon11:
        F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_9X_Sidewinder_Outer_Rail,
        )
        F15EX_2_x_AIM_260A_JATM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_260A_JATM_Outer_Rail,
        )
        F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120D_3_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120C_8_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120C_7_AMRAAM_Outer_Rail,
        )
        F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_2_x_AIM_120C_5_AMRAAM_Outer_Rail,
        )
        F15EX_AGM_88F_HCSM_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_AGM_88F_HCSM_Outer_Rail,
        )
        F15EX_AGM_88G_AARGM_ER_Outer_Rail = (
            11,
            F15EXWeapons.F15EX_AGM_88G_AARGM_ER_Outer_Rail,
        )
        F15EX_2_x_Mako_A2G_Outer_Rail = (11, F15EXWeapons.F15EX_2_x_Mako_A2G_Outer_Rail)

    pylons: Set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

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
