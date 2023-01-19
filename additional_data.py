from api_moltin import get_all_entries
from geopy.distance import distance
import requests


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        raise IndexError('Такого адреса не существует')
    most_relevant = found_places[0]
    lat, lon = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_pizzeria_distance(pizzeria):
    return pizzeria['distance']


def get_nearest_pizzeria(token, user_coord):
    all_pizzeria = get_all_entries(token)
    for pizzeria in all_pizzeria['data']:
        distance_to_client = distance(user_coord, (pizzeria['latitude'], pizzeria['longitude'])).km
        pizzeria['distance'] = distance_to_client
    min_distance = min(all_pizzeria['data'], key=get_pizzeria_distance)
    return min_distance
