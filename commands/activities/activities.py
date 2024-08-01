import discord
from discord.ext import commands
import datetime
import random
from util.fish import fetch_fish, fetch_single_fish


def generate_random_fish():
    current_month = datetime.datetime.now().strftime('%m')
    available_fish = fetch_fish(current_month)

    rarity = {
        'Common': 0.75,
        'Uncommon': 0.25,
        'Rare': 0.1
    }

    fish_list = []
    for fish in available_fish:
        fish_list.extend([fish] * int(rarity[fish['rarity']] * 100))

    catch = random.choice(fish_list)
    return catch


class Activities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='fish', description='Use your fishing rod to fish')
    async def fish(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        catch = generate_random_fish()
        fish_info = fetch_single_fish(catch['name'])[0]

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


def setup(bot):
    bot.add_cog(Activities(bot))
