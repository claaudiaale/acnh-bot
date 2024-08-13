import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_species(month, species):
    url = f'https://api.nookipedia.com/nh/{species}'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }
    params = {}
    if month is not None:
        params['month'] = month
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
    else:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return len(response.json())


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


def fetch_fossil_group(fossil_group):
    url = f'https://api.nookipedia.com/nh/fossils/all/{fossil_group}'

    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['description']
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def fetch_single_fossil(fossil_name):
    url = "https://nookipedia.com/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'titles': fossil_name,
        'prop': 'revisions',
        'rvprop': 'content',
        'rvparse': True
    }

    response = requests.get(url, params=params)
    data = response.json()

    pages = data.get('query').get('pages')
    for page_id, page in pages.items():
        information = page.get('revisions')[0].get('*')
        # print(information)
        description = get_description(information)
        return description


def get_description(information):
    pattern = re.compile(r'<div class="blathers-text">.*?<i>(.*?)</i></div>', re.DOTALL)
    match = pattern.search(information)
    text = match.group(1).strip()
    return text.strip('"')


def fetch_item_info(item_name):
    url = f'https://api.nookipedia.com/nh/items/{item_name}'

    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def fetch_clothing_info(item_name):
    url = f'https://api.nookipedia.com/nh/clothing/{item_name}'

    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        data['uses'] = 8
        data['price'] = data['buy']
        return data
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")
