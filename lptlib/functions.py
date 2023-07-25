"""Miscellaneous functions."""

from typing import Any, Iterable


__all__ = ["is_2_tuple", "contains_only_floats", "is_geo_coordinates"]


def is_2_tuple(obj: Any) -> bool:
    """Checks if the object is a 2-tuple."""

    return isinstance(obj, tuple) and len(obj) == 2


def contains_only_floats(iterable: Iterable) -> bool:
    """Checks if the object only contains floats."""

    return all(isinstance(item, float) for item in iterable)


def is_geo_coordinates(obj: Any) -> bool:
    """Checks if an object contains geo coordinates."""

    return is_2_tuple(obj) and contains_only_floats(obj)
