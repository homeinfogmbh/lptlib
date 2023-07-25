"""Translates HAFAS API responses."""

from datetime import datetime
from typing import Iterable, Iterator, Optional, Union

from hafas import Departure, Product, StopLocation, iter_products
from mdb import Address

from lptlib import clientwrapper
from lptlib.datastructures import GeoCoordinates, Stop, StopEvent
from lptlib.exceptions import NoGeoCoordinatesForAddress


__all__ = ["ClientWrapper"]


def _make_stop(stop_location: StopLocation, departures: list[StopEvent]) -> Stop:
    """Creates a stop from the respective HAFAS CoordLocation element."""

    return Stop(
        str(stop_location.id),
        str(stop_location.name),
        GeoCoordinates(float(stop_location.lat), float(stop_location.lon)),
        departures,
    )


def _make_stop_event(departure: Departure, product: Product) -> StopEvent:
    """Creates a stop from the respective HAFAS Departure element."""

    return StopEvent(
        str(product.catOutL),
        str(product.line),
        str(departure.direction),
        datetime.fromisoformat(f"{departure.date}T{departure.time}"),
        _get_estimated_arrival(departure),
    )


def _get_estimated_arrival(departure: Departure) -> Optional[datetime]:
    """Return the estimated arrival time."""

    if departure.rtTime is None:
        return None

    return datetime.fromisoformat(
        f"{departure.rtDate or departure.date}T{departure.rtTime}"
    )


def _stop_events(
    departures: Iterable[Departure], *, limit: Optional[int] = None
) -> Iterator[StopEvent]:
    """Yields stop events of a Departure node."""
    for depc, departure in enumerate(departures, start=1):
        if limit is not None and depc > limit:
            break

        for product in iter_products(departure):
            yield _make_stop_event(departure, product)


class ClientWrapper(clientwrapper.ClientWrapper):
    """Wraps a HAFAS client."""

    def get_departures_geo(
        self,
        geo: GeoCoordinates,
        *,
        stops: Optional[int] = None,
        departures: Optional[int] = None,
    ) -> Iterator[Stop]:
        """Yields stops for the given geo coordinates."""
        for stop, stop_location in enumerate(
            self.client.nearbystops(geo.latitude, geo.longitude).StopLocation, start=1
        ):
            if stops is not None and stop >= stops:
                break

            departure_board = self.client.departure_board(stop_location.id)

            # Skip stations without stop events.
            if not departure_board.Departure:
                continue

            yield _make_stop(
                stop_location,
                list(_stop_events(departure_board.Departure, limit=departures)),
            )

    def address_to_geo(self, address: Union[Address, str]) -> GeoCoordinates:
        """Converts an address into geo coordinates."""
        addresses = self.client.locations((address := str(address)), type="A")

        try:
            coord_location = addresses.CoordLocation[0]
        except IndexError:
            raise NoGeoCoordinatesForAddress(address) from None

        return GeoCoordinates(coord_location.lat, coord_location.lon)

    def get_departures_addr(
        self,
        address: Union[Address, str],
        *,
        stops: Optional[int] = None,
        departures: Optional[int] = None,
    ) -> Iterator[Stop]:
        """Yields departures for the given address."""
        yield from self.get_departures_geo(
            self.address_to_geo(address), stops=stops, departures=departures
        )
