import discord

from config import DiscordConfig
from discord.ext import commands
from discord.utils import get


def setup(bot: object) -> None:
    bot.add_cog(Utils(bot))

class Utils(commands.Cog, name = 'Utils'):
    '''
    A collection of various utilities.
    '''
    
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


    @commands.command(name = 'server_expansion')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def server_expansion(self, ctx: object):
        author = ctx.message.author
        guild = author.guild

        description = (
            'We are proposing to open the server to include more years and subjects. '
            'Now that we have a solid verification system, we feel comfortable opening the server for more students to join. '
            'Our goal has always been to bring students together and help people meet others on their course. '
            'We believe that opening the server to more students will cultivate a larger and more active community which will lead to a better experience for everyone.'
        )

        generalChats = (
            'There will be more users in the server, as such, general chats (general-chat, lecturer-chat, and some others) will remain open to all subjects meaning they will likely be more active. '
            'Furthermore, off topic chats will be available to everyone to select so there will be many more users to play games, talk about tech, and discuss how much money is too much to spend on shoes.'
        )


        subjectRoles = (
            'We will be re-evaluating and re-enforcing the subject roles to ensure that students have a familiar group of students to fall back on, maintaining the friendly and private feel that the server offered in the beginning. '
            'Choosing your subject role will grant access to a selection of private text and voice channels allowing you to talk about whatever you want within the privacy of your own course.'
        )

        helpers = (
            'We will be restructuring the role of Helpers within the server. We want to ensure that each subject has a range of knowledgeable helpers who are open to helping students navigate the subject and server as-well while allowing Moderators to tackle server-wide issues. '
            'We want to ensure that there is no power discrepancy between members and moderators of the server. '
            'The moderators are not content moderators as-much as they are there to help answer tickets and help users on a higher level such as organising server events.'
        )

        outsideMembers = (
            'We will look closely at the role of non-Aston students within the server. '
            'While we are a server mainly focussed on Aston University students, we are not completely closed to the outside world. '
            'We understand that members may want to use the off-topic channels to discuss things with friends from other universities. '
            'For users that do not use Discord much, this may be their go-to discord server. We want to encourage this and, as such, we will allow limited access to off-topic channels for non-Aston members. '
            'In the short term we will evaluate these users on a case by case basis until we have a more concrete solution for vetting members of other universities. '
        )


        outro = (
            'We would like to thank everyone for their participation in this server, if anyone has any suggestions, we are taking suggestions in the #suggestions channel. '
            'Furthermore, you may open a ticket to open a discussion with the moderation team if you are curious about any aspects of this announcement or have anything else you would like to talk about.'
        )

        embed = discord.Embed(title = 'Server Expansion', description = description, colour = discord.Colour.blurple())
        embed.set_thumbnail(url = guild.icon_url)

        embed.add_field(name = 'General Chats', value = generalChats, inline = False)
        embed.add_field(name = 'Subject Roles', value = subjectRoles, inline = False)
        embed.add_field(name = 'Helpers', value = subjectRoles, inline = False)
        embed.add_field(name = 'Non Aston Students', value = outsideMembers, inline = False)
        embed.add_field(name = 'Thank you!', value = outro, inline = False)

        await ctx.send(embed = embed)