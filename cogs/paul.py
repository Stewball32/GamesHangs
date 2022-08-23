import discord
from discord.ext import commands, tasks
import datetime
import pytz


PACIFIC = pytz.timezone('America/Los_Angeles')
NIGHT = datetime.time(hour=18, minute=30, tzinfo=PACIFIC)


class paulCommands(commands.Cog, name="🧔 Paul's Commands"):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.checkevent.start()

    async def makeevent(self):
        guild = self.bot.get_guild(758566294836215828)
        if not guild:
            return
        voice_channel = guild.voice_channels[-1]
        text_channel = guild.get_channel(758566294836215831)
        role = guild.get_role(923078735945662505)
        if not voice_channel and not text_channel:
            return

        today = datetime.date.today()
        if today.weekday() == 0:
            monday = today
        else:
            monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
        monday_night = datetime.datetime.combine(monday, datetime.time(19, 30))
        next_event = PACIFIC.localize(monday_night)

        new_event = await guild.create_scheduled_event(
            name="Monday Game Night",
            start_time=next_event,
            location=voice_channel,
            description="We hanging and gaming.",
        )

        await text_channel.send(f"Yo {role.mention}\n{new_event.url}")

    @tasks.loop(time=NIGHT)
    async def checkevent(self):
        now = datetime.datetime.now(PACIFIC)
        if now.weekday() == 6:
            await self.makeevent()

    @commands.command(brief=f"Make monday event", usage="", aliases=['mon'],
                      help="",  # help is the requirements
                      description="Create the Monday Night Game Event (7:30pm) "
                                  "and post it in the channel the command was created.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def monday(self, ctx: commands.Context):
        now = int(datetime.datetime.now(pytz.UTC).timestamp())

        for event in ctx.guild.scheduled_events:
            if event.name == "Monday Game Night" and int(event.start_time.timestamp()) > now:
                return await ctx.send("There's already a Monday Game Night Event!")

        await self.makeevent()


def setup(bot):
    bot.add_cog(paulCommands(bot))
