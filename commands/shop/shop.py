import discord
from discord.ext import commands
from util.tools import fetch_all_tools
import asyncio


def sort_tools(tool):
    tool_order = {'flimsy': 0, 'golden': 2}
    for key in tool_order:
        if key in tool:
            return tool_order[key], tool
    return 1, tool


def generate_shop_message(info):
    sorted_tools = sorted(info, key=lambda tool: sort_tools(tool.get('name')))
    message = discord.Embed(title='Nook\'s Cranny',
                            color=0x9dffb0)
    message.set_thumbnail(url='https://dodo.ac/np/images/3/3c/Timmy_%26_Tommy_NL.png')
    for item in sorted_tools:
        price_info = item.get('price', [])

        if price_info:
            price_info = item.get('price')
            for price in price_info:
                cost = price.get('price')
                currency = price.get('currency')
                if currency == 'Bells':
                    message.add_field(name=f'{item.get('name').title()}',
                                      value=f'**Price:** {cost} Bells',
                                      inline=False)
        else:
            message.add_field(name=f'{item.get('name').title()}',
                              value=f'**Price:** {item.get('sell')} Bells',
                              inline=False)
    return message


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='shop', description='Explore what Nook\'s Cranny has in store to purchase')
    async def shop(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        buttons = ['\u2B05', '\u27A1']
        tool_names = ['axe', 'shovel', 'fishing rod', 'net']
        tool_info = [fetch_all_tools(tool) for tool in tool_names]
        pages = [generate_shop_message(info) for info in tool_info]
        current_page = 0
        message = await ctx.respond(embed=pages[current_page])
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
                elif react.emoji == buttons[1] and current_page < len(pages) - 1:
                    current_page += 1
                await message.edit(embed=pages[current_page])


def setup(bot):
    bot.add_cog(Shop(bot))
