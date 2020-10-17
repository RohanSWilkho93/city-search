from json import load
from time import sleep
from typing import List, NamedTuple, Tuple

import requests
import pandas as pd


G_API_KEY =  None
REVERSE_GEOLOCATE_API = "https://maps.googleapis.com/maps/api/geocode/json?address={city},+{state}&key={api_key}"
PLACE_API = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&keyword={keyword}&key={api_key}"
PLACE_NEXT_PAGE_TOKEN = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={page_token}&key={api_key}"

with open(".google_key") as f:
    data = json.load(f)
    G_API_KEY = data["api_key"]


def fetch_city_coords(city: str, state: str) -> List[float]:
    city = city.replace(" ", "+")
    url = REVERSE_GEOLOCATE_API.format(
            city=city,
            state=state,
            api_key=G_API_KEY
        )
    resp = requests.get(url)
    data = resp.json()["results"][0]
    location = list(data["geometry"]["location"].values())
    return location

def _get_near_coords(lat: float, lng: float, offset=0.1):
    for r in [offset, -offset]:
        yield (lat + r, lng)
    for r in [offset, -offset]:
        yield (lat, lng + r)

def _perform_place_search(keyword: str, lat: float, lon: float, radius: int=15000) -> int:
    resp = requests.get(
        PLACE_API.format(
            keyword=keyword,
            lat=lat,
            lon=lon,
            radius=radius,
            api_key=G_API_KEY,
        )
    )
    data = resp.json()

    place_ids = {(place["place_id"], place["rating"]) for place in data["results"]}
    next_page_token = data.get("next_page_token")
    while next_page_token is not None:
        sleep(4)
        resp = requests.get(
            PLACE_NEXT_PAGE_TOKEN.format(
                page_token=next_page_token,
                api_key=G_API_KEY,
            )
        )
        data = resp.json()
        for place in data["results"]:
            place_ids.add((place["place_id"], place["rating"]))
        next_page_token = data.get("next_page_token")

    return place_ids

def find_place_count_by_keyword(keyword: str, lat: float, lon: float) -> List[Tuple[str, float]]:
    result = set()
    for lat, lon in _get_near_coords(lat, lon):
        result |= _perform_place_search(keyword, lat, lon)
    return list(result)
