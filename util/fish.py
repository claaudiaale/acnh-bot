import requests
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_fish(month):
    url = 'https://api.nookipedia.com/nh/fish'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }
    params = {'month': month}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        fish_names = []
        for fish in data.get('north'):
            fish_names.append({
                'name': f'{fish['name']}',
                'rarity': f'{fish['rarity']}'
            })
        return fish_names
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def fetch_single_fish(fish_name):
    url = f'https://api.nookipedia.com/nh/fish/{fish_name}'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")

