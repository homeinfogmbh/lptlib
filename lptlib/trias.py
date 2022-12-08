"""Translates TRIAS API responses."""

from datetime import datetime
from typing import Iterable, Iterator, Optional, Union

from mdb import Address
from trias import LocationResultStructure, StopEventResultStructure

from lptlib import clientwrapper
from lptlib.datastructures import GeoCoordinates, Stop, StopEvent
from lptlib.exceptions import NoGeoCoordinatesForAddress


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


def _make_stop(
        location: LocationResultStructure,
        departures: list[StopEvent]
) -> Stop:
    """Creates a stop from the respective
    Trias
        → ServiceDelivery
            → DeliveryPayload
                → LocationInformationResponse
                    → Location
    node from a location information response.
    """

    return Stop(
        str(location.Location.StopPoint.StopPointRef.value()),
        str(location.Location.StopPoint.StopPointName.Text),
        GeoCoordinates(
            float(location.Location.GeoPosition.Longitude),
            float(location.Location.GeoPosition.Latitude)
        ),
        departures
    )


def _make_stop_event(stop_event_result: StopEventResultStructure) -> StopEvent:
    """Creates a stop event from the respective
    Trias
        → DeliveryPayload
            → StopEventResponse
                → StopEventResult
    node from a stop event.response.
    """

    return StopEvent(
        str(stop_event_result.StopEvent.Service.Mode.Name.Text),
        str(stop_event_result.StopEvent.Service.PublishedLineName.Text),
        str(stop_event_result.StopEvent.Service.DestinationText.Text),
        datetime.fromtimestamp(
            (
                service_departure := stop_event_result
                    .StopEvent
                    .ThisCall
                    .CallAtStop
                    .ServiceDeparture
            ).TimetabledTime.timestamp()
        ),
        _get_estimated_arrival(service_departure.EstimatedTime)
    )


def _get_estimated_arrival(
        estimated_time: Optional[datetime]
) -> Optional[datetime]:
    """Return the estimated arrival timestamp."""

    if estimated_time is None:
        return None

    return datetime.fromtimestamp(estimated_time.timestamp())


def _stop_events(
        stop_event_results: Iterable[StopEventResultStructure],
        *,
        departures: Optional[int] = None
) -> Iterator[StopEvent]:
    """Yields stop events."""

    for depc, stop_event_result in enumerate(stop_event_results, start=1):
        if departures is not None and depc > departures:
            break

        yield _make_stop_event(stop_event_result)


class ClientWrapper(clientwrapper.ClientWrapper):
    """Wraps a TRIAS client."""

    def get_departures_geo(
            self,
            geo: GeoCoordinates,
            *,
            stops: Optional[int] = None,
            departures: Optional[int] = None
    ) -> Iterator[Stop]:
        """Yields departures for the given geo coordinates."""
        trias = self.client.stops(geo)
        payload = trias.ServiceDelivery.DeliveryPayload
        locations = payload.LocationInformationResponse.Location

        for stop, location in enumerate(locations, start=1):
            if stops is not None and stop > stops:
                break

            stop_point_ref = location.Location.StopPoint.StopPointRef.value()
            trias = self.client.stop_event(stop_point_ref)
            payload = trias.ServiceDelivery.DeliveryPayload
            stop_event_results = payload.StopEventResponse.StopEventResult
            deps = _stop_events(stop_event_results, departures=departures)
            yield _make_stop(location, list(deps))

    def address_to_geo(self, address: Union[Address, str]) -> GeoCoordinates:
        """Converts an address into geo coordinates."""
        address = str(address)

        if self.fix_address:
            address = _fix_address(address)

        if (geocoordinates := self.client.geocoordinates(address)) is None:
            raise NoGeoCoordinatesForAddress(address)

        return geocoordinates

    def get_departures_addr(
            self,
            address: Union[Address, str],
            *,
            stops: Optional[int] = None,
            departures: Optional[int] = None
    ) -> Iterator[Stop]:
        """Yields departures for the given address."""
        yield from self.get_departures_geo(
            self.address_to_geo(address), stops=stops, departures=departures
        )
