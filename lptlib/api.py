"""Generalized local public transportation API."""

from trias import Client as TriasClient
from hafas import Client as HafasClient
from wsgilib import Error

from lptlib.config import get_client
from lptlib.hafas import get_departures as get_departures_hafas
from lptlib.trias import get_departures as get_departures_trias


__all__ = ['get_departures']


def get_departures(address):
    """Returns a list of departures."""

    if address is None:
        raise Error('No address specified.')

    try:
        zip_code = int(address.zip_code)
    except TypeError:
        raise Error("No ZIP code specified in terminal's address.")
    except ValueError:
        raise Error('ZIP code is not an integer.')

    try:
        client = get_client(zip_code)
    except KeyError:
        raise Error('No API for ZIP code "{}".'.format(zip_code), status=404)

    if isinstance(client, TriasClient):
        return get_departures_trias(client, address)

    if isinstance(client, HafasClient):
        return get_departures_hafas(client, address)

    raise Error('Invalid client "{}".'.format(type(client).__name__))
