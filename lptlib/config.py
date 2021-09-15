"""Configuration file parsing."""

from configlib import loadcfg


__all__ = ['CONFIG', 'MAX_STOPS', 'MAX_DEPARTURES']


CONFIG = loadcfg('lpt.conf')
MAX_STOPS = CONFIG.getint('LPT', 'stops', fallback=3)
MAX_DEPARTURES = CONFIG.getint('LPT', 'departures', fallback=3)
