import asyncio

import discord
from discord.ext import commands
import datetime
import random
from util.activities import (fetch_species, fetch_specimen, fetch_fossils, fetch_fossil_group, fetch_single_fossil,
                             fetch_item_info)
from commands.user.profile import (add_to_inventory, has_tool, update_health, add_to_museum, get_user_profile,
                                   update_bells, has_item, remove_from_inventory, update_profile, get_swarm_limit)


def generate_random_specimen(species, no_swarm=False):
    current_month = datetime.datetime.now().strftime('%m')
    if species == 'fossils':
        available_species = fetch_fossils()
    else:
        available_species = fetch_species(current_month, species)

    species_list = []
    if species == 'fish':
        rarity = {
            'Common': 0.75,
            'Uncommon': 0.25,
            'Rare': 0.1
        }

        for specimen in available_species:
            species_list.extend([specimen] * int(rarity[specimen['rarity']] * 100))
    elif species == 'bugs' and not no_swarm:
        for specimen in available_species:
            if specimen['name'] in ['wasp', 'scorpion', 'tarantula']:
                species_list.extend([specimen] * int(0.09 * 100))
            else:
                species_list.append(specimen)
    elif species == 'bugs' and no_swarm:
        for specimen in available_species:
            if specimen['name'] in ['wasp', 'scorpion', 'tarantula']:
                species_list.pop()
            else:
                species_list.append(specimen)
    else:
        species_list = available_species

    catch = random.choice(species_list)
    return catch


async def catch_bug(ctx: discord.ApplicationContext, catch):
    tool = has_tool(str(ctx.author.id), 'net')
    bug_info = fetch_specimen('bugs', catch['name'])[0]
    museum = add_to_museum(str(ctx.author.id), 'bugs', bug_info.get('name'))

    message = discord.Embed(title=f'{bug_info.get('name').title()}',
                            color=0x9dffb0,
                            description=f'{bug_info.get('catchphrase')}')
    message.set_thumbnail(url=f'{bug_info['render_url']}')
    message.add_field(name='',
                      value=f'**Location:** {bug_info.get('location')}\n'
                            f'**Price:** {bug_info.get('sell_nook')} Bells')
    await ctx.respond(embed=message)
    if isinstance(tool, str):
        await ctx.send(tool)
    if not museum:
        add = add_to_inventory(str(ctx.author.id), {'name': bug_info.get('name'),
                                                    'sell': int(bug_info.get('sell_nook'))}, 1)
        if add:
            await ctx.send(add)


async def swarm_sting(ctx: discord.ApplicationContext, catch):
    health = update_health(str(ctx.author.id), 1)
    sting = f'Ow! Ow ow ow... You got stung by a {catch['name']} and lost one health point!'
    if health:
        await ctx.respond(sting)
        await ctx.send(health)
        return
    else:
        await ctx.respond(sting)
        return


class Activities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='fish', description='Use your fishing rod to fish')
    async def fish(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool = has_tool(str(ctx.author.id), 'rod')
        if tool:
            catch = generate_random_specimen('fish')
            fish_info = fetch_specimen('fish', catch['name'])[0]
            museum = add_to_museum(str(ctx.author.id), 'fish', fish_info.get('name'))

            message = discord.Embed(title=f'{fish_info.get('name')}',
                                    color=0x9dffb0,
                                    description=f'{fish_info.get('catchphrase')}')
            message.set_thumbnail(url=f'{fish_info['render_url']}')
            message.add_field(name='',
                              value=f'**Location:** {fish_info.get('location')}\n'
                                    f'**Price:** {fish_info.get('sell_nook')} Bells\n'
                                    f'**Rarity:** {fish_info.get('rarity')}',
                              inline=False)
            await ctx.respond(embed=message)
            if isinstance(tool, str):
                await ctx.send(tool)
            if not museum:
                add = add_to_inventory(str(ctx.author.id), {'name': fish_info.get('name'),
                                                            'sell': int(fish_info.get('sell_nook'))}, 1)
                if add:
                    await ctx.send(add)
        else:
            await ctx.respond(f'You don\'t have a fishing rod! Visit Nook\'s Cranny to buy one and fish.')

    @commands.slash_command(name='bug', description='Use your net to catch bugs')
    async def bug(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        buttons = {'\U0001F41D': 'wasp', '\U0001F982': 'scorpion', '\U0001F577': 'tarantula'}
        tool = has_tool(str(ctx.author.id), 'net')
        swarm_limit = get_swarm_limit(str(ctx.author.id)).get('swarm_count')
        if tool:
            if swarm_limit == 5:
                catch = generate_random_specimen('bugs', no_swarm=True)
            else:
                catch = generate_random_specimen('bugs')
            if catch['name'] in ['wasp', 'scorpion', 'tarantula']:
                update_profile(str(ctx.author.id), 'swarm_count')
                swarm = await ctx.send(f'A {catch['name']} is chasing you! '
                                       f'You have 5 seconds to catch the correct bug!')
                for emoji, name in buttons.items():
                    await swarm.add_reaction(emoji)

                try:
                    react, user = await self.bot.wait_for('reaction_add', timeout=5,
                                                          check=lambda r, u: r.message.id == swarm.id
                                                          and u.id == ctx.author.id and r.emoji in buttons)
                    await swarm.remove_reaction(react.emoji, user)

                    if catch['name'] == buttons[react.emoji]:
                        await swarm.delete()
                        await catch_bug(ctx, catch)
                    else:
                        await swarm.delete()
                        await swarm_sting(ctx, catch)
                except asyncio.TimeoutError:
                    await swarm.delete()
                    await swarm_sting(ctx, catch)
            else:
                await catch_bug(ctx, catch)
        else:
            await ctx.respond(f'You don\'t have a net! Visit Nook\'s Cranny to buy one and catch bugs.')

    @commands.slash_command(name='dig', description='Use your shovel to dig for fossils')
    async def dig(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool = has_tool(str(ctx.author.id), 'shovel')
        fossil_count = update_profile(str(ctx.author.id), 'fossil_count')
        if tool:
            if not fossil_count:
                await ctx.respond(f'Hmm...There are no more holes to dig for fossils today...')
            else:
                catch = generate_random_specimen('fossils')
                fossil_info = fetch_specimen('fossils', catch['name'].replace(' ', '_'))
                museum = add_to_museum(str(ctx.author.id), 'fossils', fossil_info.get('name'))

                fossil_group = fossil_info.get('fossil_group')
                if fossil_group:
                    fossil_description = fetch_fossil_group(fossil_group)
                else:
                    fossil_description = fetch_single_fossil(fossil_info.get('name'))

                message = discord.Embed(title=f'{fossil_info.get('name').title()}',
                                        color=0x9dffb0,
                                        description=f'{fossil_description}')
                message.set_thumbnail(url=f'{fossil_info['image_url']}')
                message.add_field(name='',
                                  value=f'**Price:** {fossil_info.get('sell')} Bells')
                await ctx.respond(embed=message)
                if isinstance(tool, str):
                    await ctx.send(tool)
                if not museum:
                    add = add_to_inventory(str(ctx.author.id), {'name': fossil_info.get('name'),
                                                                'sell': int(fossil_info.get('sell_nook'))}, 1)
                    if add:
                        await ctx.send(add)
        else:
            await ctx.respond(f'You don\'t have a shovel! Visit Nook\'s Cranny to buy one and dig for fossils.')

    @commands.slash_command(name='dive', description='Dive to collect sea creatures')
    async def dive(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        tool = has_tool(str(ctx.author.id), 'snorkel')
        if tool:
            catch = generate_random_specimen('sea')
            sea_info = fetch_specimen('sea', catch['name'])[0]
            museum = add_to_museum(str(ctx.author.id), 'sea', sea_info.get('name'))

            message = discord.Embed(title=f'{sea_info.get('name').title()}',
                                    color=0x9dffb0,
                                    description=f'{sea_info.get('catchphrases')[0]}')
            message.set_thumbnail(url=f'{sea_info['render_url']}')
            message.add_field(name='',
                              value=f'**Price:** {sea_info.get('sell_nook')} Bells\n',
                              inline=False)
            await ctx.respond(embed=message)
            if isinstance(tool, str):
                await ctx.send(tool)
            if not museum:
                add = add_to_inventory(str(ctx.author.id), {'name': sea_info.get('name'),
                                                            'sell': int(sea_info.get('sell_nook'))}, 1)
                if add:
                    await ctx.send(add)
        else:
            await ctx.respond(f'You don\'t have a snorkel! Visit Nook\'s Cranny to buy one and dive for sea creatures.')

    @commands.slash_command(name='shake', description='Shake trees for fruit')
    async def shake(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        buttons = {'\U0001F41D': 'wasp', '\U0001F982': 'scorpion', '\U0001F577': 'tarantula'}
        user_profile = get_user_profile(str(ctx.author.id))
        native_fruit = user_profile.get('fruit')
        chances = ['apple', 'cherry', 'orange', 'peach', 'pear']
        shake_chances = []

        fruit_count = update_profile(str(ctx.author.id), 'fruit_count')
        if not fruit_count:
            await ctx.respond('There are no more trees to shake fruit from for today!')
        else:
            for item in chances:
                if item == native_fruit:
                    shake_chances.extend([item] * 8)
                else:
                    shake_chances.extend([item] * 2)
            shake_chances.extend(['wasp', 'bells'])

            shake = random.choice(shake_chances)

            if shake == 'wasp':
                catch = {'name': 'wasp'}
                tool = has_tool(str(ctx.author.id), 'net')
                if tool:
                    swarm = await ctx.send(f'A wasp is chasing you! '
                                           f'You have 5 seconds to catch it!')
                    for emoji, name in buttons.items():
                        await swarm.add_reaction(emoji)
                    try:
                        react, user = await self.bot.wait_for('reaction_add', timeout=5,
                                                              check=lambda r, u: r.message.id == swarm.id
                                                              and u.id == ctx.author.id and r.emoji in buttons)
                        await swarm.remove_reaction(react.emoji, user)

                        if catch['name'] == buttons[react.emoji]:
                            await swarm.delete()
                            await catch_bug(ctx, catch)
                        else:
                            await swarm.delete()
                            await swarm_sting(ctx, catch)
                    except asyncio.TimeoutError:
                        await swarm.delete()
                        await swarm_sting(ctx, catch)
                else:
                    await ctx.respond(f'You don\'t have a net to catch a wasp!')
                    await swarm_sting(ctx, catch)
            elif shake == 'bells':
                await ctx.respond('You\'ve found **1,000 bells**.')
                update_bells(str(ctx.author.id), 1000)
            else:
                await ctx.respond(f'You\'ve found **1x {shake.title()}**.')
                fruit_info = fetch_item_info(shake)
                add = add_to_inventory(str(ctx.author.id), {'name': fruit_info.get('name'),
                                                            'sell': int(fruit_info.get('sell'))}, 1)
                if add:
                    await ctx.send(add)

    @commands.slash_command(name='eat', description='Eat fruits to gain health points back')
    async def eat(self, ctx: discord.ApplicationContext, quantity: int, fruit_name: str):
        await ctx.defer()
        fruits = ['apple', 'cherry', 'orange', 'peach', 'pear']
        if fruit_name in fruits:
            item_info = has_item(str(ctx.author.id), fruit_name, quantity)
            if item_info[0]:
                user_profile = get_user_profile(str(ctx.author.id))
                native_fruit = user_profile.get('fruit')
                if fruit_name == native_fruit:
                    update_health(str(ctx.author.id), 1, True)
                else:
                    update_health(str(ctx.author.id), quantity * 3, True)
                remove_from_inventory(str(ctx.author.id), item_info[1], quantity)
                updated_profile = get_user_profile(str(ctx.author.id))
                health = updated_profile.get('health')
                await ctx.respond(f'You ate **{quantity}x {fruit_name.title()}**. **Current Health: {health}**')
            else:
                await ctx.respond(f'..Hmm....You don\'t have **{quantity}x {fruit_name.title()}** to eat right now...')
        else:
            await ctx.respond('You cannot eat this.')


def setup(bot):
    bot.add_cog(Activities(bot))
