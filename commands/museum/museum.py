import discord
from discord.ext import commands
from commands.user.profile import get_museum_info, has_paintings, add_to_museum, remove_from_inventory
from util.activities import fetch_species, fetch_fossils
from util.redd import fetch_one_art
from util.embed import handle_user_selection


async def generate_museum_message(ctx):
    specimen_types = ['bugs', 'fish', 'fossils', 'sea', 'art']
    message = discord.Embed(title=f'{ctx.author.name.title()}\'s Museum',
                            color=0x9dffb0)
    message.set_thumbnail(url=ctx.author.avatar.url)
    embed_count = 0
    museum_count = 0
    completed_count = 0

    for specimen in specimen_types:
        if specimen == 'fossils':
            full_count = len(fetch_fossils())
        else:
            full_count = fetch_species(None, specimen)
        museum_count += full_count
        museum_info = get_museum_info(str(ctx.author.id), specimen)
        specimen_count = len(museum_info.get('collected'))
        completed_count += specimen_count

        message.add_field(name=f'{specimen.strip('s').title() if specimen != 'sea' else specimen.title()} Progress',
                          value=f'{specimen_count}/{full_count}\n'
                                f'*{round((specimen_count / full_count) * 100, 3)}% Completion*',
                          inline=True)
        embed_count += 1

        if embed_count % 3 == 1:
            message.add_field(name='\u200b', value='\u200b', inline=True)
            embed_count += 1

    return message, completed_count, museum_count


async def museum_check(ctx, artwork):
    museum_info = get_museum_info(str(ctx.author.id), 'art')
    for art in museum_info:
        if artwork.lower() == art.lower():
            message = discord.Embed(color=0x9dffb0,
                                    description=f'Oops! You\'ve already donated this piece to the museum, perhaps '
                                                f'the Nooklings will take up your offer on it.')
            message.set_author(name='Blathers',
                               icon_url='https://dodo.ac/np/images/1/1b/Blathers_NH.png')
            return message
    else:
        return True


async def authenticity_check(user_id, artwork):
    if artwork[0]['authenticity']:
        add_to_museum(user_id, 'art', artwork[0]['name'].lower())
        remove_from_inventory(user_id, artwork[1], 1)
        message = discord.Embed(color=0x9dffb0,
                                description=f'Hoo! The **{artwork[0]['name'].title()}**? My sincerest thanks for your '
                                            f'donation!')
    else:
        message = discord.Embed(color=0x9dffb0,
                                description=f'Hoo! Upon closer examination, I have grave news to share with you! '
                                            f'This work of art... is a FAKE! I\'m terribly sorry, you\'ll have to find '
                                            f'some place else to display this. I\'ve heard that the Nooklings may even '
                                            f'take up your offer on it.')
    message.set_author(name='Blathers',
                       icon_url='https://dodo.ac/np/images/1/1b/Blathers_NH.png')

    return message


class Museum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='museum', description='Show your museum progress')
    async def museum(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        message = await generate_museum_message(ctx)
        museum = await ctx.respond(embed=message[0])

        description = (f'**Total Completion: **{message[1]}/{message[2]} | '
                       f'{round((message[1] / message[2]) * 100, 3)}%')
        museum_dict = message[0].to_dict()
        museum_dict['description'] = description
        museum_embed = discord.Embed.from_dict(museum_dict)
        await museum.edit(embed=museum_embed)

    @commands.slash_command(name='donate', description='Donate artwork to your museum')
    async def donate(self, ctx: discord.ApplicationContext, artwork: str):
        await ctx.defer()
        art = artwork.lower().strip()
        buttons = ['\u274C', '\u2705']
        artwork_info = has_paintings(str(ctx.author.id), art, 1)
        if not artwork_info:
            await ctx.respond(f'..Hmm....You don\'t have the **{art.title()}** to donate right now...')
            return
        try:
            fetch_one_art(art)
            check = await museum_check(ctx, art)
            if isinstance(check, bool):
                confirm = await ctx.send(f'Are you sure you want to donate the **{art.title()}**?')
                for b in buttons:
                    await confirm.add_reaction(b)

                react, user = await handle_user_selection(self, ctx, confirm, buttons)
                if react:
                    if react.emoji == buttons[0]:
                        await confirm.delete()
                        await ctx.respond(f'Donate action cancelled.')
                        return
                    elif react.emoji == buttons[1]:
                        await confirm.delete()
                        authenticity = await authenticity_check(str(ctx.author.id), artwork_info[0])
                        await ctx.respond(embed=authenticity)
            else:
                await ctx.respond(embed=check)
        except Exception as e:
            if '404' in str(e):
                message = discord.Embed(color=0x9dffb0,
                                        description=f'Oops! Museum space is limited... there is no room for that '
                                                    f'piece right now.')
                message.set_author(name='Blathers',
                                   icon_url='https://dodo.ac/np/images/1/1b/Blathers_NH.png')
                await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Museum(bot))
