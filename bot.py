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
from prettytable import PrettyTable



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
bdbf.options.embedFooter= {
                "text": "Powered by Bertik23",
                "icon_url": "https://cdn.discordapp.com/avatars/452478521755828224/4cfdbde44582fe6ad05383171ac1b051.png"
                }
bdbf.options.embedColor = (37, 217, 55)

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
	async def command(self,attributes, msg):
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

class play(bdbf.commands.Command):
	async def command(self, args, msg):
		args = args.split(" ")
		if args[0] == "2048":
			try:
				if int(args[1]) > 1 and int(args[1]) < 19:
					for i in bdbf.commands.cmds["all"]:
						if str(i) == "game":
							i.activeGame[msg.author] = Game2048(msg.author, int(args[1]))
							return "Welcome to 2048, the game where you move numbers around!\nType a number to move the numbers\n0..........up\n1........left\n2........down\n3.......right\n"+i.activeGame[msg.author].printGrid(msg.author), None
				else: 
					return "Grid size must be between 1 and 19", None
			except IndexError:
				return "Options for 2048:\nGrid Size", None
			except Exception as e:
				return e, None
				raise e

bdbf.commands.cmds["all"].append(play("Play games.\nAvailable games:\n2048","`%commandPrefix%play <game> <options>` eg. `%commandPrefix%play 2048 4` or without options to show options"))

class game(bdbf.commands.Command):
	def __init__(self, description=None, usage=None):
		super().__init__(description=description, usage=usage)
		self.activeGame = {}
	async def command(self, args, msg):
		try:
			return self.activeGame[msg.author].play(args, msg)
		except Exception as e:
			print(e)

bdbf.commands.cmds["all"].append(game())

class Game2048:
	def __init__(self, player, gridSize):
		self.grids = {player: []}
		for i in range(gridSize): self.grids[player].append([0 for j in range(gridSize)])
		self.addNumber(player)
		self.addNumber(player)
		self.zeroInGrid = {player: True}

	def play(self, args, msg):
		return self.makeMove(msg.author, int(args)), None

	

	def addNumber(self, player):
		x = random.randint(0, len(self.grids[player])-1)
		y = random.randint(0, len(self.grids[player][x])-1)
		#print(x,y)

		while self.grids[player][x][y] != 0:
			x = random.randint(0, len(self.grids[player])-1)
			y = random.randint(0, len(self.grids[player][x])-1)
			#print(x,y)

		self.grids[player][x][y] = 2

	def move(self, player, direction):
		if direction == 0: #up
			for _ in range(len(self.grids[player])):
				for j in range(len(self.grids[player][_])):
					for i in range(len(self.grids[player])):
						try:
							if self.grids[player][i][j] == 0:
								self.grids[player][i][j] = self.grids[player][i+1][j]
								self.grids[player][i+1][j] = 0
							if self.grids[player][i][j] == self.grids[player][i+1][j]:
								self.grids[player][i][j] += self.grids[player][i+1][j]
								self.grids[player][i+1][j] = 0
						except IndexError:
							pass
		if direction == 1: #left
			for i in range(len(self.grids[player])):
				for _ in range(len(self.grids[player][i])):
					for j in range(len(self.grids[player][i])):
						try:
							if self.grids[player][i][j] == 0:
								self.grids[player][i][j] = self.grids[player][i][j+1]
								self.grids[player][i][j+1] = 0
							if self.grids[player][i][j] == self.grids[player][i][j+1]:
								self.grids[player][i][j] += self.grids[player][i][j+1]
								self.grids[player][i][j+1] = 0
						except IndexError:
							pass
		if direction == 3: #right
			for i in range(len(self.grids[player])):
				for _ in range(len(self.grids[player][i])):
					for j in range(-1, -len(self.grids[player][i])-1,-1):
						#print(j)
						try:
							if self.grids[player][i][j] == 0:
								self.grids[player][i][j] = self.grids[player][i][j-1]
								self.grids[player][i][j-1] = 0
							if self.grids[player][i][j] == self.grids[player][i][j-1]:
								self.grids[player][i][j] += self.grids[player][i][j-1]
								self.grids[player][i][j-1] = 0
						except IndexError:
							pass
		if direction == 2: #down
			for _ in range(len(self.grids[player])):
				for j in range(-1, -len(self.grids[player][_])-1,-1):
					for i in range(len(self.grids[player])):
						#print(j)
						try:
							if self.grids[player][i][j] == 0:
								self.grids[player][i][j] = self.grids[player][i-1][j]
								self.grids[player][i-1][j] = 0
							if self.grids[player][i][j] == self.grids[player][i-1][j]:
								self.grids[player][i][j] += self.grids[player][i-1][j]
								self.grids[player][i-1][j] = 0
						except IndexError:
							pass

	def printGrid(self, player):
		table = PrettyTable()
		table.field_names = [i for i in range(len(self.grids[player][0]))]
		for i, row in enumerate(self.grids[player]):
			table.add_row(row)
		return "`"+str(table)+"`"

	def makeMove(self, player, direction=None):
		if self.zeroInGrid[player]:
			if direction == None:
				direction = int(input(""))
			moveDirection = direction
			self.move(player, moveDirection)
			self.checkForZeros(player)
			if self.zeroInGrid[player]:
				self.addNumber(player)
			else:
				for i in bdbf.commands.cmds["all"]:
					if str(i) == "game":
						i.activeGame[player] = None
				return self.printGrid(player)+ "\n" + f"{player.mention} lost"
			return self.printGrid(player)

	def checkForZeros(self,player):
		self.zeroInGrid[player] = False
		for i in self.grids[player]:
			for j in i:
				if j == 0: self.zeroInGrid[player] = True


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
