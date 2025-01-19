# Copyright Song Meo

import requests

from data_model import Venue, GeoLocation, Money, DistanceRange

api_url = "https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues"
venue_location = "home-assignment-venue-helsinki"
static_api = f"{api_url}/{venue_location}/dynamic"
dynamic_api = f"{api_url}/{venue_location}/static"

static_response = requests.get(static_api)
dynamic_response = requests.get(dynamic_api)


def get_venue(venue_id: str) -> Venue:
    static_venue = requests.get(static_api).json().venue_raw
    dynamic_venue = requests.get(dynamic_api).json().venue_raw

    coordinates = GeoLocation(static_venue.location.coordinates.lat, static_venue.location.coordinates.lon)
    delivery_specs = dynamic_venue.delivery_specs
    order_minimum_no_surcharge = Money(delivery_specs.order_minimum_no_surcharge)
    base_price = Money(delivery_specs.base_price)
    distance_ranges_raw = delivery_specs.delivery_pricing.distance_ranges
    distance_ranges = []
    for r in distance_ranges_raw:
        distance_ranges += DistanceRange((r.min, r.max), (r.a, r.b))
    return Venue(venue_id,
                 coordinates,
                 order_minimum_no_surcharge,
                 base_price,
                 distance_ranges)
