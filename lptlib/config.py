"""Configuration file parsing."""

from functools import lru_cache
from json import load
from logging import getLogger

from configlib import loadcfg
from functoolsplus import coerce
from hafas import Client as HafasClient
from trias import Client as TriasClient


__all__ = [
    'CONFIG',
    'MAX_STOPS',
    'MAX_DEPARTURES',
    'CLIENTS_CONFIG',
    'clients',
    'get_client']


CONFIG = loadcfg('lpt.conf')
CONFIG_SECTION = CONFIG['LPT']
MAX_STOPS = int(CONFIG_SECTION.get('stops', 3))
MAX_DEPARTURES = int(CONFIG_SECTION.get('departures', 3))
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
            type_ = config['type'].strip().lower()
        except KeyError:
            logger.error('No type specified.')
            continue

        try:
            url = config['url']
        except KeyError:
            logger.error('No URL specified.')
            continue

        try:
            source = config['source']
        except KeyError:
            logger.error('No source ID specified.')

        if type_ == 'trias':
            try:
                requestor_ref = config['requestor_ref']
            except KeyError:
                logger.error('No requestor_ref specified.')
                continue

            debug = config.get('debug', False)
            client = TriasClient(url, requestor_ref, debug=debug)
        elif type_ == 'hafas':
            try:
                access_id = config['access_id']
            except KeyError:
                logger.error('No access_id specified.')
                continue

            client = HafasClient(url, access_id)
        else:
            logger.error('Invalid client type: "%s".', type_)
            continue

        client.source = source

        for (start, end) in config.get('zip_codes'):
            for zip_code in range(start, end+1):
                yield (zip_code, client)


def get_client(zip_code):
    """Loads the clients map."""

    return clients()[zip_code]  # pylint: disable=E1136
