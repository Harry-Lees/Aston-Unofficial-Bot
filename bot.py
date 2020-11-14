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
bot.load_extension('cogs.stats')
bot.load_extension('cogs.moderation')


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


@bot.event
async def on_error(ctx: object, error: Exception):
    embed = discord.Embed(title = 'Error', description = str(error), colour = discord.Colour.red())
    await ctx.send(embed = embed)


if __name__ == '__main__':
    bot.run(Config.DISCORD_BOT_TOKEN)
