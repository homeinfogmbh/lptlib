"""Generalized local public transportation API."""

from typing import Union

from mdb import Address
from wsgilib import Error, ACCEPT, XML, JSON

from lptlib.client import CLIENTS, load_clients
from lptlib.datastructures import Departures, GeoCoordinates
from lptlib.functions import is_geo_coordinates
from lptlib.dom import stops as stops_dom   # pylint: disable=E0401,E0611


__all__ = ['get_departures', 'get_response']


Target = Union[Address, str, GeoCoordinates, tuple[float, float]]


def get_departures_addr(address: Union[Address, str]) -> Departures:
    """Returns departures by address."""

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

    return (list(client.get_departures_addr(address)), client.source)


def get_departures_geo(geo: GeoCoordinates) -> Departures:
    """Returns departures by geo coordinates."""

    try:
        client = CLIENTS['18055']   # http://v3.api.efa.de/
    except KeyError:
        raise Error('General API not found.', status=404) from None

    return (list(client.get_departures_geo(geo)), client.source)


def get_departures(target: Target) -> Departures:
    """Returns a list of departures."""

    if target is None:
        raise Error('No target specified.')

    if isinstance(target, (Address, str)):
        return get_departures_addr(target)

    if isinstance(target, GeoCoordinates) or is_geo_coordinates(target):
        return get_departures_geo(target)

    raise TypeError('Cannot retrieve departures info for type:', type(target))


def get_response(target: Target) -> Union[JSON, XML]:
    """Returns the respective departures."""

    stops, source = get_departures(target)

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
