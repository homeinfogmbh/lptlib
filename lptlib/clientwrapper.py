"""Common client wrapper."""

from __future__ import annotations
from typing import Union

from hafas import Client as HafasClient
from trias import Client as TriasClient


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
