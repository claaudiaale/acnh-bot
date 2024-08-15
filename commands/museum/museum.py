import discord
from discord.ext import commands
from commands.user.profile import get_museum_info
from util.activities import fetch_species, fetch_fossils


async def generate_museum_message(ctx):
    specimen_types = ['bugs', 'fish', 'fossils', 'sea']
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


def setup(bot):
    bot.add_cog(Museum(bot))
