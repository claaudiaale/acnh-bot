import discord
from discord.ext import commands
import views.database
from views.database import db
from villagers.villagers import generate_random_villager
from villagers.villager_info import get_villager_info


def create_user_profile(user_id, username):
    new_villagers = generate_random_villager(user_id, 2)
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'username': username,
        'health': 3,
        'bells': 100000,
        'villagers': new_villagers,
        'inventory': [],
        'museum': []
    })
    return user_ref.get()


def get_user_profile(user_id):
    user_profile = db.collection('users').document(user_id)
    return user_profile.get()


def get_villager_name(villager_id):
    villager_info = get_villager_info(villager_id)
    return villager_info['name']


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='profile', description='View your profile')
    async def profile(self, ctx: discord.ApplicationContext):
        if views.database.is_registered(str(ctx.author.id)):
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
