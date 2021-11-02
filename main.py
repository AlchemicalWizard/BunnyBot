import discord
import nest_asyncio

import requests

import time
import urllib.parse

import json

import pickle
import random

import os
from dotenv import load_dotenv

global leaderboard
global timeout_dict


nest_asyncio.apply()
load_dotenv()

token = os.getenv('DISCORD_TOKEN')
prefix = os.getenv('PREFIX')
timeout_period = os.getenv('TIMEOUT_PERIOD')
timeout_warn_period = os.getenv('TIMEOUT_WARN_PERIOD')


is_relaxing = False

client = discord.Client()

@client.event
async def on_ready():
    global leaderboard
    global timeout_dict
    global is_relaxing
    
    
    timeout_dict = {"server_id" : ["timeout_until", "timeout_ignored_until"]}
    leaderboard = load_obj("leaderboard")
    
    log_message('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    try:
        
        if message.author == client.user:
            return
        
        if message.content.startswith(prefix + 'bb') and message.author.id == 177094350201683968: # My special commands :)
            
            log_message("admin commands used")
            
            #Sleep
            if message.content == prefix + 'bbsleep':
                await admin_sleep(message)
                
            #Post message to server
            elif message.content.startswith(prefix + 'bbmsg:'):
                await admin_message(message)
                
            #List servers
            elif message.content == prefix + 'bblistserver':
                await admin_list_server(message)
            
            #List server channels
            elif message.content.startswith(prefix + 'bblistserverchannels:'):
                await admin_list_server_channels(message)
                
            #Leave server
            elif message.content.startswith(prefix + 'bbleave:'):
                await admin_leave(message)
                
            elif message.content.startswith(prefix + 'bbrelax'):
                await admin_relax(message)
            
        else: # Normal user commands
            if message.content == prefix + 'bun': # Send bunny pic
                await normal_send_image(message)
                
            elif message.content == prefix + 'vid': # Send bunny vid
                await normal_send_video(message)
            
            elif message.content == prefix + 'hi':
                await normal_hi(message)
            
            elif message.content == prefix + 'based':
                await normal_based(message)
            
            elif message.content == prefix + 'leaderboard':
                await leaderboard_print_server(message)
                
            elif message.content == prefix + 'me':
                await leaderboard_print_user(message)
            
            elif random.randint(0, 150) == 25: # Randomly send pic 
                log_message("Random triggered by: " + message.author.name)
                await normal_send_image(message)
            
    except Exception as e:
        log_message("something went wrong")
        log_message(e)

##############################################################################
# NORMAL USAGE                                                               #
##############################################################################

async def normal_send_image(message):
    if await timeout_check(message):
        log_message("Bun used by: " + message.author.name)
        img_string = "<IMG SRC=\"http://www.rabbit.org/graphics/fun/netbunnies/"
        page = requests.get('https://rabbit.org/fun/net-bunnies.html')
        page_html = str(page.content)
        img_start = page_html.find(img_string)
        img_end = page_html.find("\">", img_start)
        bunny_url = page_html[img_start + 17:img_end]
        log_message("Sending bun")
        await message.channel.send('https://' + urllib.parse.quote(bunny_url))
        log_message("Bun sent")
        leader_board_update(message)
        
        
async def normal_send_video(message):
    if await timeout_check(message):
        log_message("Vid used by: " + message.author.display_name)
        page = requests.get('https://api.bunnies.io/v2/loop/random/?media=webm,mp4')
        page_json = str(page.content)[2:-1]
        page_json = json.loads(page_json)
        webm_url = page_json['media']['webm']
        log_message("Sending vid")
        await message.channel.send(webm_url)   
        log_message("Vid sent")
        leader_board_update(message)
    
        
async def normal_hi(message):
    if await timeout_check(message):
        log_message("Hi used by: " + message.author.name)
        await message.channel.send("hi <@!"+ str(message.author.id) + "> :rabbit:")
        return       
    
async def normal_based(message):
    if await timeout_check(message):
        log_message("Based used by: " + message.author.name)
        based_url = "https://media.discordapp.net/attachments/892872680901054504/896851648150925352/20211005_115431.png?width=429&height=525"
        await message.channel.send(based_url)
        return
    
##############################################################################
# ADMIN STUFF                                                                #
############################################################################## 

async def admin_list_server(message):
    log_message("bb list used")
    await message.channel.send([str(x.name) + " : " + str(x.id) for x in client.guilds])
    return

async def admin_list_server_channels(message):
    log_message("bb list channel used")
    prefixOffset = len(prefix)
    guildid = message.content[prefixOffset + 20:]
    guilds = client.guilds
    for g in guilds:
        if g.id == int(guildid):
            await message.channel.send([str(x.name) + " : " + str(x.id) for x in g.channels])
    return

async def admin_sleep(message):
    log_message("bb sleep used")
    await message.channel.send("gn <@!"+ str(message.author.id) + "> :rabbit:")
    await message.channel.send("https://tenor.com/view/sleepy-bunny-rabbit-bunny-tired-gif-9909535") 
    await client.close()
    return

async def admin_leave(message):    
    log_message("bb leave used")
    guildid = message.content[9:]
    log_message("id: " + guildid)
    guilds = client.guilds
    for g in guilds:
        if g.id == int(guildid):
            log_message("leaving: ", str(g.id))
            await g.leave()
    return

async def admin_message(message):
    log_message("bb message used")
    prefixOffset = len(prefix)
    guildid = message.content[prefixOffset + 5:prefixOffset + 23]
    channelid = message.content[prefixOffset + 24:prefixOffset + 42]
    msg_content = message.content[prefixOffset + 43:]
    guilds = client.guilds
    for g in guilds:
        if g.id == int(guildid):
            channels = g.channels
            for c in channels:
                if c.id == int(channelid):
                    await c.send(msg_content)
    return

async def admin_relax(message):
    global is_relaxing
    if is_relaxing:
        #Stop relaxing
        log_message("bb relax stopped")
        is_relaxing = False
        await message.channel.send("Ok, Will stop relaxing")
        return
    else:
        #Start relaxing
        log_message("bb relax started")
        is_relaxing = True
        await message.channel.send("Ok, Will relax")
        return
        
    
    
    
##############################################################################
# LEADERBOARD STUFF                                                          #
##############################################################################

def leader_board_update(message):
    global leaderboard
    
    server_id = message.guild.id
    user_id = message.author.id
    
    #Update leaderboard
    if server_id in leaderboard:
        if user_id in leaderboard[server_id]:
            leaderboard[server_id][user_id] = leaderboard[server_id][user_id] + 1
        else:
            leaderboard[server_id][user_id] = 1
    else:
        leaderboard[server_id] = {user_id: 1}
    
    save_obj(leaderboard, "leaderboard")
    return    

async def leaderboard_print_server(message):
    if await timeout_check(message):
        global leaderboard
        
        log_message("leaderboard print server used by: " + message.author.name)

        server_id = message.guild.id
        if server_id in leaderboard:
            server_stats = leaderboard[server_id]
            server_stats_sorted = dict(sorted(server_stats.items(), key=lambda item: item[1], reverse=True))
            string_contruct = "Server bunnybot leaderboard :rabbit: \n\n"
            current = 0
            for user in server_stats_sorted:
                if current == 5:
                    break;  
                user_object = await client.fetch_user(user)
                string_contruct += user_object.name + " : " + str(leaderboard[server_id][user]) + "\n"
                current += 1
                
            await message.channel.send(string_contruct)
        else:
            return
    
async def leaderboard_print_user(message):
    if await timeout_check(message):
        global leaderboard
        
        log_message("leaderboard print user used by: " + message.author.name)
    
        server_id = message.guild.id
        user_id = message.author.id
    
        if server_id in leaderboard:
            if user_id in leaderboard[server_id]:
                post_count = str(leaderboard[server_id][user_id])
                if post_count == "1":
                    end = "1 bunny"
                else:
                    end = str(leaderboard[server_id][user_id]) + " bunnies"
                    
                await message.channel.send("Hi <@!"+ str(message.author.id) + "> You've posted " + end)
            else:
                await message.channel.send("Hi <@!"+ str(message.author.id) + "> You've posted no bunnies :(")
        else:
            return

##############################################################################
# TIMEOUT STUFF                                                              #
##############################################################################

async def timeout_check(message):
    global timeout_dict
    
    if is_relaxing:
        return
    
    server_id = message.guild.id
    if server_id in timeout_dict:
        if timeout_dict[server_id][0] < time.time():
            timeout_dict[server_id] = [time.time() + timeout_period, time.time()]
            return 1
            
        elif timeout_dict[server_id][1] < time.time():
            timeout_dict[server_id] = [time.time() + timeout_period, time.time() + timeout_warn_period]
            await message.channel.send("Bunny bot is busy, try again soon :rabbit:")
        return False
    else:
        timeout_dict[server_id] = [time.time() + timeout_period, time.time()]
        return True

##############################################################################
# UTILITY FUNCTIONS                                                          #
##############################################################################

def log_message(message):
    timeNow = time.strftime("%d/%m/%Y, %H:%M:%S", time.localtime())
    print(timeNow + ": " + message)
        
def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


##############################################################################
# RUN BUNNY BOT                                                              #
##############################################################################
try:
    client.run(token)
except RuntimeError as e:
    if e.code == "Cannot close a running event loop":
        print("bb sleeping")
    else:
        print(e)
        