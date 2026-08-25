from dcs.point import MovingPoint
from dcs.task import (
    OptECMUsing,
    ControlledTask,
    Targets,
    EngageTargetsInZone,
)

from game.utils import nautical_miles
from .pydcswaypointbuilder import PydcsWaypointBuilder


class SeadSweepIngressBuilder(PydcsWaypointBuilder):
    def add_tasks(self, waypoint: MovingPoint) -> None:
        self.register_special_ingress_points()
        # Preemptively use ECM to better avoid getting swatted.
        self.set_ecm_using(waypoint, OptECMUsing.Values.UseIfDetectedLockByRadar)

        waypoint.add_task(
            ControlledTask(
                EngageTargetsInZone(
                    position=self.flight.flight_plan.tot_waypoint.position,
                    radius=int(
                        nautical_miles(
                            self.flight.coalition.game.settings.sead_sweep_engagement_range_distance
                        ).meters
                    ),
                    targets=[Targets.All.GroundUnits.AirDefence],
                )
            )
        )
