import discord

from config import DiscordConfig
from discord.ext import commands
from discord.utils import get
from typing import Union

def setup(bot: object) -> None:
    bot.add_cog(Moderation(bot))

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def _error(self, ctx, error: Exception):
        embed = discord.Embed(title = 'Error', description = str(error), colour = discord.Colour.red())
        await ctx.send(embed = embed)


    @commands.command(name = 'mute')
    def mute(self, ctx: object, member: Union[discord.Member, str]):
        author = ctx.message.author
        guild = author.guild

        if isinstance(member, str):
            member = get(guild.members, name = member)

        await member.edit(mute = True)
        await ctx.send(f'{member.name} has been muted')


    @mute.error
    def mute_error(self, ctx: object, error: Exception):
        await self._error(error)


    @commands.command(name = 'unmute')
    def unmute(self, ctx: object, member: Union[discord.Member, str]):
        author = ctx.message.author
        guild = author.guild

        if isinstance(member, str):
            member = get(guild.members, name = member)

        await member.edit(mute = False)
        await ctx.send(f'{member.name} has been unmuted')

    @unmute.error
    def unmute_error(self, ctx: object, error: Exception):
        await self._error(error)