from threading import Thread

import discord
from discord.ext import commands

from config import Config


__author__ = 'Harry Lees'
__credits__ = ['Harry Lees']
__status__ = 'Development'

# setup Discord connection
bot = commands.Bot(command_prefix = '!')
bot.load_extension('cogs.verification')
bot.load_extension('cogs.utils')

channel = bot.get_channel('channel id')


@bot.event
async def on_ready() -> None:
    '''
    builtin Discord.py function which runs on startup.
    '''

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


if __name__ == '__main__':
    bot.run(Config.DISCORD_BOT_TOKEN)
