"""Non-authenticated WSGI interface.

XXX: For internal use only!
"""

from flask import request

from hwdb import Deployment
from mdb import Address
from wsgilib import Application, JSON

from lptlib.api import get_departures


__all__ = ["APPLICATION"]


APPLICATION = Application("lpt", cors=True)


@APPLICATION.route("/", methods=["POST"], strict_slashes=False)
def _get_departures() -> JSON:
    """Return the respective departures as a JSON object."""

    return JSON(
        get_departures(
            get_address(),
            stops=request.json.get("stops"),
            departures=request.json.get("departures"),
        ).to_json()
    )


def get_address() -> Address:
    """Return the requested address."""

    if address_id := request.json.get("address"):
        return Address.get(Address.id == address_id)

    if deployment_id := request.json.get("deployment"):
        deployment = (
            Deployment.select(cascade=True).where(Deployment.id == deployment_id).get()
        )
        return deployment.lpt_address or deployment.address

    return Address(
        street=request.json["street"],
        house_number=request.json["houseNumber"],
        zip_code=request.json["zipCode"],
        city=request.json["city"],
        district=request.json.get("district"),
    )
