import discord
from discord.ext import commands
import datetime
import random
from views.database import db, is_registered
from util.villagers import fetch_villagers, get_villager_name
from util.tools import fetch_tools


def create_user_profile(user_id, username):
    new_villagers = generate_random_villager(user_id, new_profile=True)
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'username': username,
        'health': 3,
        'bells': 100000,
        'villagers': new_villagers,
        'museum': []
    })

    inventory_subcollection = user_ref.collection('inventory')
    new_tools = ['flimsy_axe', 'flimsy_shovel', 'flimsy_fishing_rod', 'flimsy_net']
    information = [fetch_tools(tools) for tools in new_tools]
    new_user_tools = [{
        'name': info.get('name'),
        'remaining uses': info.get('uses'),
        'image url': info.get('image_url'),
        'price': info.get('price')[0].get('price'),
        'sell': info.get('sell')
    } for tool, info in zip(new_tools, information)]

    for tool in new_user_tools:
        inventory_subcollection.add(tool)

    return user_ref.get()


def get_user_profile(user_id):
    user_profile = db.collection('users').document(user_id)
    return user_profile.get()


def generate_random_villager(user_id, new_profile=False):
    villagers_length = len(fetch_villagers())
    user_profile_ref = db.collection('users').document(user_id)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    random.seed(today)

    if new_profile:
        visitor_ids = random.sample(range(1, villagers_length - 1), 2)
        return visitor_ids
    else:
        user_profile = get_user_profile(user_id).to_dict()
        visitor_date = user_profile.get('visitor_date')

        if visitor_date == today:
            return user_profile.get('visitor')

        residents = user_profile.get('villagers')
        while True:
            visitor_id = random.randint(0, villagers_length - 1)
            if visitor_id not in residents:
                user_profile_ref.update({
                    'visitor': visitor_id,
                    'visitor_date': today
                })
                return visitor_id


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='profile', description='View your profile')
    async def profile(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        if is_registered(str(ctx.author.id)):
            await ctx.respond(f'Hello, {ctx.author.name}! Here\'s your current profile: ')
        else:
            create_user_profile(str(ctx.author.id), ctx.author.name)
            await ctx.respond(f'Welcome, {ctx.author.name}! Let\'s get a profile started for you.')

        user_profile = get_user_profile(str(ctx.author.id)).to_dict()
        villagers = user_profile.get('villagers', [])
        villager_names = {get_villager_name(villager_id) for villager_id in villagers}

        islanders = '- ' + '\n- '.join(villager_names)
        inventory = '- ' + '\n- '.join(user_profile.get('inventory', []))
        museum = '- ' + '\n- '.join(user_profile.get('museum', []))
        embed_profile = discord.Embed(title=user_profile['username'],
                                      color=0x81f1f7,
                                      description=f'**Health**: {user_profile['health']}\n'
                                                  f'**Bells**: {user_profile['bells']}\n')
        embed_profile.set_thumbnail(url=ctx.author.avatar.url)
        embed_profile.add_field(name='Villagers', value=islanders, inline=True)
        embed_profile.add_field(name='\u200b', value='\u200b', inline=True)
        embed_profile.add_field(name='Inventory', value=inventory, inline=True)
        embed_profile.add_field(name='Museum', value=museum, inline=False)

        await ctx.channel.send(embed=embed_profile)


def setup(bot):
    bot.add_cog(Profile(bot))
