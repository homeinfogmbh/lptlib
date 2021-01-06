"""Generalized local public transportation API."""

from typing import Iterator, Tuple, Union

from mdb import Address
from wsgilib import Error, ACCEPT, XML, JSON

from lptlib.client import CLIENTS, load_clients
from lptlib.datastructures import Stop
from lptlib.dom import stops as stops_dom   # pylint: disable=E0401,E0611


__all__ = ['get_departures', 'get_response']


def get_departures(address: Address) -> Tuple[Iterator[Stop], str]:
    """Returns a list of departures."""

    if address is None:
        raise Error('No address specified.')

    try:
        zip_code = int(address.zip_code)
    except TypeError:
        raise Error('Address has no ZIP code.') from None
    except ValueError:
        raise Error('ZIP code is not an integer.') from None

    if not CLIENTS:
        load_clients()

    try:
        client = CLIENTS[zip_code]
    except KeyError:
        raise Error(f'No API for ZIP code "{zip_code}".', status=404) from None

    return (client.get_departures(address), client.source)


def get_response(address: Address) -> Union[JSON, XML]:
    """Returns the respective departures."""

    stops, source = get_departures(address)

    if 'application/json' in ACCEPT:
        json = {
            'source': source,
            'stops': [stop.to_json() for stop in stops]
        }
        return JSON(json)

    xml = stops_dom()
    xml.source = source
    xml.stop = [stop.to_dom() for stop in stops]
    return XML(xml)
