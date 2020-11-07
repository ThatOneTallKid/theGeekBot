import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ID = os.getenv('DISCORD_ID')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
@client.event
async def on_message(message):
    id = client.get_guild(ID)
    if message.content.find("!hello") != -1:
        await message.channel.send("Hi") # If the user says !hello we will send back hi 
    

        
client.run(TOKEN)