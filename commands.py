import bdbf
import pkg_resources
import ksoftapi
from bdbf import *
from botFunctions import *
import prawcore, praw
import math
from botGames import Game2048

reddit = None
kclient = None

bdbf.commands.cmds[697015129199607839] = []

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
							await i.activeGame[msg.author].startGame(msg)
				else: 
					return "Grid size must be between 1 and 19", None
			except IndexError:
				return "Options for 2048:\nGrid Size", None
			except Exception as e:
				msg.channel.send(e)
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
