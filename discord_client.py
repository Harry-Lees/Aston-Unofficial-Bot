import json
from threading import Thread
from time import sleep
import asyncio

import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingPermissions, BadArgument, MissingRole

from discord.utils import get

import psycopg2 # used over SQLAlchemy for listen/ notify functionality
import psycopg2.extensions
from psycopg2.errors import UniqueViolation

from app.discord_verification.models import User
from app.extensions import database

from config import Config, DiscordConfig

# setup Discord connection
bot = commands.Bot(command_prefix = '!')
channel = bot.get_channel('channel id')

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

:warning: you will not be able to join the server without an aston.ac.uk email address :warning:

You will be allocated a teacher or student role when you join the server.
These will grant you access to all general channels that you are applicable for.
After joining, there are several things you can do:

:book:  **1. Read our info-rules channel**
This channel contains all the rules and regulations for our server.

:teacher:  **2. Join a Subject**
This gives you access to your subject specific channels where you can find people from your course!
To do this, please go into the #roles channel and react to the Subjects message with your subject.

:soccer:  **3. Join Optional Channels**
We have lots of optional channels for things such as Gaming, Music, Tech, and much more!
To do this, please go into the #roles channel and react to the Optional message with your interests.
'''


@bot.event
async def on_ready() -> None:
    '''
    builtin Discord.py function which runs on startup.
    '''

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_member_join(member: object) -> None:
    '''
    builtin Discord.py function called whenever a user joins the
    Discord server.
    '''

    embed = discord.Embed(title = 'Welcome', description = welcome_message.format(member.id), color = 0x7289DA)
    await member.send(embed = embed)


@bot.event
async def on_member_remove(member: object) -> None:
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
        
        
@bot.command(name = 'mass_dm')
@commands.has_role(DiscordConfig.ADMIN_ROLE)
async def mass_dm(ctx, role: str, *message: str):
    '''
    DM's all users with a given role.
    '''
    member = ctx.message.author
    role = get(member.guild.roles, name = role)

    joined_message = ' '.join(message)
    for member in role.members:
        await member.send(joined_message)
        await asyncio.sleep(0.5)

    await ctx.send(f'sending mass DM to users: ' + ', '.join(m.name for m in role.members))


@bot.command(name = 'verify')
@commands.has_role(DiscordConfig.ADMIN_ROLE)
async def verify(ctx, username: str, email: str, role: str):
    '''
    Manually Verify a user. Their email will be added to the database.
    '''
    username = username.strip('@')
    
    author = ctx.message.author # get the object of the author of the message
    member = get(author.guild.members, name = username)
    role = get(author.guild.roles, name = role)

    with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection: # Could convert this to SQLAlchemy
        cursor = connection.cursor()

        arguments = {
            'user_id'   : str(member.id),
            'email'     : email
        }
        
        cursor.execute(f'INSERT INTO {User.__tablename__} VALUES(%(user_id)s, %(email)s, true)', arguments)

    await member.add_roles(role)
    await ctx.send(f'{username} has been manually verified')


@verify.error
async def verify_error(ctx: object, error: Exception) -> None:
    if isinstance(error, BadArgument):
        await ctx.send('Could not verify this memeber, please check spelling and try again')
    elif isinstance(error, MissingRole):
        await ctx.send(f'Sorry {ctx.message.author}, you don\'t have permissions to do that')
    else:
        await ctx.send(f'an unexpected error occurred: {error}')


@bot.command(name = 'ping')
async def ping(ctx: object):
    '''
    Pong. Pings the server to check if it's up.
    '''

    await ctx.send('pong')


@bot.command(name = 'remove_role')
@commands.has_role(DiscordConfig.ADMIN_ROLE)
async def remove_role(ctx: object, role: str) -> None:
    '''
    Removes a given role from *all* users in the server.
    '''

    author = ctx.message.author
    role = get(author.guild.roles, name = role)

    for member in author.guild.members:
        await member.remove_roles(role)
        await asyncio.sleep(0.5)

    await ctx.send(f'removed **{role}** role from {len(author.guild.members)} members in {len(author.guild.members) * 0.5}s')


@remove_role.error
async def remove_role_error(ctx: object, error: Exception) -> None:
    if isinstance(error, BadArgument):
        await ctx.send('Could not unverify this member, please check spelling and try again')
    else:
        await ctx.send(f'An unexpected error occurred: {error}')


@bot.command(name = 'unverify')
@commands.has_role(DiscordConfig.ADMIN_ROLE)
async def unverify(ctx: object, username: str):
    '''
    Unverifies the user, removing their entry in the database. This command does not remove their roles.
    '''

    username = username.strip('@')
    author = ctx.message.author
    member = get(author.guild.members, name = username)
    
    with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection: # will only delete if record exists
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
        connection.commit()

    await ctx.send(f'{username} has had their verification revoked')


@unverify.error
async def unverify_error(ctx: object, error: Exception) -> None:
    if isinstance(error, BadArgument):
        await ctx.send('Could not unverify this member, please check spelling and try again')
    else:
        await ctx.send(f'An unexpected error occurred: {error}')


@bot.command(name = 'verification_prompt')
@commands.has_role(DiscordConfig.ADMIN_ROLE)
async def verification_prompt(ctx: object, role: str):
    '''
    sends a verification prompt to all users with a given role.
    '''

    author = ctx.message.author
    role = get(author.guild.roles, name = role)

    for member in role.members:
        embed = discord.Embed(title = 'Hey!', description = reverify_message.format(member.id), color = 0x7289DA)
        await member.send(embed = embed)


async def give_role(user_id: str, guild: object):
    user_id = int(user_id) # user_id has to be an integer for get_member
    member = guild.get_member(user_id)
    role = get(guild.roles, name = DiscordConfig.STUDENT_2020_ROLE)

    print(f'verified account {member.name}')
    await member.add_roles(role, 'verified account')


def database_notify() -> None: # I think there's a better way of doing this. Please find it :D
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

if __name__ == '__main__':
    thread = Thread(target = database_notify)
    thread.daemon = True
    thread.start()

    bot.run(DiscordConfig.DISCORD_TOKEN)
