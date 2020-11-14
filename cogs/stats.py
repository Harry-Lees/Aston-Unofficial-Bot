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
import uuid

def setup(bot: object) -> None:
    bot.add_cog(Stats(bot))

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def _error(self, ctx, error: Exception):
        embed = discord.Embed(title = 'Error', description = str(error), colour = discord.Colour.red())
        await ctx.send(embed = embed)


    @commands.command('server_info')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def server_info(self, ctx: object):
        '''
        Command displays various stats about the server.
        '''

        author = ctx.message.author
        guild = author.guild

        embed = discord.Embed(title = f'{guild.name} Info', colour = discord.Colour.blue())

        embed.set_thumbnail(url = guild.icon_url)

        if guild.banner_url:
            embed.set_image(url = guild.banner_url)

        embed.add_field(name = 'Owner', value = guild.owner, inline = True)
        embed.add_field(name = 'Region', value = guild.region, inline = True)
        embed.add_field(name = 'Created On', value = guild.created_at.strftime('%Y-%m-%d'), inline = True)
        
        embed.add_field(name = 'Members', value = guild.member_count, inline = True)
        embed.add_field(name = 'Roles', value = len(guild.roles), inline = True)
        embed.add_field(name = 'Premium Tier', value = guild.premium_tier, inline = True)
        
        embed.add_field(name = 'Description', value = guild.description, inline = False)

        embed.add_field(name = 'Text Channels', value = len(guild.text_channels), inline = True)
        embed.add_field(name = 'Voice Channels', value = len(guild.voice_channels), inline = True)
        

        if guild.premium_subscribers:
            embed.add_field(name = 'Boosters', value = ', '.join(member.nick if member.nick else member.name for member in guild.premium_subscribers), inline = False)

        await ctx.send(embed = embed)


    @commands.command('join_log')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def join_log(self, ctx: object):
        '''
        Command gives various stats about the number of members joining the server.
        '''

        filename = f'{uuid.uuid1()}.png'
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

            file = discord.File(filename, filename = 'image.png')

            embed = discord.Embed(title = 'Member Join Log', colour = discord.Colour.blue())
            embed.set_thumbnail(url = guild.icon_url)
            embed.set_image(url = 'attachment://image.png')

            embed.add_field(name = 'Total Members', value = guild.member_count, inline = False)

            for date, num in joined_dates.items():
                if num == max(joined_dates.values()):
                    temp = f'{num} people on {date}'

            embed.add_field(name = 'Most Active Day', value = temp, inline = False)
            
            embed.add_field(name = 'Average joins/day', value = round(sum(joined_dates.values()) / len(dates), 3), inline = False)

            await ctx.send(file = file, embed = embed)
            remove(filename)


    @commands.command('member_log')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def member_log(self, ctx: object):
        '''
        Command gives various stats about the number of members on the server.
        '''

        filename = f'{uuid.uuid1()}.png'
        author = ctx.message.author
        guild = author.guild
        
        async with ctx.typing():
            joined_dates = Counter([member.joined_at.date() for member in guild.members])

            start_date = min(joined_dates)
            end_date = datetime.today().date()
            delta = end_date - start_date

            dates = [(start_date + timedelta(days = i)) for i in range(delta.days + 1)]
            values = [joined_dates.get(date, 0) for date in dates]

            for i in range(1, len(values)):
                values[i] = values[i] + values[i-1]

            fig, ax = plt.subplots()

            ax.plot(dates, values)
            ax.set_ylabel('Members')
            ax.set_xlabel('Date')
            ax.set_title('Members over time')
            ax.grid(True)

            fig.autofmt_xdate()
            fig.tight_layout()
            fig.savefig(filename)

            file = discord.File(filename, filename = 'image.png')

            embed = discord.Embed(title = 'Member Join Log', colour = discord.Colour.blue())
            embed.set_thumbnail(url = guild.icon_url)
            embed.set_image(url = 'attachment://image.png')

            embed.add_field(name = 'Total Members', value = guild.member_count, inline = False)

            for date, num in joined_dates.items():
                if num == max(joined_dates.values()):
                    temp = f'{num} people on {date}'

            embed.add_field(name = 'Most Active Day', value = temp, inline = False)
            
            embed.add_field(name = 'Average joins/day', value = round(sum(joined_dates.values()) / len(dates), 3), inline = False)

            await ctx.send(file = file, embed = embed)
            remove(filename)