import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.slash_command(name='intro', description='Show basic information about the ACNH bot')
async def intro(ctx: discord.ApplicationContext):
    message = discord.Embed(title=f'Hello, {ctx.author.name}!',
                            description=f'To start or view your profile, use `/profile`',
                            color=0x9dffb0)
    message.add_field(name='Villagers',
                      value=f'At the beginning, you will start with two random villagers. Use `/campsite` to visit '
                            f'your campsite so you can find new villagers and invite them to your island! If you have '
                            f'10 island residents and you\'d like to invite a new villager, you will need to kick '
                            f'one of your current residents out using `/kick`. Use `/villagers` to view your '
                            f'current villagers. The campsite will refresh everyday at 0:00 PST.',
                      inline=True)
    message.add_field(name='\u200b',
                      value='\u200b',
                      inline=True)
    message.add_field(name='Digging, Fishing, Mining, and more!',
                      value=f'You\'ll begin with a flimsy rod and flimsy shovel. Use `/dig` to dig for fossils, use '
                            f'`/fish` to fish, use `/mine` to mine, and use `/bug` to catch bugs. New specimens '
                            f'will be automatically donated to your museum. You\'ll be able to sell extra specimens to '
                            f'Timmy and Tommy for bells. To view your current progress for your museum, use '
                            f'`/museum`.',
                      inline=True)
    message.add_field(name='Planting',
                      value=f'Your island has a native fruit tree and flower. Shake trees using `/shake`, cut them '
                            f'down using `/cut`, or plant saplings and seeds using `/plant`. You may repurchase or '
                            f'sell fruit, flowers, and items shaken from trees at Nook\'s Cranny.',
                      inline=True)
    message.add_field(name='\u200b',
                      value='\u200b',
                      inline=True)
    message.add_field(name='Surviving',
                      value='Be careful when cutting down and shaking trees, catching bugs, and mining! You have 3 '
                            'health points, being stung by a scorpion or bee will cause you to lose 1 health point. '
                            'Each one of your native fruits to gain max health back or eat any other fruit for 1 '
                            'health point. Draining all your health causes you to pass out and lose all your inventory '
                            'items.',
                      inline=True)
    message.add_field(name='Nook\'s Cranny',
                      value=f'Sell your items to Timmy and Tommy at Nook\'s Cranny using `/sell`. If you\'d like to '
                            f'view items they are currently selling, use `/shop`. To buy items, use `/buy`. The '
                            f'shop will refresh everyday at 0:00 PST.',
                      inline=True)
    message.add_field(name='\u200b',
                      value='\u200b',
                      inline=True)
    message.add_field(name='Dailies',
                      value=f'You will start off with 100,000 bells. The command `/daily` will refresh everyday at '
                            f'0:00 PST for you to receive 10,000 free bells.',
                      inline=True)
    await ctx.respond(embed=message)


@bot.event
async def on_connect():
    if bot.auto_sync_commands:
        await bot.sync_commands()
    print(f"{bot.user.name} connected.")


bot.load_extension('commands.villagers.villagers')
bot.load_extension('commands.user.profile')
bot.load_extension('commands.activities.activities')
bot.load_extension('commands.shop.shop')


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('BOT_TOKEN'))
