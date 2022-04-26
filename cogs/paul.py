import discord
from discord.ext import commands
import datetime
import pytz


class paulCommands(commands.Cog, name="🧔 Paul's Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief=f"Make monday event", usage="", aliases=['mon'],
                      help="",  # help=requirements
                      description="Create the Monday Night Game Event (7:30pm) "
                                  "and post it in the channel the command was created.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def monday(self, ctx: commands.Context):

        voice_channel = ctx.guild.voice_channels[-1]

        today = datetime.date.today()
        next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
        pacific = pytz.timezone('America/Los_Angeles')
        next_event = datetime.datetime.combine(next_monday, datetime.time(19, 30), pacific)

        new_event = await ctx.guild.create_scheduled_event(
            name="Monday Game Night",
            start_time=next_event,
            location=voice_channel,
            description="We hanging and gaming.",
        )

        await ctx.send(new_event.url)


def setup(bot):
    bot.add_cog(paulCommands(bot))
