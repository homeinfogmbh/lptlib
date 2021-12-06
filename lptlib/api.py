"""Generalized local public transportation API."""

from typing import Optional, Union

from mdb import Address
from wsgilib import Error, ACCEPT, XML, JSON

from lptlib.client import get_client_by_name, get_client_by_zip_code
from lptlib.datastructures import GeoCoordinates, Stops
from lptlib.functions import is_geo_coordinates


__all__ = ['get_departures', 'get_response']


Target = Union[Address, str, GeoCoordinates, tuple[float, float]]


def get_departures_addr(address: Union[Address, str],
                        stops: Optional[int] = None,
                        departures: Optional[int] = None) -> Stops:
    """Returns departures by address."""

    try:
        zip_code = int(address.zip_code)
    except TypeError:
        raise Error('Address has no ZIP code.') from None
    except ValueError:
        raise Error('ZIP code is not an integer.') from None

    try:
        client = get_client_by_zip_code(zip_code)
    except KeyError:
        raise Error(f'No API for ZIP code "{zip_code}".', status=404) from None

    return Stops(list(client.get_departures_addr(
        address, stops=stops, departures=departures)), client.source)


def get_departures_geo(geo: GeoCoordinates, stops: Optional[int] = None,
                       departures: Optional[int] = None) -> Stops:
    """Returns departures by geo coordinates."""

    try:
        client = get_client_by_name('EFA Deutschland')
    except KeyError:
        raise Error('General API not found.', status=404) from None

    return Stops(list(client.get_departures_geo(
        geo, stops=stops, departures=departures)), client.source)


def get_departures(target: Target, stops: Optional[int] = None,
                   departures: Optional[int] = None) -> Stops:
    """Returns a list of departures."""

    if target is None:
        raise Error('No target specified.')

    if isinstance(target, (Address, str)):
        return get_departures_addr(target, stops=stops, departures=departures)

    if isinstance(target, GeoCoordinates) or is_geo_coordinates(target):
        return get_departures_geo(target, stops=stops, departures=departures)

    raise TypeError('Cannot retrieve departures info for type:', type(target))


def get_response(target: Target, stops: Optional[int] = None,
                 departures: Optional[int] = None) -> Union[JSON, XML]:
    """Returns the respective departures."""

    stops = get_departures(target, stops=stops, departures=departures)

    if 'application/json' in ACCEPT:
        return JSON(stops.to_json())

    return XML(stops.to_dom())
