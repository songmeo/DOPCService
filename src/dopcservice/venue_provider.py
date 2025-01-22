from abc import ABC

from data_model import Venue


class VenueProvider(ABC):
    def get_venue(self) -> Venue:
        raise NotImplementedError
