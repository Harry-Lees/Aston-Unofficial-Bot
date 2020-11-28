from threading import Thread
from typing import Union
from time import sleep
from random import randint

import asyncio
import discord
import psycopg2
import psycopg2.extensions
from config import Config, DiscordConfig
from discord.ext import commands
from discord.utils import get
from psycopg2.errors import UniqueViolation

from app.discord_verification.models import User

def setup(bot: object) -> None:
    bot.add_cog(Verification(bot))


class Verification(commands.Cog, name = 'Verification'):
    '''
    Holds Verification commands allowing mods to see details about a user's verification status or modifying the users verification status from within Discord.
    '''

    reverify_message = '''
    We've just introduced a new verification bot to ensure that all users are members of Aston University.

    - If you're currently a 2nd-year student or have had a foundation year, please contact a Moderator. You will be allowed in the Server, but we have to verify you manually!

    - If you are a *lecturer* or someone from another year group, please contact a Moderator to get manually verified.

    - You will be asked to provide your "aston.ac.uk" email address so we can properly verify that you go to Aston University.

    '''


    welcome_message = '''
    Thanks for joining the **Aston Unofficial Discord Server**

    Please verify your email by [clicking here](http://astonunofficial.co.uk/discord/register?user_id={})

    :warning: You will not be able to join the server without an aston.ac.uk email address :warning:

    You will be allocated a teacher or student role when you join the server.
    These will grant you access to all general channels that you are applicable for.
    After joining, there are several things you can do:

    :book:  **1. Read our info-rules channel**
    This channel contains all the rules and regulations for our server.

    :teacher:  **2. Join a Subject**
    This gives you access to your subject specific channels where you can find people from your course!
    To do this, please go into the #roles channel and react to the Emojis related to your subject.

    :soccer:  **3. Join Optional Channels**
    We have lots of optional channels for things such as Gaming, Music, Tech, and much more!
    To do this, please go into the #roles channel and react to the Emoji related to your interest.
    '''

    def __init__(self, bot):
        self.bot = bot

        thread = Thread(target = self.database_notify)
        thread.daemon = True
        thread.start()


    @commands.Cog.listener()
    async def on_member_join(self, member: object) -> None:
        '''
        builtin Discord.py function called whenever a user joins the
        Discord server.
        '''

        print('called')

        embed = discord.Embed(title = 'Welcome', description = self.welcome_message.format(member.id), color = discord.Colour.green())
        await member.send(embed = embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member: object) -> None:
        '''
        builtin Discord.py function called whenever a user leaves the
        Discord server.
        '''

        async for message in self.bot.get_user(member.id).history(limit = 100):
            if message.author.id == self.bot.user.id:
                await message.delete()
                await asyncio.sleep(0.5)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
            connection.commit()


    @commands.command(name = 'verify')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def verify(self, ctx: object, member: Union[discord.Member, str], email: str, role: Union[discord.Role, str]) -> None:
        '''
        Manually Verify a user. Their email will be added to the database.
        '''
        author = ctx.message.author # get the object of the author of the message
        
        if not isinstance(member, discord.Member):
            member = get(author.guild.members, name = member)
        
        if not isinstance(role, discord.Role):
            role = get(author.guild.roles, name = role)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection: # Could convert this to SQLAlchemy
            cursor = connection.cursor()

            arguments = {
                'user_id'   : str(member.id),
                'email'     : email
            }
            
            cursor.execute(f'INSERT INTO {User.__tablename__} VALUES(%(user_id)s, %(email)s, true)', arguments)

        await member.add_roles(role)

        embed = discord.Embed(title = 'Success!', description = f'{member.name} has been successfully verified', colour = discord.Colour.green())
        embed.add_field(name = 'Next Steps', value = 'don\'t forget to select your subject and interest roles in the <#756115420175532133> channel')

        await ctx.send(embed = embed)


    @commands.command(name = 'get_link')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def get_link(self, ctx: object, member: Union[discord.Member, str]) -> None:
        '''
        gets a verification link for a member.
        '''

        author = ctx.message.author

        if not isinstance(member, discord.Member):
            member = get(author.guild.roles, name = member)

        description = f'Please [click here](http://astonunofficial.co.uk/discord/register?user_id={member.id}) to verify your account.'

        embed = discord.Embed(title = 'Verification Link', description = description, color = discord.Colour.green())
        embed.add_field(name = 'Next Steps', value = '**Don\'t forget** to select your subject and interest roles in the <#756115420175532133> channel. \nIf you have any questions, please feel free to contact a Moderator by opening a ticket.')

        await ctx.send(embed = embed)


    @commands.command(name = 'self_link')
    async def self_link(self, ctx: object) -> None:
        '''
        gets a verification link for the user that executes the command.
        '''

        author = ctx.message.author
        await ctx.send(f'http://astonunofficial.co.uk/discord/register?user_id={author.id}')


    @commands.command(name = 'remove_role')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def remove_role(self, ctx: object, role: Union[discord.Role, str]) -> None:
        '''
        Removes a given role from *all* users in the server.
        '''

        author = ctx.message.author

        if not isinstance(role, discord.Role):
            role = get(author.guild.roles, name = role)

        await ctx.send(f'removing **{role}** role from {len(author.guild.members)} members in {len(author.guild.members) * 0.5}s')

        for member in author.guild.members:
            await member.remove_roles(role)
            await asyncio.sleep(0.5)

        await ctx.send('finished removing roles')


    @commands.command(name = 'unverify')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def unverify(self, ctx: object, member: Union[discord.Member, str]):
        '''
        Unverifies the user, removing their entry in the database. This command does not remove their roles.
        '''

        author = ctx.message.author
        
        if not isinstance(member, discord.Member):
            member = get(author.guild.roles, name = member)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection: # will only delete if record exists
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
            connection.commit()

        await ctx.send(f'{member.name} has had their verification revoked')


    @commands.command(name = 'verification_prompt')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def verification_prompt(self, ctx: object, role: str):
        '''
        sends a verification prompt to all users with a given role.
        '''

        message_limit = 30
        messages_sent = 0
        failed_messages = []

        author = ctx.message.author
        role = get(author.guild.roles, name = role)

        for member in role.members:
            embed = discord.Embed(title = 'Hey!', description = self.reverify_message.format(member.id), color = 0x7289DA)
            embed.add_field(name = 'How to Verify', value = f'To verify your account, please [click here](http://astonunofficial.co.uk/discord/register?user_id={member.id})', inline = False)
            embed.add_field(name = 'Next Steps', value = 'To access subject-relevant channels, please (re)select your subject in the #🎭roles channel!')

            try:
                messages_sent += 1

                if messages_sent % message_limit == 0:
                    asyncio.sleep(60.0)

                await member.send(embed = embed)
                print(f'sent message to {member}')
                await asyncio.sleep(randint(1, 3))

            except discord.errors.HTTPException as error:
                print(f'RATE LIMIT: failed to send message to {member}: {error}')
                await ctx.send('Rate limit exceeded, stopping send to prevent action being taken against the bot.')
                break

            except Exception as error:
                print(f'failed to send message to {member}: {error}')
                continue

        await ctx.send('verification prompt finished!')


    @commands.command(name = 'profile')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def profile(self, ctx: object, member: Union[discord.Member, str]):
        author = ctx.message.author
        verified = False

        if not isinstance(member, discord.Member):
            member = get(author.guild.members, name = member)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM discord_user_tab WHERE id = %s', [str(member.id)])
            user = cursor.fetchone()

        print(user)

        if user:
            if user[2]:
                verified = True
                colour = discord.Colour.green()
            else:
                colour = discord.Colour.red()
        else:
            colour = discord.Colour.red()

        if member.name[-1] == 's':
            title = f'{member.name}\' Profile'
        else:
            title = f'{member.name}\'s Profile'

        embed = discord.Embed(title = title, colour = colour)
        embed.set_thumbnail(url = member.avatar_url)

        embed.add_field(name = 'ID', value = member.id, inline = True)
        embed.add_field(name = 'Nickname', value = member.nick, inline = True)
        if user:
            embed.add_field(name = 'Email', value = user[1], inline = True)

        embed.add_field(name = 'Verified', value = verified, inline = False)
        embed.add_field(name = 'Joined Discord on', value = member.joined_at.strftime('%Y-%m-%d'), inline = True)
        embed.add_field(name = 'Joined Server on', value = member.created_at.strftime('%Y-%m-%d'), inline = True)

        embed.add_field(name = 'Roles', value = ', '.join(role.name for role in member.roles if not role.name.startswith('▬'))[:1000] + '...', inline = False)

        await ctx.send(embed = embed)


    @commands.command(name = 'email_profile')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def email_profile(self, ctx: object, email: str) -> None:
        author = ctx.message.author

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM discord_user_tab WHERE email = %s', [email])
            user = cursor.fetchone()

        if user:
            member = get(author.guild.members, id = int(user[0]))

            embed = discord.Embed(title = member.nick or member.name, colour = discord.Colour.green())
            embed.add_field(name = 'Verified', value = user[2], inline = False)

            embed.set_thumbnail(url = member.avatar_url)
        else:
            embed = discord.Embed(title = 'No User found', description = 'No user is registered with that email', colour = discord.Colour.red())

        await ctx.send(embed = embed)

    def database_notify(self) -> None: # I think there's a better way of doing this. Please find it :D
        '''
        function to wait for NOTIFY commands sent to the database.
        Once an update has occurred, check if the user has been verified. 
        If they are verified, give them a suitable role.
        '''

        while True:
            try:
                with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
                    cursor = connection.cursor()

                    cursor.execute(f'LISTEN {User.__tablename__}')
                    connection.commit()

                    print(f'LISTENING TO {User.__tablename__}')
            
                    while True:
                        connection.poll()
                        while connection.notifies:
                            notify = connection.notifies.pop(0)
                            print('received NOTIFY')
                            cursor.execute(f'SELECT id FROM {User.__tablename__} WHERE email = %(email)s', {'email' : notify.payload})
                            connection.commit()

                            try:
                                user_id = cursor.fetchone()[0]
                            except TypeError as error:
                                print(f'{error}. Is the given user in the database?')

                            guild = self.bot.guilds[0] # only works if the bot is connected to a single server, may change later
                            asyncio.run_coroutine_threadsafe(self.give_role(user_id, guild), self.bot.loop)

                        sleep(1)
            except psycopg2.OperationalError:
                print('error connecting to database')


    async def give_role(self, user_id: str, guild: object) -> None:
        user_id = int(user_id) # user_id has to be an integer for get_member
        member = guild.get_member(user_id)
        role = get(guild.roles, name = DiscordConfig.STUDENT_2020_ROLE)

        print(f'verified account {member.name}')
        await member.add_roles(role, 'verified account')
