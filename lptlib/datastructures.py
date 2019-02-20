"""Common API."""

from collections import namedtuple

from timelib import isoformat

from lptlib.dom import Stop as StopDOM  # pylint: disable=E0401,E0611
from lptlib.dom import StopEvent as StopEventDOM  # pylint: disable=E0401,E0611


__all__ = ['Stop', 'StopEvent']


STOP_SLOTS = ('ident', 'name', 'longitude', 'latitude', 'departures')
STOP_EVENT_SLOTS = ('line', 'scheduled', 'estimated', 'destination', 'type')


class Stop(namedtuple('Stop', STOP_SLOTS)):
    """Represents stops."""

    __slots__ = ()

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


class StopEvent(namedtuple('StopEvent', STOP_EVENT_SLOTS)):
    """Represents stop events."""

    __slots__ = ()

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
