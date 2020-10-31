import json
from threading import Thread
from time import sleep
import asyncio

import discord
from discord.ext import commands
from discord.utils import get

import psycopg2 # used over SQLAlchemy for listen/ notify functionality
import psycopg2.extensions

from app.user.models import User
from config import Config, DiscordConfig

# setup Discord connection
bot = commands.Bot(command_prefix = '!')
channel = bot.get_channel('channel id')


welcome_message = '''
Thanks for joining the **Aston Unofficial Discord Server**

Please verify your email by clicking below:
http://harryl.co.uk/user/register?user_id={}

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
    await member.send(welcome_message.format(member.id))


@bot.event
async def on_member_remove(member: object) -> None:
    '''
    builtin Discord.py function called whenever a user leaves the
    Discord server.
    '''

    with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
        connection.commit()


@bot.command(name = 'commands')
async def commands(ctx):
    commands = '''
    ```
    !mass_dm <role> <message>
    
        - Send a DM to every member with a given role.
    
    !verify <username> <email>
    
        - Manually verify a user.
    
    !unverify <username> <email>
    
        - Manually unverify a user, this will remove their role and remove their entry in the database.
    
    !ping
    
        - Pong. Test if the server is up.
    ```
    '''
    
    await ctx.send(
        
        
@bot.command(name = 'mass_dm')
async def mass_dm(ctx, role: str, message: str):
    member = ctx.message.author
    role = get(member.guild.roles, name = role)

    for member in role.members:
        await member.send(message)

    await ctx.send(f'sending mass DM to users: ' + ', '.join(m.name for m in role.members))


@bot.command(name = 'verify')
async def verify(ctx, username: str, email: str):
    author = ctx.message.author # get the object of the author of the message
    member = get(author.guild.members, name = username)
    role = get(member.guild.roles, name = DiscordConfig.STUDENT_ROLE)

    await member.add_roles(role)
    await ctx.send(f'{username} has been manually verified')


@bot.command(name = 'ping')
async def ping(ctx):
    await ctx.send('pong')

    
@bot.command(name = 'unverify')
async def unverify(ctx, username: str, email: str):
    author = ctx.message.author
    member = get(author.guild.members, name = username)
    role = get(author.guild.roles, name = DiscordConfig.STUDENT_ROLE)
    
    await member.remove_role(role)
    await ctx.send(f'{username} has had their verification revoked')


async def give_role(user_id: str, guild: object):
    user_id = int(user_id) # user_id has to be an integer for get_member
    member = guild.get_member(user_id)
    role = get(guild.roles, name = DiscordConfig.STUDENT_ROLE)


    await member.add_roles(role, 'verified account')


def database_notify() -> None: # I think there's a better way of doing this. Please find it :D
    '''
    function to wait for NOTIFY commands sent to the database.
    Once an update has occurred, check if the user has been verified. 
    If they are verified, give them a suitable role.
    '''

    with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
        cursor = connection.cursor()

        cursor.execute(f'LISTEN {User.__tablename__}')
        connection.commit()

        print(f'LISTENING TO {User.__tablename__}')
  
        while True:
            connection.poll()
            while connection.notifies:
                notify = connection.notifies.pop(0)
                cursor.execute(f'SELECT id FROM {User.__tablename__} WHERE email = %(email)s', {'email' : notify.payload})
                user_id = cursor.fetchone()[0]

                guild = bot.guilds[0] # only works if the bot is connected to a single server, may change later
                asyncio.run_coroutine_threadsafe(give_role(user_id, guild), bot.loop)

            sleep(1)

if __name__ == '__main__':
    thread = Thread(target = database_notify)
    thread.daemon = True
    thread.start()

    bot.run(DiscordConfig.DISCORD_TOKEN)
