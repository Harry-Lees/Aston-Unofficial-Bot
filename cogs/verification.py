from threading import Thread
from typing import Union
from time import sleep

import discord
import psycopg2
import psycopg2.extensions
from config import Config, DiscordConfig
from discord.ext import commands
from discord.utils import get
from psycopg2.errors import UniqueViolation

from app.user.models import User

def setup(bot: object) -> None:
    bot.add_cog(Verification(bot))


class Verification(commands.Cog):
    reverify_message = '''
    We've just introduced a new verification bot to ensure that all users are members of Aston University. In order to do so, we have removed everyone's member & subject role. You will have to reselect your subject role after verifying.

    - If you're currently a 2nd-year student or have had a foundation year, please contact a Moderator. You will be allowed in the Server, but
    we have to verify you manually!

    - If you are a *lecturer* or someone from another year group, please contact a Moderator to get manually verified.

    - You will be asked to provide your "aston.ac.uk" email address so we can properly verify that you go to Aston University.

    **To re-verify, please click on the link below:**
    https://aston-unofficial.herokuapp.com/discord/register?user_id={}


    If you have any questions, please feel free to contact a Moderator by opening a ticket.
    '''


    welcome_message = '''
    Thanks for joining the **Aston Unofficial Discord Server**

    Please verify your email by clicking below:
    https://aston-unofficial.herokuapp.com/discord/register?user_id={}

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


    async def _error(self, ctx, error: Exception):
        embed = discord.Embed(title = 'Error', description = str(error), colour = discord.Colour.red())
        await ctx.send(embed = embed)


    async def on_member_join(self, member: object) -> None:
        '''
        builtin Discord.py function called whenever a user joins the
        Discord server.
        '''

        embed = discord.Embed(title = 'Welcome', description = welcome_message.format(member.id), color = 0x7289DA)
        await member.send(embed = embed)


    async def on_member_remove(self, member: object) -> None:
        '''
        builtin Discord.py function called whenever a user leaves the
        Discord server.
        '''

        async for message in bot.get_user(member.id).history(limit = 100):
            if message.author.id == bot.user.id:
                await message.delete()
                await asyncio.sleep(0.5)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
            connection.commit()


    @commands.command(name = 'verify')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def verify(self, ctx: object, username: Union[discord.Member, str], email: str, role: Union[discord.Role, str]) -> None:
        '''
        Manually Verify a user. Their email will be added to the database.
        '''
        author = ctx.message.author # get the object of the author of the message
        
        if isinstance(username, discord.Member):
            member = username
        else:
            member = get(author.guild.members, name = username)
        
        if not isinstance(role, discord.Role):
            role = get(author.guild.roles, name = role)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection: # Could convert this to SQLAlchemy
            cursor = connection.cursor()

            arguments = {
                'user_id'   : str(member.id),
                'email'     : email
            }
            
            cursor.execute(f'INSERT INTO {User.__tablename__} VALUES(%(user_id)s, %(email)s, true)', **arguments)

        await member.add_roles(role)
        await ctx.send(f'{username} has been manually verified')


    @verify.error
    async def verify_error(self, ctx: object, error: Exception) -> None:
        await self._error(ctx, error)


    @commands.command(name = 'get_link')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def get_link(self, ctx: object, member: Union[discord.Member, str]) -> None:
        '''
        gets a verification link for a member.
        '''

        author = ctx.message.author

        if not isinstance(member, discord.Member):
            member = get(author.guild.roles, name = member)

        description = f'Please [click here](https://aston-unofficial.herokuapp.com/discord/register?user_id={member.id}) to verify your account.'

        embed = discord.Embed(title = 'Verification Link', description = description, color = discord.Colour.green())
        embed.add_field(name = 'Next Steps', value = 'After you have completed the verification process please remember to select your subject and interests in the <#756115420175532133> channel!')

        await ctx.send(embed = embed)


    @get_link.error
    async def get_link_error(ctx, error: Exception):
        await self._error(ctx, error)

    @commands.command(name = 'self_link')
    async def self_link(self, ctx: object) -> None:
        '''
        gets a verification link for a member
        '''

        author = ctx.message.author
        await ctx.send(f'https://aston-unofficial.herokuapp.com/discord/register?user_id={author.id}')


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


    @remove_role.error
    async def remove_role_error(self, ctx: object, error: Exception) -> None:
        await self._error(ctx, error)


    @commands.command(name = 'unverify')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def unverify(self, ctx: object, member: Union[discord.Member, str]):
        '''
        Unverifies the user, removing their entry in the database. This command does not remove their roles.
        '''

        author = ctx.message.author
        member = get(author.guild.members, name = username)
        
        if not isinstance(member, discord.Member):
            member = get(author.guild.roles, name = member)

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection: # will only delete if record exists
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
            connection.commit()

        await ctx.send(f'{username} has had their verification revoked')


    @unverify.error
    async def unverify_error(self, ctx: object, error: Exception) -> None:
        await self._error(ctx, error)


    @commands.command(name = 'verification_prompt')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def verification_prompt(self, ctx: object, role: str):
        '''
        sends a verification prompt to all users with a given role.
        '''
        print('started verification')

        author = ctx.message.author
        role = get(author.guild.roles, name = role)

        for member in role.members:
            embed = discord.Embed(title = 'Hey!', description = reverify_message.format(member.id), color = 0x7289DA)
            try:
                await member.send(embed = embed)
                print(f'sent message to {member}')
                await asyncio.sleep(30)
            except discord.errors.HTTPException as error:
                print(f'RATE LIMIT: failed to send message to {member}: {error}')
                await asyncio.sleep(120)
            except Exception as error:
                print(f'failed to send message to {member}: {error}')
                await asyncio.sleep(120)

        await ctx.send('verification prompt finished!')


    @commands.command('profile')
    @commands.has_role(DiscordConfig.ADMIN_ROLE)
    async def profile(self, ctx: object, member: Union[discord.Member, str]):
        author = ctx.message.author

        if not isinstance(member, discord.Member):
            member = get(author.guild.members, name = member)    

        with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM discord_user_tab WHERE id = %(member_id)s', {'member_id' : str(member.id)})
            user = cursor.fetchone()

        if user:
            user_profile = f'''
            User ID: {member.id}
            Verified: {user[2]}
            Email: {user[1]}
            '''

            colour = discord.Colour.green()
        else:
            user_profile = f'''
            User ID: {member.id}
            Verified: False
            '''

            colour = discord.Colour.red()

        if member.name[-1] == 's':
            title = f'{member.name}\' Profile'
        else:
            title = f'{member.name}\'s Profile'

        embed = discord.Embed(title = title, description = user_profile, colour = colour)
        embed.set_thumbnail(url = member.avatar_url)

        await ctx.send(embed = embed)


    @profile.error
    async def profile_error(self, ctx: object, error: Exception):
        await self._error(ctx, error)


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

                            guild = bot.guilds[0] # only works if the bot is connected to a single server, may change later
                            asyncio.run_coroutine_threadsafe(give_role(user_id, guild), bot.loop)

                        sleep(1)
            except psycopg2.OperationalError:
                print('error connecting to database')


    async def give_role(self, user_id: str, guild: object) -> None:
        user_id = int(user_id) # user_id has to be an integer for get_member
        member = guild.get_member(user_id)
        role = get(guild.roles, name = DiscordConfig.STUDENT_2020_ROLE)

        print(f'verified account {member.name}')
        await member.add_roles(role, 'verified account')
