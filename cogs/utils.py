from os import remove

import discord
import matplotlib

matplotlib.use('Agg')
from collections import Counter
from datetime import datetime, timedelta
from os import remove

import matplotlib.pyplot as plt
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

        embed = discord.Embed(title = 'Pong', description = f'latency: {self.bot.latency*1000:.2f}ms', color = discord.Colour.green())
        await ctx.send(embed = embed)


    @commands.command('stats')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def stats(self, ctx: object):
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


    @commands.command('join_log')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
        async def join_log(self, ctx: object):
        filename = 'temp.png'
        author = ctx.message.author
        guild = author.guild
        
        async with ctx.typing():
            joined_dates = Counter([member.joined_at.date() for member in guild.members])

            start_date = min(joined_dates)
            end_date = datetime.today().date()
            delta = end_date - start_date

            dates = [(start_date + timedelta(days = i)) for i in range(delta.days + 1)]
            values = [joined_dates.get(date, 0) for date in dates]

            fig, ax = plt.subplots()

            ax.plot(dates, values)
            ax.set_ylabel('People Joined')
            ax.set_xlabel('Date')
            ax.set_title('Number of People joined over time')
            ax.grid(True)

            fig.autofmt_xdate()
            fig.tight_layout()
            fig.savefig(filename)

            await ctx.send(file = discord.File(filename))
            remove(filename)
