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
    bot.add_cog(Stats(bot))

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command('server_info')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def server_info(self, ctx: object):
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
            embed.add_field(name = 'Boosters', value = ', '.join(member.name for member in guild.premium_subscribers), inline = False)

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

            file = discord.File(filename, filename = 'image.png')
            embed = discord.Embed()
            embed.set_image(url = 'attachment://image.png')
            
            await ctx.send(file = file, embed = embed)
            remove(filename)