import copy

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

c.execute('''CREATE TABLE IF NOT EXISTS change_nickname (
    discordID INT PRIMARY KEY
    ) ''')

"https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876"

emoji_subs = {
    "🇦": "A",
    "🇧": "B",
    "🇨": "C",
    "🇩": "D",
    "🇪": "E",
    "🇫": "F",
    "🇬": "G",
    "🇭": "H",
    "🇮": "I",
    "🇯": "J",
    "🇰": "K",
    "🇱": "L",
    "🇲": "M",
    "🇳": "N",
    "🇴": "O",
    "🇵": "P",
    "🇶": "Q",
    "🇷": "R",
    "🇸": "S",
    "🇹": "T",
    "🇺": "U",
    "🇻": "V",
    "🇼": "W",
    "🇽": "X",
    "🇾": "Y",
    "🇿": "Z",
    "1️⃣": "1",
    "2️⃣": "2",
    "3️⃣": "3",
    "4️⃣": "4",
    "5️⃣": "5",
    "6️⃣": "6",
    "7️⃣": "7",
    "8️⃣": "8",
    "9️⃣": "9",
}

jef_success = [
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/jeff-channing-tatum-22jump-street-disguise-gif-8025876",
    "https://tenor.com/view/this-agree-gif-9813936",
    "https://tenor.com/view/jeff-bergman-voice-actor-actor-point-pointing-gif-15102959",
    "https://tenor.com/view/called-it-pointing-up-look-up-gif-15660507",
    "https://tenor.com/view/pointing-up-looking-up-running-approaching-taeyong-gif-14622356",
    "https://tenor.com/view/sgn-we-did-it-mission-accomplished-well-done-its-over-gif-17098451",
    "https://tenor.com/view/will-ferrell-elf-congrats-you-did-it-congratulations-gif-5618329",
    "https://tenor.com/view/dedication-hard-work-success-dreams-motivation-gif-13340821",
    "https://tenor.com/view/bored-look-up-ugh-look-wade-wilson-gif-11696925",
    "https://tenor.com/view/yeah-excellent-extra-hello-hello-u-gif-21823546",
    "https://tenor.com/view/pikachu-shocked-face-stunned-pokemon-shocked-not-shocked-omg-gif-24112152",
    "https://tenor.com/view/anime-dance-moves-happy-point-up-gif-17417642",
    "https://tenor.com/view/surprised-sorprendido-shaquille-oneal-gif-23222312",
    "https://tenor.com/view/shocked-face-shock-surprised-surprise-monkey-gif-16328898",
    "https://tenor.com/view/friends-matt-leblanc-matt-shock-omg-gif-7714163",
    "https://tenor.com/view/wow-look-just-said-that-omg-last-gif-7454422"
    "https://tenor.com/view/lebron-james-los-angeles-lakers-look-up-what-is-that-nba-gif-16045196",
    "https://tenor.com/view/look-up-there-south-park-s3e11-starvin-marvin-in-space-check-that-out-gif-21682674",

]


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

        new_nickname = ""
        for _ in range(num):
            if not emoji_list:
                return
            emoji = random.choice(emoji_list)
            emoji.replace('\u200d', '')
            emoji_list.remove(emoji)
            try:
                await message.add_reaction(emoji)
                new_nickname += emoji if emoji not in emoji_subs.keys() else emoji_subs[emoji]
            except discord.HTTPException:
                continue

        nickname_info = [i for i in c.execute('SELECT * FROM change_nickname WHERE discordID = ? ',
                                              (message.author.id,))]

        if not nickname_info:
            return

        member = message.guild.get_member(message.author.id)
        if new_nickname == "JEF" and member.id == 273320140119080961:
            await message.channel.send(random.choice(jef_success))

        try:
            await message.author.edit(nick=new_nickname)
        except discord.Forbidden:
            return


    @commands.command(brief=f"Change nickname to reactions", usage="", aliases=['tognick'],
                      help="Must have the auto-react active.",
                      description=f"Because why the fuck not?")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def togglenickname(self, ctx: commands.Context):
        nickname_info = [i for i in c.execute('SELECT * FROM change_nickname WHERE discordID = ? ',
                                              (ctx.author.id,))]

        if nickname_info:
            active_nick = False
            c.execute("DELETE FROM change_nickname WHERE discordID = ?", (ctx.author.id,))
        else:
            active_nick = True
            c.execute("INSERT OR REPLACE INTO change_nickname VALUES (?)", (ctx.author.id,))

        conn.commit()

        if active_nick:
            await f.success_embed(ctx, "Active Nickname Enabled!", ctx.author)
        else:
            await f.success_embed(ctx, "Active Nickname Disabled!", ctx.author)

    @commands.command(brief=f"Auto-react to your messages", usage="[number=1] [emojis*]", aliases=[],
                      help="Each emoji you input should have a space in between.",
                      description=f"This will make the bot be your personal fan! "
                                  f"Every time you post a message, "
                                  f"the bot will add the X emoji's from the list you gave!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def addfan(self, ctx: commands.Context, num: int = 1, *emojis: str):

        emoji_list = []
        for i in emojis:
            try:
                emoji = i.replace('\u200d', '')
                await ctx.message.add_reaction(emoji)
                emoji_list += [emoji]
            except discord.HTTPException:
                continue

        if not emoji_list:
            return await f.error_embed(ctx, "Couldn't add any emojis!\n\n"
                                            "Some emoji are actually 2 seperate ones put together, "
                                            "I tend to not be able to figure those out yet.", ctx.author)

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
