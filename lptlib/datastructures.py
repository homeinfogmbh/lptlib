"""Common API."""

from datetime import datetime
from typing import Iterable, NamedTuple

from lptlib.dom import Stop as StopDOM  # pylint: disable=E0401,E0611
from lptlib.dom import StopEvent as StopEventDOM  # pylint: disable=E0401,E0611


__all__ = ['StopEvent', 'Stop']


class StopEvent(NamedTuple):
    """Represents stop events."""

    type: str
    line: str
    destination: str
    scheduled: datetime
    estimated: datetime

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        if self.estimated is None:
            estimated = None
        else:
            estimated = self.estimated.isoformat()

        return {
            'type': self.type,
            'line': self.line,
            'destination': self.destination,
            'scheduled': self.scheduled.isoformat(),
            'estimated': estimated
        }

    def to_dom(self) -> StopEventDOM:
        """Returns an XML DOM."""
        stop_event = StopEventDOM()
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
    latitude: float
    longitude: float
    departures: Iterable[StopEvent]

    def to_json(self) -> dict:
        """Returns a JSON-ish dict."""
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'departures': [dep.to_json() for dep in self.departures]
        }

    def to_dom(self) -> StopDOM:
        """Returns an XML DOM."""
        stop = StopDOM()
        stop.id = self.id
        stop.name = self.name
        stop.latitude = self.latitude
        stop.longitude = self.longitude
        stop.departure = [departure.to_dom() for departure in self.departures]
        return stop
