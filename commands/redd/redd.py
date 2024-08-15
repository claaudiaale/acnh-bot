import discord
from discord.ext import commands
import string
import datetime
from commands.user.profile import generate_random_art, get_user_profile, add_to_inventory, update_bells
from util.redd import fetch_one_art
from util.embed import embed_arrows, handle_user_selection


def generate_art_message(art_info):
    art_full_info = fetch_one_art(f'{art_info['name'].replace(' ', '_')}')
    message = discord.Embed(title=f'{art_info['name'].title()}',
                            color=0x9dffb0,
                            description=f'{art_full_info['art_name']}')
    message.add_field(name='Author',
                      value=f'{art_full_info['author']}',
                      inline=False)
    message.add_field(name='Year',
                      value=f'{string.capwords(art_full_info['year'])}',
                      inline=False)
    message.add_field(name='Type, Style',
                      value=f'{art_full_info['art_type']}, {art_full_info['art_style']}',
                      inline=False)

    thumbnail = art_info['url']

    message.set_thumbnail(url=thumbnail)

    message_dict = message.to_dict()
    message_dict['url'] = thumbnail
    message_embed = discord.Embed.from_dict(message_dict)

    return message_embed


async def check_for_redd():
    day = datetime.datetime.now().strftime('%A')
    return day == 'Sunday'


async def get_artwork(current_shop, artwork):
    artwork_name = artwork.lower()
    for art in current_shop:
        if artwork_name == art['name'].lower():
            return art
    return None


class Redd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='shopredd', description='See what artwork Redd has to sell')
    async def shopredd(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        if not await check_for_redd():
            await ctx.respond('Redd only visits your island on Sundays, please try again another day.')
            return

        pages = []
        current_shop = generate_random_art(str(ctx.author.id))

        for art in current_shop:
            pages.append(generate_art_message(art))

        await embed_arrows(self, ctx, pages)

    @commands.slash_command(name='buyredd', description='Buy artwork from Redd')
    async def buyredd(self, ctx: discord.ApplicationContext, quantity: int, artwork: str):
        await ctx.defer()
        buttons = ['\u274C', '\u2705']

        if not await check_for_redd():
            await ctx.respond('Redd only visits your island on Sundays, please try again another day.')
            return

        user_profile = get_user_profile(str(ctx.author.id))
        current_shop = user_profile.get('artwork')

        can_buy = await get_artwork(current_shop, artwork)
        if not can_buy:
            await ctx.respond('This piece of art is currently not available in shop.')
            return

        await ctx.respond(embed=generate_art_message(can_buy))
        confirmation = await ctx.send(f'Buy **{quantity}x {artwork.title()}** for '
                                      f'{4980 * quantity} Bells?')
        for b in buttons:
            await confirmation.add_reaction(b)

        while True:
            react, user = await handle_user_selection(self, ctx, confirmation, buttons)
            if not react:
                return

            else:
                if react.emoji == buttons[0]:
                    await confirmation.delete()
                    await ctx.send(f'Buy action cancelled.')
                    return
                elif react.emoji == buttons[1]:
                    add = add_to_inventory(str(ctx.author.id), can_buy, quantity)
                    update_bells(str(ctx.author.id), (4980 * quantity), buy=True)

                    message = discord.Embed(color=0x9dffb0,
                                            description=f'You just bought **{quantity}x '
                                                        f'{artwork.title()}**. '
                                                        f'Thanks for visiting, come back again soon!')
                    message.set_author(name='Redd',
                                       icon_url='https://dodo.ac/np/images/f/f3/Redd_NL.png')
                    await ctx.send(embed=message)
                    if add:
                        await ctx.send(add)


def setup(bot):
    bot.add_cog(Redd(bot))
