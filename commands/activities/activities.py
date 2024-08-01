import discord
from discord.ext import commands
import datetime
import random
from util.activities import fetch_species, fetch_specimen, fetch_fossils


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


# def get_fossil_name(fossil_info):
#     fossil_group = fossil_info.get('fossil group', None)
#
#     if fossil_group:
#         if 'left' in fossil_info['name'] or 'right' in fossil_info['name']:
#             fossil_name = fossil_info['name'].split(' ')
#             fossil_name[1] = fossil_info['fossil group']
#             fossil_info['name'] = '_'.join(fossil_name)
#             return fossil_info
#         if '-' in fossil_info['name']:
#             fossil_info['name'] = fossil_info['name'].replace('-', ' ')
#             fossil_info['name'] = fossil_info['name'].replace(' ', '_')
#             return fossil_info
#         else:
#             if fossil_group == 'T. Rex':
#                 t_rex_part = fossil_info['name'].split(' ')
#                 t_rex_part[0] = 'T'
#                 fossil_info['name'] = '_'.join(t_rex_part)
#                 return fossil_info
#             fossil_name = fossil_info['name'].split(' ')
#             fossil_name[0] = fossil_info['fossil group']
#             fossil_info['name'] = '_'.join(fossil_name)
#     return fossil_info


class Activities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='fish', description='Use your fishing rod to fish')
    async def fish(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        catch = generate_random_specimen('fish')
        fish_info = fetch_specimen('fish', catch['name'])[0]

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

    @commands.slash_command(name='bug', description='Use your net to catch bugs')
    async def bug(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        catch = generate_random_specimen('bugs')
        bug_info = fetch_specimen('bugs', catch['name'])[0]

        message = discord.Embed(title=f'{bug_info.get('name').title()}',
                                color=0x81f1f7,
                                description=f'{bug_info.get('catchphrase')}')
        message.set_thumbnail(url=f'{bug_info['render_url']}')
        message.add_field(name='',
                          value=f'**Location:** {bug_info.get('location')}\n'
                                f'**Price:** {bug_info.get('sell_nook')}')
        await ctx.respond(embed=message)

    @commands.slash_command(name='dig', description='Use your shovel to dig for fossils')
    async def dig(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        catch = generate_random_specimen('fossils')
        fossil_info = fetch_specimen('fossils', catch['name'].replace(' ', '_'))
        # full_fossil_info = fetch_fossil_group(catch['fossil group'])

        message = discord.Embed(title=f'{fossil_info.get('name').title()}',
                                color=0x81f1f7)
        message.set_thumbnail(url=f'{fossil_info['image_url']}')
        message.add_field(name='',
                          value=f'**Price:** {fossil_info.get('sell')}')
        await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Activities(bot))
