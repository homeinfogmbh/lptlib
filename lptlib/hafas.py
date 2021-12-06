"""Translates HAFAS API responses."""

from datetime import datetime
from typing import Iterable, Iterator, Optional, Union

from hafas import Departure, StopLocation
from mdb import Address

from lptlib.clientwrapper import ClientWrapper
from lptlib.datastructures import GeoCoordinates, Stop, StopEvent
from lptlib.exceptions import NoGeoCoordinatesForAddress


__all__ = ['ClientWrapper']


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
                 limit: Optional[int] = None
                 ) -> Iterator[StopEvent]:
    """Yields stop events of a Departure node."""
    for depc, departure in enumerate(departures, start=1):
        if limit is not None and depc > limit:
            break

        yield _make_stop_event(departure)


class ClientWrapper(ClientWrapper):     # pylint: disable=E0102
    """Wraps a HAFAS client."""

    def get_departures_geo(self, geo: GeoCoordinates, *,
                           stops: Optional[int] = None,
                           departures: Optional[int] = None
                           ) -> Iterator[Stop]:
        """Yields stops for the given geo coordinates."""
        nearby_stops = self.client.nearbystops(geo.latitude, geo.longitude)
        stop_locations = nearby_stops.StopLocation

        for stop, stop_location in enumerate(stop_locations, start=1):
            if stops is not None and stop >= stops:
                break

            departure_board = self.client.departure_board(stop_location.id)

            # Skip stations without stop events.
            if not departure_board.Departure:
                continue

            deps = _stop_events(departure_board.Departure, limit=departures)
            yield _make_stop(stop_location, deps)

    def address_to_geo(self, address: Union[Address, str]) -> GeoCoordinates:
        """Converts an address into geo coordinates."""
        addresses = self.client.locations((address := str(address)), type='A')

        try:
            coord_location = addresses.CoordLocation[0]
        except IndexError:
            raise NoGeoCoordinatesForAddress(address) from None

        return GeoCoordinates(coord_location.lat, coord_location.lon)

    def get_departures_addr(self, address: Union[Address, str], *,
                            stops: Optional[int] = None,
                            departures: Optional[int] = None
                            ) -> Iterator[Stop]:
        """Yields departures for the given address."""
        yield from self.get_departures_geo(
            self.address_to_geo(address), stops=stops, departures=departures)
