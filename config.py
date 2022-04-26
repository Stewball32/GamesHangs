

bot_token = ""
""" If you don't know where to get your bot tokens, go to https://discord.com/developers/applications 
    Create an application > Bot > Add Bot > Reveal Token
    To invite your bot to a server, OAuth2 > tick Bot > Select the permissions you want > Then copy the invite link in the middle """

db_bot = './databases/bot.db'

hub_guild_id = 0  # Enter your Guild's ID Here

color_ask = int("EFE4B0", 16)       # Light Yellow
color_accept = int("22B14C", 16)    # Green
color_decline = int("ED1C24", 16)   # Red
color_info = int("00A2E8", 16)      # Light Blue
color_error = int("FF7F27", 16)     # Orange
color_timeout = int("C3C3C3", 16)   # Grey


""" You want to put your bot token in another separate file like this and import them over to the main script so you can 
    exclude all sensitive information if you are ever going to upload them on GitHub by adding this script to a .gitignore file. """
