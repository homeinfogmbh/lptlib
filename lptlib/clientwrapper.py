"""Common client wrapper."""

from __future__ import annotations
from typing import Iterator, Union

from hafas import Client as HafasClient
from mdb import Address
from trias import Client as TriasClient

from lptlib.config import MAX_STOPS, MAX_DEPARTURES
from lptlib.datastructures import GeoCoordinates, Stop


__all__ = ['ClientWrapper']


Client = Union[HafasClient, TriasClient]


class ClientWrapper:   # pylint: disable=R0903
    """A generic local public transport API client."""

    def __init__(self, client: Client, source: str,
                 fix_address: bool = False):
        """Sets client and source."""
        self.client = client
        self.source = source
        self.fix_address = fix_address

    def get_departures_geo(self, geo: GeoCoordinates, *, stops: int = MAX_STOPS,
                           departures: int = MAX_DEPARTURES) -> Iterator[Stop]:
        """Yields stops for the given geo coordinates."""
        raise NotImplementedError()

    def get_departures_addr(self, address: Union[Address, str], *,
                            stops: int = MAX_STOPS,
                            departures: int = MAX_DEPARTURES) -> Iterator[Stop]:
        """Yields departures for the given address."""
        raise NotImplementedError()
