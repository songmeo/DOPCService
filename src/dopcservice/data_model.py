# Copyright Song Meo

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Money:
    amount: int
    """
    Money in the lowest denomination of the local currency.
    In euro countries they are in cents, in Sweden they are in öre, and in Japan they are in yen.
    """


@dataclass(frozen=True)
class GeoLocation:
    lat: float
    lon: float

    def delivery_distance(self, other: GeoLocation) -> float:
        """Returns the straight line distance in meters"""
        x1, y1 = self.lat, self.lon
        x2, y2 = other
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


@dataclass(frozen=True)
class DistanceRange:
    min_max: tuple[int, int]
    """[meter]"""
    coef: tuple[int, int]
    """[cent], [cent/meter]"""


@dataclass(frozen=True)
class DeliveryFee:
    price: Money
    distance: int
    """[meter]"""


@dataclass(frozen=True)
class DeliveryOrderPrice:
    total_price: Money
    small_order_surcharge: Money
    cart_value: Money
    delivery: DeliveryFee


@dataclass(frozen=True)
class Venue:
    coordinates: GeoLocation
    order_minimum_no_surcharge: Money
    base_price: Money
    distance_ranges: List[DistanceRange]
