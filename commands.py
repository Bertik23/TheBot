import datetime
import json
import math
import random
import time

import ksoftapi
import numpy as np
import pkg_resources
import plotly.express as px
import plotly.graph_objects as go
import prawcore
import uhlovodikovac
from bdbf import *
from PIL import Image, ImageDraw, ImageFont

import botFunctions
from botFunctions import *
from botGames import Game2048, GameNim
from database import (commandLog, getCovidTipsDate, getGuildBDays, messageLog,
                      setCovidTip, timers)
from exceptions import *
from variables import *


@client.command("info")
async def info(msg, *args):
    """TheBot info"""
    await msg.reply(
        f"I'm a bot made by <@452478521755828224>\n"
        f"Version {'.'.join(str(i) for i in version)}\n"
        "I'm running on bdbf "
        f"{pkg_resources.get_distribution('bdbf').version}"
        " and discord.py "
        f"{pkg_resources.get_distribution('discord.py').version}.\n"
        "I'm and open source bot, that means that you can contribute to me on"
        "https://github.com/Bertik23/DiscordBot"
    )


@client.command("changelog")
async def command_changelog(msg, *args):
    """The changelog"""
    await msg.reply(
        embed=client.embed("Changelog", fields=[
            (i, changelog[i]) for i in changelog]))


@client.command(
    "zmena",
    worksOnlyInGuilds=[
        697015129199607839,
        793152939022745610
    ]
)
async def zmena(msg, *args):
    """Returns schedule changes for the give teacher/class today
    **Usage**: `%commandPrefix%zmena <teacher/class>`\
        eg. `%commandPrefix%zmena Lukešová Danuše` \
        or `%commandPrefix%zmena 6.A`
    """
    await msg.reply(
        f"Změny rozvrhu pro {args[0]}:\n{getZmena(args[0])}")


@client.command("rozvrh", worksOnlyInGuilds=[
    697015129199607839, 793152939022745610, 540563312857841714
    ]
)
async def rozvrh(msg, *args):
    """Returns the timatable for given teacher/class/room
    **Usage**: `%commandPrefix%rozvrh <teacher/class/room>` eg. \
    `%commandPrefix%rozvrh Lukešová Danuše` or `%commandPrefix%rozvrh 7.A` or \
    `%commandPrefix%rozvrh A307` \
    to see the rooms add `-t`, to see the timetable for the next week add `-n`\
     to see the permanent timetable add `-p`"""
    room = False
    week = "now"
    args = args[0]
    if args is None:
        args = ""
    if "-t" in args:
        room = True
        args = args.replace("-t", "").strip()
    if "-n" in args:
        week = "next"
        args = args.replace("-n", "").strip()
    if "-p" in args:
        week = "perm"
        args = args.replace("-p", "").strip()
    if args == "":
        args = "8.A"

    async with msg.channel.typing():
        await msg.reply(
            file=discord.File(
                getTimetable(getTimetableUrl(args), room=room, week=week),
                filename="rozvrh.png"))


@client.command("suggest")
async def suggest(msg, *args):
    """Suggest a command to the creator of the bot
    **Usage**: `%commandPrefix%suggest <title> *||* <text>`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    out = makeSuggestion(
        attributes.split("*||*")[0],
        attributes.split("*||*")[1] +
        f"""
***
Automaticaly issued by \
`{msg.author}` from `{msg.channel}` in `{msg.channel.guild}`
""")
    await msg.reply(out[0], embed=out[1])


@client.command("r")
async def r(msg, *args):
    """Returns a subreddit
    **Usage**: `%commandPrefix%r/ <subreddit>` eg. `%commandPrefix%r/ kofola`
    """
    if args == (None,):
        return
    else:
        attributes = args[0]
    try:
        subreddit = reddit.subreddit(attributes)
        e = client.embed(subreddit.title,
                         url=f"https://reddit.com{subreddit.url}",
                         description=subreddit.description[:2048],
                         thumbnail={"url": subreddit.icon_img},
                         fields=[("Subscribers",
                                  subreddit.subscribers,
                                  True),
                                 ("Online Subscribers",
                                  subreddit.accounts_active,
                                  True)])
        # print(vars(subreddit))
        await msg.reply(embed=e)
    except Exception as e:
        if e == prawcore.exceptions.NotFound:
            await msg.reply(
                "The subreddit `{attributes}` doesn't exist.")
        else:
            await msg.reply(
                f"`{e}` occured while trying to find subreddit `{attributes}`."
                )


@client.command(
    "gymso",
    worksOnlyInGuilds=[
        697015129199607839,
        793152939022745610
    ]
)
async def gymsoCommand(msg, *args):
    """Returns last post on [gymso.cz](https://gymso.cz)"""
    clanek = gymso()
    e = client.embed(clanek[0], url=clanek[1],
                     description=clanek[2][:2048], fields=())
    await msg.reply(embed=e)


@client.command("lyrics")
async def lyrics(msg, *args):
    """Returns lyrics to given song
    **Usage**: `%commandPrefix%lyrics <song>`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    try:
        results = await kclient.music.lyrics(query=attributes)
    except ksoftapi.NoResults:
        await msg.reply(
            f"KSoft.Si API has no lyrics for `{attributes}`.")
    else:
        lyrics = results[0]
        for i in range(math.ceil(len(lyrics.lyrics) / 2048)):
            e = client.embed(
                f"Lyrics for {lyrics.artist} - {lyrics.name} \
                from KSoft.Si API",
                description=lyrics.lyrics[(i * 2048):((i + 1) * 2048)],
                thumbnail={"url": lyrics.album_art},
                fields=())
            await msg.reply(embed=e)


@client.command("meme")
async def meme(msg, *args):
    """Returns random meme from [Reddit](https://reddit.com)"""
    meme = await kclient.images.random_meme()
    e = client.embed(
        f"{meme.title}",
        url=meme.source,
        author={
            "name": meme.author,
            "url": f"https://reddit.com/user/{meme.author[3:]}"},
        image={
            "url": meme.image_url},
        fields=())
    await msg.reply(embed=e)


@client.command(
    "eval",
    worksOnlyInGuilds=[
        697015129199607839,
        540563312857841714
    ]
)
async def evalCommand(msg, *args):
    """Returns python expresion outcome.
    **Usage**: `%commandPrefix%eval <python expresion>` eg. \
    `%commandPrefix%eval math.cos(math.pi)`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    try:
        await msg.reply(eval(attributes))
    except Exception as e:
        await msg.reply(
            f"Hej `{attributes}` fakt neudělám\nProtože: {e}")


@client.command("aww")
async def aww(msg, *args):
    """Returns random aww image from [Reddit](https://reddit.com)"""
    aww = await kclient.images.random_aww()
    e = embed(
        f"{aww.title}",
        url=aww.source,
        author={
            "name": aww.author,
            "url": f"https://reddit.com/user/{aww.author[3:]}"},
        image={
            "url": aww.image_url},
        fields=())
    await msg.reply(embed=e)


@client.command("subreddit")
async def subreddit(msg, *args):
    """Returns random image from given subreddit and givel span.
    **Usage**: `%commandPrefix%subreddit <subreddit> <span>` eg. \
    `%commandPrefix%subreddit kofola month`
    Spans: `hour`,`day`,`week`,`month`,`year`,`all`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    attributes = attributes.split(" ")
    try:
        if len(attributes) >= 2:
            subreddit_image = await kclient.images.random_reddit(
                attributes[0], attributes[1])
        else:
            subreddit_image = await kclient.images.random_reddit(attributes[0])
        e = embed(
            f"{subreddit_image.title}",
            url=subreddit_image.source,
            author={
                "name": subreddit_image.author,
                "url": f"https://reddit.com/user/{subreddit_image.author[3:]}"
                },
            image={
                "url": subreddit_image.image_url},
            fields=())
        await msg.reply(embed=e)
    except ksoftapi.NoResults:
        await msg.reply(f"No lyrics found for `{attributes}`.")


@client.command("mapa")
async def mapa(msg, *args):
    """Returns map of given place with given zoom (default 12).
    **Usage**: `%commandPrefix%mapa <place> <zoom=12>` eg. \
    `%commandPrefix%mapa Gymso 16`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    attributes = attributes.rsplit(" ", 1)
    try:
        int(attributes[1])
        attributes = " ".join(attributes).rsplit(" ", 1)
    except BaseException:
        attributes.append(12)
    try:
        mapicka = await kclient.kumo.gis(
            attributes[0],
            map_zoom=int(attributes[1]),
            include_map=True,
            fast=True)
        e = embed(
            attributes[0],
            description=f"{mapicka.address}\n {mapicka.lat} {mapicka.lon}",
            image={
                "url": mapicka.map},
            fields=())
        await msg.reply(embed=e)
    except ksoftapi.NoResults:
        await msg.reply(f"`{attributes[0]}` neexistuje!")


@client.command("joke")
async def joke(msg, *args):
    """Returns a random awful joke."""
    await msg.reply(getJokeTxt())


@client.command("fact")
async def fact(msg, *args):
    """Returns a random fact."""
    await msg.reply(getFact())


@client.command("wa")
async def wa(msg, *args):
    """Wolfram alpha query"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    for e in wolframQuery(attributes):
        await msg.reply(embed=e)


@client.command("encrypt")
async def encryptCommand(msg, *args):
    """Encrypt a text
    **Usage**: `%commandPrefix%encrypt <text> <encryptionBase>` eg. \
    `%commandPrefix%encrypt Hello, how are you? 64`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    text_to_encrypt = attributes.rsplit(" ", 1)[0]
    try:
        encryption_base = int(attributes.rsplit(" ", 1)[1])
    except ValueError as e:
        await msg.reply(f"The last word must be a encryption base\n{e}")
    else:
        await msg.reply(embed=client.embed(
            "Your encrypted text",
            description=f"```{encrypt(text_to_encrypt, encryption_base)}```",
            fields=()))


@client.command("decrypt")
async def decryptCommand(msg, *args):
    """Decrypt a text encrypted using encrypt
    **Usage**: `%commandPrefix%decrypt <encryptedTest> <encryptionBase>` eg. \
    `%commandPrefix%decrypt ^eQO3gN39aYO[>1LabKh=\\_ 64`"""
    if args == (None, ):
        return
    else:
        attributes = args[0]
    text_to_decrypt = attributes.rsplit(" ", 1)[0]
    try:
        encryption_base = int(attributes.rsplit(" ", 1)[1])
    except ValueError as e:
        await msg.reply(f"The last word must be a encryption base\n{e}")
    else:
        await msg.reply(embed=client.embed(
            "Your decrypted text",
            description=f"```{decrypt(text_to_decrypt, encryption_base)}```",
            fields=()))


@client.command("stats")
async def stats(msg, *args):
    """Shows stats"""
    if args == (None, ):
        args = None
    else:
        args = args[0]
    async with msg.channel.typing():
        if args == "commands":
            commandsList = list(np.transpose(commandLog.get_all_values()[1:]))
            commandCountTotaly = len(commandsList[0])
            commandCountGuild = len(
                [g for g in commandsList[6] if g == str(msg.channel.guild.id)])
            commandCountChannel = len(
                [g for g in commandsList[4] if g == str(msg.channel.id)])
            mostActiveCommandor = mostFrequent(commandsList[3])
            mostUsedCommand = mostFrequent(commandsList[1])

            commandTimes = commandsList[0]

            commandTimeUsage = {}
            for i, t in enumerate(commandTimes):
                if t[:10] not in commandTimeUsage.keys():
                    commandTimeUsage[t[:10]] = []
                commandTimeUsage[t[:10]].append(commandsList[1][i])

            for key in commandTimeUsage.keys():
                commandTimeUsage[key] = count(commandTimeUsage[key])

            # print(commandTimeUsage)

            commandCounts = count(commandsList[1])

            commandTimes = [
                time.isoformat() for time in map(
                    roundToTheLast30min, map(
                        datetime.datetime.fromisoformat, commandTimes))]
            commandTimesUno = deleteDuplicates(commandTimes)
            commandTimeCounts = [commandTimes.count(
                t) for t in commandTimesUno]

            # print(commandTimes)

            # fig = go.Figure()

            fig = px.bar(x=commandTimesUno, y=commandTimeCounts)

            fig.update_yaxes(type="log", range=[
                             0, math.log(max(commandTimeCounts), 10) + 0.2])

            fig_bytes = fig.to_image(format="png", width=1800, height=800)

            await msg.reply(file=discord.File(
                io.BytesIO(fig_bytes),
                filename="stats.png"))

            x = [f"{t}T00:00:00.000000" for t in commandTimeUsage.keys()]
            fig = go.Figure()

            # print(rotateDict(commandTimeUsage))

            cmds = {}

            for c in commandsList[1]:
                cmds[c] = []
                for t in commandTimeUsage.keys():
                    try:
                        cmds[c].append(commandTimeUsage[t][c])
                    except KeyError:
                        cmds[c].append(0)

            # print(cmds)

            for c in cmds.keys():
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=cmds[c],
                        mode='lines',
                        line=dict(
                            width=2,
                            color=(f"rgb({random.randint(0,255)}, "
                                   f"{random.randint(0,255)}, "
                                   f"{random.randint(0,255)})"),
                            shape='spline',
                            smoothing=0.5),
                        name=c))

            fig.update_layout(
                showlegend=True)

            fig.update_yaxes(type="log", range=[0, math.log(
                max(commandCounts.values()), 10) + 0.2])

            fig_bytes = fig.to_image(format="png", width=1800, height=800)

            await msg.reply(file=discord.File(
                io.BytesIO(fig_bytes),
                filename="stats.png"))

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=list(
                            commandCounts.keys()), values=list(
                            commandCounts.values()), textinfo="value+percent")]
                            )

            fig_bytes = fig.to_image(format="png", width=1200, height=1200)

            await msg.reply(file=discord.File(
                io.BytesIO(fig_bytes),
                filename="stats.png"))

            await msg.reply(embed=client.embed("TheBot stats", fields=[
                ("Total Commands", commandCountTotaly, True),
                ("Guild Commands", commandCountGuild, True),
                ("Channel Commands", commandCountChannel, True),
                ("Most Commands", mostActiveCommandor, True),
                ("Most Used Command", mostUsedCommand, True)]))

        elif args == "messages":
            startTime = time.time()
            messagesList = list(np.transpose(messageLog.get_all_values()[1:]))
            guildMessages = len(
                [g for g in messagesList[7] if g == str(msg.channel.guild.id)])
            channelMessages = len(
                [g for g in messagesList[5] if g == str(msg.channel.id)])
            mostActive = mostFrequent(messagesList[4])

            messageTimes = messagesList[0]

            messageGuilds = messagesList[7]

            messageTimes = [
                time.isoformat() for i, time in enumerate(
                    map(
                        roundToTheLast30min, map(
                            datetime.datetime.fromisoformat, messageTimes)))
                if messageGuilds[i] == str(
                    msg.channel.guild.id)]
            messageTimesUno = deleteDuplicates(messageTimes)
            messageTimeCounts = [messageTimes.count(
                t) for t in messageTimesUno]

            fig = px.bar(x=messageTimesUno, y=messageTimeCounts, range_x=[
                         messageTimesUno[0], messageTimesUno[-1]])

            fig_bytes = fig.to_image(format="png", width=3200, height=800)

            await msg.reply(file=discord.File(
                io.BytesIO(fig_bytes),
                filename="stats.png"))

            await msg.reply(embed=client.embed("TheBot stats", fields=[
                ("Guild Messages", guildMessages, True),
                ("Channel Messages",
                 channelMessages, True),
                ("Most Messages", mostActive, True)]))
            print(f"Took {startTime - time.time()} seconds")
        else:
            await msg.reply(embed=client.embed(
                "Available stats categories", fields=[
                    ("commands", "Command stats"),
                    ("messages", "Message stats")
                ]))


@client.command("rates")
async def rates(msg, *args):
    """Converts currencies
    **Usage**: `%commandPrefix%rates <from> <to> <count>` eg. \
    `%commandPrefix%rates EUR CZK 120`"""
    if args == (None, ):
        return
    else:
        args = args[0]
    currencies = args.split(" ")
    rate = getCurrencyConversion(currencies[0], currencies[1])
    if isinstance(rate, str):
        await msg.reply(rate)
    else:
        await msg.reply(
            f"{currencies[2]} {currencies[0]} is "
            f"{float(currencies[2])*rate} {currencies[1]}")

activeGame = {}


@client.command("play")
async def play(msg: discord.Message, *args):
    """Play games.\nAvailable games:\n2048
    **Usage**: `%commandPrefix%play <game> <options>` eg. \
    `%commandPrefix%play 2048 4` or without options to show options"""
    if args == (None,):
        return
    else:
        args = args[0]
    args = args.split(" ")
    if args[0] == "2048":
        try:
            if int(args[1]) > 1 and int(args[1]) < 19:
                activeGame[msg.author] = Game2048(msg.author, int(args[1]))
                await activeGame[msg.author].startGame(msg)
            else:
                await msg.reply("Grid size must be between 1 and 19")
        except IndexError:
            await msg.reply("Options for 2048:\nGrid Size")
        except Exception as e:
            await msg.reply(e)
            raise e
    elif args[0] == "Nim":
        try:
            collumns = list(map(int, args[2:]))
            activeGame[msg.author] = GameNim(
                msg.author,
                msg.mentions[0],
                collumns
            )
            await activeGame[msg.author].startGame(msg)
        except IndexError:
            await msg.reply("Options for 2048:\nStart position")
        except Exception as e:
            await msg.reply(e)
            raise e

# class game(Command):
#     def __init__(self, description=None, usage=None):
#         super().__init__(description=description, usage=usage)
#         self.activeGame = {}
#     async def commandos(self, args, msg):
#         try:
#             return self.activeGame[msg.author].play(args, msg)
#         except Exception as e:
#             print(e)

# bdbf.commands.cmds["all"].append(game())

# #507484929001652224 BladeX
# bdbf.commands.cmds[507484929001652224] = []

# class support(Command):
#     async def commandos(self, args, msg):
#         if 562713869957726208 not in [r.id for r in msg.author.roles]:
#             await msg.author.add_roles(discord.Object(562713869957726208))
#             if msg.author.dm_channel == None:
#                 await msg.author.create_dm()
#             await msg.author.send("You now have the tag Needs Support,
# which
#  means you can access the Support Text and Voice Channels. Ask for any
# support you may need. We ask that you please remain patient, the Support
# Team has been notified and we will be with you as soon as possible. Thank
# you.\n\nNyní máš tag Needs Support, který ti dává přístup k textovým a
# hlasovým kanálům podpory. Obrať se na podporu s jakýmkoli dotazem.
# Prosím buď trpělivý, tým podpory byl informován a bude se ti věnovat
# co nejdříve. Děkujem.")
#         else:
#             if msg.author.dm_channel == None:
#                 await msg.author.create_dm()
# await msg.author.send("You already have the Needs Support tag, please be
# patient.\n\nUž máš tag Needs Support. Prosíme, abys byl trpělivý")

# bdbf.commands.cmds[507484929001652224].append(support("Gives you the Needs
# Support role"))


@client.command("uhel")
async def uhel(msg, *args):
    """Image uhlovodik"""
    if args == (None, ):
        return
    else:
        args = args[0]
    try:
        hc = uhlovodikovac.HydroCarbon(args)
        await msg.reply(file=discord.File(
            hc.draw(),
            filename="uhlovodik.png"))
    except Exception as e:
        await msg.reply(e)

# bdbf.commands.cmds["all"].append(uhel())


@client.command("timer")
async def timer(msg, *args):
    ("""Timer command.
    **Usage**: `%commandPrefix%timer <seconds>` or \
    `%commandPrefix%timer <ISO utc time>` or \
    `%commandPrefix%timer <ordinal utc time>` eg. \
    `%commandPrefix%timer 60` or `%commandPrefix%timer \
    2020-12-31T23:59:59` or `%commandPrefix%timer 12:35` \
    \nTo get current time remaining use \
    `%commandPrefix%timer -Q` \n\
    You can add -M <message> for a message to be send when the timer ends. \
    eg. `%commandPrefix%timer 10 -M Wake up!`
    """)
    if args == (None, ):
        return
    else:
        args = args[0]
    channel = msg.channel

    if "-Q" in args:
        try:
            for id in userTimers:
                if userTimers[id].author == msg.author:
                    userTimers[id].sendMsg(True)
            return
        except BaseException:
            return

    if "-M" not in args:
        args += "-M"

    args, timerMessage = args.split("-M", 1)
    args = args.strip()

    if isDatetimeIsoFormat(args):
        t = datetime.datetime.fromisoformat(args)
    elif isStrNumber(args):
        t = (datetime.datetime.utcnow() +
             datetime.timedelta(seconds=float(args)))
    elif isTimeIsoFormat(args):
        t = datetime.datetime.combine(
            datetime.date.today(),
            datetime.time.fromisoformat(args)
        )
    else:
        await channel.send("Coudn't parse endtime for timer.")
        return

    userTimers[msg.author.id] = TimerObject()
    timers.append_row(
        [str(userTimers[msg.author.id].id),
         str(msg.author.id),
         msg.author.name,
         t.isoformat(),
         timerMessage,
         str(msg.id),
         str(msg.channel.id)]
    )

    await userTimers[msg.author.id].timer(t, msg, timerMessage)


class TimerObject():
    def __init__(self, id=None):
        self.t = -10
        self.timerMsg = None
        self.channel = None
        self.author = None
        if id is None:
            self.id = int((
                datetime.datetime.utcnow()
                - datetime.datetime.fromisoformat("2019-01-31T16:07:36.183")
                ).total_seconds() * 1_000_000
            )
        else:
            self.id = id

    async def timer(self, t, msg, timerMessage):
        self.author = msg.author
        self.start = datetime.datetime.utcnow()
        self.end = t  # datetime.datetime.utcnow() + timedelta(seconds=t)
        self.channel = msg.channel
        self.t = t
        self.sending = True
        self.commandMsg = msg
        self.timerMessage = timerMessage

        client.loop.create_task(self.sender())

    def getTime(self):
        return (self.end - datetime.datetime.utcnow()).total_seconds()

    async def sender(self):
        while self.sending:
            days, hours, minutes, seconds = await self.sendMsg()
            if (days, hours, minutes, seconds) != (0, 0, 0, 0):
                if days > 0:
                    await asyncio.sleep(minutes * 60 + seconds)
                if hours > 0:
                    await asyncio.sleep(seconds)
                else:
                    await asyncio.sleep(1)
            else:
                self.sending = False
                sendMsg = (
                    f"{self.commandMsg.author.mention} Timer completed!" +
                    (f"\n{self.timerMessage}" if self.timerMessage != ""
                        else "")
                )
                await self.channel.send(
                    sendMsg,
                    tts=True)

                timers.delete_row(
                    timers.col_values(1).index(str(self.id)) + 1
                )
                self.t = -10
                self.channel = None

    async def sendMsg(self, newMessage=False):
        # print(self.getTime())
        if self.getTime() >= 0:
            minutes, seconds = divmod(self.getTime(), 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
        else:
            days, hours, minutes, seconds = 0, 0, 0, 0

        if days > 0:
            message = (f"{self.author.mention} {addZero(int(days))} days "
                       f"{addZero(int(hours))} hours left.")
        elif hours > 0:
            message = (f"{self.author.mention} {addZero(int(hours))} hours "
                       f"{addZero(int(minutes))} minutes left.")
        else:
            message = (f"{self.author.mention} {addZero(int(minutes))}:"
                       f"{addZero(int(seconds))} left.")

        if self.timerMsg is None or newMessage:
            self.timerMsg = await self.channel.send(message)
        else:
            await self.timerMsg.edit(content=message)
        return (days, hours, minutes, seconds)


# bdbf.commands.cmds["all"].append(timer())


# class image(Command):
#     async def commandos(self, args, msg):
#         roboto = ImageFont.truetype("fonts/Roboto-Regular.ttf",15)

#         img = Image.new("RGBA", size = (1,1),
# color=(int("36",16),int("39",16),int("3F",16),255))

#         def imgURL(url):
#             return Image.open(io.BytesIO(requests.get(url).content))

#         def addImgAndText(img, image=None, text="", padding=5):
#             if image == None:
#                 image = Image.new("RGBA",size=(0,0))
#             y = img.size[1]

#             textLen = max(map(len,text.split("\n")))*10

#             size = [0,0]
#             print(img.size, image.size, textLen)
#             if img.size[0] > image.size[0] and img.size[0] > textLen:
#                 size[0] = img.size[0]
#             elif img.size[0] < textLen and image.size[0] < textLen:
#                 size[0] = padding+textLen
#             elif image.size[0] > textLen:
#                 size[0] = image.size[0]+padding
#             else:
#                 size[0] = padding+textLen

#             print(size)

#             size[1] = img.size[1] + image.size[1]+padding*2+len(text.split
# ("\n")*15)


#             img2 = Image.new("RGBA", size = size, color=(int("36",16),int
# ("39",16),int("3F",16),255))
#             img2.paste(img,(0,0,img.size[0],img.size[1]))
#             img = img2

#             img.paste(image,(padding,y + padding,image.size[0]+padding,image.
# size[1]+padding+y))

#             draw = ImageDraw.Draw(img)

#             draw.text((padding,y+image.size[1]+padding), text, font=roboto)

#             return img

#         def remove_transparency(im, bg_colour=(int("36",16),int("39",16),int(
# "3F",16))):
#             # Only process if image has transparency
# (http://stackoverflow.com/a/1963146)
# if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in
# im.info):

#                 # Need to convert to RGBA if LA format due to a bug in PIL
# (http://stackoverflow.com/a/1963146)
#                 alpha = im.convert('RGBA').split()[-1]

#                 # Create a new background image of our matt color.
#                 # Must be RGBA because paste requires both
# images have the same format
#                 # (http://stackoverflow.com/a/8720632  and
# http://stackoverflow.com/a/9459208)
#                 bg = Image.new("RGBA", im.size, bg_colour + (255,))
#                 bg.paste(im, mask=alpha)
#                 return bg

#             else:
#                 return im

#         while "%image:" in args:
#             args = args.split("%image:",1)[1]
#             img = addImgAndText(img, imgURL(args.split(" ")[0]), args.split(
# "%image:")[0].split(" ",1)[1])
#         img = remove_transparency(img)
#         img.save("temp.png")
#         with open("temp.png", "rb") as f:
#             await msg.reply(file = discord.File(f))

# bdbf.commands.cmds["all"].append(image())

@client.command("makeEmbed")
async def makeEmbedCommand(msg, *args):
    """Makes the an embed from json. \
    You can get your json [here](https://leovoel.github.io/embed-visualizer/)
    """
    if args == (None,):
        return
    embedDict = json.loads(args[0])
    embedDict.pop("timestamp", "")
    await msg.reply(embed=discord.Embed.from_dict(embedDict))


@client.command(
    "nextHour",
    worksOnlyInGuilds=[
        697015129199607839,
        793152939022745610
    ]
)
async def commandos(msg, *args):
    """Returns next hour and when it starts"""
    for hour in nextHoursAreAndStartsIn():
        message = "".join((
            f"Za {str(hour[0])[:-3]} začíná `{hour[1]}`",
            f" pro `{hour[1]}`" if hour[2] is not None else "",
            f" v `{hour[3]}`" if hour[3] != "" else ""
        )
        )
        await msg.reply(message)


@client.command("color")
async def color(msg, *args):
    """Displays a color
    **Usage**: `%commandPrefix%color <color>` eg. \
    `%commandPrefix%color ffffff`"""
    args = args[0]
    args = int(args[0:2], 16), int(args[2:4], 16), int(args[4:6], 16)
    img = Image.new("RGBA", (50, 50), args)
    img.save("temp.png")
    with open("temp.png", "rb") as f:
        await msg.reply(file=discord.File(
            io.BytesIO(f.read()),
            filename="color.png"))


@client.command("search")
async def search(msg, *args):
    """Searches the web"""
    # print(args)
    if args == ():
        return
    r = requests.get(
        f"https://api.duckduckgo.com/?q={args[0]}&format=json&kl=cz-cs").json()
    # print(msg.content)
    await msg.reply(embed=client.embed(
        r["Heading"],
        description=r["AbstractText"],
        fields=[]))


@client.command("rotate")
async def rotate(msg, *args):
    """Rotates supplied image

    **Usage**: `%commandPrefix%rotate <img_url> <angle>`
    eg. `%commandPrefix%rotate example.com/image.png 90`
    """
    args = args[0].split(" ")
    url = args[0]
    img = Image.open(io.BytesIO(requests.get(url).content))

    img = img.rotate(float(args[1]), expand=True)

    img.save("temp.png")

    with open("temp.png", "rb") as f:
        await msg.reply(file=discord.File(f))


@client.command("day")
async def day_command(msg, *args):
    """Returns day info"""
    args = args[0]
    if args is None:
        today = datetime.date.today()
    else:
        args = args.split(".")
        today = datetime.date(
            year=int(args[2]),
            month=int(args[1]),
            day=int(args[0])
        )
    countryNameDays = {}
    # for country in ["cz", "sk", "pl", "fr", "hu",
    #                 "hr", "se", "us", "at", "it",
    #                 "es", "de", "dk", "fi", "bg",
    #                 "lt", "ee", "lv", "gr", "ru"]:
    #     print(country)
    #     r = requests.post(
    #         f"https://nameday.abalin.net/today?"
    #         f"country={country}&month={today.month}&day={today.day}")
    #     print(f"{r = }, {r.text = }")
    #     r = r.json()
    #     countryNameDays[country] = r["data"]["namedays"][country]
    r = requests.post("https://nameday.abalin.net/today").json()
    countryNameDays = r["data"]["namedays"]

    querystring = {"fragment": "true", "json": "true"}

    headers = {
        'x-rapidapi-key': "3f77d232fbmsh3b6a8f03b5eb9d6p17a95ajsn29dcf1d441e0",
        'x-rapidapi-host': "numbersapi.p.rapidapi.com"
        }
    r = requests.get("https://numbersapi.p.rapidapi.com/"
                     f"{today.month}/{today.day}/date",
                     headers=headers,
                     params=querystring).json()

    def dayStr(date):
        return f"{date: %A %d %B %Y}"
    dayTrivia = f"On {dayStr(today.replace(year=r['year']))} {r['text']}"

    # print(countryNameDays)
    namedaysStr = ""
    for i in countryNameDays:
        namedaysStr += f"**{i}**: {countryNameDays[i]}\n"

    await msg.reply(embed=client.embed(
        dayStr(today),
        description=dayTrivia,
        fields=[("Week", today.isocalendar().week), ("NameDays", namedaysStr)])
    )


@client.command("cks")
async def cks_command(msg, *args):
    """CKS"""
    tridy = getCKS()
    topTrida = (
        max(tridy, key=tridy.__getitem__),
        tridy[max(tridy, key=tridy.__getitem__)]
    )
    await msg.reply(
        embed=client.embed(
            "Cesta kolem světa",
            description=f"První je {topTrida[0]} s {topTrida[1]} km",
            fields=[(i, tridy[i], True) for i in tridy]
        )
    )


@client.command("birthdays")
async def birthdays_command(msg, *args):
    """Displays the set birthdays for this guild"""
    await msg.reply(embed=client.embed(
        "Birthdays of this guild",
        fields=[
            (f"{i['Birthdate']:%d %b %Y}", i["UserMention"])
            for i in sorted(
                getGuildBDays(msg.guild.id),
                key=lambda x: x["Birthdate"].replace(year=2000))
        ]
    ))


@client.command("covidData")
async def covidData_command(msg, *args):
    """Shows covid data for last day"""
    await covidDataSend(msg.channel)


@client.command("setCovidTip")
async def setCovidTip_command(msg, *args):
    """Sets your tip for the day

    **Usage**: `%commandPrefix%setCovidTip <tip> [twitterHandle]`
    eg. `%commandPrefix%setCovidTip 123456 Bertik23`
    """
    try:
        args = f"{args[0]} "
        args, twitterUsername = args.split(" ", 1)
        tip = int(args)
    except ValueError:
        await msg.reply(f"Demente, `{args[0]}` neni číslo!")
        return

    setCovidTip(datetime.datetime.now(), tip, msg.author, twitterUsername)

    tips = getFullCovidTips(datetime.date.today())
    tips.sort(key=lambda x: x["number"])

    await msg.reply(
        embed=covidTipsEmbed(tips)
    )


@client.command("covidTips")
async def covidTips_command(msg, *args):
    """Show current covid tips"""
    if args[0] is None:
        day = datetime.date.today()
    else:
        day = datetime.date.fromisoformat(args[0])
    tips = getFullCovidTips(
        day
    )
    tips.sort(key=lambda x: x["number"])

    await msg.reply(
        embed=covidTipsEmbed(tips)
    )


@client.command("evalTips")
async def evalTips_command(msg, *args):
    """Evals the tips. Month in format YYYY-MM"""
    if args == (None,):
        await msg.reply("Dodej měsíc demente.")
        return

    if not re.match(r"\b\d{4}-\d{2}\b", args[0]):
        await msg.reply(f"`{args[0]}` neni měsíc debile!")
    points = evalTips(args[0])
    fields = [
        (f"{i}. place", f"<@{uid}> with {points[uid]} points")
        for i, uid in enumerate(sorted(
            points,
            key=lambda x: points[x],
            reverse=True
        ))
    ]

    await msg.reply(embed=client.embed(
        "Points for tipping",
        fields=fields
    ))


# @client.command("covidNumbers")
# async def covidNumbers_command(msg, *args):
#     """"""
#     covidData = oaAPI.getZakladniPrehled(os.environ["covidDataToken"])
#     testyData = oaAPI.getTestyPcrAntigenni(
#         os.environ["covidDataToken"],
#         date_after=datetime.date.today() - datetime.timedelta(days=2)
#     )
#     await covidDataSend(msg.channel, covidData, testyData)


@client.command("covidTipsDiscord")
async def covidTipsNewData_command(msg, *args):
    """Do not use"""
    if msg.author.id != 452478521755828224:
        await msg.reply("Na tohle nemáš právo.")
        return
    covidData = oaAPI.getZakladniPrehled(os.environ["covidDataToken"])
    reinfekceData = oaAPI.getPrehledReinfekceDate(
        os.environ["covidDataToken"],
        date=datetime.date.today()-datetime.timedelta(days=1)
    )
    await covidDataTipsEval(
        msg.channel,
        covidData[
            "potvrzene_pripady_vcerejsi_den"
        ],
        reinfekceData["60_dnu"],
        twitter=False, discord=True)


@client.command("covidTipsTwitter")
async def covidTipsNewData_command(msg, *args):
    """Do not use"""
    if msg.author.id != 452478521755828224:
        await msg.reply("Na tohle nemáš právo.")
        return
    covidData = oaAPI.getZakladniPrehled(os.environ["covidDataToken"])
    reinfekceData = oaAPI.getPrehledReinfekceDate(
        os.environ["covidDataToken"],
        date=datetime.date.today()-datetime.timedelta(days=1)
    )
    await covidDataTipsEval(
        msg.channel,
        covidData[
            "potvrzene_pripady_vcerejsi_den"
        ],
        reinfekceData["60_dnu"],
        twitter=True, discord=False)


@client.command("evalTwitter")
async def evalTwitter_command(msg, *args):
    """Do not use"""
    if msg.author.id != 452478521755828224:
        await msg.reply("Na tohle nemáš právo.")
        return
    args: str = args[0]
    tweetEvalTips(*args.split(" ", 2))


for command in client.commands:
    client.commands[command].__doc__ = (
        client.commands[command].__doc__.replace(
            "%commandPrefix%", client.commandPrefix))
