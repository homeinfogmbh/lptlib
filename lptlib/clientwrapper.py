"""Common client wrapper."""

from __future__ import annotations
from typing import Iterator, Optional, Union

from hafas import Client as HafasClient
from mdb import Address
from trias import Client as TriasClient

from lptlib.datastructures import GeoCoordinates, Stop


__all__ = ['ClientWrapper']


Client = Union[HafasClient, TriasClient]


class ClientWrapper:   # pylint: disable=R0903
    """A generic local public transport API client."""

    def __init__(
            self,
            client: Client,
            source: str,
            fix_address: bool = False
    ):
        """Sets client and source."""
        self.client = client
        self.source = source
        self.fix_address = fix_address

    def __str__(self):
        return f'{self.client} {self.source} {self.fix_address}'

    def get_departures_geo(
            self,
            geo: GeoCoordinates,
            *,
            stops: Optional[int] = None,
            departures: Optional[int] = None
    ) -> Iterator[Stop]:
        """Yields stops for the given geo coordinates."""
        raise NotImplementedError()

    def get_departures_addr(
            self,
            address: Union[Address, str],
            *,
            stops: Optional[int] = None,
            departures: Optional[int] = None
    ) -> Iterator[Stop]:
        """Yields departures for the given address."""
        raise NotImplementedError()
