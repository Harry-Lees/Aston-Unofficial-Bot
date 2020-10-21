import asyncio
import sqlite3
from random import randint
from threading import Thread

import discord

TOKEN = input('please input discord token: ')
client = discord.Client()
channel = client.get_channel('channel id')

welcome_message = '''
Thanks for joining the **Aston Unofficial Discord Server**

Please verify your email by clicking below:
http://localhost:5000/verify_user?user_id={}

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
async def on_member_join(member):
    add_pending_user(member)
    await member.send(welcome_message.format(member.id))

@client.event
async def on_member_remove(member):
    remove_user(member)

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)

async def add_role(user_id: str, role: str):
    roles = {
        'staff' : '761523175170244608',
        'student' : '756099685558779953',
    }

    await client.add_roles(user_id, role)

def run_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(TOKEN))
    
    thread = Thread(target=loop.run_forever)
    thread.start()

def add_pending_user(user) -> None:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    uuid = ''.join(str(randint(0, 9)) for i in range(5))
    cursor.execute('INSERT INTO pending_users VALUES(?, ?)', [user.id, uuid])
    connection.commit()

def remove_user(user) -> None:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM pending_users WHERE id = ?', [user.id])
    cursor.execute('DELETE FROM user WHERE id = ?', [user.id])

    connection.commit()
