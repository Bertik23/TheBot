import asyncio
from asyncio.tasks import wait
import datetime
import math
import os
import pickle
import random
import re
import time
from random import choice, randint

import bdbf
import discord
import ksoftapi
import numpy as np
import pkg_resources
import praw
import prawcore
import requests
import stopit
from bdbf import embed, hasLink  # , spamProtection
from bs4 import BeautifulSoup
from prettytable import PrettyTable

import botFunctions
import botGames
#import chatbot
import commands
import database
from botFunctions import (adventniKalendar, checkMZCR, getFact, getJokeTxt, getLastInstaPost,
                          getZmena, gymso, makeSuggestion, newOnGymso,
                          spamProtection, wolframQuery, nextHoursAreAndStartsIn)
from variables import *

@client.logMessage
def log(message):
    if "guild" in dir(message.channel):
        msgLog = [datetime.datetime.utcnow().isoformat(), str(message.id), message.content, str(message.author.id), message.author.name, str(message.channel.id), str(message.channel), str(message.channel.guild.id), message.channel.guild.name]
    else:
        msgLog = [datetime.datetime.utcnow().isoformat(), str(message.id), message.content, str(message.author.id), message.author.name, str(message.channel.id), str(message.channel)]
    database.messageLog.append_row(msgLog)


klubik, obecne, choco_afroAnouncements, korona_info = None,None, None, None

@client.event # event decorator/wrapper
async def on_ready():
    global klubik, obecne, choco_afroAnouncements, korona_info
    print(f"We have logged in as {client.user}")
    klubik = await client.fetch_guild(697015129199607839)
    obecne = await client.fetch_channel(697015129199607843)
    choco_afroAnouncements = await client.fetch_channel(756497789424369737)
    korona_info = await client.fetch_channel(758381540534255626)
    print(klubik, obecne, choco_afroAnouncements, korona_info)

    await obecne.send("Jsem online!")

    if heroku:
        client.loop.create_task(checkWebsites())
        client.loop.create_task(classLoop())
    #client.loop.create_task(kalendarLoop())
    
    #newRolePerms = discord.Permissions(administrator=True)
    #newRole = await klubik.create_role(permissions=newRolePerms,color=discord.Color.from_rgb(0,255,0),name="Bůh 2.0")
    #bertiksMessage = await obecne.fetch_message(746658597655805954)
    #bertik = bertiksMessage.author
    #await bertik.add_roles(discord.Object(newRole.id))

@client.event
async def on_message(message):
    global klubik, obecne
    print(f"{message.channel} ({message.channel.id}): {message.author}: {message.author.name}: {message.content}")
        #print("on_msg", obecne, klubik)
    #await spamProtection(message, 5, f"{message.author.mention} nespamuj tady!", spamDelValue = 10)#, spamDelWarnMsg = f"{message.author.mention} další zprávy už ti smažu!")
    """if not message.author.bot:
        await spamProtection(message, 3)"""

    # if message.channel.id == 766655158473850890:
    # 	chatbot.talk_to_bot(message.content)
    # 	return

    if message.author.bot and message.author.id != 788873442664906752 and message.channel.id in (790630915448504390, 790630932292829214):
        await message.delete()

    if message.channel.id not in (790630915448504390, 790630932292829214):
        for i in ["hi","dobrý den","brý den","čau","ahoj", "zdravíčko", "tě péro", "těpéro", "zdárek párek","tě guli", "čus", "olá", "ola", "guten tag"]:
            if re.search(f"(\W|^){i}(\W|$)", message.content, re.I) and not message.author.bot:
                await message.channel.send(f"Hello {message.author.mention}")
                break

        if "kdy" in message.content.lower() and "aktualizace" in message.content.lower():
            await message.channel.send("Kdo ví")

        if (re.search("(\W|^)a+da+m(\W|$)", message.content, re.I)) and not message.author.bot:
            await message.channel.send(f"A{randint(0,20)*'a'}d{randint(1,20)*'a'}m {choice(['je gay','neumí olí','už nevytírá anály','is trajin to solf da rubix kjub','was trajin to olín',''])}")

        if (re.search("(\W|^)ji+ří+(\W|$)", message.content, re.I)) and not message.author.bot:
            await message.channel.send(f"Jiří {choice([' je buzík',' nic neumí','is FUCKING NORMIEEE REEEEEEEEEEEEEEEEEEEEEE'])}")

        if "fortnite" in message.content.lower():
            await message.delete()

        if (re.search("thebot", message.content, re.I) or client.user.mentioned_in(message)) and not message.author.bot:
            await message.channel.send(choice(["Slyšel jsem snad moje jméno?",f"{message.author.mention} ty ses opovážil vyslovit moje jméno?","Ještě jednou tu zazní moje jméno a uvidíte.",f"Chceš do držky {message.author.mention}?",f"Tak to je naposledy co jste {message.author.mention} viděli.", f"Naklepu ti řízek ty pomeranči {message.author.mention}", f"{message.author.mention} zmaluju ti ksicht tak, že tě ani Adam nepozná", f"Urazim ti tvé intimní partie, btw Bohouš smrdí", f"Jestli nepřestaneš psát moje jméno, tak ti pošlu fotku Vladanovo PP"]))

        if message.tts and not message.author.bot:
            await message.channel.send(f"Hej ty {message.author.mention}, žádný ttska tady.", tts = True)

        if message.channel.id == 715621624950292593:
            if not hasLink(message.content):
                await message.delete()

        if "No lyrics found for `" in message.content:
            try:
                results = await commands.kclient.music.lyrics(message.content.split("`")[1])
            except ksoftapi.NoResults:
                await message.channel.send(f"No lyrics found for `{message.content.split('`')[1]}`.")
            else:
                lyrics = results[0]
                for i in range(math.ceil(len(lyrics.lyrics)/2048)):
                    e = embed(f"Lyrics for {lyrics.artist} - {lyrics.name}", description=lyrics.lyrics[(i*2048):((i+1)*2048)], thumbnail={"url": lyrics.album_art})
                    await message.channel.send(embed=e)
            await message.delete()		

    if type(message.channel) == discord.DMChannel:
        if message.author.id == 452478521755828224:
            try:
                msgTextSplit = message.content.split(" ",1)
                channel = await client.fetch_channel(int(msgTextSplit[0]))
                await channel.send(msgTextSplit[1])
            except Exception as e:
                await message.channel.send(e)
                raise e

@client.event
async def on_raw_reaction_add(payload):
    guild = await client.fetch_guild(payload.guild_id)
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    emoji = payload.emoji
    member = payload.member

    #print(emoji)
    
    if message.id == 746719599982280754:
        #1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣
        if emoji.name == "1️⃣":
            await member.add_roles(discord.Object(746396397280034946)) #Minecraft
            print(f"{member.name} in {guild} got role Minecraft for pressing {emoji}")
        if emoji.name == "2️⃣":
            await member.add_roles(discord.Object(746396668198649856)) #CS:GO
            print(f"{member.name} in {guild} got role CS:GO for pressing {emoji}")
        if emoji.name == "3️⃣":
            await member.add_roles(discord.Object(746712499705086013)) #Rocket League
            print(f"{member.name} in {guild} got role Rocket League for pressing {emoji}")
        if emoji.name == "4️⃣":
            await member.add_roles(discord.Object(746396772179378197)) #Fortnite
            print(f"{member.name} in {guild} got role Fortnite for pressing {emoji}")
        if emoji.name == "5️⃣":
            await member.add_roles(discord.Object(746704088070357012)) #Mobile Gaming
            print(f"{member.name} in {guild} got role Mobile Gaming for pressing {emoji}")
        if emoji.name == "6️⃣":
            await member.add_roles(discord.Object(746709189040275456)) #PS4 Gamers
            print(f"{member.name} in {guild} got role PS4 Gamers for pressing {emoji}")


# @client.event
# async def on_raw_reaction_remove(payload):
# 	guild = await client.fetch_guild(payload.guild_id)
# 	channel = await client.fetch_channel(payload.channel_id)
# 	message = await channel.fetch_message(payload.message_id)
# 	emoji = payload.emoji
# 	for m in guild.members:
# 		if m.id == payload.user_id:
# 			member = m

# 	if message.id == 746674728076312627:
        
# 		if emoji.name == "👶":
# 			await member.remove_roles(discord.Object(513730880464748557))
# 			print(guild, channel, message, member, emoji)
# 		if emoji.name == "🧒":
# 			await member.remove_roles(discord.Object(513730883824386049))
# 			print(guild, channel, message, member, emoji)
# 		if emoji.name == "👦":
# 			await member.remove_roles(discord.Object(513730888069152788))
# 			print(guild, channel, message, member, emoji)
# 		if emoji.name == "👶":
# 			await member.remove_roles(discord.Object(513730889222455309))
# 			print(guild, channel, message, member, emoji)
    

async def checkWebsites():
    while True:
        #Gymso
        try:
            print("Checking for new posts on Gymso")
            with stopit.ThreadingTimeout(10) as to_ctx_mgr:
                assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING

                clanky = newOnGymso()
                if clanky:
                    for clanek in clanky:
                        for i in range(math.ceil(len(clanek["text"])/2048)):
                            e = embed(clanek["title"], url = clanek["url"], description=clanek["text"][(i*2048):((i+1)*2048)])
                            await obecne.send(f"{klubik.default_role} nový příspěvek na Gymso", embed=e)
        except Exception as e:
            print(e)

        #choco_afro
        # try:
        # 	with stopit.ThreadingTimeout(10) as to_ctx_mgr:
        # 		assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING

        # 		print("Checking for new post on choco_afro")
        # 		lastChocoPost = getLastInstaPost("choco_afro")
        # 		if time.time() - lastChocoPost["taken_at_timestamp"] <= 7000:
        # 			await choco_afroAnouncements.send(lastChocoPost["display_url"])
        # except Exception as e:
        # 	print(e)

        #MZCR TS
        try:
            tss = checkMZCR("https://koronavirus.mzcr.cz/category/tiskove-zpravy/")
            for ts in tss:
                if ts[0] != database.dataLog.cell(2,1).value:
                    await korona_info.send(embed=embed(ts[2], url=ts[1], description=ts[3]))
                else:
                    break
            database.dataLog.update_cell(2,1, tss[0][0])

        except Exception as e:
            print(e)

        #MZCR MO
        try:
            tss = checkMZCR("https://koronavirus.mzcr.cz/category/mimoradna-opatreni/")
            for ts in tss:
                if ts[0] != database.dataLog.cell(2,2).value:
                    await korona_info.send(embed=embed(ts[2], url=ts[1], description=ts[3]))
                else:
                    break
            database.dataLog.update_cell(2,2, tss[0][0])
        except Exception as e:
            print(e)

        await asyncio.sleep(600)

async def classLoop():
    sleeping = 10
    while True:
        try:
            waitTime = 0
            print("Checking for hours.")               
            for hour in nextHoursAreAndStartsIn():
                #print(f"We are in {hour}")
                waitTime = hour[0].total_seconds()
                try:
                    if hour[2] == None:
                        role = [r for r in klubik.roles if r.name == hour[1]]
                        message = f"Za {str(hour[0])[:-3]} začíná {role[0].mention}"
                    else:
                        role = [r for r in klubik.roles if r.name == hour[2]]
                        message = f"Za {str(hour[0])[:-3]} začíná `{hour[1]}` pro {role[0].mention}"
                except:
                    message = ""
                if message != "":
                    await obecne.send(message)
            #print(waitTime)
            sleeping = 10
            await asyncio.sleep(max(waitTime-300,240))
        except Exception as e:
            sleeping = min(sleeping+30, 6000)
            await asyncio.sleep(sleeping)
            print(f"Encountered an error while checking for hours: {e}")

async def kalendarLoop():
    while True:
        try:
            now = datetime.datetime.utcnow()
            lastMessage = int(database.advantniKalendar.cell(2,11).value)
            if lastMessage < now.day:
                noon = now.replace(hour = 11, minute = 0, second = 0)
                print(f"Waiting for {max((noon-now).total_seconds(), 0)} until noon.")
                await asyncio.sleep(max((noon-now).total_seconds(), 0))
                out = adventniKalendar(now.day-1)
                channel = client.get_guild(621413546177069081).get_channel(777201859466231808)
                await channel.send(f"{out[0].mention} Gratulace vyhráváš odměnu z adventního kalendáře pro potvrzení že chceš odměnu převzít reaguj :white_check_mark:  na tuto zprávu.", file=discord.File(out[1], filename=f"adventniKalendarDay{now.day}.png"))
                database.advantniKalendar.update_cell(2,11, now.day)
            else:
                noon = now.replace(day=now.day+1, hour = 11, minute = 0, second = 0)
                print(f"Waiting for {max((noon-now).total_seconds(), 0)} until noon.")
                await asyncio.sleep(max((noon-now).total_seconds(), 0))
        except Exception as e:
            print(e)
            await asyncio.sleep(60)





client.run(token)
