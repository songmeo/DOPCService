from .data_model import Money, DeliveryOrderPrice, DeliveryFee, GeoLocation, Venue, DistanceRange


def compute_delivery_order_price(
    venue: Venue,
    cart_value: Money,
    user_location: GeoLocation,
) -> DeliveryOrderPrice | None:
    """
    Returns None if the order is not deliverable to the user's location.
    Expectations:
    - The order of the objects inside distance_ranges is sorted by min.
    - The currency is the same for all instances of Money.
    """
    order_minimum_no_surcharge = venue.order_minimum_no_surcharge
    distance_ranges = venue.distance_ranges
    base_price = venue.base_price

    small_order_surcharge = Money(max(order_minimum_no_surcharge.amount - cart_value.amount, 0))
    distance = venue.location.get_great_circle_distance(user_location)
    rng: DistanceRange | None = None
    for r in distance_ranges:
        if r.max is None:
            break
        if distance < r.max:
            rng = r
            break
    if rng is None:
        return None

    delivery_fee = base_price + rng.constant + Money(round(rng.multiplier * distance / 10))
    total_price = cart_value + small_order_surcharge + delivery_fee

    return DeliveryOrderPrice(
        total_price=total_price,
        small_order_surcharge=small_order_surcharge,
        cart_value=cart_value,
        delivery=DeliveryFee(delivery_fee, distance),
    )


def _test_business_logic_empty_distance_range() -> None:
    v = Venue(
        id="pho-viet-helsinki",
        location=GeoLocation(lat=60.16771, lon=24.93664),
        order_minimum_no_surcharge=Money(1000),
        base_price=Money(190),
        distance_ranges=[],
    )
    cart_value = Money(1000)
    user_location = GeoLocation(lat=60.189714, lon=24.838463)
    delivery_order_price = compute_delivery_order_price(venue=v, cart_value=cart_value, user_location=user_location)
    assert delivery_order_price is None


# TODO: change pytest config to detect test starting with _
def _test_business_logic() -> None:
    import pytest

    v = Venue(
        id="pho-viet-helsinki",
        location=GeoLocation(lat=60.16771, lon=24.93664),
        order_minimum_no_surcharge=Money(1000),
        base_price=Money(190),
        distance_ranges=[
            DistanceRange(max=500, constant=Money(0), multiplier=1),
            DistanceRange(max=1000, constant=Money(100), multiplier=1),
            DistanceRange(max=10000, constant=Money(500), multiplier=2),
            DistanceRange(max=None, constant=Money(0), multiplier=0),
        ],
    )
    cart_value = Money(1000)
    user_location = GeoLocation(lat=60.189714, lon=24.838463)
    delivery_order_price = compute_delivery_order_price(venue=v, cart_value=cart_value, user_location=user_location)
    assert delivery_order_price is not None
    assert delivery_order_price.total_price == Money(2882)
    assert delivery_order_price.small_order_surcharge == Money(0)
    assert delivery_order_price.delivery.fee == Money(1882)
    assert delivery_order_price.delivery.distance == pytest.approx(5961.3)


def _test_business_logic_user_too_far() -> None:
    v = Venue(
        id="pho-viet-helsinki",
        location=GeoLocation(lat=60.16771, lon=24.93664),
        order_minimum_no_surcharge=Money(1000),
        base_price=Money(190),
        distance_ranges=[
            DistanceRange(max=500, constant=Money(0), multiplier=1),
            DistanceRange(max=1000, constant=Money(100), multiplier=1),
            DistanceRange(max=10000, constant=Money(500), multiplier=2),
            DistanceRange(max=None, constant=Money(0), multiplier=0),
        ],
    )
    cart_value = Money(1000)
    user_location = GeoLocation(lat=82, lon=80)
    delivery_order_price = compute_delivery_order_price(venue=v, cart_value=cart_value, user_location=user_location)
    assert delivery_order_price is None
