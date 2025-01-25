import asyncio
import requests

from fastapi import FastAPI
from .data_model import Venue, GeoLocation, Money, DistanceRange, DeliveryOrderPrice, DeliveryFee
from .business_logic import compute_delivery_order_price

app = FastAPI()

VENUE_SOURCE_URL = "https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues"


@app.get("/api/v1/delivery-order-price")
async def get_delivery_order_price(
    venue_slug: str, cart_value: int, user_lat: float, user_lon: float
) -> dict[str, object]:
    venue = await fetch_venue(venue_slug)
    if not venue:
        return {"status": "404", "error": "Invalid venue."}
    dop = compute_delivery_order_price(
        venue=venue, cart_value=Money(cart_value), user_location=GeoLocation(lat=user_lat, lon=user_lon)
    )
    if dop is None:
        return {"status": "404", "error": "Delivery isn't possible."}
    return {
        "total_price": dop.total_price.amount,
        "small_order_surcharge": dop.small_order_surcharge.amount,
        "cart_value": dop.cart_value,
        "delivery": {"fee": dop.delivery.fee, "distance": dop.delivery.distance},
    }


async def fetch_venue(venue_slug: str) -> Venue | None:
    static_api = f"{VENUE_SOURCE_URL}/{venue_slug}/static"
    dynamic_api = f"{VENUE_SOURCE_URL}/{venue_slug}/dynamic"

    loop = asyncio.get_running_loop()  # gain access to the scheduler

    response = await loop.run_in_executor(None, requests.get, static_api)
    static_venue_raw = response.json().get("venue_raw")
    if response.status_code != 200 or static_venue_raw is None:
        return None

    response = await loop.run_in_executor(None, requests.get, dynamic_api)
    dynamic_venue_raw = response.json().get("venue_raw")
    if response.status_code != 200 or dynamic_venue_raw is None:
        return None

    coordinates = GeoLocation(
        lon=static_venue_raw["location"]["coordinates"][0],
        lat=static_venue_raw["location"]["coordinates"][1],
    )
    delivery_specs = dynamic_venue_raw["delivery_specs"]
    order_minimum_no_surcharge = Money(delivery_specs["order_minimum_no_surcharge"])
    base_price = Money(delivery_specs["delivery_pricing"]["base_price"])
    distance_ranges_raw = delivery_specs["delivery_pricing"]["distance_ranges"]
    distance_ranges: list[DistanceRange] = []
    for r in distance_ranges_raw:
        distance_range = DistanceRange(
            max=None if r["max"] == 0 else r["max"], constant=Money(r["a"]), multiplier=r["b"]
        )
        distance_ranges.append(distance_range)
    return Venue(
        slug=venue_slug,
        location=coordinates,
        order_minimum_no_surcharge=order_minimum_no_surcharge,
        base_price=base_price,
        distance_ranges=distance_ranges,
    )


async def _test_fetch_venue_not_found() -> None:
    venue_slug = "not-found-venue"
    venue = await fetch_venue(venue_slug)
    assert venue is None


async def _test_fetch_venue() -> None:
    import pytest

    venue_slug = "home-assignment-venue-helsinki"
    venue = await fetch_venue(venue_slug)
    assert venue is not None
    assert venue.slug == "home-assignment-venue-helsinki"
    assert venue.location.lat == pytest.approx(60.17012143)
    assert venue.location.lon == pytest.approx(24.92813512)
    assert venue.order_minimum_no_surcharge == Money(1000)
    assert venue.base_price == Money(190)
    assert venue.distance_ranges == [
        DistanceRange(max=500, constant=Money(amount=0), multiplier=0),
        DistanceRange(max=1000, constant=Money(amount=100), multiplier=0),
        DistanceRange(max=1500, constant=Money(amount=200), multiplier=0),
        DistanceRange(max=2000, constant=Money(amount=200), multiplier=1),
        DistanceRange(max=None, constant=Money(amount=0), multiplier=0),
    ]
