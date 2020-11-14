import discord

from config import DiscordConfig
from discord.ext import commands
from discord.utils import get


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

        embed = discord.Embed(title = 'Pong', description = f':stopwatch: latency: {self.bot.latency*1000:.2f}ms', color = discord.Colour.green())
        await ctx.send(embed = embed)