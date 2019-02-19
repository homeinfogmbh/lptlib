"""Translates HAFAS API responses."""

from lptlib.common import Stop, StopEvent
from lptlib.config import MAX_STOPS, MAX_DEPARTURES


__all__ = ['get_departures']


def _stop_events(departures):
    """Yields stop events of a Departure node."""

    for depc, departure in enumerate(departures, start=1):
        if depc > MAX_DEPARTURES:
            break

        yield StopEvent.from_hafas(departure)


def get_departures(client, address):
    """Returns departures from the respective HAFAS client."""

    location_list = client.locations(str(address), type='S')  # Stations only.
    stop_locations = location_list.StopLocation
    stops = []

    for stopc, stop_location in enumerate(stop_locations, start=1):
        if stopc > MAX_STOPS:
            break

        departure_board = client.departure_board(stop_location.id)
        departures = list(_stop_events(departure_board.Departure))
        stop = Stop.from_hafas(stop_location, departures)
        stops.append(stop)

    return stops
