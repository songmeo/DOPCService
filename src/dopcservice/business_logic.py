from data_model import DeliveryOrderPrice, UserOrder, Venue, DistanceRange


def compute_delivery_order_price(venue: Venue, order: UserOrder) -> DeliveryOrderPrice:
    distance = venue.coordinates.get_great_arc_distance(order.coordinates)
    small_order_surcharge = venue.order_minimum_no_surcharge - order.cart_value
    total_price = (venue.base_price + DistanceRange.a + DistanceRange.b * distance / 10)
    # delivery_fee =
    return DeliveryOrderPrice(total_price, small_order_surcharge, order.cart_value)
