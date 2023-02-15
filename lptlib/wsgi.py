"""Non-authenticated WSGI interface.

XXX: For internal use only!
"""

from flask import request

from mdb import Address
from wsgilib import Application, JSON

from lptlib.api import get_departures


__all__ = ['APPLICATION']


APPLICATION = Application('lpt', cors=True)


@APPLICATION.route('/', methods=['POST'], strict_slashes=False)
def _get_departures() -> JSON:
    """Return the respective departures as a JSON object."""

    return JSON(
        get_departures(
            Address(
                street=request.json['street'],
                house_number=request.json['houseNumber'],
                zip_code=request.json['zipCode'],
                city=request.json['city']
            ),
            stops=request.json.get('stops'),
            departures=request.json.get('departures')
        ).to_json()
    )
