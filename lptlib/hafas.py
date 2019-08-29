"""Translates HAFAS API responses."""

from logging import getLogger

from timelib import strpdatetime

from lptlib.config import MAX_STOPS, MAX_DEPARTURES
from lptlib.datastructures import Stop, StopEvent


__all__ = ['get_departures']


LOGGER = getLogger('HAFAS')


def _make_stop(stop_location, departures):
    """Creates a stop from the respective HAFAS CoordLocation element."""

    ident = str(stop_location.id)
    name = str(stop_location.name)
    latitude = float(stop_location.lat)
    longitude = float(stop_location.lon)
    return Stop(ident, name, longitude, latitude, departures)


def _make_stop_event(departure):
    """Creates a stop from the respective HAFAS Departure element."""

    line = str(departure.Product.line)
    scheduled = f'{departure.date}T{departure.time}'
    scheduled = strpdatetime(scheduled)

    if departure.rtTime is None:
        estimated = None
    else:
        estimated_date = departure.rtDate or departure.date
        estimated = f'{estimated_date}T{departure.rtTime}'
        estimated = strpdatetime(estimated)

    destination = str(departure.direction)
    type_ = str(departure.Product.catOutL)
    return StopEvent(line, scheduled, estimated, destination, type_)


def _stop_events(departures):
    """Yields stop events of a Departure node."""

    for depc, departure in enumerate(departures, start=1):
        if depc > MAX_DEPARTURES:
            break

        yield _make_stop_event(departure)


def get_departures(client, address):
    """Returns departures from the respective HAFAS client."""

    LOGGER.debug('Address: %s', address)
    # Re-format address string for best matches within a certain city.
    addresses = client.locations(str(address), type='A')
    LOGGER.debug('Address list: %s', addresses.toxml())

    try:
        coord_location = addresses.CoordLocation[0]
    except IndexError:
        return []

    nearby_stops = client.nearbystops(coord_location.lat, coord_location.lon)
    LOGGER.debug('Stops list: %s', nearby_stops.toxml())
    stopc = 1
    stops = []

    for stop_location in nearby_stops.StopLocation:
        if stopc > MAX_STOPS:
            break

        departure_board = client.departure_board(stop_location.id)

        if not departure_board.Departure:  # Skip stations without stop events.
            continue

        stopc += 1
        LOGGER.debug('Departure board: %s', departure_board.toxml())
        departures = list(_stop_events(departure_board.Departure))
        stop = _make_stop(stop_location, departures)
        stops.append(stop)

    return stops
