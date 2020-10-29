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
client = discord.Client()
channel = client.get_channel('channel id')
bot = commands.Bot(command_prefix = '!')


welcome_message = '''
Thanks for joining the **Aston Unofficial Discord Server**

Please verify your email by clicking below:
http://localhost/user/register?user_id={}

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


@client.event
async def on_ready() -> None:
    '''
    builtin Discord.py function which runs on startup.
    '''

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_member_join(member: object) -> None:
    '''
    builtin Discord.py function called whenever a user joins the
    Discord server.
    '''
    await member.send(welcome_message.format(member.id))


@client.event
async def on_member_remove(member: object) -> None:
    '''
    builtin Discord.py function called whenever a user leaves the
    Discord server.
    '''

    with psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI) as connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM {User.__tablename__} WHERE id = %(user_id)s', {'user_id' : str(member.id)})
        connection.commit()

@bot.command(name = 'test', pass_context = True)
async def test(ctx):
    await context.message.channel.send('working!')


@bot.command(name = 'verify', pass_context = True)
async def verify(ctx, user_id: str, email: str):
    await context.message.channel.send(f'{name} has been manually verified')


# @client.event
# async def on_message(message):
#     arguments = str()

#     if message.author == client.user:
#         return
#     else:
#         if message.content.startswith('!test'):
#             await message.channel.send('working!')


async def give_role(user_id, guild):
    member = get(guild.members, name = user_id)
    role = get(guild.roles, name = DiscordConfig.STUDENT_ROLE)

    await member.add_roles(role, 'verified account')


def database_notify():
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

                guild = client.guilds[0] # only works if the bot is connected to a single server, may change later
                asyncio.run(give_role(notify.payload, guild))

            sleep(1)

if __name__ == '__main__':
    thread = Thread(target = database_notify)
    thread.daemon = True
    thread.start()

    client.run(DiscordConfig.DISCORD_TOKEN)