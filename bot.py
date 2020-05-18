from random import choice
import os
import math
import requests
from bs4 import BeautifulSoup
import botFunctions
from botFunctions import getZmena, embed, command, gymso
import praw
import prawcore
import ksoftapi

kclient = ksoftapi.Client(os.environ.get("ksoft_token", None))

reddit = praw.Reddit(client_id = os.environ.get("reddit_client_id", None),
                     client_secret = os.environ.get("reddit_client_secret", None),
                     user_agent = os.environ.get("reddit_user_agent", None))

botId = 540563812890443794
#84032 permissions int
#https://discordapp.com/oauth2/authorize?client_id=540563812890443794&scope=bot&permissions=84032

token = os.environ.get('TOKEN', None)




import discord
client = discord.Client()
guild = client.get_guild(540563312857841714)

botFunctions.commandPrefix = "~"

spamValue = 5

last10messagesAuthors = {}


@client.event # event decorator/wrapper
async def on_ready():
	print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
	print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
	if message.channel not in last10messagesAuthors:
		last10messagesAuthors[message.channel] = []
	if not message.author.bot:
		last10messagesAuthors[message.channel].append(message.author)
	if len(last10messagesAuthors[message.channel]) > spamValue:
		del last10messagesAuthors[message.channel][0]
	a = 0
	for author in last10messagesAuthors[message.channel]:
		if author == message.author:
			a += 1
		else:
			break
	if a >= spamValue and message.author.name != "TheBot":
		await message.channel.send(f"{message.author.mention} nespamuj!")

	for i in ["dobrý den","brý den","čau","ahoj", "zdravíčko", "tě péro","zdárek párek","tě guli", "čus"]:
		if i in message.content.lower() and not message.author.bot:
			await message.channel.send(f"Hello {message.author.mention}")

	if "kdy" in message.content.lower() and "aktualizace" in message.content.lower():
		await message.channel.send("Kdo ví")
	
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
				}
				]
			)
		await message.channel.send(embed=e)

	if "randomCSM" == commandos:
		with open("teams.txt","r") as teams:
			team = choice(teams.read().split("\n"))
			print(team)
			await message.channel.send(team)

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



client.run(token)
