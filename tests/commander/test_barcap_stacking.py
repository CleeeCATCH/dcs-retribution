"""Tests for stacking BARCAPs over the same objective at different altitudes."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from game.ato.flighttype import FlightType
from game.ato.flightplans.barcap import BARCAP_STACK_OFFSETS, Builder
from game.utils import feet


def _package(target: Any, count: int = 1) -> Any:
    package = SimpleNamespace(target=target, flights=[])
    for _ in range(count):
        package.flights.append(SimpleNamespace(flight_type=FlightType.BARCAP))
    return package


def _builder(flight: Any, package: Any, ato_packages: list[Any]) -> Builder:
    builder = Builder.__new__(Builder)
    builder.flight = flight
    # package and coalition are properties derived from the flight.
    flight.package = package
    flight.coalition = SimpleNamespace(ato=SimpleNamespace(packages=ato_packages))
    return builder


def test_first_barcap_keeps_its_preferred_altitude() -> None:
    target = object()
    package = _package(target)
    builder = _builder(package.flights[0], package, [package])

    assert builder.stack_index() == 0
    assert BARCAP_STACK_OFFSETS[0] == feet(0)


def test_later_barcaps_of_the_same_target_are_stacked() -> None:
    target = object()
    first, second, third = _package(target), _package(target), _package(target)
    ato = [first, second, third]

    assert _builder(second.flights[0], second, ato).stack_index() == 1
    assert _builder(third.flights[0], third, ato).stack_index() == 2


def test_barcaps_of_other_targets_do_not_count() -> None:
    target = object()
    other = _package(object(), count=2)
    package = _package(target)

    assert _builder(package.flights[0], package, [other, package]).stack_index() == 0


def test_package_being_planned_goes_after_existing_ones() -> None:
    target = object()
    existing = _package(target)
    new = _package(target)

    assert _builder(new.flights[0], new, [existing]).stack_index() == 1


def test_offsets_give_high_and_low_layers() -> None:
    assert set(BARCAP_STACK_OFFSETS) == {feet(0), feet(5000), feet(-5000)}
