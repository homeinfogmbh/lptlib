"""Translates TRIAS API responses."""

from lptlib.common import Stop, StopEvent
from lptlib.config import MAX_STOPS, MAX_DEPARTURES


__all__ = ['get_departures']


def _stop_events(stop_event_results):
    """Yields stop events."""

    for depc, stop_event_result in enumerate(stop_event_results, start=1):
        if depc > MAX_DEPARTURES:
            break

        yield StopEvent.from_trias(stop_event_result)


def get_departures(client, address):
    """Returns departures from the respective Trias client."""

    geo_coordinates = client.geocoordinates(str(address))
    trias = client.stops(geo_coordinates)
    payload = trias.ServiceDelivery.DeliveryPayload
    locations = payload.LocationInformationResponse.Location
    stops = []

    for stopc, location in enumerate(locations, start=1):
        if stopc > MAX_STOPS:
            break

        stop_point_ref = location.Location.StopPoint.StopPointRef.value()
        trias = client.stop_event(stop_point_ref)
        payload = trias.ServiceDelivery.DeliveryPayload
        stop_event_results = payload.StopEventResponse.StopEventResult
        departures = list(_stop_events(stop_event_results))
        stop = Stop.from_trias(location, departures)
        stops.append(stop)

    return stops
