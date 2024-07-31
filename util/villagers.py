import requests
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_villagers(villager_name=None):
    url = 'https://api.nookipedia.com/villagers'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }
    params = {'game': 'NH'}

    if villager_name:
        params['name'] = villager_name

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def get_villager_info(identifier):
    if isinstance(identifier, int):
        villagers = fetch_villagers()
        return villagers[identifier]
    elif isinstance(identifier, str):
        villager_info = fetch_villagers(identifier)
        return villager_info[0]


def get_villager_name(villager_id):
    villager_info = get_villager_info(villager_id)
    return villager_info['name']
