from discord.ext import commands
from villagers.villagers import generate_random_villager
from villagers.villager_info import generate_villager_message


class Campsite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='campsite')
    async def campsite(self, ctx):
        visitor_id = generate_random_villager(str(ctx.author.id))
        message = generate_villager_message(visitor_id)
        await ctx.channel.send(embed=message)


async def setup(bot):
    await bot.add_cog(Campsite(bot))
