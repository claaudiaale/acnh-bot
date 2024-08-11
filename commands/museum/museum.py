import discord
from discord.ext import commands
from commands.user.profile import get_museum_info
from util.activities import fetch_species, fetch_fossils


class Museum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='museum', description='Show your museum progress')
    async def museum(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        specimen_types = ['bugs', 'fish', 'fossils']
        message = discord.Embed(title=f'{ctx.author.name.title()}\'s Museum',
                                color=0x81f1f7)
        message.set_thumbnail(url=ctx.author.avatar.url)
        museum_count = 0
        completed_count = 0
        for specimen in specimen_types:
            if specimen == 'fossils':
                full_count = len(fetch_fossils())
            else:
                full_count = fetch_species(None, specimen)
            museum_count += full_count
            specimen_count = len(get_museum_info(str(ctx.author.id), specimen)) + 1
            completed_count += specimen_count
            message.add_field(name=f'{specimen.strip('s').title()} Progress',
                              value=f'{specimen_count}/{full_count}\n'
                                    f'*{round(specimen_count/full_count, 3)}% Completion*',
                              inline=True)
        # message.edit_description(f'{completed_count}/{museum_count} | {completed_count/museum_count}% Completion')
        await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Museum(bot))
