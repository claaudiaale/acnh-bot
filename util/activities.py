import requests
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_species(month, species):
    url = f'https://api.nookipedia.com/nh/{species}'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }
    params = {'month': month}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        names = []
        for specimen in data.get('north'):
            specimen_data = {'name': specimen['name']}
            if species == 'fish':
                specimen_data['rarity'] = specimen['rarity']
            names.append(specimen_data)
        return names
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def fetch_fossils():
    url = f'https://api.nookipedia.com/nh/fossils/individuals'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        fossil_names = []
        for fossil in data:
            specimen_data = {'name': fossil['name']}
            if fossil['fossil_group']:
                specimen_data['fossil group'] = fossil['fossil_group']
            fossil_names.append(specimen_data)
        return fossil_names
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def fetch_specimen(species, specimen):
    if species == 'fossils':
        url = f'https://api.nookipedia.com/nh/{species}/individuals/{specimen}'
    else:
        url = f'https://api.nookipedia.com/nh/{species}/{specimen}'

    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


# def fetch_fossil_group():
#     url = 'https://api.nookipedia.com/nh/fossils/all'
#
#     headers = {
#         'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
#         'Accept-Version': '1.0.0'
#     }
#
#     response = requests.get(url, headers=headers)
#
#     if response.status_code == 200:
#         data = response.json()
#         print(data)
#         return data
#     else:
#         data = response.json()
#         print(data)
#         print(url)
#         raise Exception(f"Error: {response.status_code}: {response.text}")
