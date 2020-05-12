from random import choice
import os
import requests
from bs4 import BeautifulSoup
botId = 540563812890443794
#84032 permissions int
#https://discordapp.com/oauth2/authorize?client_id=540563812890443794&scope=bot&permissions=84032

token = os.environ.get('TOKEN', None)


import discord
client = discord.Client()
guild = client.get_guild(540563312857841714)

spamValue = 5

last10messagesAuthors = {}

def getZmena(parametr):
	zmeny = requests.get("https://bakalari.gymso.cz/next/zmeny.aspx")
	zmeny = BeautifulSoup(zmeny.text, "html.parser")
	tables = zmeny.find_all("table", {"class":"datagrid"})
	for table in tables:
		if table.find("th").text in ["Změny v rozvrzích tříd","Změny v rozvrzích učitelů"]:
			trs = table.find_all("tr")
			#print([t.find_all("td") for t in trs])
			p = False
			for tr1 in trs:
				for i,b in [([u.text for u in t.find_parent().find_previous_siblings()],t) for t in tr1.find_all("table")]:
					print(i)
					if i[0] == parametr:
						e = [[d.text for d in c.find_all("td")] for c in b.find_all("tr")]
						text = ""
						for f in e:
							try:
								text += f"{f[0]}. hod {f[1]} {f[2]} {f[3]} {f[4]} {f[5]}\n"
							except:
								text += f"{f[0]}\n"
						return text

@client.event # event decorator/wrapper
async def on_ready():
	print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
	print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
	if message.channel not in last10messagesAuthors:
		last10messagesAuthors[message.channel] = []
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

	if "~help" in message.content[:5]:
		e = discord.Embed.from_dict({
    "title": "Help for TheBot",
    "color": 2480439,
    "fields": [
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
        "value": "will return lyrics of the now playing song, waiting for Bot approval by [KSoft.Si API](https://api.ksoft.si/)",
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
	  }
     ]
   })
		await message.channel.send(embed=e)

	for i in ["hi","dobrý den","brý den","čau","ahoj"]:
		if i in message.content.lower():
			await message.channel.send("Hello")

	if "kdy" in message.content.lower() and "aktualizace" in message.content.lower():
		await message.channel.send("Kdo ví")
	
	if "~vypadni" in message.content:
		quit()

	if "~randomCSM" in message.content:
		with open("teams.txt","r") as teams:
			team = choice(teams.read().split("\n"))
			print(team)
			await message.channel.send(team)

	if "~zmena" in message.content[:6]:
		await message.channel.send(f"Změny rozvrhu pro {message.content[7:]}:\n{getZmena(message.content[7:])}")

	if "~embedTest" in message.content:
		e = discord.Embed.from_dict({
    "title": "title ~~(did you know you can have markdown here too?)~~",
    "description": "this supports [named links](https://discordapp.com) on top of the previously shown subset of markdown. ```\nyes, even code blocks```",
    "url": "https://discordapp.com",
    "color": 1210266,
	"timestamp": 1,
    "footer": {
      "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png",
      "text": "footer text"
    },
    "thumbnail": {
      "url": "https://cdn.discordapp.com/embed/avatars/0.png"
    },
    "image": {
      "url": "https://cdn.discordapp.com/embed/avatars/0.png"
    },
    "author": {
      "name": "author name",
      "url": "https://discordapp.com",
      "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
    }})
		await message.channel.send(embed=e)

	if "~suggest" in message.content[:8]:
		with open("suggestions.txt","a") as suggestions:
			suggestions.write(message.content[8:]+"\n")
		await message.channel.send(f"Your suggestion `{message.content[8:]}` was accepted")

client.run(token)
