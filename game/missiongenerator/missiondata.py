from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from dcs.flyingunit import FlyingUnit
from dcs.unitgroup import ShipGroup

from game.dcs.aircrafttype import AircraftType
from game.dcs.groundunittype import GroundUnitType
from game.missiongenerator.aircraft.flightdata import FlightData
from game.runways import RunwayData

if TYPE_CHECKING:
    from game.radio.radios import RadioFrequency
    from game.radio.tacan import TacanChannel
    from game.theater.player import Player
    from game.utils import Distance
    from uuid import UUID


@dataclass
class GroupInfo:
    group_name: str
    callsign: str
    freq: RadioFrequency
    blue: Player


@dataclass
class UnitInfo(GroupInfo):
    unit_name: str


@dataclass
class AwacsInfo(GroupInfo):
    """AWACS information for the kneeboard."""

    depature_location: Optional[str]
    start_time: datetime
    end_time: datetime
    unit: FlyingUnit  # reference to be used as L16 donor


@dataclass
class TankerInfo(GroupInfo):
    """Tanker information for the kneeboard."""

    variant: str
    tacan: Optional[TacanChannel]
    start_time: datetime
    end_time: datetime


@dataclass
class CarrierInfo(UnitInfo):
    """Carrier information."""

    tacan: TacanChannel
    icls_channel: int | None
    link4_freq: RadioFrequency | None
    ship_group: ShipGroup


@dataclass
class JtacInfo(UnitInfo):
    """JTAC information."""

    region: str
    code: str


@dataclass
class EscortInfo:
    """Escort leash information."""

    escort_group_id: int
    escorted_group_id: int
    engagement_range_meters: int


@dataclass
class CargoInfo:
    """Cargo information."""

    unit_type: str = field(default_factory=str)
    spawn_zone: str = field(default_factory=str)
    amount: int = field(default=1)


@dataclass
class LogisticsInfo:
    """Logistics information."""

    pilot_names: list[str]
    transport: AircraftType
    blue: Player

    logistic_unit: str = field(default_factory=str)
    pickup_zone: str = field(default_factory=str)
    drop_off_zone: str = field(default_factory=str)
    target_zone: str = field(default_factory=str)
    cargo: list[CargoInfo] = field(default_factory=list)
    preload: bool = field(default=False)


@dataclass
class FrontlineUnitGroupsInfo:
    group_name: str
    unit_type: GroundUnitType


@dataclass
class FrontLineSectorInfo:
    # pydcs x/y, which are DCS vec3 x/z.
    x: float
    y: float
    width: int


@dataclass
class FrontLineSideInfo:
    stance: str
    main_effort: Optional[int]
    forward_heading: int
    # The enemy base exploitation task forces drive to.
    enemy_base_x: float
    enemy_base_y: float


@dataclass
class FrontLineGroupInfo:
    group_name: str
    side: str
    role: str
    sector: Optional[int]
    reserve: bool
    # Maximum weapon range in meters, used for artillery fire missions.
    weapon_range: int = 0


@dataclass
class FrontLineEventInfo:
    kind: str
    side: str
    # Late-activated groups, the director activates them when the event fires.
    groups: list[FrontLineGroupInfo]
    # Where a column drives to. pydcs x/y, which are DCS vec3 x/z.
    destination_x: float
    destination_y: float


@dataclass
class FrontLineDirectorInfo:
    name: str
    sectors: list[FrontLineSectorInfo]
    blue: FrontLineSideInfo
    red: FrontLineSideInfo
    groups: list[FrontLineGroupInfo]
    events: list[FrontLineEventInfo] = field(default_factory=list)


@dataclass
class MissionData:
    awacs: list[AwacsInfo] = field(default_factory=list)
    runways: list[RunwayData] = field(default_factory=list)
    carriers: list[CarrierInfo] = field(default_factory=list)
    flights: list[FlightData] = field(default_factory=list)
    packages: dict[int, list[FlightData]] = field(default_factory=dict)
    tankers: list[TankerInfo] = field(default_factory=list)
    jtacs: list[JtacInfo] = field(default_factory=list)
    logistics: list[LogisticsInfo] = field(default_factory=list)
    escorts: list[EscortInfo] = field(default_factory=list)
    cp_stack: dict[UUID, Distance] = field(default_factory=dict)
    player_frontline_groups: list[FrontlineUnitGroupsInfo] = field(default_factory=list)
    enemy_frontline_groups: list[FrontlineUnitGroupsInfo] = field(default_factory=list)
    front_line_director: list[FrontLineDirectorInfo] = field(default_factory=list)
    # Undeployed armor per control point still free for front line events. A
    # control point fighting on several fronts shares it between them.
    front_line_event_spares: dict[UUID, dict[GroundUnitType, int]] = field(
        default_factory=dict
    )
