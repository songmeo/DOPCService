from typing import Union, Any
from fastapi import FastAPI
import requests
from .data_model import Venue, GeoLocation, Money, DistanceRange


app = FastAPI()

api_url = "https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues"
venue_location = "home-assignment-venue-helsinki"
static_api = f"{api_url}/{venue_location}/dynamic"
dynamic_api = f"{api_url}/{venue_location}/static"


@app.get("/")
def read_root() -> dict[str, Any]:
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Any]:
    return {"item_id": item_id, "q": q}


def get_venue(venue_id: str) -> Venue:
    static_venue = requests.get(static_api).json().venue_raw
    dynamic_venue = requests.get(dynamic_api).json().venue_raw

    coordinates = GeoLocation(static_venue.location.coordinates.lat, static_venue.location.coordinates.lon)
    delivery_specs = dynamic_venue.delivery_specs
    order_minimum_no_surcharge = Money(delivery_specs.order_minimum_no_surcharge)
    base_price = Money(delivery_specs.base_price)
    distance_ranges_raw = delivery_specs.delivery_pricing.distance_ranges
    distance_ranges: list[DistanceRange] = []
    for r in distance_ranges_raw:
        distance_ranges.append(DistanceRange(max=r.max, constant=r.a, multiplier=r.b))
    return Venue(venue_id, coordinates, order_minimum_no_surcharge, base_price, distance_ranges)


# TODO: WRITE TEST FOR get_venue()
