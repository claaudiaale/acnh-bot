import discord
from discord.ext import commands
import datetime
import random
from util.activities import fetch_species, fetch_specimen, fetch_fossils, fetch_fossil_group, fetch_single_fossil
from commands.user.profile import add_to_inventory, has_tool


def generate_random_specimen(species):
    current_month = datetime.datetime.now().strftime('%m')
    if species == 'fossils':
        available_species = fetch_fossils()
    else:
        available_species = fetch_species(current_month, species)

    species_list = []
    if species == 'fish':
        rarity = {
            'Common': 0.75,
            'Uncommon': 0.25,
            'Rare': 0.1
        }

        for specimen in available_species:
            species_list.extend([specimen] * int(rarity[specimen['rarity']] * 100))
    else:
        species_list = available_species

    catch = random.choice(species_list)
    return catch


class Activities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='fish', description='Use your fishing rod to fish')
    async def fish(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool = has_tool(str(ctx.author.id), 'fishing rod')
        if tool:
            catch = generate_random_specimen('fish')
            fish_info = fetch_specimen('fish', catch['name'])[0]
            add = add_to_inventory(str(ctx.author.id), {'name': fish_info.get('name'),
                                                        'sell': int(fish_info.get('sell_nook'))}, 1)

            message = discord.Embed(title=f'{fish_info.get('name')}',
                                    color=0x81f1f7,
                                    description=f'{fish_info.get('catchphrase')}')
            message.set_thumbnail(url=f'{fish_info['render_url']}')
            message.add_field(name='',
                              value=f'**Location:** {fish_info.get('location')}\n'
                                    f'**Price:** {fish_info.get('sell_nook')}\n'
                                    f'**Rarity:** {fish_info.get('rarity')}',
                              inline=False)
            await ctx.respond(embed=message)
            if isinstance(tool, str):
                await ctx.send(tool)
            if add:
                await ctx.send(add)
        else:
            await ctx.respond(f'You don\'t have a fishing rod! Visit Nook\'s Cranny to buy one and fish.')

    @commands.slash_command(name='bug', description='Use your net to catch bugs')
    async def bug(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool = has_tool(str(ctx.author.id), 'net')
        if tool:
            catch = generate_random_specimen('bugs')
            bug_info = fetch_specimen('bugs', catch['name'])[0]
            add = add_to_inventory(str(ctx.author.id), {'name': bug_info.get('name'),
                                                        'sell': int(bug_info.get('sell_nook'))}, 1)

            message = discord.Embed(title=f'{bug_info.get('name').title()}',
                                    color=0x81f1f7,
                                    description=f'{bug_info.get('catchphrase')}')
            message.set_thumbnail(url=f'{bug_info['render_url']}')
            message.add_field(name='',
                              value=f'**Location:** {bug_info.get('location')}\n'
                                    f'**Price:** {bug_info.get('sell_nook')}')
            await ctx.respond(embed=message)
            if isinstance(tool, str):
                await ctx.send(tool)
            if add:
                await ctx.send(add)
        else:
            await ctx.respond(f'You don\'t have a net! Visit Nook\'s Cranny to buy one and catch bugs.')

    @commands.slash_command(name='dig', description='Use your shovel to dig for fossils')
    async def dig(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool = has_tool(str(ctx.author.id), 'shovel')
        if tool:
            catch = generate_random_specimen('fossils')
            fossil_info = fetch_specimen('fossils', catch['name'].replace(' ', '_'))
            add = add_to_inventory(str(ctx.author.id), {'name': fossil_info.get('name'),
                                                        'sell': fossil_info.get('sell')}, 1)
            fossil_group = fossil_info.get('fossil_group')
            if fossil_group:
                fossil_description = fetch_fossil_group(fossil_group)
            else:
                fossil_description = fetch_single_fossil(fossil_info.get('name'))

            message = discord.Embed(title=f'{fossil_info.get('name').title()}',
                                    color=0x81f1f7,
                                    description=f'{fossil_description}')
            message.set_thumbnail(url=f'{fossil_info['image_url']}')
            message.add_field(name='',
                              value=f'**Price:** {fossil_info.get('sell')}')
            await ctx.respond(embed=message)
            if isinstance(tool, str):
                await ctx.send(tool)
            if add:
                await ctx.send(add)
        else:
            await ctx.respond(f'You don\'t have a shovel! Visit Nook\'s Cranny to buy one and dig for fossils.')


def setup(bot):
    bot.add_cog(Activities(bot))
