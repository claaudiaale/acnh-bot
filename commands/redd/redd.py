import discord
from discord.ext import commands
import asyncio
import string
import datetime
from commands.user.profile import generate_random_art
from util.redd import fetch_one_art


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


class Redd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='shopredd', description='See what artwork Redd has to sell')
    async def shopredd(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        day = datetime. datetime.now().strftime('%A')
        if day == 'Sunday':
            buttons = ['\u2B05', '\u27A1']
            pages = []
            current_shop = generate_random_art(str(ctx.author.id))

            for art in current_shop:
                pages.append(generate_art_message(art))

            current_page = 0
            message = await ctx.respond(embed=pages[current_page])
            for b in buttons:
                await message.add_reaction(b)

            while True:
                try:
                    react, user = await self.bot.wait_for('reaction_add', timeout=60,
                                                          check=lambda r, u: r.message.id == message.id
                                                          and u.id == ctx.author.id and r.emoji in buttons)
                    await message.remove_reaction(react.emoji, user)
                except asyncio.TimeoutError:
                    return await message.delete()

                else:
                    if react.emoji == buttons[0] and current_page > 0:
                        current_page -= 1
                    elif react.emoji == buttons[1] and current_page < len(pages) - 1:
                        current_page += 1
                    await message.edit(embed=pages[current_page])
        elif day != 'Sunday':
            await ctx.respond('Redd only visits your island on Sundays, please try again another day.')

    # @commands.slash_command(name='shopredd', description='See what artwork Redd has to sell')
    # async def shopredd(self, ctx: discord.ApplicationContext):
    #     pass


def setup(bot):
    bot.add_cog(Redd(bot))
