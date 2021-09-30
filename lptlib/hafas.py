"""Translates HAFAS API responses."""

from datetime import datetime
from typing import Iterable, Iterator, Union

from hafas import Departure, StopLocation
from mdb import Address

from lptlib.clientwrapper import ClientWrapper
from lptlib.config import MAX_STOPS, MAX_DEPARTURES
from lptlib.datastructures import GeoCoordinates, Stop, StopEvent


__all__ = ['ClientWrapper']


class NoCoordLocationFound(Exception):
    """Indicates that no CoordLocation has been found."""


def _make_stop(stop_location: StopLocation,
               departures: list[StopEvent]) -> Stop:
    """Creates a stop from the respective HAFAS CoordLocation element."""

    ident = str(stop_location.id)
    name = str(stop_location.name)
    geo = GeoCoordinates(float(stop_location.lat), float(stop_location.lon))
    return Stop(ident, name, geo, departures)


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


def _stop_events(departures: Iterable[Departure], *,
                 limit: int = MAX_DEPARTURES) -> Iterator[StopEvent]:
    """Yields stop events of a Departure node."""

    for depc, departure in enumerate(departures, start=1):
        if depc > limit:
            break

        yield _make_stop_event(departure)


class ClientWrapper(ClientWrapper):     # pylint: disable=E0102
    """Wraps a HAFAS client."""

    def get_departures_geo(self, geo: GeoCoordinates, *, stops: int = MAX_STOPS,
                           departures: int = MAX_DEPARTURES) -> Iterator[Stop]:
        """Yields stops for the given geo coordinates."""
        nearby_stops = self.client.nearbystops(geo.latitude, geo.longitude)

        for stop, stop_location in enumerate(nearby_stops.StopLocation, start=1):
            if stop >= stops:
                break

            departure_board = self.client.departure_board(stop_location.id)

            if not departure_board.Departure:  # Skip stations without stop events.
                continue

            deps = _stop_events(departure_board.Departure, limit=departures)
            yield _make_stop(stop_location, deps)

    def address_to_geo(self, address: Union[Address, str]) -> GeoCoordinates:
        """Converts an address into geo coordinates."""
        addresses = self.client.locations(str(address), type='A')

        try:
            coord_location = addresses.CoordLocation[0]
        except IndexError:
            raise NoCoordLocationFound() from None

        return GeoCoordinates(coord_location.lat, coord_location.lon)


    def get_departures_addr(self, address: Union[Address, str], *,
                            stops: int = MAX_STOPS,
                            departures: int = MAX_DEPARTURES) -> Iterator[Stop]:
        """Returns departures from the respective HAFAS client."""
        try:
            geo_coordinates = self.address_to_geo(address)
        except NoCoordLocationFound:
            return

        yield from self.get_departures_geo(
            geo_coordinates, stops=stops, departures=departures)
