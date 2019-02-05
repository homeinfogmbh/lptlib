"""Translates HAFAS API responses."""

from lptlib.common import Stop, StopEvent
from lptlib.config import MAX_STOPS, MAX_DEPARTURES


__all__ = ['get_departures']


def get_departures(client, address):
    """Returns departures from the respective HAFAS client."""

    location_list = client.locations(repr(address))
    stop_locations = location_list.StopLocation
    stops = []

    for stopc, stop_location in enumerate(stop_locations, start=1):
        if stopc > MAX_STOPS:
            break

        departure_board = client.departure_board(stop_location.id)
        departures = []

        for depc, departure in enumerate(departure_board.Departure, start=1):
            if depc > MAX_DEPARTURES:
                break

            departure = StopEvent.from_hafas(departure)
            departures.append(departure)

        stop = Stop.from_hafas(stop_location, departures)
        stops.append(stop)

    return stops
