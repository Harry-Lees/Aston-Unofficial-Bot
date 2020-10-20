import discord
import asyncio
from threading import Thread
from bot.email.send_email import send_email

TOKEN = input('please enter token: ')
client = discord.Client()
channel = client.get_channel('channel id')

welcome_message = '''
Thanks for joining the **Aston Unofficial Discord Server**

Please verify your email by responding to this message with your email address.
You should receive an email in your inbox to verify your address.

Once you're all set up, here's what you can do:

**1. Read our info-rules channel**
This channel contains all the rules and regulations for our server.

**2. Join a Subject**
This gives you access to your subject specific channels where you can find people from your course!
To do this, please go into the #roles channel and react to the Subjects message with your subject.

**3. Join Optional Channels**
We have lots of optional channels for things such as Gaming, Music, Tech, and much more!
To do this, please go into the #roles channel and react to the Optional message with your interests.
'''

verification_message = '''
A verification link has been sent to your email! If you did not receive an email,
please send another message containing your email address.
'''

verified_ids = []

@client.event
async def on_member_join(member):
    await member.send(welcome_message)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.guild:
        if verified(message.author.id):
            await message.channel.send('You have already been verified on this server.')
        elif check_regex(message):
            send_email('10')
            await message.channel.send(verification_message)
        else:
            await message.channel.send('This is not a valid Email address. Please use a valid aston.ac.uk email address.')
    else:
        print('not working')

@client.event
async def on_ready():
    print('Logged in as:')
    print(client.user.name)
    print(client.user.id)

def verified(author_id):
    if author_id in verified_ids:
        return True
    else:
        verified_ids.append(author_id)
        return False

def check_regex(message):
    return True

def run_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(TOKEN))
    
    thread = Thread(target=loop.run_forever)
    thread.start()