"""Translates HAFAS API responses."""

from datetime import datetime
from typing import Iterable, Iterator, List

from hafas.client import Departure, StopLocation

from lptlib.config import MAX_STOPS, MAX_DEPARTURES
from lptlib.datastructures import Stop, StopEvent


__all__ = ['get_departures']


def _make_stop(stop_location: StopLocation,
               departures: List[StopEvent]) -> Stop:
    """Creates a stop from the respective HAFAS CoordLocation element."""

    ident = str(stop_location.id)
    name = str(stop_location.name)
    latitude = float(stop_location.lat)
    longitude = float(stop_location.lon)
    return Stop(ident, name, latitude, longitude, departures)


def _make_stop_event(departure: Departure) -> StopEvent:
    """Creates a stop from the respective HAFAS Departure element."""

    line = str(departure.Product.line)
    scheduled = datetime.fromisoformat(f'{departure.date}T{departure.time}')

    if departure.rtTime is None:
        estimated = None
    else:
        est_date = departure.rtDate or departure.date
        estimated = datetime.fromisoformat(f'{est_date}T{departure.rtTime}')

    destination = str(departure.direction)
    type_ = str(departure.Product.catOutL)
    return StopEvent(type_, line, destination, scheduled, estimated)


def _stop_events(departures: Iterable[Departure]) -> Iterator[StopEvent]:
    """Yields stop events of a Departure node."""

    for depc, departure in enumerate(departures, start=1):
        if depc > MAX_DEPARTURES:
            break

        yield _make_stop_event(departure)


def get_departures(client, address: str) -> Iterator[Stop]:
    """Returns departures from the respective HAFAS client."""

    addresses = client.locations(str(address), type='A')

    try:
        coord_location = addresses.CoordLocation[0]
    except IndexError:
        return

    nearby_stops = client.nearbystops(coord_location.lat, coord_location.lon)

    for stops, stop_location in enumerate(nearby_stops.StopLocation, start=1):
        if stops >= MAX_STOPS:
            break

        departure_board = client.departure_board(stop_location.id)

        if not departure_board.Departure:  # Skip stations without stop events.
            continue

        departures = list(_stop_events(departure_board.Departure))
        yield _make_stop(stop_location, departures)
