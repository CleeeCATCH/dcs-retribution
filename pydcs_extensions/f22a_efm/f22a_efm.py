"""F-22A Raptor with the BHOOP/NIGHTSTORM "Enhancement Mod" weapon set.

This is the same DCS airframe as the stock Grinnelli F-22A that
pydcs_extensions.f22a describes, but the enhancement pack replaces the mod's
stores with a much larger set and renames most of the CLSIDs, so the two cannot
share a pylon table. `retribution_id` gives this one its own entry in
Retribution's registry and its own data file while `id` stays "F-22A" so
generated missions still name the real DCS type.

Weapon names and weights are taken from the mod's own declare_loadout calls in
Mods/aircraft/F-22A/Weapons/, and the pylon tables from its F-22A.lua.
"""

from typing import Any, Dict, Set

from dcs import task
from dcs.planes import PlaneType
from dcs.weapons_data import Weapons

from game.modsupport import planemod
from pydcs_extensions.weapon_injector import inject_weapons


class F22AEFMWeapons:
    AIM_9X_2_Sidewinder_IR_AAM = {
        "clsid": "{AIM-9X2}",
        "name": "AIM-9X-2 Sidewinder IR AAM",
        "weight": 84.46,
    }
    AIM_9X_3_Sidewinder_IR_AAM = {
        "clsid": "{AIM-9X3}",
        "name": "AIM-9X-3 Sidewinder IR AAM",
        "weight": 84.46,
    }
    AIM_2000_IRIS_T_IR_AAM = {
        "clsid": "{AIM-2000}",
        "name": "AIM-2000 IRIS-T IR AAM",
        "weight": 85.5,
    }
    V3E_A_Darter_IR_AAM = {
        "clsid": "{A-DARTER}",
        "name": "V3E A-Darter IR AAM",
        "weight": 85.5,
    }
    # Suffixed because stock pydcs already exposes `Python_5_IR_AAM` for the Gripen's
    # {JAS39_PYTHON-5}. Injecting under the bare name would have this module and
    # pydcs_extensions.jas39 overwrite each other depending on import order.
    Python_5_IR_AAM_F22 = {
        "clsid": "{PYTHON}",
        "name": "Python-5 IR AAM",
        "weight": 85.5,
    }
    AIM_74A_MUTANT_Active_Radar_AAM = {
        "clsid": "{AIM-74A}",
        "name": "AIM-74A MUTANT - Active Radar AAM",
        "weight": 165.0,
    }
    AIM_74B_MUTANT_Active_Radar_AAM = {
        "clsid": "{AIM-74B}",
        "name": "AIM-74B MUTANT - Active Radar AAM",
        "weight": 165.0,
    }
    AIM_272A_LRAAM_Active_Radar_AAM = {
        "clsid": "{AIM-272A}",
        "name": "AIM-272A LRAAM - Active Radar AAM",
        "weight": 165.0,
    }
    AIM_200A_Peregrine_Active_Radar_AAM = {
        "clsid": "{AIM-200A}",
        "name": "AIM-200A Peregrine Active Radar AAM",
        "weight": 161.48,
    }
    Fuel_tank_600_gal = {
        "clsid": "{600_Gallon}",
        "name": "Fuel tank 600 gal",
        "weight": 2045.8767,
    }
    Conformal_Fuel_tank_600_gal = {
        "clsid": "{Conformal_Tank}",
        "name": "Conformal Fuel tank 600 gal",
        "weight": 2045.8767,
    }
    LDTP_Fuel_tank_600_gal = {
        "clsid": "{LDTP_FUEL_Tank}",
        "name": "LDTP Fuel tank 600 gal",
        "weight": 2045.8767,
    }
    AGM_88G_AARGM_Anti_Radiation_AGM = {
        "clsid": "{LAU_118A_AGM-88G}",
        "name": "*AGM-88G AARGM* - Anti-Radiation AGM",
        "weight": 411,
    }
    _2_x_Mako_Multi_Mission_Hypersonic_Missile_Anti_Radiation_AGM = {
        "clsid": "{BRU_33A_2x_MAKO_A2G_C}",
        "name": "*2 x *Mako Multi-Mission Hypersonic Missile* - Anti-Radiation AGM",
        "weight": 1230,
    }
    LAU_115_with_2_x_LAU_127_AIM_9X_2_Sidewinder_IR_AAM = {
        "clsid": "{LAU_115_2xAIM-9X-2}",
        "name": "LAU-115 with 2 x LAU-127 AIM-9X-2 Sidewinder IR AAM",
        "weight": 218.92,
    }
    LAU_115_with_2_x_LAU_127_AIM_9X_3_Sidewinder_IR_AAM = {
        "clsid": "{LAU_115_2xAIM-9X-3}",
        "name": "LAU-115 with 2 x LAU-127 AIM-9X-3 Sidewinder IR AAM",
        "weight": 218.92,
    }
    LAU_115_with_2_x_LAU_127_AIM_2000_IRIS_T_IR_AAM = {
        "clsid": "{LAU_115_2xAIM-2000",
        "name": "LAU-115 with 2 x LAU-127 AIM-2000 IRIS-T - IR AAM",
        "weight": 221.0,
    }
    LAU_115_with_2_x_LAU_127_AIM_132_ASRAAM_IR_AAM = {
        "clsid": "{LAU_115_2xAIM-132",
        "name": "LAU-115 with 2 x LAU-127 AIM-132 ASRAAM - IR AAM",
        "weight": 221.0,
    }
    LAU_115_with_2_x_LAU_127_V3E_A_Darter_IR_AAM = {
        "clsid": "{LAU_115_2xA-DARTER}",
        "name": "LAU-115 with 2 x LAU-127 V3E A-Darter - IR AAM",
        "weight": 221.0,
    }
    LAU_115_with_2_x_LAU_127_Python_5_IR_AAM = {
        "clsid": "{LAU_115_2xPYTHON}",
        "name": "LAU-115 with 2 x LAU-127 Python-5 - IR AAM",
        "weight": 221.0,
    }
    LAU_115_with_2_x_LAU_127_MICA_NG_IR_AAM = {
        "clsid": "{LAU_115_2xMICA-IR}",
        "name": "LAU-115 with 2 x LAU-127 MICA NG - IR AAM",
        "weight": 221.0,
    }
    LAU_115_with_2_x_LAU_127_AIM_120C_6_AMRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-120C-6}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120C-6 AMRAAM - Active Radar AAM",
        "weight": 365.7,
    }
    LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-120C-7}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120C-7 AMRAAM - Active Radar AAM",
        "weight": 372.96,
    }
    LAU_115_with_2_x_LAU_127_AIM_120C_8_AMRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-120C-8}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120C-8 AMRAAM - Active Radar AAM",
        "weight": 372.96,
    }
    LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-120D-3}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120D-3 AMRAAM - Active Radar AAM",
        "weight": 380,
    }
    LAU_115_with_2_x_LAU_127_AIM_120E_AMRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-120E}",
        "name": "LAU-115 with 2 x LAU-127 AIM-120E AMRAAM - Active Radar AAM",
        "weight": 380,
    }
    LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-260A}",
        "name": "LAU-115 with 2 x LAU-127 AIM-260A JATM - Active Radar AAM",
        "weight": 370.0,
    }
    LAU_115_with_2_x_LAU_127_AIM_260B_JATM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-260B}",
        "name": "LAU-115 with 2 x LAU-127 AIM-260B JATM - Active Radar AAM",
        "weight": 370.0,
    }
    LAU_115_with_2_x_LAU_127_MICA_NG_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xMICA-RF}",
        "name": "LAU-115 with 2 x LAU-127 MICA NG - Active Radar AAM",
        "weight": 372.96,
    }
    LAU_115_with_2_x_LAU_127_AIM_74A_MUTANT_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-74A}",
        "name": "LAU-115 with 2 x LAU-127 AIM-74A MUTANT - Active Radar AAM",
        "weight": 380.0,
    }
    LAU_115_with_2_x_LAU_127_AIM_74B_MUTANT_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-74B}",
        "name": "LAU-115 with 2 x LAU-127 AIM-74B MUTANT - Active Radar AAM",
        "weight": 380.0,
    }
    LAU_115_with_2_x_LAU_127_AIM_272A_LRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xAIM-272A}",
        "name": "LAU-115 with 2 x LAU-127 AIM-272A LRAAM - Active Radar AAM",
        "weight": 380.0,
    }
    _2_x_Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = {
        "clsid": "{BRU_33A_2x_MAKO_A2A_C}",
        "name": "2 x Mako Multi-Mission Hypersonic Missile - Active Radar AAM",
        "weight": 370.0,
    }
    Meteor_BVRAAM_Active_Radar_AAM = {
        "clsid": "{LAU_118A_METR}",
        "name": "Meteor BVRAAM - Active Radar AAM",
        "weight": 210,
    }
    Meteor_BVRAAM_Active_Radar_AAM_ = {
        "clsid": "{LAU_118A_MDBA_METEOR}",
        "name": "Meteor BVRAAM - Active Radar AAM",
        "weight": 240,
    }
    LAU_115_with_2_x_LAU_127_MDBA_Meteor_Active_Radar_AAM = {
        "clsid": "{LAU_115_2xMETR}",
        "name": "LAU-115 with 2 x LAU-127 MDBA Meteor - Active Radar AAM",
        "weight": 430,
    }
    AIM_120C_6_AMRAAM_Active_Radar_AAM = {
        "clsid": "{AIM-120C-6}",
        "name": "AIM-120C-6 - AMRAAM - Active Radar AAM",
        "weight": 161.48,
    }
    AIM_120C_7_AMRAAM_Active_Radar_AAM = {
        "clsid": "{AIM-120C-7}",
        "name": "AIM-120C-7 - AMRAAM - Active Radar AAM",
        "weight": 161.48,
    }
    AIM_120C_8_AMRAAM_Active_Radar_AAM = {
        "clsid": "{AIM-120C-8}",
        "name": "AIM-120C-8 - AMRAAM - Active Radar AAM",
        "weight": 161.48,
    }
    AIM_120D_3_AMRAAM_Active_Radar_AAM = {
        "clsid": "{AIM-120D-3}",
        "name": "AIM-120D-3 - AMRAAM - Active Radar AAM",
        "weight": 165,
    }
    AIM_120E_AMRAAM_Active_Radar_AAM = {
        "clsid": "{AIM-120E}",
        "name": "AIM-120E - AMRAAM - Active Radar AAM",
        "weight": 165,
    }
    AIM_260A_JATM_Active_Radar_AAM = {
        "clsid": "{AIM-260A}",
        "name": "AIM-260A JATM - Active Radar AAM",
        "weight": 160.0,
    }
    Meteor_BVRAAM_Active_Rdr_AAM = {
        "clsid": "{JAS39_Meteor}",
        "name": "Meteor BVRAAM Active Rdr AAM",
        "weight": 191.0,
    }
    AIM_260B_JATM_Active_Radar_AAM = {
        "clsid": "{AIM-260B}",
        "name": "AIM-260B JATM - Active Radar AAM",
        "weight": 160.0,
    }
    _2_x_AIM_200A_Peregrine_Active_Radar_AAM = {
        "clsid": "{AIM200-2XRACK}",
        "name": "2 x AIM-200A Peregrine Active Radar AAM",
        "weight": 347.96,
    }
    MICA_NG_RF_Active_Radar_AAM = {
        "clsid": "{MICA-RF}",
        "name": "MICA NG RF - Active Radar AAM",
        "weight": 161.48,
    }
    Meteor_BVRAAM_Active_Radar_AAM__ = {
        "clsid": "{Meteor}",
        "name": "Meteor BVRAAM - Active Radar AAM",
        "weight": 160,
    }
    Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = {
        "clsid": "{MAKO_A2A_C}",
        "name": "Mako Multi-Mission Hypersonic Missile - Active Radar AAM",
        "weight": 160.0,
    }
    AIM_120C_6_AMRAAM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_120C_6_IRST_LEFT}",
        "name": "*AIM-120C-6 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    AIM_120C_7_AMRAAM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_120C_7_IRST_LEFT}",
        "name": "*AIM-120C-7 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    AIM_120C_8_AMRAAM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_120C_8_IRST_LEFT}",
        "name": "*AIM-120C-8 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    AIM_120D_3_AMRAAM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_120D_3_IRST_LEFT}",
        "name": "*AIM-120D-3 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 270,
    }
    AIM_120E_AMRAAM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_120E_IRST_LEFT}",
        "name": "*AIM-120E AMRAAM - Active Radar AAM + IRST POD",
        "weight": 270,
    }
    AIM_260A_JATM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_260A_IRST_LEFT}",
        "name": "*AIM-260A JATM - Active Radar AAM + IRST POD",
        "weight": 265.0,
    }
    AIM_260B_JATM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_260B_IRST_LEFT}",
        "name": "*AIM-260B JATM - Active Radar AAM + IRST POD",
        "weight": 265.0,
    }
    AIM_272A_LRAAM_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM_272A_IRST_LEFT}",
        "name": "*AIM-272A LRAAM - Active Radar AAM + IRST POD",
        "weight": 270.0,
    }
    MICA_NG_RF_Active_Radar_AAM_IRST_POD = {
        "clsid": "{MICA_RF_IRST_LEFT}",
        "name": "*MICA NG RF - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    _2_x_AIM_200A_Peregrine_Active_Radar_AAM_IRST_POD = {
        "clsid": "{AIM200_2XRACK_IRST_LEFT}",
        "name": "*2 x AIM-200A Peregrine Active Radar AAM + IRST POD",
        "weight": 347.96,
    }
    IRST_Sensor_Pod = {
        "clsid": "{IRST_SENSOR_Pod}",
        "name": "IRST Sensor Pod",
        "weight": 105,
    }
    MK_83_1000lb_General_Purpose_Bomb = {
        "clsid": "{MK83}",
        "name": "*MK-83* 1000lb General Purpose Bomb",
        "weight": 467,
    }
    GBU_32_JDAM_1000lb_GPS_Guided_Bomb = {
        "clsid": "{GBU-32}",
        "name": "*GBU-32* JDAM, 1000lb GPS Guided Bomb",
        "weight": 467,
    }
    _2_x_IRST_Sensor_Pod = {
        "clsid": "{F22_IRST_PAIR}",
        "name": "2 x IRST Sensor Pod",
        "weight": 0,
    }
    AIM_120C_6_AMRAAM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_120C_6_IRST_RIGHT}",
        "name": "*AIM-120C-6 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    AIM_120C_7_AMRAAM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_120C_7_IRST_RIGHT}",
        "name": "*AIM-120C-7 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    AIM_120C_8_AMRAAM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_120C_8_IRST_RIGHT}",
        "name": "*AIM-120C-8 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    AIM_120D_3_AMRAAM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_120D_3_IRST_RIGHT}",
        "name": "*AIM-120D-3 AMRAAM - Active Radar AAM + IRST POD",
        "weight": 270,
    }
    AIM_120E_AMRAAM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_120E_IRST_RIGHT}",
        "name": "*AIM-120E AMRAAM - Active Radar AAM + IRST POD",
        "weight": 270,
    }
    AIM_260A_JATM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_260A_IRST_RIGHT}",
        "name": "*AIM-260A JATM - Active Radar AAM + IRST POD",
        "weight": 265.0,
    }
    AIM_260B_JATM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_260B_IRST_RIGHT}",
        "name": "*AIM-260B JATM - Active Radar AAM + IRST POD",
        "weight": 265.0,
    }
    AIM_272A_LRAAM_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM_272A_IRST_RIGHT}",
        "name": "*AIM-272A LRAAM - Active Radar AAM + IRST POD",
        "weight": 270.0,
    }
    MICA_NG_RF_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{MICA_RF_IRST_RIGHT}",
        "name": "*MICA NG RF - Active Radar AAM + IRST POD",
        "weight": 266.48,
    }
    _2_x_AIM_200A_Peregrine_Active_Radar_AAM_IRST_POD_ = {
        "clsid": "{AIM200_2XRACK_IRST_RIGHT}",
        "name": "*2 x AIM-200A Peregrine Active Radar AAM + IRST POD",
        "weight": 347.96,
    }
    AIM_174B_Gunslinger_Active_Radar_ULRAAM = {
        "clsid": "{LAU_118_AIM-174B}",
        "name": "AIM-174B Gunslinger - Active Radar ULRAAM",
        "weight": 910.0,
    }
    LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_NGAAM = {
        "clsid": "{LAU_115_2xAIM-260}",
        "name": "LAU-115 with 2 x LAU-127 AIM-260A JATM - Active Radar NGAAM",
        "weight": 370.0,
    }


inject_weapons(F22AEFMWeapons)


@planemod
class F_22A_EFM(PlaneType):
    id = "F-22A"
    retribution_id = "F-22A_EFM"
    flyable = True
    height = 4.88
    width = 13.05
    length = 19.1
    fuel_max = 8200
    max_speed = 2649.996
    chaff = 120
    flare = 120
    charge_total = 240
    chaff_charge_size = 1
    flare_charge_size = 2
    eplrs = True
    category = "Interceptor"  # {78EFB7A2-FD52-4b57-A6A6-3BF0E1D6555F}
    radio_frequency = 127.5

    property_defaults: Dict[str, Any] = {
        "BAY_DOOR_OPTION": False,
    }

    class Properties:
        class BAY_DOOR_OPTION:
            id = "BAY_DOOR_OPTION"

    livery_name = "F-22A"  # from type

    class Pylon1:
        AIM_9M_Sidewinder_IR_AAM = (1, Weapons.AIM_9M_Sidewinder_IR_AAM)
        AIM_9X_Sidewinder_IR_AAM = (1, Weapons.AIM_9X_Sidewinder_IR_AAM)
        AIM_9L_Sidewinder_IR_AAM = (1, Weapons.AIM_9L_Sidewinder_IR_AAM)
        AIM_9X_2_Sidewinder_IR_AAM = (1, F22AEFMWeapons.AIM_9X_2_Sidewinder_IR_AAM)
        AIM_9X_3_Sidewinder_IR_AAM = (1, F22AEFMWeapons.AIM_9X_3_Sidewinder_IR_AAM)
        AIM_2000_IRIS_T_IR_AAM = (1, F22AEFMWeapons.AIM_2000_IRIS_T_IR_AAM)
        V3E_A_Darter_IR_AAM = (1, F22AEFMWeapons.V3E_A_Darter_IR_AAM)
        Python_5_IR_AAM_F22 = (1, F22AEFMWeapons.Python_5_IR_AAM_F22)
        AIM_74A_MUTANT_Active_Radar_AAM = (
            1,
            F22AEFMWeapons.AIM_74A_MUTANT_Active_Radar_AAM,
        )
        AIM_74B_MUTANT_Active_Radar_AAM = (
            1,
            F22AEFMWeapons.AIM_74B_MUTANT_Active_Radar_AAM,
        )
        AIM_272A_LRAAM_Active_Radar_AAM = (
            1,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        AIM_200A_Peregrine_Active_Radar_AAM = (
            1,
            F22AEFMWeapons.AIM_200A_Peregrine_Active_Radar_AAM,
        )

    class Pylon2:
        LAU_115_2_LAU_127_AIM_120B = (2, Weapons.LAU_115_2_LAU_127_AIM_120B)
        LAU_115_2_LAU_127_AIM_120C = (2, Weapons.LAU_115_2_LAU_127_AIM_120C)
        Fuel_tank_600_gal = (2, F22AEFMWeapons.Fuel_tank_600_gal)
        Conformal_Fuel_tank_600_gal = (2, F22AEFMWeapons.Conformal_Fuel_tank_600_gal)
        LDTP_Fuel_tank_600_gal = (2, F22AEFMWeapons.LDTP_Fuel_tank_600_gal)
        AGM_88G_AARGM_Anti_Radiation_AGM = (
            2,
            F22AEFMWeapons.AGM_88G_AARGM_Anti_Radiation_AGM,
        )
        _2_x_Mako_Multi_Mission_Hypersonic_Missile_Anti_Radiation_AGM = (
            2,
            F22AEFMWeapons._2_x_Mako_Multi_Mission_Hypersonic_Missile_Anti_Radiation_AGM,
        )
        LAU_115_with_2_x_LAU_127_AIM_9X_2_Sidewinder_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_9X_2_Sidewinder_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_9X_3_Sidewinder_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_9X_3_Sidewinder_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_2000_IRIS_T_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_2000_IRIS_T_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_132_ASRAAM_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_132_ASRAAM_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_V3E_A_Darter_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_V3E_A_Darter_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_Python_5_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_Python_5_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_MICA_NG_IR_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_MICA_NG_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120E_AMRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_NGAAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_NGAAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_260B_JATM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260B_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_MICA_NG_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_MICA_NG_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_74A_MUTANT_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_74A_MUTANT_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_74B_MUTANT_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_74B_MUTANT_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_272A_LRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_272A_LRAAM_Active_Radar_AAM,
        )
        _2_x_Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = (
            2,
            F22AEFMWeapons._2_x_Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM,
        )
        AIM_174B_Gunslinger_Active_Radar_ULRAAM = (
            2,
            F22AEFMWeapons.AIM_174B_Gunslinger_Active_Radar_ULRAAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            2,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            2,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM_ = (
            2,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM_,
        )
        LAU_115_with_2_x_LAU_127_MDBA_Meteor_Active_Radar_AAM = (
            2,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_MDBA_Meteor_Active_Radar_AAM,
        )

    class Pylon3:
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            3,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            3,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        AIM_260A_JATM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Rdr_AAM = (3, F22AEFMWeapons.Meteor_BVRAAM_Active_Rdr_AAM)
        AIM_260B_JATM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM,
        )
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM = (
            3,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM,
        )
        MICA_NG_RF_Active_Radar_AAM = (3, F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM)
        AIM_272A_LRAAM_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM__ = (
            3,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM__,
        )
        Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = (
            3,
            F22AEFMWeapons.Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM,
        )

    class Pylon4:
        Meteor_BVRAAM_Active_Rdr_AAM = (4, F22AEFMWeapons.Meteor_BVRAAM_Active_Rdr_AAM)
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            4,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            4,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        MICA_NG_RF_Active_Radar_AAM = (4, F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM)
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM = (
            4,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM,
        )
        AIM_260A_JATM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM,
        )
        AIM_260B_JATM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM,
        )
        AIM_272A_LRAAM_Active_Radar_AAM = (
            4,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM_IRST_POD,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM_IRST_POD,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM_IRST_POD,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM_IRST_POD,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM_IRST_POD,
        )
        AIM_260A_JATM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM_IRST_POD,
        )
        AIM_260B_JATM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM_IRST_POD,
        )
        AIM_272A_LRAAM_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM_IRST_POD,
        )
        MICA_NG_RF_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM_IRST_POD,
        )
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM_IRST_POD = (
            4,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM_IRST_POD,
        )
        IRST_Sensor_Pod = (4, F22AEFMWeapons.IRST_Sensor_Pod)

    class Pylon5:
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            5,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            5,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        AIM_260A_JATM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Rdr_AAM = (5, F22AEFMWeapons.Meteor_BVRAAM_Active_Rdr_AAM)
        AIM_260B_JATM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM,
        )
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM = (
            5,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM,
        )
        MICA_NG_RF_Active_Radar_AAM = (5, F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM)
        AIM_272A_LRAAM_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM__ = (
            5,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM__,
        )
        Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = (
            5,
            F22AEFMWeapons.Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM,
        )
        MK_83_1000lb_General_Purpose_Bomb = (
            5,
            F22AEFMWeapons.MK_83_1000lb_General_Purpose_Bomb,
        )
        GBU_32_JDAM_1000lb_GPS_Guided_Bomb = (
            5,
            F22AEFMWeapons.GBU_32_JDAM_1000lb_GPS_Guided_Bomb,
        )

    class Pylon6:
        _2_x_IRST_Sensor_Pod = (6, F22AEFMWeapons._2_x_IRST_Sensor_Pod)

    class Pylon7:
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            7,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            7,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        AIM_260A_JATM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Rdr_AAM = (7, F22AEFMWeapons.Meteor_BVRAAM_Active_Rdr_AAM)
        AIM_260B_JATM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM,
        )
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM = (
            7,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM,
        )
        MICA_NG_RF_Active_Radar_AAM = (7, F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM)
        AIM_272A_LRAAM_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM__ = (
            7,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM__,
        )
        Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = (
            7,
            F22AEFMWeapons.Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM,
        )
        MK_83_1000lb_General_Purpose_Bomb = (
            7,
            F22AEFMWeapons.MK_83_1000lb_General_Purpose_Bomb,
        )
        GBU_32_JDAM_1000lb_GPS_Guided_Bomb = (
            7,
            F22AEFMWeapons.GBU_32_JDAM_1000lb_GPS_Guided_Bomb,
        )

    class Pylon8:
        Meteor_BVRAAM_Active_Rdr_AAM = (8, F22AEFMWeapons.Meteor_BVRAAM_Active_Rdr_AAM)
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            8,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            8,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        MICA_NG_RF_Active_Radar_AAM = (8, F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM)
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM = (
            8,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM,
        )
        AIM_260A_JATM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM,
        )
        AIM_260B_JATM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM,
        )
        AIM_272A_LRAAM_Active_Radar_AAM = (
            8,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_260A_JATM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_260B_JATM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM_IRST_POD_,
        )
        AIM_272A_LRAAM_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM_IRST_POD_,
        )
        MICA_NG_RF_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM_IRST_POD_,
        )
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM_IRST_POD_ = (
            8,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM_IRST_POD_,
        )
        IRST_Sensor_Pod = (8, F22AEFMWeapons.IRST_Sensor_Pod)

    class Pylon9:
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            9,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            9,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        AIM_120E_AMRAAM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        AIM_260A_JATM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_260A_JATM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Rdr_AAM = (9, F22AEFMWeapons.Meteor_BVRAAM_Active_Rdr_AAM)
        AIM_260B_JATM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_260B_JATM_Active_Radar_AAM,
        )
        _2_x_AIM_200A_Peregrine_Active_Radar_AAM = (
            9,
            F22AEFMWeapons._2_x_AIM_200A_Peregrine_Active_Radar_AAM,
        )
        MICA_NG_RF_Active_Radar_AAM = (9, F22AEFMWeapons.MICA_NG_RF_Active_Radar_AAM)
        AIM_272A_LRAAM_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM__ = (
            9,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM__,
        )
        Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = (
            9,
            F22AEFMWeapons.Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM,
        )

    class Pylon10:
        LAU_115_2_LAU_127_AIM_120B = (10, Weapons.LAU_115_2_LAU_127_AIM_120B)
        LAU_115_2_LAU_127_AIM_120C = (10, Weapons.LAU_115_2_LAU_127_AIM_120C)
        Fuel_tank_600_gal = (10, F22AEFMWeapons.Fuel_tank_600_gal)
        Conformal_Fuel_tank_600_gal = (10, F22AEFMWeapons.Conformal_Fuel_tank_600_gal)
        LDTP_Fuel_tank_600_gal = (10, F22AEFMWeapons.LDTP_Fuel_tank_600_gal)
        AGM_88G_AARGM_Anti_Radiation_AGM = (
            10,
            F22AEFMWeapons.AGM_88G_AARGM_Anti_Radiation_AGM,
        )
        _2_x_Mako_Multi_Mission_Hypersonic_Missile_Anti_Radiation_AGM = (
            10,
            F22AEFMWeapons._2_x_Mako_Multi_Mission_Hypersonic_Missile_Anti_Radiation_AGM,
        )
        LAU_115_with_2_x_LAU_127_AIM_9X_2_Sidewinder_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_9X_2_Sidewinder_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_9X_3_Sidewinder_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_9X_3_Sidewinder_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_2000_IRIS_T_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_2000_IRIS_T_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_132_ASRAAM_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_132_ASRAAM_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_V3E_A_Darter_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_V3E_A_Darter_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_Python_5_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_Python_5_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_MICA_NG_IR_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_MICA_NG_IR_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_6_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_6_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_7_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120C_8_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120C_8_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120D_3_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_120E_AMRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_120E_AMRAAM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_NGAAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_NGAAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260A_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_260B_JATM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_260B_JATM_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_MICA_NG_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_MICA_NG_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_74A_MUTANT_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_74A_MUTANT_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_74B_MUTANT_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_74B_MUTANT_Active_Radar_AAM,
        )
        LAU_115_with_2_x_LAU_127_AIM_272A_LRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_AIM_272A_LRAAM_Active_Radar_AAM,
        )
        _2_x_Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM = (
            10,
            F22AEFMWeapons._2_x_Mako_Multi_Mission_Hypersonic_Missile_Active_Radar_AAM,
        )
        AIM_120C_AMRAAM___Active_Radar_AAM = (
            10,
            Weapons.AIM_120C_AMRAAM___Active_Radar_AAM,
        )
        AIM_120B_AMRAAM___Active_Radar_AAM = (
            10,
            Weapons.AIM_120B_AMRAAM___Active_Radar_AAM,
        )
        AIM_174B_Gunslinger_Active_Radar_ULRAAM = (
            10,
            F22AEFMWeapons.AIM_174B_Gunslinger_Active_Radar_ULRAAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM,
        )
        Meteor_BVRAAM_Active_Radar_AAM_ = (
            10,
            F22AEFMWeapons.Meteor_BVRAAM_Active_Radar_AAM_,
        )
        LAU_115_with_2_x_LAU_127_MDBA_Meteor_Active_Radar_AAM = (
            10,
            F22AEFMWeapons.LAU_115_with_2_x_LAU_127_MDBA_Meteor_Active_Radar_AAM,
        )

    class Pylon11:
        AIM_9M_Sidewinder_IR_AAM = (11, Weapons.AIM_9M_Sidewinder_IR_AAM)
        AIM_9X_Sidewinder_IR_AAM = (11, Weapons.AIM_9X_Sidewinder_IR_AAM)
        AIM_9L_Sidewinder_IR_AAM = (11, Weapons.AIM_9L_Sidewinder_IR_AAM)
        AIM_9X_2_Sidewinder_IR_AAM = (11, F22AEFMWeapons.AIM_9X_2_Sidewinder_IR_AAM)
        AIM_9X_3_Sidewinder_IR_AAM = (11, F22AEFMWeapons.AIM_9X_3_Sidewinder_IR_AAM)
        AIM_2000_IRIS_T_IR_AAM = (11, F22AEFMWeapons.AIM_2000_IRIS_T_IR_AAM)
        V3E_A_Darter_IR_AAM = (11, F22AEFMWeapons.V3E_A_Darter_IR_AAM)
        Python_5_IR_AAM_F22 = (11, F22AEFMWeapons.Python_5_IR_AAM_F22)
        AIM_74A_MUTANT_Active_Radar_AAM = (
            11,
            F22AEFMWeapons.AIM_74A_MUTANT_Active_Radar_AAM,
        )
        AIM_74B_MUTANT_Active_Radar_AAM = (
            11,
            F22AEFMWeapons.AIM_74B_MUTANT_Active_Radar_AAM,
        )
        AIM_272A_LRAAM_Active_Radar_AAM = (
            11,
            F22AEFMWeapons.AIM_272A_LRAAM_Active_Radar_AAM,
        )
        AIM_200A_Peregrine_Active_Radar_AAM = (
            11,
            F22AEFMWeapons.AIM_200A_Peregrine_Active_Radar_AAM,
        )

    pylons: Set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

    tasks = [
        task.CAP,
        task.Escort,
        task.FighterSweep,
        task.Intercept,
        task.Reconnaissance,
    ]
    task_default = task.CAP

    @classmethod
    def load_payloads(cls) -> Dict[str, Dict[str, Any]]:
        """Prefer payloads written for this variant, then fall back to plain F-22A ones.

        pydcs matches a payload file to an airframe on its `unitType` field, which for
        both F-22A variants is the DCS type name, so the base variant's Retribution
        loadouts would otherwise win on name. Reading "F-22A_EFM" first gives this
        variant its own defaults while the user's own F-22A loadouts, saved by the
        Mission Editor under the real type name, still show up in the payload editor.
        """
        if cls.payloads is not None:
            return cls.payloads

        original_id = cls.id
        try:
            cls.id = cls.retribution_id
            cls.payloads = None
            super().load_payloads()
            efm_payloads: Dict[str, Dict[str, Any]] = cls.payloads or {}
        finally:
            cls.id = original_id

        cls.payloads = None
        super().load_payloads()
        # Names already claimed by the EFM-specific file take precedence.
        cls.payloads = (cls.payloads or {}) | efm_payloads
        return cls.payloads
