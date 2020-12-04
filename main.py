import os
import time
import discord
import asyncio
from dotenv import load_dotenv
from googlesearch import search
import requests
import html5lib
from datetime import date
from bs4 import BeautifulSoup
import json
import csv
from profanityfilter import ProfanityFilter

# loads the env file and assign the var
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ID = os.getenv('DISCORD_ID')
Task_file=os.getenv('TASK_FILE')
Admin_file=os.getenv('ADMINS_LIST')

client = discord.Client()

pf1=ProfanityFilter() #for user defined slangs (just a workaround)
pf2=ProfanityFilter() #for pre defined slangs

Profane_file='./slangs.csv';
slang_list=[]
with open(Profane_file,'r') as pf:
    slangs=csv.reader(pf)
    for slang in slangs:
        slang_list.append(slang[0]) # slang is [word], so slang[0] is word
    print('profane list loaded [OK]')

pf1.set_censor('*')    
pf1.define_words(slang_list)
print("define slangs [OK]")

#getting admins
admin_list=[]
with open(Admin_file,'r') as adms:
    _list=csv.reader(adms)
    for name in _list:
        admin_list.append(name[0])
    print('admin list loaded [OK]')    

@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
@client.event   
async def on_message(message):
    if message.content == "--hello":
        await message.channel.send("👋 Hi! Nice to meet you, I am **Geek Bot**.\n Use __**--help**__ to know more") 

    #bad words remover
    if pf1.is_profane(message.content) or pf2.is_profane(message.content):
            await message.channel.purge(limit=1)
    
    # help tab, lists all the commands
    if message.content == "--help":
        embed = discord.Embed(title="__**Usage Details**__", description="Some user commands",color=0xF8C300)
        embed.add_field(name="--hello", value= "Greets the user")
        embed.add_field(name="--search [topic]", value= "Shows top geeksgforgeeks results")
        embed.add_field(name="--events", value= "Info about live coding contests/hackathons")
        embed.add_field(name="--tasks", value= "Shows ongoing/assigned tasks")
        embed.add_field(name="--[domain]", value= "lists tasks of the specified domain") 
        await message.channel.send(content=None, embed=embed)
        #if user is admin then show admin specific commands
        if str(message.author) in admin_list:
            admin_cmd=discord.Embed(title="__**Admin Specific Commands**__", description="Some user commands",color=0xF8C300)
            admin_cmd.add_field(name="--tasks assign [domain] [task details]", value= "assigns task to a specific domain(only for admins)")
            admin_cmd.add_field(name="--tasks delete [domain] [task number]", value= "deletes mentioned task number from task list") 
            await message.channel.send(content=None, embed=admin_cmd)

    # events scraping 
    # TODO: Needs to be improved
    if message.content == "--events":
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
        embed=discord.Embed(title="__**Events**__ ⏳",description="coding event details", color=0x00C09A)
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
        if(x[0] == "--search"):
            arg = x[1:]
            input_query=''.join(arg)
            count = 1
            modified_query=input_query+" geeks for geeks"
            embed = discord.Embed(title="__**Geek Search**__ 🔍", description=input_query, color=0xFD0061)
            if len(input_query) > 0:
                for j in search(modified_query, tld="co.in", num=7, stop=7, pause=1):
                    embed.add_field(name=str(count)+").", value= j)
                    count+=1
            else:
                embed.add_field(name="⚠️ Invalid usage",value="use __**--help**__ to know usage details")
           
            await message.channel.send(content=None, embed=embed)
    
    # task tracker feature for members:
    # --tasks assign [domain] [tasks...]
    # --tasks delete [domain] [task number]=>do int check for task number
    if message.content:
        processed_msg=message.content.split()
        Task_file
        bot_cmd=["events","tasks","help","hello","search"]
        command=processed_msg[0]
        args=processed_msg[1:] # args=[assign/delete,domain,tasks...]
        if command=="--tasks":
            #fetch tasks from file
            with open(Task_file,'r') as tf:
                task_list=json.load(tf)    
            #if args len = 0 then display existing tasks
            if len(args) == 0:
                if len(task_list)>0:
                    embed=discord.Embed(title="__**Tasks**__ 👩‍💻👨‍💻",description="list of tasks:-",color=0xA652BB)
                    for domain in task_list:
                        count=1
                        if len(task_list[domain])>0:
                            for tasks in task_list[domain]:
                                embed.add_field(name="__Domain__ ",value=domain)
                                embed.add_field(name="__Task "+str(count)+"__", value=tasks+"\n")
                                count+=1
                                embed.add_field(name = chr(173), value = chr(173))
                            await message.channel.send(content=None,embed=embed)
                    if count==1:
                        await message.channel.send("✅ No tasks to complete \n 😎 __***Good Job!***__ 👍")

                else:
                    await message.channel.send("✅ No tasks to complete \n 😎 __***Perfectly done!***__ 👍")

            elif len(args) >= 2:
                if str(message.author) in admin_list:
                    if args[0]=='assign':
                        domain=args[1]
                        new_tasks=' '.join(args[2:])
                        #if tasks is empty/no tasks provided
                        if len(new_tasks) == 0:
                            await message.channel.send("⚠️ no task provided to add to the task list! ⚠️\nuse __--help__ to know about usage")
                            return
                        #if domain does not exists in task list, then make new list
                        if domain not in task_list:
                            task_list[domain]=list()            
                        #assigning
                        task_list[domain].append(new_tasks)
                        #save file
                        with open(Task_file,'w') as tf:
                            json.dump(task_list,tf)
                        embed=discord.Embed(title="__**New Task Added**__ 🥳",description="details", color=0x00C09A)
                        embed.add_field(name="Domain: ",value=domain)
                        embed.add_field(name="Tasks: ",value=new_tasks)
                        await message.channel.send(content=None,embed=embed)

                    # --tasks delete [domain] [task number]
                    elif args[0]=='delete':
                        domain=args[1]
                        if domain not in task_list:
                            await message.channel.send("⚠️ No domain '"+domain+"' exists in tasks list⚠️")
                            return
                        # check if args[2] is a number or not
                        if not args[2].isdigit():
                            await message.channel.send("⚠️ Invalid task number provided! ⚠️")
                            return
                        #if task list in domain is empty
                        if len(task_list[domain]) == 0:
                            task_list.pop(domain)
                            #saving changes to file
                            with open(Task_file,'w') as tf:
                                json.dump(task_list,tf)
                            await message.channel.send("⚠️ No tasks left to delete in tasks list ⚠️\n 🏄 __***you are all done***__ 🏄")
                            return

                        task_num=int(args[2])-1
                        delete_task=task_list[domain][task_num]
                        task_list[domain].remove(delete_task)
                        #response message
                        embed=discord.Embed(title="__**Task Deleted Successfully**__ ✅",description="details", color=0xFD0061)
                        embed.add_field(name="Domain: ",value=domain)
                        embed.add_field(name="Tasks: ",value=delete_task)
                        await message.channel.send(content=None,embed=embed)
                        #saving file
                        with open(Task_file,'w') as tf:
                            json.dump(task_list,tf)
                    else:
                        await message.channel.send("⚠️ Unknown command '"+args[0]+"' ⚠️\n Use __--help__ for usage details")            
                else:
                    await message.channel.send("🚫 Oops! looks like you are not an admin! 🚫") 
            else:
                await message.channel.send("⚠️ Invalid **--tasks** usage ⚠️\n __use --help to know about usage__")
        #if commad of the form --[domain name]
        #avoiding command collision
        if command[:2]=='--' and command[2:] not in bot_cmd:
            #fetch tasks from file
            domain=command[2:]
            with open(Task_file,'r') as tf:
                task_list=json.load(tf)    

            if domain in task_list and len(task_list[domain])>0:
               embed=discord.Embed(title="__**Tasks**__ 👩‍💻👨‍💻",description=domain,color=0x0099E1)
               count=1
               for tasks in task_list[domain]:
                    embed.add_field(name="__SNo__",value=count)
                    embed.add_field(name="__Task__",value=tasks+"\n")
                    count+=1
                    embed.add_field(name = chr(173), value = chr(173))
               await message.channel.send(content=None,embed=embed)
            else:
                await message.channel.send("⚠️ No tasks for '"+domain+"' in tasks list ⚠️\n 🏄 __***you are all done***__ 🏄")

@client.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == "general":
            await channel.send_message(f"""Welcome to the server {member.mention}""") 
        
client.run(TOKEN)
