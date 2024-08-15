import discord
import asyncio


async def embed_arrows(self, ctx: discord.ApplicationContext, pages):
    buttons = ['\u2B05', '\u27A1']
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

            embed = pages[current_page]
            embed.set_footer(text=f'Page {current_page + 1} of {len(pages)}',
                             icon_url='https://dodo.ac/np/images/5/52/NH_Logo_English.png')
            await message.edit(embed=embed)


async def handle_user_selection(self, ctx: discord.ApplicationContext, message, buttons):
    try:
        react, user = await self.bot.wait_for(
            'reaction_add', timeout=60,
            check=lambda r, u: r.message.id == message.id and u.id == ctx.author.id and r.emoji in buttons)
        await message.remove_reaction(react.emoji, user)
        return react, user
    except asyncio.TimeoutError:
        await message.delete()
        return None, None

