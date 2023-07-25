"""Configuration file parsing."""

from functools import cache, partial

from configlib import load_config


__all__ = ["get_config", "get_max_stops", "get_max_departures"]


get_config = partial(cache(load_config), "lptlib.conf")


def get_max_stops() -> int:
    """Returns the maximum amount of displayed stops."""

    return get_config().getint("LPT", "stops", fallback=3)


def get_max_departures() -> int:
    """Returns the maximum amount of displayed departures per stop."""

    return get_config().getint("LPT", "departures", fallback=3)
