from data_model import Money, DeliveryOrderPrice, DeliveryFee, GeoLocation, Venue, DistanceRange


def compute_delivery_order_price(
    venue: Venue,
    cart_value: Money,
    user_location: GeoLocation,
) -> DeliveryOrderPrice | None:
    order_minimum_no_surcharge = venue.order_minimum_no_surcharge
    distance_ranges = venue.distance_ranges
    base_price = venue.base_price

    small_order_surcharge = Money(max(order_minimum_no_surcharge.amount - cart_value.amount, 0))
    distance = venue.location.get_great_arc_distance(user_location)

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


def _test_business_logic() -> None:
    pass  # TODO: Song write tests :3
