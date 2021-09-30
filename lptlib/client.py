"""Generic LPT client."""

from __future__ import annotations
from json import load
from logging import getLogger
from pathlib import Path

from hafas import Client as HafasClient
from trias import Client as TriasClient

from lptlib.clientwrapper import ClientWrapper
from lptlib.hafas import ClientWrapper as HafasClientWrapper
from lptlib.trias import ClientWrapper as TriasClientWrapper


__all__ = ['CLIENTS', 'load_clients']


CLIENTS_CONFIG = Path('/usr/local/etc/lpt.json')
CLIENTS = {}
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


def load_clients(path: Path = CLIENTS_CONFIG):
    """Loads ZIP code / client tuples into CLIENTS."""

    CLIENTS.clear()

    try:
        with path.open('rb') as file:
            json = load(file)
    except FileNotFoundError:
        LOGGER.error('Config file "%s" not found.', path)
        return

    for name, config in json.items():
        LOGGER.info('Loading %s.', name)

        try:
            client = load_client(config)
        except KeyError as key_error:
            LOGGER.error('No %s specified.', key_error)
            continue
        except ValueError as value_error:
            LOGGER.error(value_error)
            continue

        for (start, end) in config.get('zip_codes'):
            for zip_code in range(start, end+1):
                CLIENTS[zip_code] = client
