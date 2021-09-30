"""Common API."""

from datetime import datetime
from typing import Iterable, NamedTuple, Optional

from lptlib import dom  # pylint: disable=E0611


__all__ = ['GeoCoordinates', 'StopEvent', 'Stop', 'Stops']


class GeoCoordinates(NamedTuple):
    """Geo coordinates."""

    latitude: float
    longitude: float


class StopEvent(NamedTuple):
    """Represents stop events."""

    type: str
    line: str
    destination: str
    scheduled: datetime
    estimated: Optional[datetime] = None

    @property
    def estimated_str(self) -> Optional[str]:
        """Returns the estimated datetime string."""
        if self.estimated is None:
            return None

        return self.estimated.isoformat()

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {
            'type': self.type,
            'line': self.line,
            'destination': self.destination,
            'scheduled': self.scheduled.isoformat(),
            'estimated': self.estimated_str
        }

    def to_dom(self) -> dom.StopEvent:
        """Returns an XML DOM."""
        stop_event = dom.StopEvent()
        stop_event.type = self.type
        stop_event.line = self.line
        stop_event.destination = self.destination
        stop_event.scheduled = self.scheduled
        stop_event.estimated = self.estimated
        return stop_event


class Stop(NamedTuple):
    """Represents stops."""

    id: str
    name: str
    geo: GeoCoordinates
    departures: Iterable[StopEvent]

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {
            'id': self.id,
            'name': self.name,
            'geo': [self.geo.latitude, self.geo.longitude],
            'departures': [dep.to_json() for dep in self.departures]
        }

    def to_dom(self) -> dom.Stop:
        """Returns an XML DOM."""
        stop = dom.Stop()
        stop.id = self.id
        stop.name = self.name
        stop.latitude = self.geo.latitude
        stop.longitude = self.geo.longitude
        stop.departure = [departure.to_dom() for departure in self.departures]
        return stop


class Stops(NamedTuple):
    """Contains departures info."""

    stops: list[Stop]
    source: str

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {
            'stops': [stop.to_json() for stop in self.stops],
            'source': self.source
        }

    def to_dom(self) -> dom.stops:
        """Returns an XML DOM."""
        stops = dom.stops()
        stops.stop = [stop.to_dom() for stop in self.stops]
        stops.source = self.source
        return stops
