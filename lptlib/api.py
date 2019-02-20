"""Generalized local public transportation API."""

from hafas import Client as HafasClient
from trias import Client as TriasClient
from wsgilib import Error, ACCEPT, XML, JSON

from lptlib.config import get_client
from lptlib.dom import stops as stops_dom   # pylint: disable=E0401,E0611
from lptlib.hafas import get_departures as get_departures_hafas
from lptlib.trias import get_departures as get_departures_trias


__all__ = ['get_departures', 'get_response']


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
        stops = get_departures_trias(client, address)
    elif isinstance(client, HafasClient):
        stops = get_departures_hafas(client, address)
    else:
        raise Error('Invalid client "{}".'.format(type(client).__name__))

    return (stops, client.source)


def get_response(address):
    """Returns the respective departures."""

    stops, source = get_departures(address)

    if 'application/json' in ACCEPT:
        json = {
            'source': source,
            'stops': [stop.to_json() for stop in stops]}
        return JSON(json)

    xml = stops_dom()
    xml.source = source
    xml.stop = [stop.to_dom() for stop in stops]
    return XML(xml)
