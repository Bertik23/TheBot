import datetime
import math
import os
import random
import asyncio

import bdbf
import gspread
import ksoftapi
import pkg_resources
import plotly.express as px
import plotly.graph_objects as go
import praw
import prawcore
from bdbf import *
from oauth2client.service_account import ServiceAccountCredentials

import botFunctions
import smaz
from botFunctions import *
from botGames import Game2048
from database import commandLog, messageLog
import uhlovod
from exceptions import *

logging = True


class Command(bdbf.commands.Command):
    async def command(self, args, msg):
        try:
            log = [datetime.utcnow().isoformat(), str(self), str(msg.author.id), msg.author.name, str(msg.channel.id), str(msg.channel), str(msg.channel.guild.id), str(msg.channel.guild), msg.content]
            try:
                c = await self.commandos(args, msg)
            except Exception as e:
                log.append("Failed")
                log.append(str(e))
                c = str(e), None
                print(e)
            else:
                log.append("Succeded")

            if logging:
                commandLog.append_row(log)
            return c
        except Exception as e:
            print(e)
            return f"{e} is the error", None
    async def commandos(self, args, msg):
        pass

reddit = None
kclient = None

bdbf.commands.cmds[697015129199607839] = []

class test(Command):
    async def commandos(self, args, msg):
        r = [datetime.datetime.utcnow().isoformat() ,"test","testoo"]
        try:
            commandLog.append_row(r)
        except Exception as e:
            print(e)
            return r, None

#bdbf.commands.cmds["all"].append(test("TheBot info"))

class info(Command):
    async def commandos(self, args, msg):
        return f"I'm a bot made by Bertik23#9997\nI'm running on bdbf {pkg_resources.get_distribution('bdbf').version} and discord.py {pkg_resources.get_distribution('discord.py').version}"+"\nI'm and open source bot, that means that you can contribute to me on https://github.com/Bertik23/DiscordBot", None

bdbf.commands.cmds["all"].append(info("TheBot info"))




class zmena(Command):
    async def commandos(self,args, msg):
        return f"Změny rozvrhu pro {args}:\n{getZmena(args)}",None

bdbf.commands.cmds[697015129199607839].append(zmena("Returns schedule changes for the give teacher/class today","`%commandPrefix%zmena <teacher/class>` eg. `%commandPrefix%zmena Lukešová Danuše` or `%commandPrefix%zmena 6.A`"))

class rozvrh(Command):
    async def commandos(self, args, msg):
        room = None
        try:
            arguments = args.rsplit(" ",1)
            if arguments[-1] == "-t":
                room = True
        except:
            arguments = [args]
            room=False
        
        async with msg.channel.typing():
            await msg.channel.send(file = discord.File(getTimetable(getTimetableUrl(arguments[0]), room=room), filename="rozvrh.png"))

bdbf.commands.cmds[697015129199607839].append(rozvrh("Returns the timatable for given teacher/class/room","`%commandPrefix%rozvrh <teacher/class/room>` eg. `%commandPrefix%rozvrh Lukešová Danuše` or `%commandPrefix%rozvrh 7.A` or `%commandPrefix%rozvrh A307"))

class suggest(Command):
    async def commandos(self,attributes, msg):
        out = makeSuggestion(attributes.split("*||*")[0], attributes.split("*||*")[1] +
            f"""
***
Automaticaly issued by `{msg.author}` from `{msg.channel}` in `{msg.channel.guild}`
            """)
        return out[0], out[1]

bdbf.commands.cmds["all"].append(suggest("Suggest a command to the creator of the bot","`%commandPrefix%suggest <title> *||* <text>`"))

class r(Command):
    async def commandos(self,attributes, msg):
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

class gymso(Command):
    async def commandos(self,attributes, msg):
        clanek = gymso()
        e = embed(clanek[0], url=clanek[1], description=clanek[2][:2048])
        return None, e

bdbf.commands.cmds[697015129199607839].append(gymso("Returns last post on [gymso.cz](https://gymso.cz)"))

class lyrics(Command):
    async def commandos(self,attributes, msg):
        try:
            results = await kclient.music.lyrics(attributes)
        except ksoftapi.NoResults:
            return f"No lyrics found for `{attributes}`.", None
        else:
            lyrics = results[0]
            for i in range(math.ceil(len(lyrics.lyrics)/2048)):
                e = embed(f"Lyrics for {lyrics.artist} - {lyrics.name} from KSoft.Si API", description=lyrics.lyrics[(i*2048):((i+1)*2048)], thumbnail={"url": lyrics.album_art})
                return None, e

bdbf.commands.cmds["all"].append(lyrics("Returns lyrics to given song","`%commandPrefix%lyrics <song>`"))

class meme(Command):
    async def commandos(self,attributes, msg):
        meme = await kclient.images.random_meme()
        e = embed(f"{meme.title}", url=meme.source, author={"name":meme.author,"url":f"https://reddit.com/user/{meme.author[3:]}"}, image={"url":meme.image_url})
        return None, e

bdbf.commands.cmds["all"].append(meme("Returns random meme from [Reddit](https://reddit.com)"))

class evaluate(Command):
    async def commandos(self,attributes, msg):
        try: 
            return eval(attributes), None
        except Exception as e:
            print(e)
            return f"Hej `{attributes}` fakt neudělám", None

bdbf.commands.cmds["all"].append(evaluate("Returns python expresion outcome.","`%commandPrefix%eval <python expresion>` eg. `%commandPrefix%eval math.cos(math.pi)`"))

class aww(Command):
    async def commandos(self,attributes, msg):
        aww = await kclient.images.random_aww()
        e = embed(f"{aww.title}", url=aww.source, author={"name":aww.author,"url":f"https://reddit.com/user/{aww.author[3:]}"}, image={"url":aww.image_url})
        return None, e

bdbf.commands.cmds["all"].append(aww("Returns random aww image from [Reddit](https://reddit.com)"))

class subreddit(Command):
    async def commandos(self,attributes, msg):
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

class mapa(Command):
    async def commandos(self,attributes, msg):
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

class joke(Command):
    async def commandos(self,attributes, msg):
        return getJokeTxt(), None

bdbf.commands.cmds["all"].append(joke("Returns a random awful joke."))

class fact(Command):
    async def commandos(self,attributes, msg):
        return getFact(), None

bdbf.commands.cmds["all"].append(fact("Returns a random fact."))

class wa(Command):
    async def commandos(self,attributes, msg):
        for e in wolframQuery(attributes):
            yield None, e

bdbf.commands.cmds["all"].append(wa())

class encrypt(Command):
    async def commandos(self, attributes, msg):
        text_to_encrypt = attributes.rsplit(" ", 1)[0]
        try:
            encryption_base = int(attributes.rsplit(" ", 1)[1])
        except ValueError as e:
            return f"The last word must be a encryption base\n{e}", None

        return None, embed("Your encrypted text", description=f"```{botFunctions.encrypt(text_to_encrypt, encryption_base)}```")

bdbf.commands.cmds["all"].append(encrypt("Encrypt a text", "`%commandPrefix%encrypt <text> <encryptionBase>` eg. `%commandPrefix%encrypt Hello, how are you? 64`"))

class decrypt(Command):
    async def commandos(self, attributes, msg):
        text_to_decrypt = attributes.rsplit(" ", 1)[0]
        try:
            encryption_base = int(attributes.rsplit(" ", 1)[1])
        except ValueError as e:
            return f"The last word must be a encryption base\n{e}", None

        return None, embed("Your decrypted text", description=f"```{botFunctions.decrypt(text_to_decrypt, encryption_base)}```")

bdbf.commands.cmds["all"].append(decrypt("Decrypt a text encrypted using encrypt", "`%commandPrefix%decrypt <encryptedTest> <encryptionBase>` eg. `%commandPrefix%decrypt ^eQO3gN39aYO[>1LabKh=\_ 64`"))


class stats(Command):
    async def commandos(self, args, msg):
        async with msg.channel.typing():
            if args == "commands":
                commandCountTotaly = len(commandLog.col_values(1))-1
                commandsList = commandLog.col_values(2)[1:]
                commandCountGuild = len([g for g in commandLog.col_values(7) if g == str(msg.channel.guild.id)])
                commandCountChannel = len([g for g in commandLog.col_values(5) if g == str(msg.channel.id)])
                mostActiveCommandor = mostFrequent(commandLog.col_values(4))
                mostUsedCommand = mostFrequent(commandsList)

                commandTimes = commandLog.col_values(1)[1:]

                commandTimes = commandLog.col_values(1)[1:]

                commandTimeUsage = {}
                for i, t in enumerate(commandTimes):
                    if t[:10] not in commandTimeUsage.keys():
                        commandTimeUsage[t[:10]] = []
                    commandTimeUsage[t[:10]].append(commandsList[i])

                for key in commandTimeUsage.keys():
                    commandTimeUsage[key] = count(commandTimeUsage[key])

                # print(commandTimeUsage)

                commandCounts = count(commandsList)

                commandTimes = [time.isoformat() for time in map(roundToTheLast30min,map(datetime.fromisoformat, commandTimes))]
                commandTimesUno = deleteDuplicates(commandTimes)
                commandTimeCounts = [commandTimes.count(t) for t in commandTimesUno]

                #print(commandTimes)

                #fig = go.Figure()

                fig = px.bar(x = commandTimesUno, y = commandTimeCounts)

                fig.update_yaxes(type = "log", range=[0, math.log(max(commandTimeCounts),10)+0.2])

                fig_bytes = fig.to_image(format="png", width=1800, height=800)

                await msg.channel.send(file=discord.File(io.BytesIO(fig_bytes), filename="stats.png"))

                x=[f"{t}T00:00:00.000000" for t in commandTimeUsage.keys()]
                fig = go.Figure()

                # print(rotateDict(commandTimeUsage))

                cmds = {}

                for c in commandsList:
                    cmds[c] = []
                    for t in commandTimeUsage.keys():
                        try:
                            cmds[c].append(commandTimeUsage[t][c])
                        except KeyError:
                            cmds[c].append(0)

                #print(cmds)

                for c in cmds.keys():
                    fig.add_trace(go.Scatter(
                        x=x, y=cmds[c],
                        mode='lines',
                        line=dict(width=2, color=f"rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})", shape= 'spline', smoothing= 0.5),
                        name=c))

                fig.update_layout(
                    showlegend=True)

                fig.update_yaxes(type = "log", range=[0, math.log(max(commandCounts.values()),10)+0.2])

                fig_bytes = fig.to_image(format="png", width=1800, height=800)

                await msg.channel.send(file=discord.File(io.BytesIO(fig_bytes), filename="stats.png"))

                fig = go.Figure(data=[go.Pie(labels=list(commandCounts.keys()), values=list(commandCounts.values()), textinfo="value+percent")])

                fig_bytes = fig.to_image(format="png", width=1200, height=1200)

                await msg.channel.send(file=discord.File(io.BytesIO(fig_bytes), filename="stats.png"))

                return None, embed("TheBot stats", fields=[{"name": "Total Commands",
                                                            "value": commandCountTotaly,
                                                            "inline": True},
                                                            {"name": "Guild Commands",
                                                            "value": commandCountGuild,
                                                            "inline": True},
                                                            {"name": "Channel Commands",
                                                            "value": commandCountChannel,
                                                            "inline": True},
                                                            {"name": "Most Commands",
                                                            "value": mostActiveCommandor,
                                                            "inline": True},
                                                            {"name": "Most Used Command",
                                                            "value": mostUsedCommand,
                                                            "inline": True}])
            elif args == "messages":
                guildMessages = len([g for g in messageLog.col_values(8) if g == str(msg.channel.guild.id)])
                channelMessages = len([g for g in messageLog.col_values(6) if g == str(msg.channel.id)])
                mostActive = mostFrequent(messageLog.col_values(5))

                messageTimes = messageLog.col_values(1)[1:]

                messageGuilds = messageLog.col_values(8)[1:]

                messageTimes = [time.isoformat() for i,time in enumerate(map(roundToTheLast30min,map(datetime.fromisoformat, messageTimes))) if messageGuilds[i] == str(msg.channel.guild.id)]
                print(len(messageTimes))
                messageTimesUno = deleteDuplicates(messageTimes)
                messageTimeCounts = [messageTimes.count(t) for t in messageTimesUno]

                fig = px.bar(x = messageTimesUno, y = messageTimeCounts, range_x=[messageTimesUno[0], messageTimesUno[-1]])

                fig_bytes = fig.to_image(format="png", width=1800, height=800)

                await msg.channel.send(file=discord.File(io.BytesIO(fig_bytes), filename="stats.png"))

                return None, embed("TheBot stats", fields=[
                                                {"name": "Guild Messages",
                                                "value": guildMessages,
                                                "inline": True},
                                                {"name": "Channel Messages",
                                                "value": channelMessages,
                                                "inline": True},
                                                {"name": "Most Messages",
                                                "value": mostActive,
                                                "inline": True}])
            else:
                return None, embed("Available stats categories", fields=[
                                                                        {"name":"commands",
                                                                         "value":"Command stats"
                                                                        },
                                                                        {"name":"messages",
                                                                         "value":"Message stats"
                                                                        }])

bdbf.commands.cmds["all"].append(stats())

class rates(Command):
    async def commandos(self, args, msg):
        currencies = args.split(" ")
        rate = getCurrencyConversion(currencies[0], currencies[1])
        if type(rate) == str:
            return rate, None
        else:
            return f"{currencies[2]} {currencies[0]} is {float(currencies[2])*rate} {currencies[1]}", None

bdbf.commands.cmds["all"].append(rates("Converts currencies", "`%commandPrefix%rates <from> <to> <count>` eg. `%commandPrefix%rates EUR CZK 120`"))



class play(Command):
    async def commandos(self, args, msg):
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

class game(Command):
    def __init__(self, description=None, usage=None):
        super().__init__(description=description, usage=usage)
        self.activeGame = {}
    async def commandos(self, args, msg):
        try:
            return self.activeGame[msg.author].play(args, msg)
        except Exception as e:
            print(e)

bdbf.commands.cmds["all"].append(game())

#507484929001652224 BladeX
bdbf.commands.cmds[507484929001652224] = []

class support(Command):
    async def commandos(self, args, msg):
        if 562713869957726208 not in [r.id for r in msg.author.roles]:
            await msg.author.add_roles(discord.Object(562713869957726208))
            if msg.author.dm_channel == None:
                await msg.author.create_dm()
            await msg.author.send("You now have the tag Needs Support, which means you can access the Support Text and Voice Channels. Ask for any support you may need. We ask that you please remain patient, the Support Team has been notified and we will be with you as soon as possible. Thank you.\n\nNyní máš tag Needs Support, který ti dává přístup k textovým a hlasovým kanálům podpory. Obrať se na podporu s jakýmkoli dotazem. Prosím buď trpělivý, tým podpory byl informován a bude se ti věnovat co nejdříve. Děkujem.")
        else:
            if msg.author.dm_channel == None:
                await msg.author.create_dm()
            await msg.author.send("You already have the Needs Support tag, please be patient.\n\nUž máš tag Needs Support. Prosíme, abys byl trpělivý")

bdbf.commands.cmds[507484929001652224].append(support("Gives you the Needs Support role"))

class uhel(Command):
    async def commandos(self, args, msg):
        await msg.channel.send(file= discord.File(uhlovod.make_img(args), filename="uhlovodik.png"))

bdbf.commands.cmds["all"].append(uhel())

class timer(Command):
    def __init__(self,a=None,b=None):
        super().__init__(a,b)
        self.userTimers = {}
    async def commandos(self, args, msg):
        channel = msg.channel

        if "-Q" in args:
            try:
                await self.userTimers[msg.author].sendMsg(True)
                return
            except:
                return

        try:
            if self.userTimers[msg.author].t > 0 and "-F" not in args:
                await channel.send(f"{msg.author.mention} you already have an active timer. If you wish to overwrite it add -F to your command")
                return None
            elif self.userTimers[msg.author] and "-F" in args:
                await channel.send(f"{msg.author.mention} you have overwritten your old timer. This action is not reversible.")
                args = args.replace("-F", "")

        except:
            pass

        sendMsgs = False
        if "-M" in args:
            sendMsgs = True
            args = args.replace("-M", "")

        if "-t" not in args:
            t = int(args)
        else:
            args = args.split("-t")
            t = (datetime.fromisoformat(args[1].rstrip().lstrip()) - datetime.utcnow()).total_seconds()

        self.userTimers[msg.author] = TimerObject()
        await self.userTimers[msg.author].timer(t, msg, sendMsgs)


class TimerObject():
    def __init__(self):
        self.t = -10
        self.timerMsg = None
        self.channel = None
        self.author = None
    async def timer(self, t, msg, sendMsgs = False):
        self.author = msg.author
        self.start = datetime.utcnow()
        self.end = datetime.utcnow()+timedelta(seconds=t)
        self.channel = msg.channel
        self.t = t

        await self.sender()

        await self.channel.send(f"{msg.author.mention} Timer completed!", tts=True)
        self.t = -10
        self.channel = None
    def getTime(self):
        return (self.end-datetime.utcnow()).total_seconds()

    async def sender(self):
        while True:
            try:
                await self.sendMsg()
                await asyncio.sleep(1)
            except GetOutOfLoop:
                break

    async def sendMsg(self, newMessage = False):
        # print(self.getTime())
        if self.getTime() >= 0:
            minutes, seconds = divmod(self.getTime(), 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
        else:
            days, hours, minutes, seconds = 0,0,0,0

        def addZero(x):
            if x < 10:
                return "0" + str(x)
            return x
            
        if self.timerMsg == None or newMessage:
            self.timerMsg = await self.channel.send(f"{self.author.mention} {addZero(int(days))}:{addZero(int(hours))}:{addZero(int(minutes))}:{addZero(int(round(seconds,0)))} left.")  
        else:
            await self.timerMsg.edit(content=f"{self.author.mention} {addZero(int(days))}:{addZero(int(hours))}:{addZero(int(minutes))}:{addZero(int(round(seconds,0)))} left.")
        if (days, hours, minutes, seconds) == (0,0,0,0):
            raise GetOutOfLoop


bdbf.commands.cmds["all"].append(timer("Timer command.","`%commandPrefix%timer <seconds>` or `%commandPrefix%timer -t <ISO utc time>` eg. `%commandPrefix%timer 60` or `%commandPrefix%timer -t 2020-12-31T23:59:59`\nTo display countdown messages add `-M`\nTo get current time remaining use `%commandPrefix%timer -Q`"))
