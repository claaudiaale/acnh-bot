import discord
from discord.ext import commands
from util.tools import fetch_all_tools, fetch_tools
from util.embed import embed_arrows, handle_user_selection
from util.activities import fetch_item_info, fetch_clothing_info
from commands.user.profile import (add_to_inventory, has_item, remove_from_inventory, update_bells, get_user_profile,
                                   has_paintings)


def sort_tools(tool):
    tool_order = {'flimsy': 0, 'golden': 2}
    for key in tool_order:
        if key in tool:
            return tool_order[key], tool
    return 1, tool


def generate_shop_message(info, fruit=False, user_id=None):
    if not fruit:
        sorted_items = sorted(info, key=lambda tool: sort_tools(tool.get('name')))
    else:
        fruit_names = ['apple', 'cherry', 'orange', 'peach', 'pear']
        sorted_items = [fetch_item_info(fruit) for fruit in fruit_names]

    message = discord.Embed(title='Nook\'s Cranny',
                            color=0x9dffb0)
    message.set_thumbnail(url='https://dodo.ac/np/images/3/3c/Timmy_%26_Tommy_NL.png')
    for item in sorted_items:
        price_info = item.get('price', 'buy')

        if len(price_info) > 0:
            price_info = item.get('price')[0] if item.get('price') else item.get('buy')[0]
            cost = price_info.get('price')
            user_profile = get_user_profile(user_id)
            native_fruit = user_profile.get('fruit')
            if fruit and item.get('name') == native_fruit:
                message.add_field(name=f'{item.get('name').title()}',
                                  value=f'**Price:** {cost} Bells',
                                  inline=False)
            else:
                message.add_field(name=f'{item.get('name').title()}',
                                  value=f'**Price:** {cost * 3} Bells',
                                  inline=False)
        else:
            message.add_field(name=f'{item.get('name').title()}',
                              value=f'**Price:** {(item.get('sell')*4)} Bells',
                              inline=False)
    return message


async def handle_sell_action(ctx, react, buttons, message, inv_item, quantity, item):
    if react.emoji == buttons[0]:
        await message.delete()
        await ctx.send(f'Sell action cancelled.')
        return
    elif react.emoji == buttons[1]:
        remove_from_inventory(str(ctx.author.id), inv_item[1], quantity)
        update_bells(str(ctx.author.id), (inv_item[0].get('sell') * quantity))

        message = discord.Embed(color=0x9dffb0,
                                description=f'You just sold **{quantity}x {item.title()}**. Thanks '
                                            f'for visiting, come back again soon!')
        message.set_author(name='Timmy and Tommy',
                           icon_url='https://play.nintendo.com/'
                                    'images/masthead-img-timmy-tommy.f4b49fb7.cf659c6f.png')
        await ctx.send(embed=message)
        return


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='shop', description='Explore what Nook\'s Cranny has in store to purchase')
    async def shop(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool_names = ['shovel', 'fishing rod', 'net']
        tool_info = [fetch_all_tools(tool) for tool in tool_names]
        pages = [generate_shop_message(info) for info in tool_info]

        fruit_page = generate_shop_message([], fruit=True, user_id=(str(ctx.author.id)))
        pages.insert(0, fruit_page)

        snorkel = fetch_clothing_info('snorkel_mask')
        snorkel_price = snorkel.get('buy')[0]
        pages[2].add_field(name=f'{snorkel.get('name').title()}',
                           value=f'**Price:** {snorkel_price.get('price')} Bells',
                           inline=False)

        await embed_arrows(self, ctx, pages)

    @commands.slash_command(name='buy', description='Buy items from Nook\'s Cranny')
    async def buy(self, ctx: discord.ApplicationContext, quantity: int, item: str):
        buttons = ['\u274C', '\u2705']
        if item == 'snorkel mask':
            item_info = fetch_clothing_info('snorkel_mask')
        else:
            item_info = fetch_tools(item.replace(' ', '_'))
        price_info = item_info.get('price', [])

        if len(price_info) > 0:
            price_info = item_info.get('price')[0]
            cost = price_info.get('price')
            confirmation = await ctx.send(f'Buy **{quantity}x {item.title()}** for {cost * quantity} Bells?')
        else:
            confirmation = await ctx.send(f'Buy **{quantity}x {item.title()}** for {(item_info.get('sell')*4) *
                                                                                    quantity} Bells?')
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
                    price = item_info.get('price')[0].get('price') \
                        if item_info.get('price') else item_info.get('sell')*4
                    add = add_to_inventory(str(ctx.author.id), {'name': item_info.get('name'),
                                                                'remaining_uses': item_info.get('uses'),
                                                                'original_uses': item_info.get('uses'),
                                                                'price': price,
                                                                'sell': item_info.get('sell')}, quantity)
                    update_bells(str(ctx.author.id), (price * quantity), buy=True)

                    message = discord.Embed(color=0x9dffb0,
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
        if 'painting' in item.strip().lower() or 'statue' in item.strip().lower():
            if not has_paintings(str(ctx.author.id), item, quantity)[1]:
                donate = discord.Embed(color=0x9dffb0,
                                       description=f'Oops! You have more than 1 kind of these pieces in your '
                                                   f'inventory, it would be best to visit Blathers and identify '
                                                   f'authenticity before selling us a piece. See you again soon!')
                donate.set_author(name='Timmy and Tommy',
                                  icon_url='https://play.nintendo.com/'
                                           'images/masthead-img-timmy-tommy.f4b49fb7.cf659c6f.png')
                await ctx.respond(embed=donate)
                return
        inv_item = has_item(str(ctx.author.id), item, quantity)
        if inv_item[0]:

            confirmation = discord.Embed(color=0x9dffb0,
                                         description=f'**{quantity}x {item.title()}?** Sure! How about if I offer you '
                                                     f'{inv_item[0].get('sell') * quantity} Bells?')
            confirmation.set_author(name='Timmy and Tommy',
                                    icon_url='https://play.nintendo.com/'
                                             'images/masthead-img-timmy-tommy.f4b49fb7.cf659c6f.png')
            message = await ctx.respond(embed=confirmation)

            for b in buttons:
                await message.add_reaction(b)

            while True:
                react, user = await handle_user_selection(self, ctx, message, buttons)
                if not react:
                    return

                else:
                    await handle_sell_action(ctx, react, buttons, message, inv_item, quantity, item)
                    return
        else:
            await ctx.respond(f'..Hmm....You don\'t have **{quantity}x {item.title()}** to sell right now...')
            return


def setup(bot):
    bot.add_cog(Shop(bot))
