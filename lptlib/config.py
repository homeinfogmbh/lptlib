"""Configuration file parsing."""

from configlib import loadcfg


__all__ = ['CONFIG', 'MAX_STOPS', 'MAX_DEPARTURES']


CONFIG = loadcfg('lpt.conf')
CONFIG_SECTION = CONFIG['LPT']
MAX_STOPS = int(CONFIG_SECTION.get('stops', 3))
MAX_DEPARTURES = int(CONFIG_SECTION.get('departures', 3))
