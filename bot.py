from random import choice

botId = 540563812890443794
token = "NTQwNTYzODEyODkwNDQzNzk0.DzSvSQ.0EIosr33WmHA7ig4UIuvSylplPY"
#84032 permissions int
#https://discordapp.com/oauth2/authorize?client_id=540563812890443794&scope=bot&permissions=84032


import discord
client = discord.Client()
guild = client.get_guild(540563312857841714)

@client.event # event decorator/wrapper
async def on_ready():
	print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
	print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

	if "Hi!" in message.content:
		await message.channel.send("Hello")

	if "kdy" in message.content.lower() and "aktualizace" in message.content.lower():
		await message.channel.send("Kdo ví")
	
	if "!vypadni" in message.content:
		quit()

	if "!random" in message.content:
		with open("teams.txt","r") as teams:
			team = choice(teams.read().split("\n"))
			print(team)
			await message.channel.send(team)

client.run(token)
