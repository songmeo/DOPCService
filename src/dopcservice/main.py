import asyncio
from typing import Any

import requests

from fastapi import FastAPI, Response
from .data_model import Venue, GeoLocation, Money, DistanceRange
from .business_logic import compute_delivery_order_price

app = FastAPI()

VENUE_SOURCE_URL = "https://consumer-api.development.dev.woltapi.com/home-assignment-api/v1/venues"


@app.get("/api/v1/delivery-order-price", status_code=200)
async def get_delivery_order_price(
    venue_slug: str, cart_value: int, user_lat: float, user_lon: float, response: Response
) -> dict[str, object]:
    venue = await fetch_venue(venue_slug)
    if not venue:
        response.status_code = 404
        return {"error": "Venue not found."}
    dop = compute_delivery_order_price(
        venue=venue, cart_value=Money(cart_value), user_location=GeoLocation(lat=user_lat, lon=user_lon)
    )
    if dop is None:
        response.status_code = 418
        return {"error": "The user is too far from the venue."}
    return {
        "total_price": dop.total_price.amount,
        "small_order_surcharge": dop.small_order_surcharge.amount,
        "cart_value": dop.cart_value.amount,
        "delivery": {"fee": dop.delivery.fee.amount, "distance": dop.delivery.distance},
    }


async def fetch_venue_raw(api_url: str) -> dict[str, Any] | None:
    loop = asyncio.get_running_loop()  # gain access to the scheduler

    response = await loop.run_in_executor(None, requests.get, api_url)
    venue_raw = response.json().get("venue_raw")

    if response.status_code != 200 or venue_raw is None:
        return None
    return venue_raw  # type: ignore


async def fetch_venue(venue_slug: str) -> Venue | None:
    static_api = f"{VENUE_SOURCE_URL}/{venue_slug}/static"
    dynamic_api = f"{VENUE_SOURCE_URL}/{venue_slug}/dynamic"

    static_venue_raw = await fetch_venue_raw(static_api)

    if static_venue_raw is None:
        return None

    dynamic_venue_raw = await fetch_venue_raw(dynamic_api)

    if dynamic_venue_raw is None:
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


async def _test_get_delivery_order_price() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get(
        "/api/v1/delivery-order-price?venue_slug=home-assignment-venue-helsinki&cart_value=1000"
        "&user_lat=60.17094&user_lon=24.93087"
    )
    assert response.status_code == 200
    assert response.json() == {
        "total_price": 1190,
        "small_order_surcharge": 0,
        "cart_value": 1000,
        "delivery": {"fee": 190, "distance": 177},
    }


async def _test_get_delivery_order_price_venue_not_found() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get(
        "/api/v1/delivery-order-price?venue_slug=not_found_venue&cart_value=1000&user_lat=60.17094&user_lon=24.93087"
    )
    assert response.status_code == 404
    assert response.json() == {"error": "Venue not found."}


async def _test_get_delivery_order_price_client_too_far() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get(
        "/api/v1/delivery-order-price?venue_slug=home-assignment-venue-helsinki&cart_value=1000&user_lat=80&user_lon=82"
    )
    assert response.status_code == 418
    assert response.json() == {"error": "The user is too far from the venue."}


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
