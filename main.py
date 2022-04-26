import os
import pathlib

from typing import List

path = pathlib.Path(__file__).parent
os.chdir(path)
import datetime
import discord
import config as cf
from discord.ext import commands
from discord.ext.commands import has_permissions
import math
import platform
import pytz
import requests
import sqlite3
import subprocess
import traceback
import logging

import asyncio

now = int(datetime.datetime.now(pytz.timezone("UTC")).timestamp())

conn = sqlite3.connect(cf.db_bot, timeout=5.0)
c = conn.cursor()
conn.row_factory = sqlite3.Row

help_extensions = ['help']

c.execute('''CREATE TABLE IF NOT EXISTS prefix (
        `guild_id` INT PRIMARY KEY,
        `prefix` TEXT)''')

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def determine_prefix(mybot: discord.bot, message):
    try:
        current_prefix = prefixDictionary[message.guild.id]
        return commands.when_mentioned_or(current_prefix)(mybot, message)
    except KeyError:
        c.execute(''' INSERT OR REPLACE INTO prefix VALUES (?, ?)''', (message.guild.id, defaultPrefix))
        conn.commit()
        prefixDictionary.update({message.guild.id: defaultPrefix})
        print(f"Error Detected: Created a prefix database for {message.guild.id}: {message.guild}")
        return commands.when_mentioned_or(defaultPrefix)(mybot, message)
    except AttributeError:
        return commands.when_mentioned_or("!@#$%^&*()")(mybot, message)


intents = discord.Intents.all()
# intents.members

bot = commands.AutoShardedBot(command_prefix=determine_prefix, help_command=None, intents=intents)

bot.owner_ids = [
    266815915604049920,  # Stewball32#2228
    734484432106422373,  # StarPaul00#3629
    273320140119080961,  # XTFOX#7620
    524418749034659877,  # Edward#1711
]


defaultPrefix = '-'

print("loading cogs", end="...")
cog_num = 0
for cog in os.listdir("./cogs/"):
    cog_num += 1
    try:
        if cog == '__pycache__':
            continue
        else:
            newCog = cog.replace(".py", "")
            bot.load_extension(f"cogs.{newCog}")
            print(f'{cog}', end=", ")
            if cog_num % 5 == 0:
                print()

    except Exception as e:
        exc = f'{type(e).__name__}: {e}'
        print(f'Failed to load extension {cog}\n{exc}')
        traceback.print_exc()
        print("loading cogs...", end="")
        cog_num = 0


@bot.command(help="Loads an extension. Bot Owner only!")
@commands.is_owner()
async def load(ctx: commands.Context, extension_name: str):
    try:

        bot.load_extension(extension_name)

    except (AttributeError, ImportError) as err:

        await ctx.send(f"```py\n{type(err).__name__}: {str(err)}\n```")
        return

    await ctx.send(f"{extension_name} loaded.")


@bot.command(help="Unloads an extension. Bot Owner only!")
@commands.is_owner()
async def unload(ctx: commands.Context, extension_name: str):
    bot.unload_extension(extension_name)
    await ctx.send(f"{extension_name} unloaded.")


@bot.command()
@has_permissions(manage_messages=True)
async def setprefix(ctx: commands.Context, new):
    guild = ctx.message.guild.id
    name = bot.get_guild(guild)

    for key, value in c.execute('SELECT guild_id, prefix FROM prefix'):

        if key == guild:
            c.execute(''' UPDATE prefix SET prefix = ? WHERE guild_id = ? ''', (new, guild))
            conn.commit()
            prefixDictionary.update({ctx.guild.id: f"{new}"})

            embed = discord.Embed(description=f"{name}'s Prefix has now changed to `{new}`.")
            await ctx.send(embed=embed)


@bot.command()
async def myprefix(ctx: commands.Context):
    c.execute(f'SELECT prefix FROM prefix WHERE guild_id = {ctx.message.guild.id}')
    current_prefix = c.fetchall()[0][0]

    name = bot.get_guild(ctx.message.guild.id)
    embed = discord.Embed(description=f"{name}'s Prefix currently is `{current_prefix}`.")
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    # print(f"Logging in as {str(bot.user)}")
    print(f"{str(bot.user)} has connected to Discord!")
    print(f"Discord: {discord.__version__}  |  ", end="")
    print(f"Python: {platform.python_version()}  |  ", end="")
    print(f"Sqlite3: {sqlite3.sqlite_version}")
    print(f"{str(bot.user)} Connections: Servers", end="")
    print(f"({len([s for s in bot.guilds])}) ", end="")
    print("Players", end="")
    print(f"({sum(guild.member_count for guild in bot.guilds)})")

    guild_id_database = [row[0] for row in c.execute('SELECT guild_id FROM prefix')]

    async for guild in bot.fetch_guilds():
        if guild.id not in guild_id_database:
            c.execute(''' INSERT OR REPLACE INTO prefix VALUES (?, ?)''', (guild.id, defaultPrefix))
            conn.commit()
            prefixDictionary.update({guild.id: defaultPrefix})
            print(f"Bot started up: Created a prefix database for {guild.id}: {guild}")


@bot.event
async def on_guild_join(guild):
    guild_id_database = [row[0] for row in c.execute('SELECT guild_id FROM prefix')]

    if guild.id not in guild_id_database:
        c.execute(''' INSERT OR REPLACE INTO prefix VALUES (?, ?)''', (guild.id, defaultPrefix))
        conn.commit()
        prefixDictionary.update({guild.id: f"{defaultPrefix}"})
        print(f"Bot joined a new server: Created a prefix database for {guild.id}: {guild}")


@bot.event
async def on_command_error(ctx: commands.Context, error):
    logger.error(f'Error {error}: {ctx.guild.name} > {ctx.author.name} > {ctx.command} "{ctx.message.content}"')

    if isinstance(error, commands.CommandOnCooldown):

        seconds = error.retry_after
        minutes = seconds / 60
        hours = seconds / 3600

        if ctx.message.author.id in [140488317685727232, 147865777939152896]:  # Harry/Niki ignored
            return

        if ctx.message.author.id == 266815915604049920:
            await ctx.reinvoke()
            return

        if seconds / 60 < 1:
            embed = discord.Embed(
                description=f'You\'re using this command too often! Try again in {str(int(seconds))} seconds!', colour=cf.color_timeout)
            await ctx.send(embed=embed)
            return

        elif minutes / 60 < 1:
            embed = discord.Embed(
                description=f'You\'re using this command too often! Try again in {math.floor(minutes)} minutes and '
                            f'{(int(seconds) - math.floor(minutes) * 60)} seconds!', colour=cf.color_timeout)
            await ctx.send(embed=embed)
            return

        else:
            embed = discord.Embed(
                description=f'You\'re using this command too often! Try again in {math.floor(hours)} hours, '
                            f'{(int(minutes) - math.floor(hours) * 60)} minutes, {(int(seconds) - math.floor(minutes) * 60)} seconds!', colour=cf.color_timeout)
            await ctx.send(embed=embed)
            return

    # error_embed = discord.Embed(title=f"‼Error Reported‼", description=f"`{error}`",
    #                             color=cf.color_error, url=ctx.message.jump_url)
    # error_embed.add_field(name=f"Guild", value=f"{ctx.guild}")
    # error_embed.add_field(name=f"User", value=f"{ctx.author.name}")
    # error_embed.add_field(name=f"Command", value=f"{ctx.command}")
    # error_embed.set_footer(text=f"Message: {ctx.message.content}")
    #
    # error_channel = bot.get_guild(cf.hub_guild_id).get_channel(cf.hub_error_id)
    # await error_channel.send(embed=error_embed)

    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(description='You do not have the permission to do this!', colour=cf.color_timeout)
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(description='Missing arguments on your command! Please check and retry again!', colour=cf.color_timeout)
        await ctx.send(embed=embed)
        return

    if isinstance(error, sqlite3.OperationalError):
        embed = discord.Embed(description="There was a database error!")
        await ctx.send(embed=embed)
        return

    if isinstance(error, commands.CommandNotFound):
        print("'Command Not Found' Error has been triggered from user-end.")
        return

    if isinstance(error, commands.MissingPermissions):
        print("'Missing Permissions' Error has been triggered from user-end.")
        return

    raise error


@bot.event
async def on_command(ctx: commands.Context):
    logger.info(f'Command Started: {ctx.guild.name} > {ctx.author.name} > {ctx.command} "{ctx.message.content}"')


@bot.event
async def on_command_completion(ctx: commands.Context):
    logger.info(f'Command Ended Successfully: {ctx.guild.name} > {ctx.author.name} > {ctx.command} "{ctx.message.content}"')


@bot.command()
async def ping(ctx: commands.Context):
    ping_embed = discord.Embed(description=f"Pong! Time taken: **{round(bot.latency, 3) * 1000} ms**!", color=cf.color_info)
    ping_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=ping_embed)


@bot.command()
async def layout(ctx: commands.Context):
    embed_team = discord.Embed(title="Embed Title", color=cf.color_info,
                               description="Embed Description")
    embed_team.set_author(name="Embed Author", icon_url='https://upload.wikimedia.org/wikipedia/commons/5/51/Pokebola-pokeball-png-0.png')
    embed_team.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/5/51/Pokebola-pokeball-png-0.png')
    embed_team.add_field(name="1 Add Field Name", value="1 Add Field Value")
    embed_team.add_field(name="2 Add Field Name", value="2 Add Field Value")
    embed_team.add_field(name="3 Add Field Name", value="3 Add Field Value")
    embed_team.add_field(name="4 Add Field Name", value="4 Add Field Value")
    embed_team.add_field(name="5 Add Field Name", value="5 Add Field Value")
    embed_team.add_field(name="6 Add Field Name", value="6 Add Field Value", inline=False)
    embed_team.add_field(name="7 Add Field Name", value="7 Add Field Value")
    embed_team.add_field(name="8 Add Field Name", value="8 Add Field Value")
    embed_team.add_field(name="9 Add Field Name", value="9 Add Field Value")
    embed_team.add_field(name="10 Add Field Name", value="10 Add Field Value")
    embed_team.set_footer(text="Embed Footer")
    embed_team.set_image(url="https://upload.wikimedia.org/wikipedia/commons/5/51/Pokebola-pokeball-png-0.png")

    embed_msg = await ctx.send(embed=embed_team)


@bot.command()
async def emoji(ctx: commands.Context):
    guild = ctx.guild
    emojis = await guild.fetch_emojis()

    if emojis:
        string = ""
        emoji_string1 = "{\n"
        for i in emojis:
            current = f"{i}"
            name = current.split(":")[1]
            emoji_string1 += f'"{name}": "{i}",\n'
            string += f"{i} "
        emoji_string1 += "}"
        emoji_dict = eval(emoji_string1)

        emoji_string2 = "{\n"
        for i in sorted(emoji_dict):
            emoji_string2 += f'"{i}": "{emoji_dict[i]}",\n'

        print(emoji_string2)
        await ctx.send(f"{string}")
    else:
        await ctx.send("No emojis!")


@bot.command()
async def channel(ctx: commands.Context):
    await ctx.send(f"{ctx.channel.name}")


@bot.command()
async def roles(ctx: commands.Context):
    all_roles: List[discord.Role] = ctx.author.roles
    post = ""
    for x in all_roles:
        post += f"{x.name}\n"

    await ctx.send(f"{post}")


prefixDictionary = {}

for prefix in c.execute(f'SELECT guild_id, prefix FROM prefix'):
    prefixDictionary.update({prefix[0]: f"{prefix[1]}"})

bot.remove_command('help')


if __name__ == "__main__":
    for extension in help_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = f'{type(e).__name__}: {e}'
            print(f'Failed to load extension {extension}\n{exc}')


# bot.login(cf.bot_token)
# bot.connect(reconnect=True)
bot.run(f'{cf.bot_token}', reconnect=True)
