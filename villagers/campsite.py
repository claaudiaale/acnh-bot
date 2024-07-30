import discord
from discord.ext import commands
from villagers.villagers import generate_random_villager
from villagers.villager_info import generate_villager_message


class Campsite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='campsite', description='Check your campsite for a visitor')
    async def campsite(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        visitor_id = generate_random_villager(str(ctx.author.id))
        message = generate_villager_message(visitor_id)
        await ctx.respond(embed=message)


def setup(bot):
    bot.add_cog(Campsite(bot))
