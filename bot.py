import random
import numpy as np
from random import choice, randint
import os
import math
import requests
from bs4 import BeautifulSoup
import botFunctions
from botFunctions import getZmena, gymso, newOnGymso, getJokeTxt, getFact, wolframQuery
import praw
import prawcore
import ksoftapi
import re
import bdbf
from bdbf import spamProtection, command, embed, hasLink
import asyncio
import discord
import pickle

kclient = ksoftapi.Client(os.environ.get("ksoft_token", None))

reddit = praw.Reddit(client_id = os.environ.get("reddit_client_id", None),
                     client_secret = os.environ.get("reddit_client_secret", None),
                     user_agent = os.environ.get("reddit_user_agent", None))

botId = 540563812890443794
#84032 permissions int
#https://discordapp.com/oauth2/authorize?client_id=540563812890443794&scope=bot&permissions=84032

token = os.environ.get('TOKEN', None)




client = discord.Client()
klubik = None #client.get_guild(697015129199607839)
obecne = None #klubik.get_channel(697015129199607843)

bdbf.commandPrefix = "~"
bdbf.embedFooter= {
                "text": "Powered by Bertik23",
                "icon_url": "https://cdn.discordapp.com/avatars/452478521755828224/4cfdbde44582fe6ad05383171ac1b051.png"
                }
bdbf.embedColor = (37, 217, 55)

bdbf.commands.cmds[697015129199607839] = []

##COMMANDS

class zmena(bdbf.commands.Command):
	def command(self,args):
		return f"Změny rozvrhu pro {args}:\n{getZmena(args)}",None

bdbf.commands.cmds[697015129199607839].append(zmena("Returns schedule changes for the give teacher/class today","`~zmena <teacher/class>` eg. `~zmena Lukešová Danuše` or `~zmena 6.A`"))

@client.event # event decorator/wrapper
async def on_ready():
	print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
	global klubik, obecne
	print(f"{message.channel} ({message.channel.id}): {message.author}: {message.author.name}: {message.content}")
	if message.channel.guild.id == 697015129199607839:
		klubik = message.channel.guild
	if message.channel.id == 697015129199607843:
		obecne = message.channel
		#print("on_msg", obecne, klubik)
	#await spamProtection(message, 5, f"{message.author.mention} nespamuj tady!", spamDelValue = 10)#, spamDelWarnMsg = f"{message.author.mention} další zprávy už ti smažu!")

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
		await message.channel.send(choice(["Slyšel jsem snad moje jméno?",f"{message.author.mention} ty ses opovážil vyslovit moje jméno?","Ještě jednou tu zazní moje jméno a uvidíte.",f"Chceš do držky {message.author.mention}?",f"Tak to je naposledy co jste {message.author.mention} viděli."]))

	if message.tts and not message.author.bot:
		await message.channel.send(f"Hej ty {message.author.mention}, žádný ttska tady.", tts = True)

	if message.channel.id == 715621624950292593:
		if not hasLink(message.content):
			await message.delete()

	if "No lyrics found for `" in message.content:
		try:
			results = await kclient.music.lyrics(message.content.split("`")[1])
		except ksoftapi.NoResults:
			await message.channel.send(f"No lyrics found for `{message.content.split('`')[1]}`.")
		else:
			lyrics = results[0]
			for i in range(math.ceil(len(lyrics.lyrics)/2048)):
				e = embed(f"Lyrics for {lyrics.artist} - {lyrics.name}", description=lyrics.lyrics[(i*2048):((i+1)*2048)], thumbnail={"url": lyrics.album_art})
				await message.channel.send(embed=e)
		await message.delete()		
	
	commandos, attributes = command(message.content)

	if "help" == commandos:
		e = embed("Help for TheBot", fields=[
				{
					"name": "`~help`",
					"value": "returns this",
					"inline": True
				},
				{
					"name": "`~randomCSM`",
					"value": "returns a random team from [CSM](https://www.csmweb.net/)",
					"inline": True
				},
				{
					"name": "`~lyrics`",
					"value": "**Usage:** `~lyrics <song>`\nReturns lyrics to given song",
					"inline": True
				},
				{
					"name": "`~suggest`",
					"value": "**Usage:** `~suggest <text>`\nsuggest a command to the creator of the bot",
					"inline": True
				},
				{
					"name": "`~zmena`",
					"value": "**Usage:** `~zmena <teacher/class>` eg. `~zmena Lukešová Danuše` or `~zmena 6.A`\nReturns schedule changes for the give teacher/class today",
					"inline": True
				},
				{
					"name": "`~r/`",
					"value": "**Usage:** `~r/ <subreddit>` eg. `~r/ kofola`\nReturns a subreddit",
					"inline": True
				},
				{
					"name": "`~gymso`",
					"value": "Returns last post on [gymso.cz](https://gymso.cz)",
					"inline": True
				},
				{
					"name": "`~meme`",
					"value": "Returns random meme from [Reddit](https://reddit.com)",
					"inline": True
				},
				{
					"name": "`~eval`",
					"value":"**Usage:** `~eval <python expresion>` eg. `~eval math.cos(math.pi)`\nReturns python expresion outcome.",
					"inline": True
				},
				{
					"name": "`~aww`",
					"value": "Returns random aww image from [Reddit](https://reddit.com)",
					"inline": True
				},
				{
					"name": "`~subreddit`",
					"value": "**Usage:** `~subreddit <subreddit> <span>` eg. `~subreddit kofola month`\nReturns random image from given subreddit and givel span.\n Spans: `hour`,`day`,`week`,`month`,`year`,`all`",
					"inline": True
				},
				{
					"name": "`~mapa`",
					"value": "**Usage:** `~mapa <place> <zoom=12>` eg. `~mapa Gymso 16`\nReturns map of given place with given zoom (default 12).",
					"inline": True
				},
				{
					"name": "`~joke`",
					"value": "Returns a random awful joke.",
					"inline": True
				},
				{
					"name": "`~fact`",
					"value": "Returns a random fact.",
					"inline": True
				}
				]
			)
		await message.channel.send(embed=e)

	if "zmena" == commandos:
		await message.channel.send(f"Změny rozvrhu pro {attributes}:\n{getZmena(attributes)}")

	if "suggest" == commandos:
		with open("suggestions.txt","a") as suggestions:
			suggestions.write(attributes+"\n")
		await message.channel.send(f"Your suggestion `{attributes}` was accepted")

	if "r/" == commandos:
		try:
			subreddit = reddit.subreddit(attributes)
			e = embed(subreddit.title, url=f"https://reddit.com{subreddit.url}", description=subreddit.description[:2048], thumbnail={"url": subreddit.icon_img}, fields=[{"name": "Subscribers", "value": subreddit.subscribers, "inline":True}, {"name":"Online Subscribers", "value": subreddit.accounts_active, "inline": True}])
			#print(vars(subreddit))
			await message.channel.send(embed = e)
		except Exception as e:
			if e == prawcore.exceptions.NotFound:
				await message.channel.send(f"The subreddit `{attributes}` doesn't exist.")
			else:
				await message.channel.send(f"`{e}` occured while trying to find subreddit `{attributes}`.")
				raise e

	if "gymso" == commandos:
		clanek = gymso()
		e = embed(clanek[0], url=clanek[1], description=clanek[2][:2048])
		await message.channel.send(embed=e)

	if "lyrics" == commandos:
		try:
			results = await kclient.music.lyrics(attributes)
		except ksoftapi.NoResults:
			await message.channel.send(f"No lyrics found for `{attributes}`.")
		else:
			lyrics = results[0]
			for i in range(math.ceil(len(lyrics.lyrics)/2048)):
				e = embed(f"Lyrics for {lyrics.artist} - {lyrics.name}", description=lyrics.lyrics[(i*2048):((i+1)*2048)], thumbnail={"url": lyrics.album_art})
				await message.channel.send(embed=e)

	if "meme" == commandos:
		meme = await kclient.images.random_meme()
		e = embed(f"{meme.title}", url=meme.source, author={"name":meme.author,"url":f"https://reddit.com/user/{meme.author[3:]}"}, image={"url":meme.image_url})
		await message.channel.send(embed=e)

	if "eval" == commandos:
		try: 
			await message.channel.send(eval(attributes))
		except Exception as e:
			print(e)
			await message.channel.send(f"Hej `{attributes}` fakt neudělám")

	if "aww" == commandos:
		aww = await kclient.images.random_aww()
		e = embed(f"{aww.title}", url=aww.source, author={"name":aww.author,"url":f"https://reddit.com/user/{aww.author[3:]}"}, image={"url":aww.image_url})
		await message.channel.send(embed = e)

	if "subreddit" == commandos:
		attributes = attributes.split(" ")
		try:
			if len(attributes) >= 2:
				subreddit_image = await kclient.images.random_reddit(attributes[0], attributes[1])
			else:
				subreddit_image = await kclient.images.random_reddit(attributes[0])
			e = embed(f"{subreddit_image.title}", url=subreddit_image.source, author={"name":subreddit_image.author,"url":f"https://reddit.com/user/{subreddit_image.author[3:]}"}, image={"url":subreddit_image.image_url})
			await message.channel.send(embed = e)
		except ksoftapi.NoResults:
			await message.channel.send(f"No lyrics found for `{attributes}`.")

	"""if "recommend" == commandos:
		attributes = attributes.split(" ")
		provider = "youtube"
		recommendType = None
		for p in ["ids","titles","spotify"]:
			if p in attributes:
				if p in ["ids","titles"]:
					provider = f"youtube_{p}"
				elif p == "spotify":
					provider = "spotify"
				attributes.remove(p)

		for r in ["track", "link", "id"]:
			if r in attributes:
				if r in ["link","id"]:
					recommendType = f"youtube_{r}"
				elif r == "track":
					recommendType = "track"
				attributes.remove(r)

		print(attributes, provider)
		recommendations = await kclient.music.recommendations(attributes, provider)
		await message.channel.send([dir(i) for i in recommendations])"""

	if "mapa" == commandos:
		attributes = attributes.rsplit(" ",1)
		try:
			qwertzuiopasdfghjklyxcvbnmqwertzuiopasdfghjklyxcvbnmqwertzuiopasdfghjkyxcvbnmqweuioadfghjklyxcvbnmqwertzuiopasdfghjklyxcvbnm = attributes[1]
		except:
			attributes.append(12)
		try:
			mapicka = await kclient.kumo.gis(attributes[0],map_zoom=int(attributes[1]),include_map=True, fast=True)
			e = embed(attributes[0],description=f"{mapicka.address}\n {mapicka.lat} {mapicka.lon}",image={"url":mapicka.map})
			await message.channel.send(embed=e)
		except ksoftapi.NoResults:
			await message.channel.send(f"`{attributes[0]}` neexistuje!")

	if "joke" == commandos:
		await message.channel.send(getJokeTxt())

	if "fact" == commandos:
		await message.channel.send(getFact())

	if "wa" == commandos:
		for e in wolframQuery(attributes):
			await message.channel.send(embed=e)

async def checkGymso():
	while True:
		try:
			print("Checking for new posts on Gymso")
			clanky = newOnGymso()
			if clanky:
				for clanek in clanky:
					for i in range(math.ceil(len(clanek["text"])/2048)):
						e = embed(clanek["title"], url = clanek["url"], description=clanek["text"][(i*2048):((i+1)*2048)])
						await obecne.send(f"{klubik.default_role} nový příspěvek na Gymso", embed=e)
		except Exception as e:
			print(e)
		await asyncio.sleep(600)


client.loop.create_task(checkGymso())

client.run(token)
