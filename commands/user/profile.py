import discord
from discord.ext import commands
import datetime
import random

from google.cloud.firestore_v1 import FieldFilter
from google.cloud import firestore

from views.database import db, is_registered
from util.villagers import fetch_villagers, get_villager_name
from util.tools import fetch_tools


def create_user_profile(user_id):
    new_villagers = generate_random_villager(user_id, new_profile=True)
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'health': 3,
        'bells': 100000,
        'villagers': new_villagers,
        'museum': []
    })

    inventory = user_ref.collection('inventory')
    new_tools = ['flimsy_axe', 'flimsy_shovel', 'flimsy_fishing_rod', 'flimsy_net']
    information = [fetch_tools(tools) for tools in new_tools]
    new_user_tools = [{
        'name': info.get('name'),
        'remaining_uses': info.get('uses'),
        'price': info.get('price')[0].get('price'),
        'sell': info.get('sell'),
        'count': 1
    } for tool, info in zip(new_tools, information)]

    for tool in new_user_tools:
        inventory.add(tool)

    return user_ref.get()


def get_user_profile(user_id):
    user_profile = db.collection('users').document(user_id)
    return user_profile.get()


def update_profile(user_id, command):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    user_profile = get_user_profile(user_id).to_dict()
    last_update = user_profile.get(f'{command}_last_update', '')

    if last_update != today:
        return True
    return False


def generate_random_villager(user_id, new_profile=False):
    villagers_length = len(fetch_villagers())
    user_profile_ref = db.collection('users').document(user_id)
    user_profile = get_user_profile(user_id).to_dict()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    random.seed(today)

    if new_profile:
        visitor_ids = random.sample(range(1, villagers_length - 1), 2)
        return visitor_ids

    if not update_profile(user_id, 'visitor'):
        return user_profile.get('visitor')

    residents = user_profile.get('villagers')
    while True:
        visitor_id = random.randint(0, villagers_length - 1)
        if visitor_id not in residents:
            user_profile_ref.update({
                'visitor': visitor_id,
                'visitor_last_update': today
            })
            return visitor_id


def has_tool(user_id, item):
    user_ref = db.collection('users').document(user_id)
    inventory = user_ref.collection('inventory')

    tools = inventory.where(filter=FieldFilter('remaining_uses', '>', 0)).get()

    for tool in tools:
        if item in tool.get('name').lower():
            doc_id = tool.id
            update_use = inventory.document(doc_id)
            current_uses = tool.get('remaining_uses')
            if current_uses - 1 > 0:
                update_use.update({
                    'remaining_uses': current_uses - 1
                })
                return 1
            else:
                update_use.delete()
                return f'Your {item} broke! Visit Nook\'s Cranny to buy a new one.'

    return False


def add_to_inventory(user_id, item, quantity):
    user_ref = db.collection('users').document(user_id)
    inventory = user_ref.collection('inventory')
    count = inventory.count()
    inventory_count = count.get()

    if inventory_count[0][0].value <= 18:
        add_inventory_stack(user_id, item, quantity)
        return
    if inventory_count[0][0].value == 19:
        add_inventory_stack(user_id, item, quantity)
        return (f'Your pockets are full! **The next specimen you catch will be released.** Visit Nook\'s Cranny to '
                f'sell items and empty your inventory.')
    else:
        return f'...Huh? Your pockets are full already! Visit Nook\'s Cranny to sell items and empty your inventory.'


def add_inventory_stack(user_id, item, quantity):
    user_ref = db.collection('users').document(user_id)
    inventory_ref = user_ref.collection('inventory')
    inv_item = inventory_ref.where(filter=FieldFilter('name', '==', item.get('name').lower())).get()

    if inv_item:
        matched_item = inventory_ref.document(inv_item[0].id)
        matched_item.update({
            'count': firestore.Increment(quantity)
        })
    else:
        item['count'] = quantity
        inventory_ref.add(item)


def has_item(user_id, item):
    user_ref = db.collection('users').document(user_id)
    inventory_ref = user_ref.collection('inventory')
    inv_item = inventory_ref.where(filter=FieldFilter('name', '==', item)).get()

    if inv_item:
        return inv_item[0].to_dict(), inv_item[0].id
    else:
        return None, None


def remove_from_inventory(user_id, item_id, quantity):
    user_ref = db.collection('users').document(user_id)
    inventory = user_ref.collection('inventory')

    inventory.document(item_id).update({
        'count': firestore.Increment(-quantity)
    })

    updated_item = inventory.document(item_id).get()
    new_count = updated_item.get('count')
    if new_count == 0:
        inventory.document(item_id).delete()
    return


def update_bells(user_id, bells, buy=False):
    user_ref = db.collection('users').document(user_id)

    if buy:
        user_ref.update({
            'bells': firestore.Increment(-bells)
        })
        return
    else:
        user_ref.update({
            'bells': firestore.Increment(bells)
        })
        return


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='profile', description='View your profile')
    async def profile(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        if is_registered(str(ctx.author.id)):
            await ctx.respond(f'Hello, {ctx.author.name}! Here\'s your current profile: ')
        else:
            create_user_profile(str(ctx.author.id))
            await ctx.respond(f'Welcome, {ctx.author.name}! Let\'s get a profile started for you.')

        user_profile = get_user_profile(str(ctx.author.id)).to_dict()
        villagers = user_profile.get('villagers', [])
        villager_names = {get_villager_name(villager_id) for villager_id in villagers}
        islanders = '- ' + '\n- '.join(villager_names)

        user_ref = db.collection('users').document(str(ctx.author.id))
        user_inventory = user_ref.collection('inventory')
        items = user_inventory.stream()
        item_names = [item.to_dict().get('name').title() for item in items]
        inventory = '- ' + '\n- '.join(item_names)

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

    @commands.slash_command(name='daily', description='Get 10,000 free bells daily')
    async def daily(self, ctx: discord.ApplicationContext):
        if not update_profile(str(ctx.author.id), 'daily'):
            message = discord.Embed(color=0x81f1f7,
                                    description=f'Welcome back, {ctx.author.name}. You\'ve already claimed your daily '
                                                f'reward, come back tomorrow!')
            message.set_author(name='Tom Nook',
                               icon_url='https://dodo.ac/np/images/6/68/Tom_Nook_NH_Character_Icon.png')
            await ctx.respond(embed=message)

        else:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            user_ref = db.collection('users').document(str(ctx.author.id))
            update_bells(str(ctx.author.id), 10000)
            user_ref.update({
                'daily_last_update': today
            })

            message = discord.Embed(color=0x81f1f7,
                                    description=f'Welcome back, {ctx.author.name}! Here\'s 10,000 bells for visiting, '
                                                f'come back tomorrow!')
            message.set_author(name='Tom Nook',
                               icon_url='https://dodo.ac/np/images/6/68/Tom_Nook_NH_Character_Icon.png')
            await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Profile(bot))
