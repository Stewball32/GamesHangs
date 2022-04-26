import discord
from discord.ext import commands
import sqlite3
import random
import cogs.functions as f


conn = sqlite3.connect("./databases/jeff.db", timeout=5.0)
c = conn.cursor()
conn.row_factory = sqlite3.Row

c.execute('''CREATE TABLE IF NOT EXISTS react (
    discordID INT PRIMARY KEY,
    emojis TEXT,
    number INT
    ) ''')

class jeffCommands(commands.Cog, name="👨 Jeff's Commands"):
    def __init__(self, bot: discord.Bot):
        self.bot: discord.Bot = bot

    @discord.Cog.listener("on_message")
    async def check_jeff(self, message: discord.Message):
        userinfo = [i for i in c.execute('SELECT emojis, number FROM react WHERE discordID = ? ',
                                         (message.author.id,))]
        if not userinfo:
            return

        emoji_str, num = userinfo[0]
        emoji_str: str = emoji_str[2:-2]
        emoji_list = emoji_str.split("', '")

        for _ in range(num):
            if not emoji_list:
                return
            emoji = random.choice(emoji_list)
            emoji.replace('\u200d', '')
            emoji_list.remove(emoji)
            await message.add_reaction(emoji)

    @commands.command(brief=f"Auto-react to your messages", usage="[number=1] [emojis*]", aliases=[],
                      help="Each emoji you input should have a space in between.",
                      description=f"This will make the bot be your personal fan! "
                                  f"Every time you post a message, "
                                  f"the bot will add the X emoji's from the list you gave!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def addfan(self, ctx: commands.Context, num: int = 1, *emojis: str):

        emoji_list = []
        for i in emojis:
            print(i, end="")
            try:
                emoji = i.replace('\u200d', '')
                await ctx.message.add_reaction(emoji)
                emoji_list += [emoji]
                print("y")
            except discord.HTTPException:
                print("n")
                continue

        c.execute("INSERT OR REPLACE INTO react VALUES (?, ?, ?)",
                  (ctx.author.id, str(emoji_list), num))

        try:
            conn.commit()
            await f.success_embed(ctx, f"Emoji's added!\n{' '.join(emoji_list)}", ctx.author)
        except sqlite3.Error:
            await f.error_embed(ctx, f"Something went wrong.", ctx.author)

    @commands.command(brief=f"Stop the autoreact", usage="", aliases=[],
                      help="",
                      description=f"This will remove your list of emojis "
                                  f"so the bot will no longer react to your messages.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def removefan(self, ctx: commands.Context, num: int = 1, *emojis: str):

        c.execute('DELETE FROM react WHERE discordID = ?',
                  (ctx.author.id,))
        try:
            conn.commit()
            await f.success_embed(ctx, f"All Emoji's Removed", ctx.author)
        except sqlite3.Error:
            await f.error_embed(ctx, f"Something went wrong.", ctx.author)



def setup(bot):
    bot.add_cog(jeffCommands(bot))
