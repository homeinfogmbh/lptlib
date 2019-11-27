"""Generic LPT client."""

from functools import lru_cache
from json import load
from logging import getLogger

from functoolsplus import coerce
from hafas import Client as HafasClient
from trias import Client as TriasClient

from lptlib.hafas import get_departures as get_departures_hafas
from lptlib.trias import get_departures as get_departures_trias


__all__ = ['clients', 'get_client', 'Client']


CLIENTS_CONFIG = '/usr/local/etc/lpt.json'


@lru_cache()
@coerce(dict)
def clients():
    """Loads the clients map."""

    logger = getLogger('LPT')

    try:
        with open(CLIENTS_CONFIG, 'r') as file:
            json = load(file)
    except FileNotFoundError:
        logger.error('Config file "%s" not found.', CLIENTS_CONFIG)
        return

    for name, config in json.items():
        logger.info('Loading %s.', name)

        try:
            client = Client.from_config(config)
        except KeyError as key_error:
            logger.error('No %s specified.', key_error)
            continue
        except ValueError as value_error:
            logger.error(value_error)
            continue

        for (start, end) in config.get('zip_codes'):
            for zip_code in range(start, end+1):
                yield (zip_code, client)


def get_client(zip_code):
    """Loads the clients map."""

    return clients()[zip_code]  # pylint: disable=E1136


class Client:   # pylint: disable=R0903
    """A generic local public transport API client."""

    def __init__(self, client, source, fix_address=False):
        """Sets client and source."""
        self.client = client
        self.source = source
        self.fix_address = fix_address

    def get_departures(self, address):
        """Returns the respective departures."""
        if isinstance(self.client, HafasClient):
            return get_departures_hafas(self.client, address)

        if isinstance(self.client, TriasClient):
            return get_departures_trias(
                self.client, address, fix_address=self.fix_address)

        raise TypeError(f'Invalid client type "{self.client}".')

    @classmethod
    def from_config(cls, config):
        """Creates an instance from the respective config entry."""
        type_ = config['type'].strip().lower()
        url = config['url']
        debug = config.get('debug', False)
        fix_address = config.get('fix_address', False)

        if type_ == 'trias':
            version = config.get('version', '1.1')
            requestor_ref = config['requestor_ref']
            validate = config.get('validate', True)
            client = TriasClient.get(
                version, url, requestor_ref, validate=validate, debug=debug)
        elif type_ == 'hafas':
            access_id = config.get('access_id')
            client = HafasClient(url, access_id)
        else:
            raise ValueError(f'Invalid client type: {type_}.')

        source = config['source']
        return cls(client, source, fix_address=fix_address)
