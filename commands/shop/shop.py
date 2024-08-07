import discord
from discord.ext import commands
from util.tools import fetch_all_tools, fetch_tools
from commands.user.profile import add_to_inventory, has_item, remove_from_inventory, add_bells
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

        if len(price_info) > 0:
            price_info = item.get('price')[0]
            cost = price_info.get('price')
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

    @commands.slash_command(name='buy', description='Buy items from Nook\'s Cranny')
    async def buy(self, ctx: discord.ApplicationContext, quantity: int, item: str):
        buttons = ['\u274C', '\u2705']
        item_info = fetch_tools(item.replace(' ', '_'))
        price_info = item_info.get('price', [])

        if len(price_info) > 0:
            price_info = item_info.get('price')[0]
            cost = price_info.get('price')
            confirmation = await ctx.send(f'Buy **{quantity}x {item.title()}** for {cost * quantity} Bells?')
        else:
            confirmation = await ctx.send(f'Buy **{quantity}x {item.title()}** for {item_info.get('sell') *
                                                                                    quantity} Bells?')
        for b in buttons:
            await confirmation.add_reaction(b)

        while True:
            try:
                react, user = await self.bot.wait_for(
                    'reaction_add', timeout=60,
                    check=lambda r, u: r.message.id == confirmation.id and u.id == ctx.author.id and r.emoji in buttons)
                await confirmation.remove_reaction(react.emoji, user)
            except asyncio.TimeoutError:
                return await confirmation.delete()

            else:
                if react.emoji == buttons[0]:
                    await confirmation.delete()
                    await ctx.send(f'Buy action cancelled.')
                    return
                elif react.emoji == buttons[1]:
                    add = add_to_inventory(str(ctx.author.id), {'name': item_info.get('name'),
                                                                'remaining_uses': item_info.get('uses'),
                                                                'price': item_info.get('price')[0].get('price'),
                                                                'sell': item_info.get('sell')})

                    message = discord.Embed(color=0x81f1f7,
                                            description=f'You just bought **{quantity}x {item.title()}**. '
                                                        f'Thanks for visiting us, come back again soon!')
                    message.set_author(name='Timmy and Tommy',
                                       icon_url='https://play.nintendo.com/'
                                                'images/masthead-img-timmy-tommy.f4b49fb7.cf659c6f.png')
                    await ctx.send(embed=message)
                    if add:
                        await ctx.send(add)

    @commands.slash_command(name='sell', description='Sell items from your inventory to Timmy and Tommy')
    async def sell(self, ctx: discord.ApplicationContext, quantity: int, item: str):
        await ctx.defer()
        buttons = ['\u274C', '\u2705']
        inv_item = has_item(str(ctx.author.id), item)
        if inv_item[0]:
            confirmation = discord.Embed(color=0x81f1f7,
                                         description=f'**{item.title()}?** Sure! How about if I offer you '
                                                     f'{inv_item[0].get('sell')} Bells?')
            confirmation.set_author(name='Timmy and Tommy',
                                    icon_url='https://play.nintendo.com/'
                                             'images/masthead-img-timmy-tommy.f4b49fb7.cf659c6f.png')
            message = await ctx.respond(embed=confirmation)

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
                    if react.emoji == buttons[0]:
                        await message.delete()
                        await ctx.send(f'Sell action cancelled.')
                        return
                    elif react.emoji == buttons[1]:
                        remove_from_inventory(str(ctx.author.id), inv_item[1])
                        add_bells(str(ctx.author.id), inv_item[0].get('sell'))

                        message = discord.Embed(color=0x81f1f7,
                                                description=f'You just sold **{quantity}x {item.title()}**. Thanks '
                                                            f'for visiting, come back again soon!')
                        message.set_author(name='Timmy and Tommy',
                                           icon_url='https://play.nintendo.com/'
                                                    'images/masthead-img-timmy-tommy.f4b49fb7.cf659c6f.png')
                        await ctx.send(embed=message)
                        return
        else:
            await ctx.respond(f'..Hmm....You don\'t have **{quantity}x {item.title()}** to sell right now...')
            return


def setup(bot):
    bot.add_cog(Shop(bot))
