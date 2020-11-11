from os import remove

import discord
import matplotlib.pyplot as plt
from discord.ext import commands
from discord.utils import get

from config import DiscordConfig

def setup(bot: object) -> None:
    bot.add_cog(Utils(bot))

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name = 'mass_dm')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def mass_dm(self, ctx, role: str, *message: str):
        '''
        DM's all users with a given role.
        '''
        member = ctx.message.author
        role = get(member.guild.roles, name = role)

        joined_message = ' '.join(message)
        for member in role.members:
            await member.send(joined_message)
            await asyncio.sleep(1.5) # add sleep to avoid rate limit

        await ctx.reply(f'sending mass DM to {len(role.members)} users')


    @commands.command(name = 'ping')
    async def ping(self, ctx: object):
        '''
        Pong. Pings the server to check if it's up.
        '''

        embed = discord.Embed(title = 'Pong', description = f'latency: {self.bot.latency*1000:.2f}ms', color = discord.Colour.green())
        await ctx.send(embed = embed)


    @commands.command('stats')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def stats(ctx: object):
        author = ctx.message.author
        roles = author.guild.roles

        desc = f'''
        A Collection of {author.guild.name}'s stats
        Members:  {len(author.guild.members)}
        Roles:    {len(author.guild.roles)}
        Channels: {len(author.guild.channels)}
        '''

        embed = discord.Embed(title = f'{author.guild.name} Stats!', description = desc, colour = discord.Colour.blue())

        embed.add_field(name = 'Role', value = '\n'.join(role.name for role in roles if len(role.members) > 1), inline = True)
        embed.add_field(name = 'Num. Members', value = '\n'.join(str(len(role.members)) for role in roles if len(role.members) > 1), inline = True)
        embed.set_thumbnail(url = author.guild.icon_url)
        
        await ctx.send(embed = embed)