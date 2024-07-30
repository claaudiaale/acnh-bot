import discord
from discord.ext import commands
from dotenv import load_dotenv
from views.database import db
import asyncio
from util.villagers import generate_random_villager, get_villager_info, get_villager_name
from commands.user.profile import get_user_profile

load_dotenv()


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


class Villagers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='villagerinfo', description='Get information about a villager by their name')
    async def villagerinfo(self, ctx: discord.ApplicationContext, villager: str):
        message = generate_villager_message(villager)
        await ctx.respond(embed=message)

    @commands.slash_command(name='residents', description='View all current island residents')
    async def residents(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        buttons = ['\u2B05', '\u27A1']
        user_profile = get_user_profile(str(ctx.author.id))
        residents = [(generate_villager_message(resident)) for resident in user_profile.get('villagers')]
        current_page = 0
        message = await ctx.respond(embed=residents[current_page])
        for b in buttons:
            await message.add_reaction(b)

        while True:
            try:
                react, user = await self.bot.wait_for('reaction_add', timeout=60, check=lambda r, u: r.message.id ==
                                                      message.id and u.id == ctx.author.id and r.emoji in buttons)
                await message.remove_reaction(react.emoji, user)
            except asyncio.TimeoutError:
                return await message.delete()

            else:
                if react.emoji == buttons[0] and current_page > 0:
                    current_page -= 1
                elif react.emoji == buttons[1] and current_page < len(residents) - 1:
                    current_page += 1
                await message.edit(embed=residents[current_page])

    @commands.slash_command(name='kick', description='Kick a resident from your island')
    async def kick(self, ctx: discord.ApplicationContext, resident: str):
        await ctx.defer()
        buttons = ['\u274C', '\u2705']
        user_profile = get_user_profile(str(ctx.author.id)).to_dict()
        villagers = user_profile.get('villagers')
        names_and_id = {(get_villager_name(villager_id), villager_id) for villager_id in villagers}
        for name, villager_id in names_and_id:
            if name.lower() == resident:
                confirm = await ctx.respond(f'Are you sure you want to kick **{resident.title()}** from your island?')
                for b in buttons:
                    await confirm.add_reaction(b)

                while True:
                    try:
                        react, user = await self.bot.wait_for(
                            'reaction_add', timeout=60, check=lambda r, u: r.message.id ==
                            confirm.id and u.id == ctx.author.id and r.emoji in buttons)
                        await confirm.remove_reaction(react.emoji, user)
                    except asyncio.TimeoutError:
                        return await confirm.delete()

                    else:
                        if react.emoji == buttons[0]:
                            await confirm.delete()
                            await ctx.respond(f'Kick action cancelled.')
                            return
                        elif react.emoji == buttons[1]:
                            user_profile_ref = db.collection('users').document(str(ctx.author.id))
                            villagers.remove(villager_id)
                            user_profile_ref.update({'villagers': villagers})
                            await ctx.respond(f'{resident.title()} has been kicked from your island.')
                            return
        await ctx.respond(f'**{resident.title()}** is not a current resident on your island!')

    @commands.slash_command(name='campsite', description='Check your campsite for a visitor')
    async def campsite(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        visitor_id = generate_random_villager(str(ctx.author.id))
        message = generate_villager_message(visitor_id)
        await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Villagers(bot))
