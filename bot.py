import discord
from discord.ext import commands
from cogs.help import CustomHelp

from config import Config


__author__ = 'Harry Lees'
__credits__ = ['Harry Lees']
__status__ = 'Development'

# setup Discord connection
bot = commands.Bot(command_prefix = '!')
bot.help_command = CustomHelp()

cogs = ('cogs.verification', 'cogs.utils', 'cogs.stats', 'cogs.moderation', 'cogs.fun_things')
for cog in cogs:
    bot.load_extension(cog)

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
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Tony's Saxophone"))

@bot.event
async def on_command_error(ctx: object, error: Exception):
    embed = discord.Embed(title = 'Error', description = str(error), colour = discord.Colour.red())
    await ctx.send(embed = embed)


@bot.event
async def on_error(ctx: object, error: Exception):
    embed = discord.Embed(title = 'Error', description = str(error), colour = discord.Colour.red())
    await ctx.send(embed = embed)


@bot.event
async def send_bot_help(ctx: object):
    await ctx.send('help')

if __name__ == '__main__':
    bot.run(Config.DISCORD_BOT_TOKEN)
