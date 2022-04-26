import asyncio
import discord
from discord.ext import commands
import sqlite3
import subprocess

import config as cf

conn = sqlite3.connect(cf.db_bot, timeout=5.0)
c = conn.cursor()
conn.row_factory = sqlite3.Row


async def request_embed(ctx: commands.Context, description: str, author: discord.User, send=True):
    embed = discord.Embed(description=f"{description}", color=cf.color_info)
    # embed.set_thumbnail(url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/white-question-mark_2754.png")
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


async def sent_embed(ctx: commands.Context, title: str, author: discord.User, msg: discord.Message, send=True):
    embed = discord.Embed(title=f"{title}", color=cf.color_info, url=msg.jump_url)
    # embed.set_thumbnail(url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/white-question-mark_2754.png")
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


async def hub_invite_embed(ctx: commands.Context, title: str, author: discord.User, send=True):
    embed = discord.Embed(title=f"{title}", color=cf.color_info, url=cf.hub_invite_url)
    # embed.set_thumbnail(url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/white-question-mark_2754.png")
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


async def error_embed(ctx: commands.Context, description: str, author: discord.User, send=True):
    embed = discord.Embed(description=f"⚠ {description}", color=cf.color_error)
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


async def reject_embed(ctx: commands.Context, description: str, author: discord.User, send=True):
    embed = discord.Embed(description=f"🛑 {description}", color=cf.color_decline)
    # embed.set_thumbnail(url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/313/cross-mark_274c.png")
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


async def success_embed(ctx: commands.Context, description: str, author: discord.User, send=True):
    embed = discord.Embed(description=f"✅ {description}", color=cf.color_accept)
    # embed.set_thumbnail(url="https://emojipedia-us.s3.amazonaws.com/source/skype/289/check-mark_2714-fe0f.png")
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


async def spiderman_embed(ctx: commands.Context, description: str, author: discord.User, send=True):
    embed = discord.Embed(description=f"{description}", color=cf.color_decline)
    embed.set_thumbnail(url="https://i.imgur.com/C87xx6T.jpg")
    if send:
        embed.set_footer(text=f"Responding to {author}", icon_url=author.display_avatar.url)
        return await ctx.reply(embed=embed)
    return embed


class functions_embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_guild_join(self, guild):
    #
    #     guild_database = [row for row in c.execute('SELECT server_id FROM server')]
    #
    #     if guild.id not in guild_database:
    #         createGuildProfile(guild.id)
    #
    #
    # @commands.Cog.listener()
    # async def on_ready(self):
    #
    #     guild_database = [row[0] for row in c.execute('SELECT server_id FROM server')]
    #
    #     for guild in self.bot.guilds:
    #         if guild.id not in guild_database:
    #             createGuildProfile(guild.id)


def setup(bot):
    bot.add_cog(functions_embed(bot))
