from typing import Type

from dcs.helicopters import HelicopterType, helicopter_map
from dcs.planes import PlaneType, plane_map
from dcs.unittype import UnitType, VehicleType, ShipType, StaticType
from dcs.vehicles import vehicle_map
from dcs.ships import ship_map
from dcs.statics import cargo_map, fortification_map


def retribution_id(unit_type: Type[UnitType]) -> str:
    """The key a unit type is registered and looked up under inside Retribution.

    This is normally the DCS type name, but a mod may ship a second loadout set for an
    airframe that stock DCS (or another mod) already provides, in which case two pydcs
    classes need the same `id` -- the mission has to name the real DCS type -- while
    still being distinct aircraft as far as Retribution is concerned. Such a class sets
    `retribution_id` to claim its own registry key and its own
    resources/units/aircraft data file.
    """
    return getattr(unit_type, "retribution_id", unit_type.id)


def helicoptermod(helicopter: Type[HelicopterType]) -> Type[HelicopterType]:
    helicopter_map[retribution_id(helicopter)] = helicopter
    return helicopter


def planemod(plane: Type[PlaneType]) -> Type[PlaneType]:
    plane_map[retribution_id(plane)] = plane
    return plane


def vehiclemod(vehicle: Type[VehicleType]) -> Type[VehicleType]:
    vehicle_map[vehicle.id] = vehicle
    return vehicle


def shipmod(ship: Type[ShipType]) -> Type[ShipType]:
    ship_map[ship.id] = ship
    return ship


def cargomod(static: Type[StaticType]) -> Type[StaticType]:
    cargo_map[static.id] = static
    return static


def fortificationmod(static: Type[StaticType]) -> Type[StaticType]:
    fortification_map[static.id] = static
    return static
