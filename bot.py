import random
import numpy as np
from random import choice, randint
import os
import math
import requests
from bs4 import BeautifulSoup
import botFunctions
from botFunctions import getZmena, gymso, newOnGymso, getJokeTxt, getFact, wolframQuery, makeSuggestion
import praw
import prawcore
import ksoftapi
import re
import bdbf
from bdbf import spamProtection, embed, hasLink
import asyncio
import discord
import pickle
import pkg_resources



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

bdbf.commands.commandPrefix = "~"
bdbf.embedFooter= {
                "text": "Powered by Bertik23",
                "icon_url": "https://cdn.discordapp.com/avatars/452478521755828224/4cfdbde44582fe6ad05383171ac1b051.png"
                }
bdbf.embedColor = (37, 217, 55)

bdbf.commands.cmds[697015129199607839] = []

##COMMANDS
class info(bdbf.commands.Command):
	async def command(self, args, msg):
		return f"""I'm a bot made by Bertik23#9997
				   I'm running on bdbf {pkg_resources.get_distribution("bdbf").version} and discord.py {pkg_resources.get_distribution("discord.py").version}""", None

bdbf.commands.cmds["all"].append(info("TheBot info"))

class zmena(bdbf.commands.Command):
	async def command(self,args, msg):
		return f"Změny rozvrhu pro {args}:\n{getZmena(args)}",None

bdbf.commands.cmds[697015129199607839].append(zmena("Returns schedule changes for the give teacher/class today","`%commandPrefix%zmena <teacher/class>` eg. `%commandPrefix%zmena Lukešová Danuše` or `%commandPrefix%zmena 6.A`"))

class suggest(bdbf.commands.Command):
	async def command(self,attributes, msg):
		out = makeSuggestion(attributes.split("*||*")[0], attributes.split("*||*")[1] +
			f"""
			***
			Automaticaly issued by `{msg.author}` from `{msg.channel}` in `{msg.channel.guild}`
			""")
		return out[0], out[1]

bdbf.commands.cmds["all"].append(suggest("Suggest a command to the creator of the bot","`%commandPrefix%suggest <title> *||* <text>`"))

class r(bdbf.commands.Command):
	async def command(self,attributes, msg):
		try:
			subreddit = reddit.subreddit(attributes)
			e = embed(subreddit.title, url=f"https://reddit.com{subreddit.url}", description=subreddit.description[:2048], thumbnail={"url": subreddit.icon_img}, fields=[{"name": "Subscribers", "value": subreddit.subscribers, "inline":True}, {"name":"Online Subscribers", "value": subreddit.accounts_active, "inline": True}])
			#print(vars(subreddit))
			return None,e
		except Exception as e:
			if e == prawcore.exceptions.NotFound:
				return "The subreddit `{attributes}` doesn't exist.",None
			else:
				return f"`{e}` occured while trying to find subreddit `{attributes}`.", None

bdbf.commands.cmds["all"].append(r("Returns a subreddit","`%commandPrefix%r/ <subreddit>` eg. `%commandPrefix%r/ kofola`"))

class gymso(bdbf.commands.Command):
	async def command(self,attributes, msg):
		clanek = gymso()
		e = embed(clanek[0], url=clanek[1], description=clanek[2][:2048])
		return None, e

bdbf.commands.cmds[697015129199607839].append(gymso("Returns last post on [gymso.cz](https://gymso.cz)"))

class lyrics(bdbf.commands.Command):
	async def command(self,attributes, msg):
		try:
			results = await kclient.music.lyrics(attributes)
		except ksoftapi.NoResults:
			return f"No lyrics found for `{attributes}`.", None
		else:
			lyrics = results[0]
			for i in range(math.ceil(len(lyrics.lyrics)/2048)):
				e = embed(f"Lyrics for {lyrics.artist} - {lyrics.name}", description=lyrics.lyrics[(i*2048):((i+1)*2048)], thumbnail={"url": lyrics.album_art})
				return None, e

bdbf.commands.cmds["all"].append(lyrics("Returns lyrics to given song","`%commandPrefix%lyrics <song>`"))

class meme(bdbf.commands.Command):
	async def command(self,attributes, msg):
		meme = await kclient.images.random_meme()
		e = embed(f"{meme.title}", url=meme.source, author={"name":meme.author,"url":f"https://reddit.com/user/{meme.author[3:]}"}, image={"url":meme.image_url})
		return None, e

bdbf.commands.cmds["all"].append(meme("Returns random meme from [Reddit](https://reddit.com)"))

class evaluate(bdbf.commands.Command):
	async def command(sefl,attributes, msg):
		try: 
			return eval(attributes), None
		except Exception as e:
			print(e)
			return f"Hej `{attributes}` fakt neudělám", None

bdbf.commands.cmds["all"].append(evaluate("Returns python expresion outcome.","`%commandPrefix%eval <python expresion>` eg. `%commandPrefix%eval math.cos(math.pi)`"))

class aww(bdbf.commands.Command):
	async def command(self,attributes, msg):
		aww = await kclient.images.random_aww()
		e = embed(f"{aww.title}", url=aww.source, author={"name":aww.author,"url":f"https://reddit.com/user/{aww.author[3:]}"}, image={"url":aww.image_url})
		return None, e

bdbf.commands.cmds["all"].append(aww("Returns random aww image from [Reddit](https://reddit.com)"))

class subreddit(bdbf.commands.Command):
	async def command(self,attributes, msg):
		attributes = attributes.split(" ")
		try:
			if len(attributes) >= 2:
				subreddit_image = await kclient.images.random_reddit(attributes[0], attributes[1])
			else:
				subreddit_image = await kclient.images.random_reddit(attributes[0])
			e = embed(f"{subreddit_image.title}", url=subreddit_image.source, author={"name":subreddit_image.author,"url":f"https://reddit.com/user/{subreddit_image.author[3:]}"}, image={"url":subreddit_image.image_url})
			return None, e
		except ksoftapi.NoResults:
			return f"No lyrics found for `{attributes}`.", None

bdbf.commands.cmds["all"].append(subreddit("Returns random image from given subreddit and givel span.","`%commandPrefix%subreddit <subreddit> <span>` eg. `%commandPrefix%subreddit kofola month`\nSpans: `hour`,`day`,`week`,`month`,`year`,`all`"))

class mapa(bdbf.commands.Command):
	async def command(self,attributes, msg):
		attributes = attributes.rsplit(" ",1)
		try:
			qwertzuiopasdfghjklyxcvbnmqwertzuiopasdfghjklyxcvbnmqwertzuiopasdfghjkyxcvbnmqweuioadfghjklyxcvbnmqwertzuiopasdfghjklyxcvbnm = attributes[1]
		except:
			attributes.append(12)
		try:
			mapicka = await kclient.kumo.gis(attributes[0],map_zoom=int(attributes[1]),include_map=True, fast=True)
			e = embed(attributes[0],description=f"{mapicka.address}\n {mapicka.lat} {mapicka.lon}",image={"url":mapicka.map})
			return None, e
		except ksoftapi.NoResults:
			return f"`{attributes[0]}` neexistuje!", None

bdbf.commands.cmds["all"].append(mapa("Returns map of given place with given zoom (default 12).","`%commandPrefix%mapa <place> <zoom=12>` eg. `%commandPrefix%mapa Gymso 16`"))

class joke(bdbf.commands.Command):
	async def command(self,attributes, msg):
		return getJokeTxt(), None

bdbf.commands.cmds["all"].append(joke("Returns a random awful joke."))

class fact(bdbf.commands.Command):
	async def command(self,attributes, msg):
		return getFact(), None

bdbf.commands.cmds["all"].append(fact("Returns a random fact."))

class wa(bdbf.commands.Command):
	async def command(self,attributes, msg):
		for e in wolframQuery(attributes):
			yield None, e

bdbf.commands.cmds["all"].append(wa())

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

	await bdbf.commands.checkForCommands(message)
	
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
