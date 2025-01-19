# Copyright Song Meo

from __future__ import annotations
from dataclasses import dataclass


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

    def great_circle_distance(self, other: GeoLocation) -> float:
        """Returns the arc length in meters"""
        # TODO implement
        return 0


@dataclass(frozen=True)
class DistanceCluster:
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
    pass
