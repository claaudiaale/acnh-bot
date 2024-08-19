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
                            f'one of your current residents out using `/kick`. Use `/residents` to view your '
                            f'current villagers and use `/villagerinfo` to get information about any villager. '
                            f'The campsite will refresh everyday at 0:00 PST.',
                      inline=True)
    message.add_field(name='\u200b',
                      value='\u200b',
                      inline=True)
    message.add_field(name='Digging, Fishing, Mining, and more!',
                      value=f'You\'ll begin with a flimsy fishing rod, shovel, and net. Use `/dig` to dig for '
                            f'fossils, use `/fish` to fish, and use `/bug` to catch bugs. You\'ll need to buy a '
                            f'snorkel mask from Nook\'s Cranny before using `/dive` to dive for sea creatures. New '
                            f'specimens will be automatically donated to your museum. You\'ll be able to sell extra '
                            f'specimens to Timmy and Tommy for bells. To view your current progress for your museum, '
                            f'use `/museum`.',
                      inline=True)
    message.add_field(name='Artwork',
                      value='Redd will visit your island every Sunday. Use `/shopredd` to view what he\'s currently '
                            'selling and `/buyredd` to purchase items from him. Use `/donate` to donate pieces to '
                            'your museum. Be careful about what pieces you decide to buy, counterfeit artwork cannot '
                            'be donated to the museum! The command `/artworkinfo` will return information about '
                            'any piece, but it\'s up to you to compare authentic images of artwork to what Redd has '
                            'in shop.',
                      inline=True)
    message.add_field(name='\u200b',
                      value='\u200b',
                      inline=True)
    message.add_field(name='Fruits',
                      value=f'Your island has a native fruit tree, shake trees using `/shake` to find your own native '
                            f'fruit or rare exotic fruits. Be sure to carry a net in case you encounter a wasp\'s '
                            f'nest!',
                      inline=True)
    message.add_field(name='Nook\'s Cranny',
                      value=f'Sell your items to Timmy and Tommy at Nook\'s Cranny using `/sell`. If you\'d like to '
                            f'view items they are currently selling, use `/shop`. To buy items, use `/buy`.',
                      inline=True)
    message.add_field(name='\u200b',
                      value='\u200b',
                      inline=True)
    message.add_field(name='Daily',
                      value=f'You will start off with 100,000 bells. The command `/daily` will refresh everyday at '
                            f'0:00 PST for you to receive 10,000 free bells.',
                      inline=True)
    message.add_field(name='Surviving',
                      value='Be careful when encountering bugs! You have 5 health points, being stung by a scorpion, '
                            'bee, or tarantula will cause you to lose 1 health point. Use `/eat` to eat one of your '
                            'native fruits to gain 1 health point or eat any other fruit to gain 3 health points. '
                            'Draining all your health causes you to pass out and lose all your inventory items.',
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
bot.load_extension('commands.museum.museum')
bot.load_extension('commands.redd.redd')


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('BOT_TOKEN'))
