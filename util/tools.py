import requests
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_tools(tool_name, parameter=None):
    url = f'https://api.nookipedia.com/nh/tools/{tool_name}'
    headers = {
        'X-API-KEY': os.getenv(f'ACNH_API_KEY'),
        'Accept-Version': '1.0.0'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        uses = data.get('uses')
        if '–' in uses:
            max_uses = uses.split('–')
            uses = int(max_uses[1])
        else:
            uses = int(uses)
            if uses > 10:
                uses = uses * 0.2

        tool_info = {
            'name': data.get('name'),
            'uses': uses,
            'image_url': data.get('url'),
            'sell': data.get('sell'),
            'price': data.get('buy')
        }
        return tool_info
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")