import requests
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_all_art():
    url = f'https://api.nookipedia.com/nh/art'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        artwork = []
        for information in data:
            info = {'name': information['name'],
                    'has_fake': information['has_fake'],
                    'art_type': information['art_type']}
            artwork.append(info)
        return artwork
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def fetch_one_art(art_name):
    url = f'https://api.nookipedia.com/nh/art/{art_name}'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")
