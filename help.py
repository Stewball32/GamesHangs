import asyncio
import config
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import sqlite3
import config as cf

conn = sqlite3.connect(config.db_bot, timeout=5.0)
c = conn.cursor()
conn.row_factory = sqlite3.Row


class Help(commands.Cog, name="Help"):

    def __init__(self, bot):
        self.bot: discord.Bot = bot
        print("help.py extension has loaded!")

    # commands.command(
    #     name='help',
    #     description='The help command!',
    #     aliases=['commands', 'command'],
    #     usage='cog'
    # )
    @commands.command()
    async def help(self, ctx: commands.Context):
        # Other Cogs: "👪 Team Commands", "🛡️ Captain Commands",
        cog_name_list = ["💫 'Naut Commands", "🧍 Player Commands", "🎲 Scrim Commands"]
        cogs = [cog for cog in cog_name_list if len(self.bot.get_cog(cog).get_commands()) != 0]

        prefix_dict = {}
        for prefix in c.execute(f'SELECT guild_id, prefix FROM prefix'):
            prefix_dict.update({prefix[0]: f"{prefix[1]}"})

        current_prefix = prefix_dict[ctx.message.guild.id]

        cog_index = 0
        command_index = 0

        async def select_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message(
                    f"Only {ctx.author.mention} can use that menu. "
                    f"Use `{current_prefix}help` to make your own embed.", ephemeral=True)
            else:
                nonlocal current_embed
                nonlocal cog_index
                nonlocal command_index
                command_index = int(interaction.data["values"][0])
                current_embed = all_embeds[cog_index-1][command_index]
                if hasattr(view.children[0], "placeholder"):
                    view.children[0].placeholder = f"{current_embed.title}"
                for child in view.children:
                    child.disabled = False
                await msg.edit(embed=current_embed, view=view)

        async def button_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message(
                    f"Only {ctx.author.mention} can use that button. "
                    f"Use `{current_prefix}help` to make your own embed.", ephemeral=True)
            else:
                nonlocal current_embed
                nonlocal cog_index
                view.clear_items()
                cog_index = int(interaction.data["custom_id"][0])
                view.add_item(all_selects[cog_index-1])
                for button in all_buttons:
                    view.add_item(button)

                current_embed = all_embeds[cog_index-1][0]
                for child in view.children:
                    child.disabled = False
                    child.style = discord.ButtonStyle.blurple
                view.children[cog_index].disabled = True

                if hasattr(view.children[0], "placeholder"):
                    view.children[0].placeholder = f"{current_embed.title}"

                if hasattr(view.children[cog_index], "style"):
                    view.children[cog_index].style = discord.ButtonStyle.green
                await msg.edit(embed=current_embed, view=view)

        footer = f"{ctx.message.guild}'s prefix: {current_prefix}\n" \
                 f"Click a button for more category help!"

        home_embed = discord.Embed(colour=cf.color_info, title=f"🏠 All Commands",
                                   description=f"Type `{current_prefix}myprefix` for this server's prefix.\n")
        # home_embed.set_author(name=f"🏠 All Commands")
        home_embed.set_footer(text=footer, icon_url=self.bot.user.display_avatar.url)

        for cog_name in cogs:
            cog_commands = self.bot.get_cog(cog_name).get_commands()
            cog_name = f"{cog_name}"

            commands_list = ''
            for comm in cog_commands:
                if comm.hidden is True:
                    continue
                commands_list += f'`{comm}` '

            home_embed.add_field(name=cog_name, value=commands_list, inline=False)

        home_option = discord.SelectOption(label="🏠 All Commands", value=str(0), emoji="🏠")

        quick_embed = discord.Embed(colour=cf.color_info, title=f"🏠 QuickStart Info",
                                    description="Get a jump into the Ladder System!\n"
                                                "*brackets[] are to show input, you don't need the brackets"
                                                "when entering the info*")
        # quick_embed.set_author(name=f"🏠 QuickStart Info")
        quick_embed.add_field(name="Step 1: Join the Ladder system", inline=False,
                              value=f'Use `{current_prefix}newplayer`\n'
                                    f'Register yourself for the ladder to see you.\n\u200b')
        quick_embed.add_field(name="Step 2: Create a Team or Join a Team.", inline=False,
                              value=f'*You can skip this step if you\'re only interested in 1v1s*\n'
                                    f'Use `{current_prefix}newteam` or `{current_prefix}jointeam`.\n'
                                    f'Create your own team and invite people `{current_prefix}inviteplayer [player]`, '
                                    f'or find your friend\'s team and join them `{current_prefix}jointeam [team tag]`\n\u200b')
        quick_embed.add_field(name="Step 3: Join a Ladder.", inline=False,
                              value=f'Use `{current_prefix}joinladder [ladder tag]` to join a ladder to compete in!\n'
                                    f'Can\'t find a ladder to join? Use `{current_prefix}infoladder` to find one you like!\n\u200b')
        quick_embed.add_field(name=f"Step 4: Challenge someone to a Match!", inline=False,
                              value=f"Use `{current_prefix}newmatch [ladder tag] (team tag)` to schedule a match "
                                    f"against an opponent!\n\u200b")
        quick_embed.set_footer(text=footer, icon_url=self.bot.user.display_avatar.url)

        quick_option = discord.SelectOption(label="🏠 QuickStart Info", value=str(1), emoji="🏠")

        home_select = discord.ui.Select(custom_id="Home", placeholder="🏠 All Commands",
                                        options=[home_option, quick_option])
        home_select.callback = select_callback

        all_embeds = [[home_embed, quick_embed]]
        all_selects = [home_select]

        for cog_name in cogs:
            cog = self.bot.get_cog(f"{cog_name}")
            cog_commands = cog.get_commands()

            help_embed = discord.Embed(title=f'{cog_name} Overview', color=cf.color_info,
                                       description=f"{cog.description}\n\n"
                                                   f"*Template: {current_prefix}command [required] (optional=default)*")
            help_embed.set_footer(text=footer, icon_url=self.bot.user.display_avatar.url)

            select_options = [discord.SelectOption(label=f"{f'{cog_name[2:]}'.replace(' Commands', '')} Overview",
                                                   emoji=cog_name[0], value=str(0))]
            cog_embeds = [help_embed]
            comm_count = 1
            for comm in cog_commands:
                if comm.hidden is True:  # Skips hidden commands, meant to hide that admin commands.
                    continue

                command_option = discord.SelectOption(label=comm.name, value=str(comm_count), emoji=cog_name[0])
                select_options += [command_option]
                comm_count += 1

                help_embed.add_field(name="\u200b", inline=True,
                                     value=f"**{comm.brief}**\n"
                                           f"`{current_prefix}{comm.name}{f' {comm.usage}' if comm.usage else ''}`\n"
                                           f"*{'alt: ' + ', '.join(comm.aliases) if comm.aliases else ''}\u200b*")

                comm_embed = discord.Embed(title=f"{cog_name[0]} '{comm.name}' Command Details", color=cf.color_info,
                                           description=f"{f'*{comm.description}*' if comm.description else ''}\n\u200b")
                if comm.help:
                    comm_embed.add_field(name="Requirements", value=f"{comm.help}\n\u200b", inline=False)
                if comm.usage:
                    comm_embed.add_field(name=f"{current_prefix}commandname [Required] (Optional=Default)",
                                         value=f"`{current_prefix}{comm.name}{f' {comm.usage}' if comm.usage else ''}`\n"
                                               f"Don't type brackets when using command\n\u200b", inline=True)
                if comm.aliases:
                    comm_embed.add_field(name="Aliases", value=f"{', '.join(comm.aliases)}\n\u200b", inline=True)

                comm_embed.set_footer(text=footer, icon_url=self.bot.user.display_avatar.url)

                cog_embeds += [comm_embed]

            cog_select = discord.ui.Select(custom_id=f"{cog_name}", placeholder=f"{cog_name} Overview",
                                           options=select_options)
            cog_select.callback = select_callback

            all_embeds += [cog_embeds]
            all_selects += [cog_select]

        view = discord.ui.View()
        home_button = discord.ui.Button(label="All", emoji="🏠", style=discord.ButtonStyle.green, disabled=True, custom_id="1")
        home_button.callback = button_callback
        all_buttons = [home_button]
        count = 2
        for cog_name in cogs:
            label = f"{cog_name[2:]}".replace(" Commands", "")
            cog_button = discord.ui.Button(label=label, emoji=cog_name[0], style=discord.ButtonStyle.blurple, custom_id=str(count))
            cog_button.callback = button_callback
            all_buttons += [cog_button]
            count += 1

        view.add_item(all_selects[0])
        for i in all_buttons:
            view.add_item(i)

        current_embed = all_embeds[0][0]

        msg = await ctx.send(embed=current_embed, view=view)

        if await view.wait():
            current_embed.set_footer(text=f"This embed has timed out. Use {current_prefix}help to make a new one.",
                                     icon_url=self.bot.user.display_avatar.url)
            current_embed.colour = cf.color_timeout
            await msg.edit(embed=current_embed, view=None)


def setup(bot):
    bot.add_cog(Help(bot))
