"""Generic LPT client."""

from __future__ import annotations
from functools import cache
from json import load
from logging import getLogger
from pathlib import Path

from hafas import Client as HafasClient
from trias import Client as TriasClient

from lptlib.clientwrapper import ClientWrapper
from lptlib.hafas import ClientWrapper as HafasClientWrapper
from lptlib.trias import ClientWrapper as TriasClientWrapper


__all__ = ['get_client_by_name', 'get_client_by_zip_code']


CLIENTS_CONFIG = Path('/usr/local/etc/lpt.json')
LOGGER = getLogger('LPT')


def load_client(config: dict) -> ClientWrapper:
    """Creates an instance from the respective config entry."""

    type_ = config['type'].strip().casefold()
    url = config['url']

    if type_ == 'trias':
        client = TriasClient(
            config.get('version', '1.1'), url, config['requestor_ref'],
            validate=config.get('validate', True),
            debug=config.get('debug', False))
        wrapper = TriasClientWrapper
    elif type_ == 'hafas':
        client = HafasClient(url, config['access_id'])
        wrapper = HafasClientWrapper
    else:
        raise ValueError(f'Invalid client type: {type_}.')

    return wrapper(client, config['source'],
                   fix_address=config.get('fix_address', False))


@cache
def load_json(path: Path = CLIENTS_CONFIG) -> dict:
    """Loads the JSON config file."""

    try:
        with path.open('rb') as file:
            return load(file)
    except FileNotFoundError:
        LOGGER.error('Config file "%s" not found.', path)
        return {}


@cache
def load_clients(json: dict) -> dict[str, ClientWrapper]:
    """Loads name / client map."""

    clients = {}

    for name, config in json.get('clients', {}).items():
        LOGGER.info('Loading %s.', name)

        try:
            clients[name] = load_client(config)
        except KeyError as key_error:
            LOGGER.error('No %s specified.', key_error)
            continue
        except ValueError as value_error:
            LOGGER.error(value_error)
            continue

    return clients


@cache
def load_map(json: dict) -> dict[int, ClientWrapper]:
    """Loads ZIP code / client map."""

    clients = load_clients(json)
    map_ = {}

    for name, zip_codes in json.get('map', {}).items():
        LOGGER.info('Mapping %s.', name)

        for (start, end) in zip_codes:
            for zip_code in range(start, end + 1):
                try:
                    map_[zip_code] = clients[name]
                except KeyError:
                    LOGGER.error('No such client: %s', name)

    return map_


def get_client_by_name(name: str) -> ClientWrapper:
    """Returns a client for the given ZIP code."""

    return load_clients(load_json())[name]


def get_client_by_zip_code(zip_code: int) -> ClientWrapper:
    """Returns a client for the given ZIP code."""

    return load_map(load_json())[zip_code]
