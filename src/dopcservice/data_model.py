# Copyright Song Meo

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from math import radians, sin, cos, sqrt, atan2


@dataclass(frozen=True)
class Money:
    amount: int = 0
    """
    Money in the lowest denomination of the local currency.
    In euro countries they are in cents, in Sweden they are in öre, and in Japan they are in yen.
    """

    def __add__(self, other: Any) -> Money:
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        return NotImplemented


@dataclass(frozen=True)
class GeoLocation:
    lat: float
    lon: float
    RADIUS_OF_EARTH = 6378e3

    def get_great_arc_distance(self, other: GeoLocation) -> float:
        """
        Returns distance in meters.
        >>> loc1 = GeoLocation(59.451949, 24.726974)
        >>> loc2 = GeoLocation(59.438150, 24.750183)
        >>> round(loc1.get_great_arc_distance(loc2))
        2021
        """
        lat1, lon1, lat2, lon2 = map(radians, [self.lat, self.lon, other.lat, other.lon])
        delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
        # Haversine formula
        a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        return 2 * self.RADIUS_OF_EARTH * atan2(sqrt(a), sqrt(1 - a))


@dataclass(frozen=True)
class DistanceRange:
    max: int | None
    """
    [meter]
    The upper (exclusive) bound for the distance range.
    If None, the delivery is not available for delivery distances equal or longer than the value of min.
    """
    constant: Money
    multiplier: int
    """[cent/meter]"""

    def __post_init__(self) -> None:
        if self.max <= 0:
            raise ValueError(f"max cannot be zero")
        # TODO: add more validators


@dataclass(frozen=True)
class DeliveryFee:
    fee: Money
    distance: float
    """[meter]"""


@dataclass(frozen=True)
class UserOrder:
    location: GeoLocation
    venue_slug: str
    cart_value: Money


@dataclass(frozen=True)
class DeliveryOrderPrice:
    total_price: Money
    small_order_surcharge: Money
    cart_value: Money
    delivery: DeliveryFee


@dataclass(frozen=True)
class Venue:
    id: str
    location: GeoLocation
    order_minimum_no_surcharge: Money
    base_price: Money
    distance_ranges: list[DistanceRange]
