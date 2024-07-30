import datetime
import random
import requests
import os
from dotenv import load_dotenv
from views.database import db

load_dotenv()


def fetch_all_villagers():
    url = 'https://api.nookipedia.com/villagers'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }
    params = {'game': 'NH'}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")


def generate_random_villager(user_id, number_of_villagers=1):
    villagers_length = len(fetch_all_villagers())
    user_profile_ref = db.collection('users').document(user_id)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    random.seed(today)
    if number_of_villagers == 1:
        visitor_id = random.randint(0, villagers_length - 1)
        user_profile_ref.update(
            {'visitor': visitor_id}
        )
        return visitor_id
    else:
        visitor_ids = random.sample(range(1, villagers_length - 1), number_of_villagers)
        return visitor_ids
