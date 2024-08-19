import discord
from discord.ext import commands
import string
import datetime
from commands.user.profile import (generate_random_art, get_user_profile, add_to_inventory, update_bells,
                                   update_purchased_art)
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
    return day == 'Monday'


async def get_artwork(current_shop, artwork):
    for art in current_shop:
        if artwork == art['name'].lower():
            if not art['purchased']:
                return art
            elif art['purchased']:
                message = discord.Embed(color=0x9dffb0,
                                        description=f'My art is one of a kind, you\'ve already purchased this piece. '
                                                    f'I\'ll be back next week with new pieces!')
                message.set_author(name='Redd',
                                   icon_url='https://dodo.ac/np/images/f/f3/Redd_NL.png')
                return message
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
    async def buyredd(self, ctx: discord.ApplicationContext, artwork: str):
        await ctx.defer()
        art = artwork.lower().strip()
        buttons = ['\u274C', '\u2705']

        if not await check_for_redd():
            await ctx.respond('Redd only visits your island on Sundays, please try again another day.')
            return

        user_profile = get_user_profile(str(ctx.author.id))
        current_shop = user_profile.get('artwork')

        can_buy = await get_artwork(current_shop, art)
        if not can_buy:
            await ctx.respond('This piece of art is currently not available in shop.')
            return
        elif isinstance(can_buy, dict):
            await ctx.respond(embed=generate_art_message(can_buy))
            confirmation = await ctx.send(f'Buy **{art.title()}** for '
                                          f'4980 Bells?')
            for b in buttons:
                await confirmation.add_reaction(b)

            react, user = await handle_user_selection(self, ctx, confirmation, buttons)
            if react:
                if react.emoji == buttons[0]:
                    await confirmation.delete()
                    await ctx.send(f'Buy action cancelled.')
                    return
                elif react.emoji == buttons[1]:
                    add = add_to_inventory(str(ctx.author.id), can_buy, 1)
                    update_bells(str(ctx.author.id), 4980, buy=True)
                    update_purchased_art(str(ctx.author.id), art)

                    message = discord.Embed(color=0x9dffb0,
                                            description=f'You just bought **{art.title()}**. '
                                                        f'Thanks for visiting, come back again soon!')
                    message.set_author(name='Redd',
                                       icon_url='https://dodo.ac/np/images/f/f3/Redd_NL.png')
                    await ctx.send(embed=message)
                    if add:
                        await ctx.send(add)
        else:
            await ctx.respond(embed=can_buy)

    @commands.slash_command(name='artworkinfo', description='Show information about a piece of art')
    async def artworkinfo(self, ctx: discord.ApplicationContext, artwork: str):
        await ctx.defer()
        try:
            artwork_info = fetch_one_art(artwork.lower().strip().replace(' ', '_'))
            if artwork_info['art_type'] == 'Painting':
                artwork_info['url'] = artwork_info['texture_url']
            elif artwork_info['art_type'] == 'Statue':
                artwork_info['url'] = artwork_info['image_url']

            message = generate_art_message(artwork_info)
            await ctx.respond(embed=message)
        except Exception as e:
            if '404' in str(e):
                message = discord.Embed(color=0x9dffb0,
                                        description=f'Hmm...I can\'t find any information on that piece at the '
                                                    f'moment...')
                message.set_author(name='Blathers',
                                   icon_url='https://dodo.ac/np/images/1/1b/Blathers_NH.png')
                await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Redd(bot))
