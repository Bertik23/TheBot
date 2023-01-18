import asyncio
import datetime
import json
import math
import re
import subprocess
import traceback
from asyncio.tasks import wait
from random import choice, randint
from string import Template
import sys

import discord
import iepy
import ksoftapi
import requests
import stopit
from bdbf import __version__, embed, hasLink  # , spamProtection
from dotenv import load_dotenv

import commands
import database
import variables
from botFunctions import (checkMZCR, covidDataSend, covidDataTipsEval,
                          getTwitterTips, newOnGymso, nextHoursAreAndStartsIn,
                          now, tweetCovidNumberAndWiner, waitUntil)
import oaAPI
from variables import *

from pprint import pprint

load_dotenv()

# try:
#     print(tweetCovidNumberAndWiner(
#         123456,
#         "@Bertik23",
#         1234576,
#         [
#             {"username": "@CovidTipsBot", "number": 1},
#             {"username": "@CeskyIE", "number": 3}
#         ]
#     ))
#     for tweet, user in getTwitterTips():
#         print(tweet, user)
#         # print(dir(tweet))
#         # pprint(dict(zip(dir(tweet),
#         # map(lambda x: getattr(tweet, x, "Nic"), dir(tweet)))))
# except Exception as e:
#     print(e)
#     # print(dir(e))
#     # print(e.api_codes, e.api_errors, e.api_messages, e.args, e.response)
#     # print(dir(e.response))
#     # print(e.response.text, e.response.content)
#     raise

print(
    f"BDBF vesion: {bdbf.__version__}\n"
    f"Discord.py version: {discord.__version__}\n"
    f"IEpy version: {iepy.__version__}\n"
    f"KSoftApi version: {ksoftapi.__version__}"
)


@client.logMessage
def log(message):
    if "guild" in dir(message.channel):
        msgLog = [
            message.created_at.isoformat(),
            str(message.id), message.content,
            str(message.author.id),
            message.author.name,
            str(message.channel.id),
            str(message.channel),
            str(message.channel.guild.id),
            message.channel.guild.name
        ]
    else:
        msgLog = [
            message.created_at.isoformat(),
            str(message.id),
            message.content,
            str(message.author.id),
            message.author.name,
            str(message.channel.id),
            str(message.channel)
        ]
    with open(f"msgToLog/{message.id}.txt", "w", encoding="utf-8") as f:
        f.write(str(msgLog))


@client.logCommand
def logC(command, msg, time, e):
    Clog = [
        msg.created_at.isoformat(),
        command, str(msg.author.id),
        msg.author.name,
        str(msg.channel.id),
        str(msg.channel),
        str(msg.channel.guild.id) if "guild" in dir(msg.channel) else "",
        str(msg.channel.guild) if "guild" in dir(msg.channel) else "",
        msg.content,
        "Succeded" if e == "" else "Failed",
        e,
        time
    ]
    # database.commandLog.append_row(Clog)
    with open(f"cmdToLog/{msg.id}.txt", "w", encoding="utf-8") as f:
        f.write(str(Clog))


@client.event  # event decorator/wrapper
async def on_ready():
    global klubik, obecne, choco_afroAnouncements, korona_info, botspam
    global hodinyUpozorneni
    print(f"We have logged in as {client.user}")
    klubik = await client.fetch_guild(697015129199607839)
    obecne = await client.fetch_channel(697015129199607843)
    botspam = await client.fetch_channel(804091646609850390)
    hodinyUpozorneni = await client.fetch_channel(849243732145995796)
    choco_afroAnouncements = await client.fetch_channel(756497789424369737)
    korona_info = await client.fetch_channel(758381540534255626)
    print(klubik, obecne, choco_afroAnouncements, korona_info)
    variables.botReadyTimes.append(datetime.datetime.utcnow())

    client.loop.create_task(covidNumbers())

    if heroku:
        await botspam.send("<@452478521755828224> Jsem online!")
        if len(botReadyTimes) <= 1:
            client.loop.create_task(ieAddLoop())
            client.loop.create_task(ieTweetLoop())
            client.loop.create_task(checkWebsites())
            client.loop.create_task(classLoop())
            client.loop.create_task(bDayLoop())
            if tuple(
                    int(i) for i in database.dataLog.cell(2, 3)
                    .value.split(".")
            ) < version:
                await obecne.send(
                    "Nová verze!",
                    embed=client.embed(
                        "Changelog",
                        fields=[
                            (
                                i,
                                changelog[i]
                            ) for i in list(changelog.keys())[:5]
                        ]
                    )
                )

            for t in database.timers.get_all_values()[1:]:
                if t[0] == "":
                    continue
                userTimers[int(t[1])] = commands.TimerObject(t[0])
                await userTimers[int(t[1])].timer(
                    datetime.datetime.fromisoformat(t[3]),
                    await (await client.fetch_channel(
                        int(t[6]))).fetch_message(int(t[5])),
                    t[4]
                )
    if client.logging:
        loggingProcess = subprocess.Popen([sys.executable, "sheetsLoging.py"])
        print(loggingProcess)


@client.event
async def on_message(message):
    global klubik, obecne
    print(
        f"{message.channel} ({message.channel.id}): {message.author}: "
        f"{message.author.name}: {message.content}"
    )
    if message.channel.id == 905841944507322428:
        return {"log": False}

    if (message.author.bot and message.author.id != 788873442664906752 and
            message.channel.id in (790630915448504390, 790630932292829214)):
        await message.delete()

    try:
        if (message.channel.guild.id == 793152939022745610 and
                not message.author.bot):
            for i in ["bob", "bohouš"]:
                if i in message.content.lower():
                    await message.channel.send("Bohouš smrdí")

        if (message.channel.id not in (790630915448504390, 790630932292829214)
            and
                message.channel.guild.id in (
                    697015129199607839,
                    540563312857841714
                    # 1028368345898172517
        )):
            for i in [
                    "hi", "dobrý den", "brý den",
                    "čau", "ahoj", "zdravíčko",
                    "tě péro", "těpéro", "zdárek párek",
                    "tě guli", "čus", "olá",
                    "ola", "guten tag"
            ]:
                if (re.search(f"(\\W|^){i}(\\W|$)", message.content, re.I) and
                        not message.author.bot):
                    await message.channel.send(
                        f"Hello {message.author.mention}"
                    )
                    break

            if ("kdy" in message.content.lower()
                    and "aktualizace" in message.content.lower()):
                await message.channel.send("Kdo ví")

            # if ((re.search("(\\W|^)a+da+m(\\W|$)", message.content, re.I))
            #         and not message.author.bot):
            #     await message.channel.send(
            #         "A"+randint(0, 20)*'a'+"d"+randint(1, 20)*'a'+"m "
            #         + choice([
            #             'je gay', 'neumí olí', 'už nevytírá anály',
            #             'is trajin to solf da rubix kjub',
            #             'was trajin to olín', ''])
            #     )

            # if ((re.search("(\\W|^)ji+ří+(\\W|$)", message.content, re.I)
            #         ) and
            #         not message.author.bot):
            #     await message.channel.send("Jiří "+choice([
            #                 'je buzík',
            #                 'nic neumí',
            #                 'is FUCKING NORMIEEE REEEEEEEEEEEEEEEEEEEEEE']))

            if "fortnite" in message.content.lower():
                await message.delete()

            if ((re.search("thebot", message.content, re.I) or
                    client.user.mentioned_in(message)) and
                    not message.author.bot):
                with open("hlasky.json", encoding="utf-8") as f:
                    hlasky = json.load(f)["onMention"]
                    await message.reply(
                        Template(
                            choice(hlasky)
                        ).substitute(
                            author=message.author.mention
                        )
                    )

            if message.tts and not message.author.bot:
                await message.channel.send(
                    f"Hej ty {message.author.mention}, žádný ttska tady.",
                    tts=True)

            if message.channel.id == 715621624950292593 and not hasLink(
                message.content
            ):
                await message.delete()

            if "No lyrics found for `" in message.content:
                try:
                    results = await commands.kclient.music.lyrics(
                        message.content.split("`")[1])
                except ksoftapi.NoResults:
                    await message.channel.send(
                        "No lyrics found for `"
                        + message.content.split('`')[1]
                        + "`.")
                else:
                    lyrics = results[0]
                    for i in range(math.ceil(len(lyrics.lyrics)/2048)):
                        e = embed(
                            f"Lyrics for {lyrics.artist} - {lyrics.name}",
                            description=lyrics.lyrics[(
                                i*2048):((i+1)*2048)],
                            thumbnail={"url": lyrics.album_art})
                        await message.channel.send(embed=e)
                await message.delete()
    except AttributeError:
        pass

    if (
        type(message.channel) == discord.DMChannel
        and message.author.id == 452478521755828224
    ):
        try:
            msgTextSplit = message.content.split(" ", 1)
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
    # print(emoji)

    if message.id == 746719599982280754:
        emoji = payload.emoji
        member = payload.member

        # 1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣
        if emoji.name == "1️⃣":
            # Minecraft
            await member.add_roles(discord.Object(746396397280034946))
            print(member.name
                  + " in "
                  + guild
                  + " got role Minecraft for pressing "
                  + emoji)
        if emoji.name == "2️⃣":
            await member.add_roles(discord.Object(746396668198649856))  # CS:GO
            print(member.name
                  + " in "
                  + guild
                  + " got role CS:GO for pressing "
                  + emoji)
        if emoji.name == "3️⃣":
            # Rocket League
            await member.add_roles(discord.Object(746712499705086013))
            print(member.name
                  + " in "
                  + guild
                  + " got role Rocket League for pressing "
                  + emoji)
        if emoji.name == "4️⃣":
            # Fortnite
            await member.add_roles(discord.Object(746396772179378197))
            print(member.name
                  + " in "
                  + guild
                  + " got role Fortnite for pressing "
                  + emoji)
        if emoji.name == "5️⃣":
            # Mobile Gaming
            await member.add_roles(discord.Object(746704088070357012))
            print(member.name
                  + " in "
                  + guild
                  + " got role Mobile Gaming for pressing "
                  + emoji)
        if emoji.name == "6️⃣":
            # PS4 Gamers
            await member.add_roles(discord.Object(746709189040275456))
            print(member.name
                  + " in "
                  + guild
                  + " got role PS4 Gamers for pressing "
                  + emoji)


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
        # Gymso
        # try:
        #    print("Checking for new posts on Gymso")
        #    with stopit.ThreadingTimeout(10) as to_ctx_mgr:
        #        assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
        #
        #        clanky = newOnGymso()
        #        if clanky:
        #            for clanek in clanky:
        #                for i in range(math.ceil(len(clanek["text"])/2048)):
        #                    e = embed(clanek["title"],
        #                              url=clanek["url"],
        #                              description=clanek["text"][(
        #                                i*2048):((i+1)*2048)])
        #                    await obecne.send(
        #                        f"{klubik.default_role} nový příspěvek na "
        #                        "Gymso",
        #                        embed=e
        #                    )
        # except Exception as e:
        #    print(e)

        # choco_afro
        # try:
        # 	with stopit.ThreadingTimeout(10) as to_ctx_mgr:
        # 		assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING

        # 		print("Checking for new post on choco_afro")
        # 		lastChocoPost = getLastInstaPost("choco_afro")
        # 		if time.time() - lastChocoPost["taken_at_timestamp"] <= 7000:
        # 			await choco_afroAnouncements.send(lastChocoPost["display_url"])
        # except Exception as e:
        # 	print(e)

        # MZCR TS
        try:
            tss = checkMZCR(
                "https://koronavirus.mzcr.cz/category/tiskove-zpravy/")
            for ts in tss:
                if ts[0] != database.dataLog.cell(2, 1).value:
                    await korona_info.send(embed=embed(ts[2],
                                                       url=ts[1],
                                                       description=ts[3]))
                else:
                    break
            database.dataLog.update_cell(2, 1, tss[0][0])

        except Exception as e:
            print(e)

        # MZCR MO
        try:
            tss = checkMZCR(
                "https://koronavirus.mzcr.cz/category/mimoradna-opatreni/")
            for ts in tss:
                if ts[0] != database.dataLog.cell(2, 2).value:
                    await korona_info.send(embed=embed(ts[2],
                                                       url=ts[1],
                                                       description=ts[3]))
                else:
                    break
            database.dataLog.update_cell(2, 2, tss[0][0])
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
                print(f"We are in {hour}")
                waitTime = hour[0].total_seconds()
                try:
                    if False:
                        if hour[2] is None:
                            role = [
                                r for r in klubik.roles if r.name == hour[1]
                            ]
                        else:
                            role = [
                                r for r in klubik.roles if r.name == hour[2]
                            ]
                    else:
                        if hour[2] is None:
                            role = [Dummy(mention=f"`{hour[1]}`")]
                        else:
                            role = role = [Dummy(mention=f"`{hour[2]}`")]
                    message = "".join((
                        f"Za {str(hour[0])[:-3]} začíná ",
                        f"{role[0].mention}" if hour[2] is None
                        else f"`{hour[1]}`",
                        f" pro {role[0].mention}" if hour[2] is not None
                        else "",
                        f" v `{hour[3]}`" if hour[3] != "" else ""
                        )
                    )
                except Exception as e:
                    traceback.print_exc()
                    message = ""
                if message != "":
                    await hodinyUpozorneni.send(message)
            # print(waitTime)
            sleeping = 10
            await asyncio.sleep(max(waitTime-300, 240))
        except Exception as e:
            sleeping = min(sleeping+30, 6000)
            await asyncio.sleep(sleeping)
            print(f"Encountered an error while checking for hours: {e}")


async def bDayLoop():
    while True:
        print("BDay check loop start")
        if datetime.date.today() > database.lastCheckedBDay():
            print("Waiting until 9:00 today")
            await asyncio.sleep(max(0, (
                datetime.datetime.utcnow().replace(hour=7, minute=0)
                - datetime.datetime.now()
            ).total_seconds()))
            for bDay in database.getTodayBDays():
                for g, ch in zip(bDay["GuildIDs"], bDay["ChannelIDs"]):
                    channel = await client.fetch_channel(ch)
                    await channel.send(
                        f"Jej! Dnes slaví své "
                        f"""{int(
                            (
                                datetime.date.today() - bDay['Birthdate']
                            ).total_seconds() // (24*60*60*365))
                        }."""
                        f" narozeniny {bDay['UserMention']}."
                    )
            for bDay in database.getTodayBDays(
                today=datetime.date.today()+datetime.timedelta(days=1)
            ):
                for g, ch in zip(bDay["GuildIDs"], bDay["ChannelIDs"]):
                    channel = await client.fetch_channel(ch)
                    await channel.send(
                        f"Zítra oslaví své "
                        f"""{int(
                            (
                                datetime.date.today() - bDay['Birthdate']
                            ).total_seconds() // (24*60*60*365))
                        }."""
                        f" narozeniny {bDay['UserMention']}."
                    )
            database.updateLastCheckedBDay()
        else:
            print("Waiting until tomorow.")
            await asyncio.sleep(max(0, (
                datetime.datetime.utcnow().replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
                - datetime.datetime.now()
            ).total_seconds()))


async def ieAddLoop():
    try:
        lastTweetTime = database.getIEDataTimes()[1]
    except IndexError:
        lastTweetTime = datetime.datetime.fromordinal(1)
    while True:
        events = iepy.getTodayEvents()
        for i, event in enumerate(events):
            eventsToday = len(events)+1
            for eventLang in event:
                if eventLang.language == "cz":
                    tweetTime = (datetime.datetime.fromisoformat(
                            datetime.date.today().isoformat()
                        )
                        + datetime.timedelta(hours=10)
                        + datetime.timedelta(hours=8)*(i+1)/eventsToday)
                    if tweetTime <= lastTweetTime:
                        continue
                    database.addIEData(
                        tweetTime,
                        eventLang.description if (
                            eventLang.description != ""
                        ) else eventLang.summary,
                        i
                    )
        await asyncio.sleep(
            (datetime.datetime.fromisoformat(
                (
                    datetime.date.today() + datetime.timedelta(days=1)
                ).isoformat()
            ) - datetime.datetime.now()).total_seconds()
        )


async def ieTweetLoop():
    while True:
        try:
            nextTime = database.getIEDataTimes()[1]
            await waitUntil(nextTime)
            event = iepy.getTodayEvents()[
                database.getIEDataT(nextTime)["eventIndex"]
            ]
            for eventLang in event:
                if eventLang.language == "cz":
                    iepy.tweetEvent(
                        eventLang,
                        os.environ["consumerKey"],
                        os.environ["consumerSecret"],
                        os.environ["accessToken"],
                        os.environ["accessTokenSecret"]
                    )
            database.deleteIEData(nextTime)
        except IndexError:
            await asyncio.sleep(10)
        except iepy.tweepy.TweepError as e:
            if e.api_code == 187:
                database.deleteIEData(nextTime)
            else:
                raise


async def covidNumbers():
    while True:
        try:
            if datetime.date.today() != datetime.date.fromisoformat(
                database.getLastCovidTime()
            ):
                covidData: dict = oaAPI.getZakladniPrehled(
                    os.environ["covidDataToken"]
                )
                testyData = oaAPI.getTestyPcrAntigenni(
                    os.environ["covidDataToken"],
                    date_after=datetime.date.today()
                    - datetime.timedelta(days=8)
                )
                reinfekceData = oaAPI.getPrehledReinfekceDate(
                    os.environ["covidDataToken"],
                    date=datetime.date.today()-datetime.timedelta(days=1)
                )
                hospitalizaceData = oaAPI.getHospilatizace(
                    os.environ["covidDataToken"],
                    date_after=datetime.date.today()
                    - datetime.timedelta(days=8)
                )
                # print(len(testyData), len(hospitalizaceData))
                # pprint(testyData)
                # pprint(hospitalizaceData)
                if (
                    "title" not in covidData
                    and
                    "title" not in reinfekceData
                    and
                    len(testyData) >= 8
                    and
                    len(hospitalizaceData) >= 8
                ):
                    await covidDataSend(
                        obecne,
                        covidData,
                        testyData,
                        reinfekceData,
                        hospitalizaceData,
                        twitter=True,
                        discordSend=False
                    )
                    await covidDataTipsEval(
                        obecne,
                        covidData[
                            "potvrzene_pripady_vcerejsi_den"
                        ] + reinfekceData["60_dnu"],
                        reinfekceData["60_dnu"]
                    )
                    database.setLastCovidTime(
                        datetime.date.today().isoformat()
                    )
        except Exception as e:
            print(e)
        await asyncio.sleep(60*15)


client.run(token)
