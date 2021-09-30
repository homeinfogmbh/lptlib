"""Translates TRIAS API responses."""

from datetime import datetime
from typing import Iterable, Iterator, Union

from mdb import Address
from trias import LocationResultStructure, StopEventResultStructure

from lptlib.clientwrapper import ClientWrapper
from lptlib.config import MAX_STOPS, MAX_DEPARTURES
from lptlib.datastructures import GeoCoordinates, Stop, StopEvent


__all__ = ['ClientWrapper']


STRING_REPLACEMENTS = {
    'ß': 'ss',
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'Ä': 'Ae',
    'Ö': 'Oe',
    'Ü': 'Ue'
}


def _fix_address(address: str) -> str:
    """Fixes addresses."""

    for key, value in STRING_REPLACEMENTS.items():
        address = address.replace(key, value)

    return address


def _make_stop(location: LocationResultStructure,
               departures: list[StopEvent]) -> Stop:
    """Creates a stop from the respective
    Trias
        → ServiceDelivery
            → DeliveryPayload
                → LocationInformationResponse
                    → Location
    node from a location information response.
    """

    ident = str(location.Location.StopPoint.StopPointRef.value())
    name = str(location.Location.StopPoint.StopPointName.Text)
    geo = GeoCoordinates(float(location.Location.GeoPosition.Longitude),
                         float(location.Location.GeoPosition.Latitude))
    return Stop(ident, name, geo, departures)


def _make_stop_event(stop_event_result: StopEventResultStructure) -> StopEvent:
    """Creates a stop event from the respective
    Trias
        → DeliveryPayload
            → StopEventResponse
                → StopEventResult
    node from a stop event.response.
    """

    _service = stop_event_result.StopEvent.Service
    line = str(_service.PublishedLineName.Text)
    _call_at_stop = stop_event_result.StopEvent.ThisCall.CallAtStop
    scheduled = _call_at_stop.ServiceDeparture.TimetabledTime
    scheduled = datetime.fromtimestamp(scheduled.timestamp())

    if _call_at_stop.ServiceDeparture.EstimatedTime is None:
        estimated = None
    else:
        estimated = _call_at_stop.ServiceDeparture.EstimatedTime
        estimated = datetime.fromtimestamp(estimated.timestamp())

    destination = str(_service.DestinationText.Text)

    try:
        route = _service.RouteDescription.Text
    except AttributeError:
        route = None
    else:
        route = str(route)

    type_ = str(_service.Mode.Name.Text)
    return StopEvent(type_, line, destination, scheduled, estimated)


def _stop_events(stop_event_results: Iterable[StopEventResultStructure], *,
                 departures: int = MAX_DEPARTURES) -> Iterator[StopEvent]:
    """Yields stop events."""

    for depc, stop_event_result in enumerate(stop_event_results, start=1):
        if depc > departures:
            break

        yield _make_stop_event(stop_event_result)


class ClientWrapper(ClientWrapper):     # pylint: disable=E0102
    """Wraps a TRIAS client."""

    def get_departures_geo(self, geo: GeoCoordinates, *, stops: int = MAX_STOPS,
                           departures: int = MAX_DEPARTURES) -> Iterator[Stop]:
        """Yields departures for the given geo coordinates."""
        trias = self.client.stops(geo)
        payload = trias.ServiceDelivery.DeliveryPayload
        locations = payload.LocationInformationResponse.Location

        for stop, location in enumerate(locations, start=1):
            if stop > stops:
                break

            stop_point_ref = location.Location.StopPoint.StopPointRef.value()
            trias = self.client.stop_event(stop_point_ref)
            payload = trias.ServiceDelivery.DeliveryPayload
            stop_event_results = payload.StopEventResponse.StopEventResult
            departures = _stop_events(stop_event_results, departures=departures)
            yield _make_stop(location, list(departures))

    def address_to_geo(self, address: Union[Address, str]) -> GeoCoordinates:
        """Converts an address into geo coordinates."""
        address = str(address)

        if self.fix_address:
            address = _fix_address(address)

        return self.client.geocoordinates(address)

    def get_departures_addr(self, address: Union[Address, str], *,
                           stops: int = MAX_STOPS,
                           departures: int = MAX_DEPARTURES) -> Iterator[Stop]:
        """Yields departures for the given address."""
        yield from self.get_departures_geo(
            self.address_to_geo(address), stops=stops, departures=departures)
