import asyncio
from collections import defaultdict
from json import load
# from time import sleep
from typing import List, NamedTuple, Tuple, Set

import requests
import pandas as pd


G_API_KEY =  None
REVERSE_GEOLOCATE_API = "https://maps.googleapis.com/maps/api/geocode/json?address={city},+{state}&key={api_key}"
PLACE_API = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&keyword={keyword}&key={api_key}"
PLACE_NEXT_PAGE_TOKEN = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={page_token}&key={api_key}"

with open(".google_key") as f:
    data = load(f)
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

async def _perform_place_search(keyword: str, lat: float, lon: float, radius: int=15000) -> Set:
    master_set = set()
    
    for lat, lon in _get_near_coords(lat, lon):
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
            await asyncio.sleep(4)
            resp = requests.get(
                PLACE_NEXT_PAGE_TOKEN.format(
                    page_token=next_page_token,
                    api_key=G_API_KEY,
                )
            )
            data = resp.json()
            for place in data["results"]:
                place_ids.add((place["place_id"], place.get("rating", 0.0)))
            next_page_token = data.get("next_page_token")

        master_set |= place_ids
    return {(lat, lon): master_set}

async def find_place_count_by_keyword(keyword: str, lats: List[float], lons: List[float]) -> List[Tuple[str, float]]:
    result = defaultdict(set)

    tasks = [
        _perform_place_search(keyword, lat, lon)
        for lat, lon in zip(lats, lons)
    ]
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    from pprint import pprint
    pprint(asyncio.run(find_place_count_by_keyword("burger", [37.4418834, 26.1420358], [-122.1430195, -81.7948103])))    