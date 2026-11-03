from __future__ import annotations

from datetime import timedelta
from typing import Type

from game.theater import FrontLine
from game.utils import Distance, Speed, feet
from .capbuilder import CapBuilder
from .invalidobjectivelocation import InvalidObjectiveLocation
from .patrolling import PatrollingFlightPlan, PatrollingLayout
from .waypointbuilder import WaypointBuilder


class BarCapFlightPlan(PatrollingFlightPlan[PatrollingLayout]):
    @staticmethod
    def builder_type() -> Type[Builder]:
        return Builder

    @property
    def patrol_duration(self) -> timedelta:
        return self.flight.coalition.game.settings.desired_barcap_mission_duration

    @property
    def patrol_speed(self) -> Speed:
        return self.flight.unit_type.preferred_patrol_speed(
            self.layout.patrol_start.alt
        )

    @property
    def engagement_distance(self) -> Distance:
        return self.flight.coalition.doctrine.cap_engagement_range


#: Altitude offsets given to successive BARCAPs over the same objective, so that
#: CAPs on station together (or handing over) cover a high and a low layer instead
#: of sharing one altitude.
BARCAP_STACK_OFFSETS = (feet(0), feet(5000), feet(-5000))


class Builder(CapBuilder[BarCapFlightPlan, PatrollingLayout]):
    def stack_index(self) -> int:
        """Position of this flight among the coalition's BARCAPs of the same target.

        The order follows the ATO, so it stays stable when flight plans are
        regenerated. A package that isn't in the ATO yet is still being planned and
        goes after the existing ones.
        """
        index = 0
        for package in self.coalition.ato.packages:
            if package is self.package:
                break
            if package.target is not self.package.target:
                continue
            index += sum(
                1 for f in package.flights if f.flight_type is self.flight.flight_type
            )
        for flight in self.package.flights:
            if flight is self.flight:
                break
            if flight.flight_type is self.flight.flight_type:
                index += 1
        return index

    def stacked_patrol_altitude(self, builder: WaypointBuilder) -> Distance:
        offset = BARCAP_STACK_OFFSETS[self.stack_index() % len(BARCAP_STACK_OFFSETS)]
        if self.flight.is_helo or offset == feet(0):
            return builder.get_patrol_altitude
        preferred = self.flight.unit_type.preferred_patrol_altitude
        return builder.get_altitude(preferred + offset)

    def layout(self) -> PatrollingLayout:
        location = self.package.target

        if isinstance(location, FrontLine):
            raise InvalidObjectiveLocation(self.flight.flight_type, location)

        start_pos, end_pos = self.cap_racetrack_for_objective(location, barcap=True)

        builder = WaypointBuilder(self.flight)
        patrol_alt = self.stacked_patrol_altitude(builder)

        start, end = builder.race_track(start_pos, end_pos, patrol_alt)

        return PatrollingLayout(
            departure=builder.takeoff(self.flight.departure),
            nav_to=builder.nav_path(
                self.flight.departure.position, start.position, patrol_alt
            ),
            nav_from=builder.nav_path(
                end.position, self.flight.arrival.position, patrol_alt
            ),
            patrol_start=start,
            patrol_end=end,
            arrival=builder.land(self.flight.arrival),
            divert=builder.divert(self.flight.divert),
            bullseye=builder.bullseye(),
            custom_waypoints=list(),
        )

    def build(self, dump_debug_info: bool = False) -> BarCapFlightPlan:
        return BarCapFlightPlan(self.flight, self.layout())
