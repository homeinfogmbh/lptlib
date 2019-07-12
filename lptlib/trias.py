"""Translates TRIAS API responses."""

from datetime import datetime

from lptlib.config import MAX_STOPS, MAX_DEPARTURES
from lptlib.datastructures import Stop, StopEvent


__all__ = ['get_departures']


STRING_REPLACEMENTS = {
    'ß': 'ss',
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'Ä': 'Ae',
    'Ö': 'Oe',
    'Ü': 'Ue'
}


def _fix_address(address):
    """Fixes addresses."""

    for key, value in STRING_REPLACEMENTS.items():
        address = address.replace(key, value)

    return address


def _make_stop(location, departures):
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
    longitude = float(location.Location.GeoPosition.Longitude)
    latitude = float(location.Location.GeoPosition.Latitude)
    return Stop(ident, name, longitude, latitude, departures)


def _make_stop_event(stop_event_result):
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
    return StopEvent(line, scheduled, estimated, destination, type_)


def _stop_events(stop_event_results):
    """Yields stop events."""

    for depc, stop_event_result in enumerate(stop_event_results, start=1):
        if depc > MAX_DEPARTURES:
            break

        yield _make_stop_event(stop_event_result)


def get_departures(client, address, fix_address=False):
    """Returns departures from the respective Trias client."""

    address = str(address)

    if fix_address:
        address = _fix_address(address)

    geo_coordinates = client.geocoordinates(address)
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
        stop = _make_stop(location, departures)
        stops.append(stop)

    return stops
