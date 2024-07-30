import discord
from discord.ext import commands
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


def generate_villager_message(identifier):
    villager_info = get_villager_info(identifier)
    villager_colour = villager_info['title_color']
    message = discord.Embed(title=f'{villager_info['name']}',
                            color=int(villager_colour, 16),
                            description=f'{villager_info['quote']}')
    message.set_thumbnail(url=f'{villager_info['image_url']}')
    message.add_field(name='Species',
                      value=f'{villager_info['species']}',
                      inline=True)
    message.add_field(name='Personality',
                      value=f'{villager_info['personality']}',
                      inline=True)
    message.add_field(name='Gender',
                      value=f'{villager_info['gender']}',
                      inline=True)
    message.add_field(name='Sign',
                      value=f'{villager_info['sign']}',
                      inline=True)
    message.add_field(name='Birthday',
                      value=f'{villager_info['birthday_month'] + ' '
                               + villager_info['birthday_day']}',
                      inline=True)
    message.add_field(name='Catchphrase',
                      value=f'{villager_info['phrase']}',
                      inline=True)
    return message


class Villager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='villager', description='Get information about a villager by their name')
    async def villager(self, ctx: discord.ApplicationContext, villager_name: str):
        message = generate_villager_message(villager_name)
        await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Villager(bot))
