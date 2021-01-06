"""Generic LPT client."""

from __future__ import annotations
from json import load
from logging import getLogger
from pathlib import Path
from typing import Iterator, Union

from hafas import Client as HafasClient
from trias import Client as TriasClient

from lptlib.datastructures import Stop
from lptlib.hafas import get_departures as get_departures_hafas
from lptlib.trias import get_departures as get_departures_trias


__all__ = ['CLIENTS', 'load_clients', 'Client']


CLIENTS_CONFIG = Path('/usr/local/etc/lpt.json')
CLIENTS = {}
LOGGER = getLogger('LPT')


def load_clients(path: Path = CLIENTS_CONFIG):
    """Loads ZIP code / client tuples into CLIENTS."""

    CLIENTS.clear()

    try:
        with path.open('r') as file:
            json = load(file)
    except FileNotFoundError:
        LOGGER.error('Config file "%s" not found.', path)
        return

    for name, config in json.items():
        LOGGER.info('Loading %s.', name)

        try:
            client = Client.from_config(config)
        except KeyError as key_error:
            LOGGER.error('No %s specified.', key_error)
            continue
        except ValueError as value_error:
            LOGGER.error(value_error)
            continue

        for (start, end) in config.get('zip_codes'):
            for zip_code in range(start, end+1):
                CLIENTS[zip_code] = client


class Client:   # pylint: disable=R0903
    """A generic local public transport API client."""

    def __init__(self, client: Union[HafasClient, TriasClient], source: str,
                 fix_address: bool = False):
        """Sets client and source."""
        self.client = client
        self.source = source
        self.fix_address = fix_address

    def get_departures(self, address: str) -> Iterator[Stop]:
        """Returns the respective departures."""
        if isinstance(self.client, HafasClient):
            return get_departures_hafas(self.client, address)

        return get_departures_trias(
            self.client, address, fix_address=self.fix_address)

    @classmethod
    def from_config(cls, config: dict) -> Client:
        """Creates an instance from the respective config entry."""
        type_ = config['type'].strip().casefold()
        url = config['url']

        if type_ == 'trias':
            version = config.get('version', '1.1')
            requestor_ref = config['requestor_ref']
            validate = config.get('validate', True)
            client = TriasClient(
                version, url, requestor_ref, validate=validate)
        elif type_ == 'hafas':
            access_id = config['access_id']
            client = HafasClient(url, access_id)
        else:
            raise ValueError(f'Invalid client type: {type_}.')

        return cls(client, config['source'],
                   fix_address=config.get('fix_address', False))
