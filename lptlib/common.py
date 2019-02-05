"""Common API."""

from datetime import datetime

from timelib import isoformat, strpdatetime

from lptlib.dom import Stop as StopDOM  # pylint: disable=E0401,E0611
from lptlib.dom import StopEvent as StopEventDOM  # pylint: disable=E0401,E0611


__all__ = ['Stop', 'StopEvent']


class Stop:
    """Represents stops."""

    __slots__ = ('ident', 'name', 'longitude', 'latitude', 'departures')

    def __init__(self, ident, name, longitude, latitude, departures):
        """Creates a new stop."""
        self.ident = ident
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.departures = departures

    @classmethod
    def from_trias(cls, location, departures):
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
        return cls(ident, name, longitude, latitude, departures)

    @classmethod
    def from_hafas(cls, stop_location, departures):
        """Creates a stop from the respective HAFAS CoordLocation element."""
        ident = str(stop_location.id)
        name = str(stop_location.name)
        latitude = float(stop_location.lat)
        longitude = float(stop_location.lon)
        return cls(ident, name, longitude, latitude, departures)

    def to_json(self):
        """Returns a JSON-ish dict."""
        return {
            'ident': self.ident,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'departures': [
                departure.to_json() for departure in self.departures]}

    def to_dom(self):
        """Returns an XML DOM."""
        stop = StopDOM()
        stop.ident = self.ident
        stop.name = self.name
        stop.latitude = self.latitude
        stop.longitude = self.longitude
        stop.departure = [departure.to_dom() for departure in self.departures]
        return stop


class StopEvent:
    """Represents stop events."""

    __slots__ = ('line', 'scheduled', 'estimated', 'destination', 'type')

    def __init__(self, line, scheduled, estimated, destination, type_):
        """Sets the, line name, scheduled and estimated departure,
        destination of line and an optional route description.
        """
        self.line = line
        self.scheduled = scheduled
        self.estimated = estimated
        self.destination = destination
        self.type = type_

    @classmethod
    def from_trias(cls, stop_event_result):
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
        return cls(line, scheduled, estimated, destination, type_)

    @classmethod
    def from_hafas(cls, departure):
        """Creates a stop from the respective HAFAS Departure element."""
        line = str(departure.Product.line)
        scheduled = '{}T{}'.format(departure.date, departure.time)
        scheduled = strpdatetime(scheduled)

        if departure.rtTime is None:
            estimated = None
        else:
            estimated_date = departure.rtDate or departure.date
            estimated = '{}T{}'.format(estimated_date, departure.rtTime)
            estimated = strpdatetime(estimated)

        destination = str(departure.direction)
        type_ = str(departure.Product.catOutL)
        return cls(line, scheduled, estimated, destination, type_)

    def to_json(self):
        """Returns a JSON-ish dict."""
        return {
            'line': self.line,
            'scheduled': self.scheduled.isoformat(),
            'estimated': isoformat(self.estimated),
            'destination': self.destination,
            'type': self.type}

    def to_dom(self):
        """Returns an XML DOM."""
        stop_event = StopEventDOM()
        stop_event.line = self.line
        stop_event.scheduled = self.scheduled
        stop_event.estimated = self.estimated
        stop_event.destination = self.destination
        stop_event.type = self.type
        return stop_event
