import os
import time
import discord
import asyncio
from dotenv import load_dotenv
from googlesearch import search
import requests
import html5lib
from bs4 import BeautifulSoup

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
    bad_words  = [ "fuck" , "motherfucker"]
    if message.content == "!hello":
        await message.channel.send("Hi") # If the user says !hello we will send back hi 
    
    for word in bad_words:
        if message.content.count(word) > 0:
            print("A bad word was said")
            await message.channel.purge(limit=1)

    if message.content == "!help":
        embed = discord.Embed(title="Help on BOT", description="Some user commands")
        embed.add_field(name="!hello", value= "Greets the user")
        embed.add_field(name="*search <topic>", value= "Shows top geeksgforgeeks results")
        await message.channel.send(content=None, embed=embed)  

    # events scraping
    if message.content == "!events":
        URL = "https://www.stopstalk.com/contests"

        r = requests.get(URL)

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, "html5lib")

        table = soup.findAll('table',{"class":"centered bordered"})[0]
        tr = table.findAll(['tr'])[1:]
        info = []

        for row in tr:
            td = row.findAll('td')
            row_info = {}
            row_info['name'] = td[0].text
            if bool(td[0].findAll('span')) == True:
                row_info['status'] = 'live'
            else:
                row_info['status'] = 'upcom'
            row_info['end-date'] = td[3].text
    
            link = td[4].find('a')
            row_info['link'] = link.get('href')
            info.append(row_info)

        count=1
        embed=discord.Embed(title="Events", discription="events details")
        for i in info:
            if count > 9:
                break
            details="status: "+i['status']+"\nend date: "+i['end-date']+"\nlink: "+i['link']
            embed.add_field(name=i['name'],value=details)
            count+=1
        await message.channel.send(content=None, embed=embed)

    # search logic
    if message.content:
        x = message.content.split()
        arg = ""
        if(x[0] == "*search"):
            arg = x[1:]
            input_query=''.join(arg)
            count = 1
            modified_query=input_query+" geeks for geeks"
            embed = discord.Embed(title="Geek Search", description=input_query)
            if len(input_query) > 0:
                for j in search(modified_query, tld="co.in", num=7, stop=7, pause=1):
                    embed.add_field(name=str(count)+").", value= j)
                    count+=1
                await message.channel.send(content=None, embed=embed) 



@client.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send_message(f"""Welcome to the server {member.mention}""") 
        
client.run(TOKEN)
