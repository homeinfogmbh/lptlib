"""Common exceptions."""

__all__ = ['NoGeoCoordinatesForAddress']


class NoGeoCoordinatesForAddress(Exception):
    """Indicates that there are no geo coordinates for the given address."""

    def __init__(self, address: str):
        super().__init__(address)
        self.address = address
