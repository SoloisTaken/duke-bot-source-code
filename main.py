#!/usr/bin/env python3

import os

from discord.ext import commands

# necessary to host bot on ReplIt 
from webserver import keep_alive

bot = commands.Bot(command_prefix='d!', help_command=None)
bot.load_extension("cmds")

@commands.is_owner()
@bot.command(description='Reload bot, hidden=True')
async def reload(ctx):
    try:
        bot.reload_extension("cmds")
        # green checkmark
        await ctx.message.add_reaction('\u2705')
    except commands.errors.ExtensionNotLoaded:
        # red X
        await ctx.message.add_reaction('\u274C')
        raise

def main():
    keep_alive()

    token = os.environ.get("DISCORD_BOT_SECRET")
    bot.run(token)

if __name__ == "__main__":
    main()
