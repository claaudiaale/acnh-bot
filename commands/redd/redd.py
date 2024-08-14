import discord
from discord.ext import commands
import random
import asyncio
import string
from util.redd import fetch_all_art, fetch_one_art


def generate_art_message(art_info):
    message = discord.Embed(title=f'{art_info['name'].title()}',
                            color=0x9dffb0,
                            description=f'{art_info['art_name']}')
    message.add_field(name='Author',
                      value=f'{art_info['author']}',
                      inline=False)
    message.add_field(name='Year',
                      value=f'{string.capwords(art_info['year'])}',
                      inline=False)
    message.add_field(name='Type, Style',
                      value=f'{art_info['art_type']}, {art_info['art_style']}',
                      inline=False)

    thumbnail = None

    if art_info['art_type'] == 'Painting':
        if art_info['texture_url']:
            thumbnail = art_info['texture_url']
        elif art_info['fake_texture_url']:
            thumbnail = art_info['fake_texture_url']
    else:
        if art_info['image_url']:
            thumbnail = art_info['image_url']
        elif art_info['fake_image_url']:
            thumbnail = art_info['fake_image_url']

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
        buttons = ['\u2B05', '\u27A1']
        pages = []
        artwork = fetch_all_art()
        current_shop = random.sample(artwork, 3)

        for art in current_shop:
            art_info = fetch_one_art(art['name'].replace(' ', '_'))
            if art_info['has_fake'] and art_info['art_type'] == 'Painting':
                decision = random.choice(['fake_texture_url', 'texture_url'])
                art_info[decision] = ''
                pages.append(generate_art_message(art_info))
            elif art_info['has_fake'] and art_info['art_type'] == 'Statue':
                decision = random.choice(['fake_image_url', 'image_url'])
                art_info[decision] = ''
                pages.append(generate_art_message(art_info))
            else:
                pages.append(generate_art_message(art_info))
            print(art_info)

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


def setup(bot):
    bot.add_cog(Redd(bot))
