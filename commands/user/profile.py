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
        'health': 5,
        'bells': 100000,
        'villagers': new_villagers,
        'fruit': random.choice(['apple', 'cherry', 'orange', 'peach', 'pear'])
    })

    add_museum(user_id)
    add_limits(user_id)

    inventory = user_ref.collection('inventory')
    new_tools = ['flimsy_shovel', 'flimsy_fishing_rod', 'flimsy_net']
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


def add_museum(user_id):
    user_ref = db.collection('users').document(user_id).collection('museum')

    collection = ['bugs', 'fish', 'fossils']

    for specimen in collection:
        user_ref.document(specimen).set({
            'collected': []
        })


def add_limits(user_id):
    user_ref = db.collection('users').document(user_id).collection('daily')
    user_ref.document('limits').set({
        'campsite': False,
        'daily_command': False,
        'fossil_count': 0,
        'fruit_count': 0,
        'swarm_count': 0,
        'last_reset': ''
    })


def get_user_profile(user_id):
    user_profile = db.collection('users').document(user_id)
    return user_profile.get()


def reset_data(user_id, command):
    fields = ['campsite', 'daily_command', 'fossil_count', 'fruit_count', 'swarm_count']
    daily_limits = db.collection('users').document(user_id).collection('daily').document('limits')

    limits = daily_limits.get().to_dict()

    reset = {}
    for field in fields:
        if field != command:
            if isinstance(limits.get(field), bool):
                reset[field] = False
            elif isinstance(limits.get(field), int):
                reset[field] = 0

    daily_limits.update(reset)
    return


def update_profile(user_id, command):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    daily_limits = db.collection('users').document(user_id).collection('daily').document('limits')
    limits = daily_limits.get().to_dict()

    last_reset = limits.get('last_reset', '')
    check = limits.get(command)
    if command in ['fossil_count', 'fruit_count', 'swarm_count']:
        if last_reset != today or check < 5:
            if last_reset != today:
                reset_data(user_id, command)
            daily_limits.update({
                f'{command}': firestore.Increment(1),
                'last_reset': today
            })
            return True
    elif command in ['daily_command', 'campsite']:
        if last_reset != today or not check:
            if last_reset != today:
                reset_data(user_id, command)
            daily_limits.update({
                f'{command}': True,
                'last_reset': today
            })
            return True


def get_limit(user_id):
    daily_limits = db.collection('users').document(user_id).collection('daily').document('limits')
    return daily_limits.get().to_dict()


def generate_random_villager(user_id, new_profile=False):
    villagers_length = len(fetch_villagers())
    user_profile_ref = db.collection('users').document(user_id)
    user_profile = get_user_profile(user_id).to_dict()

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    seed = user_id + today.replace('-', '')
    random.seed(int(seed))

    if new_profile:
        visitor_ids = random.sample(range(1, villagers_length - 1), 2)
        return visitor_ids

    if not update_profile(user_id, 'campsite'):
        return user_profile.get('visitor')

    residents = user_profile.get('villagers')
    while True:
        visitor_id = random.randint(0, villagers_length - 1)
        if visitor_id not in residents:
            user_profile_ref.update({
                'visitor': visitor_id,
            })
            return visitor_id


def has_tool(user_id, item):
    user_ref = db.collection('users').document(user_id)
    inventory = user_ref.collection('inventory')
    tools = (inventory.where(filter=FieldFilter('remaining_uses', '>', 0))
                      .order_by('count', direction=firestore.Query.DESCENDING)
                      .order_by('remaining_uses', direction=firestore.Query.DESCENDING)).get()
    for tool in tools:
        if item in tool.get('name').lower():
            update_use = inventory.document(tool.id)
            if 'golden' in tool.get('name').lower():
                return 1
            else:
                update_use.update({
                    'remaining_uses': firestore.Increment(-1)
                })
                updated_item = inventory.document(tool.id).get()
                new_uses = updated_item.get('remaining_uses')
                count = updated_item.get('count')
                if new_uses > 0:
                    return 1
                elif new_uses == 0 and count > 1:
                    original_uses = updated_item.get('original_uses')
                    update_use.update({
                        'count': firestore.Increment(-1),
                        'remaining_uses': original_uses
                    })
                    return 1
                elif new_uses == 0 and count == 1:
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


def has_item(user_id, item, quantity):
    user_ref = db.collection('users').document(user_id)
    inventory_ref = user_ref.collection('inventory')
    inv_item = inventory_ref.where(filter=FieldFilter('name', '==', item)).get()

    if inv_item:
        count = inv_item[0].get('count')
        if quantity > int(count):
            return None, None
        else:
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


def update_health(user_id, quantity, add=False):
    user_ref = db.collection('users').document(user_id)
    if add:
        user_ref.update({
            'health': firestore.Increment(quantity)
        })
    else:
        user_ref.update({
            'health': firestore.Increment(-quantity)
        })

        updated_profile = user_ref.get()
        if updated_profile.get('health') == 0:
            user_ref.update({
                'health': 5
            })
            user_inventory = user_ref.collection('inventory')
            inventory = user_inventory.stream()
            for inv in inventory:
                inv.reference.delete()

            return (f'You lost all your health points and passed out. All items from your inventory were dropped, '
                    f'visit Nook\'s Cranny to repurchase tools!')
        else:
            return False


def add_to_museum(user_id, specimen_type, specimen_name):
    doc_ref = db.collection('users').document(user_id).collection('museum').document(specimen_type)
    current_museum = doc_ref.get()
    if specimen_name not in current_museum.to_dict().get('collected'):
        doc_ref.update({
            'collected': firestore.ArrayUnion([specimen_name])
        })
        return True
    else:
        return False


def get_museum_info(user_id, specimen_type):
    doc_ref = db.collection('users').document(user_id).collection('museum').document(specimen_type)
    return doc_ref.get().to_dict()


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='profile', description='View your profile')
    async def profile(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        fruit_emojis = {'apple': '\U0001F34E', 'cherry': '\U0001F352', 'orange': '\U0001F34A',
                        'peach': '\U0001F351', 'pear': '\U0001F350'}
        if is_registered(str(ctx.author.id)):
            await ctx.respond(f'Hello, {ctx.author.name}! Here\'s your current profile: ')
        else:
            create_user_profile(str(ctx.author.id))
            await ctx.respond(f'Welcome, {ctx.author.name}! Let\'s get a profile started for you.')

        user_profile = get_user_profile(str(ctx.author.id)).to_dict()

        native_fruit = user_profile['fruit']

        villagers = user_profile.get('villagers')
        villager_names = {get_villager_name(villager_id) for villager_id in villagers}
        islanders = '- ' + '\n- '.join(villager_names)

        user_ref = db.collection('users').document(str(ctx.author.id))
        user_inventory = user_ref.collection('inventory')
        items = user_inventory.stream()
        item_names = [item.to_dict().get('name').title() for item in items]
        inventory = '- ' + '\n- '.join(item_names)

        embed_profile = discord.Embed(title=ctx.author.name.title(),
                                      color=0x9dffb0,
                                      description=f'**Native Fruit:** {native_fruit.title()} '
                                                  f'{fruit_emojis[native_fruit]}\n'
                                                  f'**Health**: {user_profile['health']} \U00002764\U0000FE0F\n'
                                                  f'**Bells**: {user_profile['bells']} \U0001F514\n')
        embed_profile.set_thumbnail(url=ctx.author.avatar.url)
        embed_profile.add_field(name='Villagers \U000026FA', value=islanders, inline=True)
        embed_profile.add_field(name='\u200b', value='\u200b', inline=True)
        embed_profile.add_field(name='Inventory \U0001F392', value=inventory, inline=True)

        await ctx.send(embed=embed_profile)

    @commands.slash_command(name='daily', description='Get 10,000 free bells daily')
    async def daily(self, ctx: discord.ApplicationContext):
        if not update_profile(str(ctx.author.id), 'daily_command'):
            message = discord.Embed(color=0x9dffb0,
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

            limits = db.collection('users').document(str(ctx.author.id)).collection('daily').document('limits')
            limits.update({
                'daily_command': True
            })

            message = discord.Embed(color=0x81f1f7,
                                    description=f'Welcome back, {ctx.author.name}! Here\'s 10,000 bells for visiting, '
                                                f'come back tomorrow!')
            message.set_author(name='Tom Nook',
                               icon_url='https://dodo.ac/np/images/6/68/Tom_Nook_NH_Character_Icon.png')
            await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Profile(bot))
