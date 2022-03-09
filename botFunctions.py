# import database
import asyncio
import datetime
import io
import json
import os
import pprint
import random
import re
import zlib
from datetime import date, datetime, time, timedelta, timezone

import bdbf
import discord
import numpy as np
import oaAPI
import plotly.graph_objects as go
import requests
import tomd
import tweepy
import wolframalpha
from bdbf.functions import embed
from bs4 import BeautifulSoup
from numpy.lib.twodim_base import eye
from PIL import Image, ImageDraw, ImageFont
from prettytable import ALL, PrettyTable

from variables import *

wClient = wolframalpha.Client("TV7GVY-8YLJ26PPK9")
githubToken = os.environ.get("GithubToken", None)


def mostFrequent(List):
    counter = 0
    num = List[0]

    for i in List:
        if isinstance(List, np.ndarray):
            a, b = np.unique(List, return_counts=True)
            c = dict(zip(a, b))
            return max(c, key=c.get)
        else:
            curr_frequency = List.count(i)
            if(curr_frequency > counter):
                counter = curr_frequency
                num = i

    return num


def count(List):
    out = {}
    for i in List:
        if isinstance(List, np.ndarray):
            a, b = np.unique(List, return_counts=True)
            return dict(zip(a, b))
        out[i] = List.count(i)
    return out


def rotateDict(Dict):
    out = {}
    for i in Dict.keys():
        for j in Dict[i]:
            if j not in out.keys():
                out[j] = []
            out[j].append(i)

    return out


def roundToTheLast30min(time):
    return time - (time - datetime.datetime.min) % timedelta(minutes=30)


def makeGithubIssue(title: str, body: str = None, labels: list = None):
    """Create an issue on github.com using the given parameters"""
    # Url to create issues via POST
    url = 'https://api.github.com/repos/Bertik23/discordbot/issues'

    # Headers
    headers = {
        "Authorization": f"token {githubToken}",
        "Accept": "application/vnd.github.VERSION.html+json"
    }

    # Create our issue
    data = {'title': title,
            'body': body,
            'labels': labels
            }

    payload = json.dumps(data)

    # Add the issue to our repository
    response = requests.request("POST", url, data=payload, headers=headers)
    if response.status_code != 201:
        return (f"Could not create Issue {title} Response: {response.content}",
                None)

    out = [
        eval(
            response.text.replace(
                "false",
                "False").replace(
                "true",
                "True").replace(
                "null",
                "None"))[i] for i in (
                    "url",
                    "title",
            "body_html")]
    return f"Successfully created Issue `{title}`", bdbf.embed(
        out[1],
        out[0].replace("api.", "").replace("/repos/", "/"),
        tomd.convert(out[2]))


def makeSuggestion(title: str, body: str = None):
    title = title
    body = body
    labels = [
        "enhancement",
        "automated"
    ]
    suggestion = makeGithubIssue(title, body, labels)
    return suggestion[0].replace("Issue", "suggestion"), suggestion[1]


def getZmena(parametr):
    zmeny = requests.get("https://bakalari.gymso.eu/next/zmeny.aspx")
    zmeny = BeautifulSoup(zmeny.text, "html.parser")
    tables = zmeny.find_all("table", {"class": "datagrid"})
    for table in tables:
        if table.find("th").text in [
                "Změny v rozvrzích tříd", "Změny v rozvrzích učitelů"]:
            trs = table.find_all("tr")
            # print([t.find_all("td") for t in trs])
            p = False
            for tr1 in trs:
                for i, b in [([u.text for u in t.find_parent()
                                .find_previous_siblings()], t)
                             for t in tr1.find_all("table")]:
                    # print(i)
                    if i[0] == parametr:
                        e = [[d.text for d in c.find_all(
                            "td")] for c in b.find_all("tr")]
                        text = ""
                        for f in e:
                            try:
                                text += (
                                    f"{f[0]}. hod {f[1]} {f[2]}"
                                    f"{f[3]} {f[4]} {f[5]}\n")
                            except BaseException:
                                text += f"{f[0]}\n"
                        return text


def gymso():
    gymso = requests.get("https://www.gymso.cz", timeout=10)
    gymso = BeautifulSoup(gymso.text, features="html.parser")
    clanekDiv = gymso.find("div", attrs={"class": "blog-item"})
    clanekTitle = clanekDiv.find("h2", attrs={"class": "article-title"})
    clanekText = clanekDiv.find("section", attrs={"class": "article-intro"})
    return (clanekTitle.a["title"],
            f"https://gymso.cz{clanekTitle.a['href']}",
            clanekText.text)


def newOnGymso():
    clanky = []
    gymso = requests.get("https://www.gymso.cz", timeout=10)
    gymso = BeautifulSoup(gymso.text, features="html.parser")
    clankyDiv = gymso.findAll("div", attrs={"class": "blog-item"})
    for clanekDiv in clankyDiv:
        clanekTime = datetime.datetime.fromisoformat(
            clanekDiv.find("time")["datetime"])  # .split("+")[0])
        if datetime.datetime.now(timezone(timedelta(hours=2))) - \
                clanekTime < timedelta(minutes=15):
            clanekTitle = clanekDiv.find(
                "h2", attrs={"class": "article-title"})
            clanekText = clanekDiv.find(
                "section", attrs={"class": "article-intro"})
            clanky.append(
                {
                    "title": clanekTitle.a["title"],
                    "url": f"https://gymso.cz{clanekTitle.a['href']}",
                    "time": clanekTime,
                    "text": clanekText.text})
    return clanky


def getJokeTxt():
    return requests.get(
        "https://sv443.net/jokeapi/v2/joke/Any?format=txt").text


def getFact():
    return requests.get(
        "https://uselessfacts.jsph.pl/random.txt?language=en").text


def wolframQuery(query):
    for pod in wClient.query(query):
        for subpod in pod.subpods:
            imgs = list(subpod.img)
            for img in imgs:
                yield bdbf.embed(
                    f"{subpod.title}",
                    image={"url": img.src},
                    fields=())
        # yield bdbf.embed("")


def getTimetableUrl(query: str):
    tableSoup = BeautifulSoup(
        requests.get(
            "https://bakalari.gymso.eu/timetable/public",
            timeout=10).text,
        features="html.parser")
    teachers = tableSoup.find(
        "select", id="selectedTeacher").find_all("option")
    rooms = tableSoup.find("select", id="selectedRoom").find_all("option")
    classes = tableSoup.find("select", id="selectedClass").find_all("option")

    for teacher in teachers:
        if query in teacher.text:
            return "Teacher/" + teacher.get("value")

    for room in rooms:
        if query in room.text:
            return "Room/" + room.get("value")

    for c in classes:
        if query in c.text:
            return "Class/" + c.get("value")

    return None, query


def getTimetable(url: str, room=False, week="now"):
    try:
        if url[0] is None:
            return f"{url[1]} doesn't have a timetable."
    except BaseException:
        pass
    url = "https://bakalari.gymso.eu/Timetable/Public/Actual/" + url
    if week == "next":
        url = url.replace("Actual", "Next")
    elif week == "perm":
        url = url.replace("Actual", "Permanent")
    tableSoup = BeautifulSoup(
        requests.get(
            url,
            timeout=10).text,
        features="html.parser")
    table = []
    days = tableSoup.find_all("div", class_="bk-timetable-row")
    dList = []
    field_names = ["Den", "0.", "1.", "2.",
                   "3.", "4.", "5.", "6.", "7.", "8.", "9."]
    for day in days:
        row = []
        dList.append(day.find(class_="bk-day-day").text +
                     "<br>" + day.find(class_="bk-day-date").text)
        for hour in day.find_all("div", class_="bk-timetable-cell"):
            try:
                row.append("<br>".join(
                    f"<b>{h.text}</b>" for h in hour.find_all(class_="middle")
                        )
                    )
                if room:
                    row[-1] = row[-1].split("<br>")
                    for i, h in enumerate(hour.find_all(class_="first")):
                        row[-1][i] += "<br>" + "<i>" + h.text + "</i>"

                    row[-1] = "<br>".join(row[-1])
            except BaseException:
                row.append("")
        table.append(row)

    table = np.array([np.array(t) for t in table])

    # print(table)

    table = table.transpose()
    # print(table)
    # table = rotateTable(table)
    # print(table)

    table = list(table)

    table.insert(0, dList)

    fig = go.Figure(data=[go.Table(header=dict(values=field_names),
                                   cells=dict(values=table))
                          ])

    lines = [
        sum(map(len, [s.split("<br>") for s in column]))
        for column in table
    ]
    # print(lines)

    fig_bytes = fig.to_image(format="png", width=600,
                             height=max(lines) * 30 + 30 + 100)
    return io.BytesIO(fig_bytes)


def rotateTable(table):
    newTable = []
    for _ in range(max(map(len, table))):
        newTable.append([])
        for _ in range(len(table)):
            newTable[-1].append("")
    for i, row in enumerate(table):
        for ii, s in enumerate(row):
            newTable[ii][i] = s

    return newTable


def getLastInstaPost(user):
    instaResponse = requests.get(
        f"https://www.instagram.com/{user}/?__a=1", timeout=10)
    # print(instaResponse, instaResponse.text)

    instaJson = instaResponse.json()  # json.loads(instaResponse.text)

    # print("test")
    return (instaJson["graphql"]
                     ["user"]
                     ["edge_owner_to_timeline_media"]
                     ["edges"]
                     [0]
                     ["node"])


def encrypt(text_to_encrypt, encryption_base):
    digits = []
    for i in range(48, 48 + encryption_base):
        try:
            digits.append(bytes(chr(i), "utf-8").decode("utf-8"))
        except UnicodeEncodeError:
            pass
    text = zlib.compress(bytes(text_to_encrypt, encoding="utf-8"))
    textInts = [i for i in text]
    textNum = ""
    result = -1
    remainder = -1
    cipher = """"""
    for i in textInts:
        m = str(i)
        for _ in range(3 - len(m)):
            m = f"0{m}"
        textNum = f"{textNum}{m}"

    try:
        result = int(textNum)
    except BaseException:
        result = 0
    while result != 0:
        remainder = result % len(digits)
        result //= len(digits)
        cipher = f"{digits[remainder]}{cipher}"
    return cipher


def decrypt(text_to_decrypt, encryption_base):
    digits = [
        bytes(chr(i), "utf-8").decode("utf-8")
        for i in range(48, 48 + encryption_base)
    ]

    cipher = text_to_decrypt
    num = 0
    power = len(cipher) - 1
    text = ""
    for c in cipher:  # [2:-1]:
        num += (digits.index(c) * (len(digits) ** power))
        power -= 1
    for _ in range(3 - (len(str(num)) % 3) if len(str(num)) % 3 != 0 else 0):
        num = f"0{num}"
    num = str(num)
    n = 3
    nums = [int(num[i:i + n]) for i in range(0, len(num), n)]
    return zlib.decompress(bytes(nums)).decode("utf-8")


def deleteDuplicates(inputList):
    outputList = []
    for i in inputList:
        if i not in outputList:
            outputList.append(i)
    return outputList


def checkMZCR(url):
    ts = requests.get(url)
    tsSoup = BeautifulSoup(ts.text, features="html.parser")
    articles = tsSoup.find_all("article", class_="post")
    articleLinks = [article.find("a") for article in articles]
    return [(article.get("id"),
             articleLinks[i].get("href"),
             articleLinks[i].get("title"),
             article.find("p",
                          class_="summary").text) for i,
            article in enumerate(articles)]


def getCurrencyConversion(fromCurrency, toCurrency):
    rates = requests.get(
        f"https://v6.exchangerate-api.com/\
        v6/1782af866122d90f03c1567c/latest/{fromCurrency}").json()

    if rates["result"] == "error":
        return rates["error-type"]

    return rates["conversion_rates"][toCurrency]


async def spamProtection(message: discord.Message, testForMessages: int):
    lastMessages = []
    count = 0

    async for msg in message.channel.history():
        if msg.author == message.author:
            count += 1
            lastMessages.append(msg.content)
            if count >= testForMessages:
                break

    areMessagesSame = all(
        m == lastMessages[i - 1] for i, m in enumerate(lastMessages)
    )

    if areMessagesSame:
        await message.delete()


def addZero(num):
    if num < 10:
        return "0" + str(num)
    return num


def nextHoursAreAndStartsIn():
    url = getTimetableUrl("7.A")

    now = datetime.datetime.utcnow()
    todayDate = date.today()
    hourDate = date.today()
    today = now.weekday() if now.hour <= 23 else now.weekday() + 1
    now = (now.hour + 2, now.minute)
    actualNow = now

    try:
        tableSoup = BeautifulSoup(
            requests.get(
                "https://bakalari.gymso.eu/Timetable/Public/Actual/" +
                url,
                timeout=10).text,
            features="html.parser")

        hoursList = [i.text for i in tableSoup.find_all("span", class_="from")]
        hoursList = [(int(i.split(":")[0]), int(i.split(":")[1]))
                     for i in hoursList]

        days = tableSoup.find_all("div", class_="bk-timetable-row")
        dList = []
        # field_names =
        # ["Den","0.","1.","2.","3.","4.","5.","6.","7.","8.","9."]
        day = days[today]
        row = []
        groups = []
        rooms = []
        dList.append(day.find(class_="bk-day-day").text +
                     "<br>" + day.find(class_="bk-day-date").text)
        for hour in day.find_all("div", class_="bk-timetable-cell"):
            row.append([h.text for h in hour.find_all(class_="middle")])
            groups.append([h.text.replace("\n", "") for h in hour.find_all(
                class_="left") if h.text.replace("\n", "") != ""])
            rooms.append(
                [
                    h.text.replace("\n", "") for h in hour.find_all(
                        class_="first"
                    ) if h.text.replace("\n", "") != ""]
            )
        # print(groups)

        # print(row)

        modifiedHoursList = [
            h for i, h in enumerate(hoursList) if row[i] != []]

        if modifiedHoursList[-1] < now:
            def addDay(today, hourDate):
                today += 1
                hourDate = hourDate + timedelta(days=1)
                now = (0, 0)

                tableSoup = BeautifulSoup(
                    requests.get(
                        "https://bakalari.gymso.eu/Timetable/Public/Actual/" +
                        url,
                        timeout=10).text,
                    features="html.parser")

                hoursList = [i.text for i in tableSoup.find_all(
                    "span", class_="from")]
                hoursList = [(int(i.split(":")[0]), int(i.split(":")[1]))
                             for i in hoursList]

                days = tableSoup.find_all("div", class_="bk-timetable-row")
                dList = []
                # field_names =
                # ["Den","0.","1.","2.","3.","4.","5.","6.","7.","8.","9."]
                day = days[today]
                row = []
                groups = []
                rooms = []
                dList.append(day.find(class_="bk-day-day").text +
                             "<br>" + day.find(class_="bk-day-date").text)
                for hour in day.find_all("div", class_="bk-timetable-cell"):
                    row.append(
                        [h.text for h in hour.find_all(class_="middle")])
                    groups.append(
                        [h.text.replace("\n", "") for h in hour.find_all(
                            class_="left") if h.text.replace("\n", "") != ""])
                    rooms.append(
                        [
                            h.text.replace("\n", "") for h in hour.find_all(
                                class_="first"
                            ) if h.text.replace("\n", "") != ""]
                    )
                return today, hourDate, now, row, groups, rooms
            today, hourDate, now, row, groups, rooms = addDay(today, hourDate)
            while len(row) <= 0 or row == [[]]:
                today, hourDate, now, row, groups, rooms = addDay(
                    today, hourDate
                )
    except BaseException:
        hourDate = hourDate.replace(day=hourDate.day + 7 - today)
        now = (0, 0)
        today = 0
        tableSoup = BeautifulSoup(
            requests.get(
                "https://bakalari.gymso.eu/Timetable/Public/Next/" +
                url,
                timeout=10).text,
            features="html.parser")

        hoursList = [i.text for i in tableSoup.find_all("span", class_="from")]
        hoursList = [(int(i.split(":")[0]), int(i.split(":")[1]))
                     for i in hoursList]

        days = tableSoup.find_all("div", class_="bk-timetable-row")
        dList = []
        # field_names =
        # ["Den","0.","1.","2.","3.","4.","5.","6.","7.","8.","9."]
        # print("One")
        day = days[today]
        row = []
        groups = []
        rooms = []
        dList.append(day.find(class_="bk-day-day").text +
                     "<br>" + day.find(class_="bk-day-date").text)
        for hour in day.find_all("div", class_="bk-timetable-cell"):
            row.append([h.text for h in hour.find_all(class_="middle")])
            groups.append([h.text.replace("\n", "") for h in hour.find_all(
                class_="left") if h.text.replace("\n", "") != ""])
            rooms.append(
                [
                    h.text.replace("\n", "") for h in hour.find_all(
                        class_="first"
                    ) if h.text.replace("\n", "") != ""]
            )

    modifiedHoursList = [h for i, h in enumerate(hoursList) if row[i] != []]
    modifiedGroups = [h for i, h in enumerate(groups) if row[i] != []]
    modifiedRow = [h for h in row if h != []]
    modifiedRooms = [h for i, h in enumerate(rooms) if row[i] != []]

    for i, item in enumerate(modifiedGroups):
        if item == []:
            modifiedGroups[i] = [""]

    # print(modifiedGroups)
    nextHour = [("", "")]
    nextHourTime = (0, 0)
    for i, (t, h, r) in enumerate(zip(
        modifiedHoursList, modifiedRow, modifiedRooms
    )):
        if t > now:
            if len(r) == 0:
                r = ["" for i in h]
            nextHour = zip(h, modifiedGroups[i], r)
            nextHourTime = t
            break
    for h, g, r in nextHour:
        yield (
            datetime.datetime.combine(
                hourDate, time(nextHourTime[0], nextHourTime[1])
            ) - datetime.datetime.combine(todayDate, time(
                    actualNow[0], actualNow[1]
                    )
                ),
            h, g if g != "" else None, r
        )


def isDatetimeIsoFormat(string):
    try:
        datetime.datetime.fromisoformat(string)
        return True
    except ValueError:
        return False


def isTimeIsoFormat(string):
    try:
        time.fromisoformat(string)
        return True
    except ValueError:
        return False


def isStrNumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# def makeAdventniCalendarImage(text, textXY, padding, dayXY):
#     roboto = ImageFont.truetype("fonts/MinecraftRegular.ttf", 30)

#     todayCalendar = Image.open(
#         "adventniKalendarMCT/aKemptyLatest.png").convert("RGBA")
#     fullCalendar = Image.open(
#                   "adventniKalendarMCT/aKfull.png").convert("RGBA")

#     fullCalendar = fullCalendar.crop(dayXY)

#     todayCalendar.paste(fullCalendar, dayXY)

#     draw = ImageDraw.Draw(todayCalendar)

#     width, height = draw.textsize(text, font=roboto)

#     print(width)
#     print(height)

#     padding = (((textXY[2] - padding[0] / 2) - (textXY[0] +
#                padding[0] / 2)) / 2 - width / 2, padding[1])

#     # draw.line((77+padding, 265-height, 77+padding+width, 265), fill=(0,0,0)
# )

#     draw.text((textXY[0] + padding[0], textXY[1]),
#               text, font=roboto, fill=(0, 0, 0))

#     todayCalendar.save("adventniKalendarMCT/aKemptyLatest.png")

#     with open("adventniKalendarMCT/aKemptyLatest.png", "rb") as f:
#         return io.BytesIO(f.read())


# def adventniKalendar(day):
#     with open("adventniKalendarMCT/okynka.json") as f:
#         days = eval(f.read())
#     role = client.get_guild(621413546177069081).get_role(777201923270246440)
#     never = database.advantniKalendar.col_values(1)[1:]
#     once = database.advantniKalendar.col_values(3)[1:]
#     twice = database.advantniKalendar.col_values(5)[1:]
#     thrice = database.advantniKalendar.col_values(7)[1:]
#     fourTimes = database.advantniKalendar.col_values(9)[1:]
#     gotten = 0
#     aligable = [m for m in role.members if str(
#         m.id) not in never and str(m.id) not in once]
#     if len(aligable) == 0:
#         gotten = 1
#         aligable = [m for m in role.members if str(
#             m.id) not in never and str(m.id) not in twice]
#     if len(aligable) == 0:
#         gotten = 2
#         aligable = [m for m in role.members if str(
#             m.id) not in never and str(m.id) not in thrice]
#     if len(aligable) == 0:
#         gotten = 3
#         aligable = [m for m in role.members if str(
#             m.id) not in never and str(m.id) not in fourTimes]
#     if len(aligable) == 0:
#         gotten = -1
#         aligable = [m for m in role.members if str(m.id) not in never]
#     member = random.choice(aligable)
#     if gotten != -1:
#         database.advantniKalendar.update_cell(len(
#           [once, twice, thrice, fourTimes]
# [gotten]) + 2, [3, 5, 7, 9][gotten],
#           str(member.id))
#         database.advantniKalendar.update_cell(len(
#           [once, twice, thrice, fourTimes]
# [gotten]) + 2, [4, 6, 8, 10][gotten],
#           str(member.name))

#     print(days[day])

#     return member, makeAdventniCalendarImage(
#         member.name, days[day][1], (8, 5), days[day][0])


# makeAdventniCalendarImage("test",(77,250,265,264), (8,5), (67,62,267,266))
# makeAdventniCalendarImage("test2",(306,250,502,264), (8,5), (306,63,504,266))

def getCKS():
    r = requests.get("http://projekty.gymso.cz/cks/")
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, from_encoding="utf-8", features="html.parser")
    script = soup.find("script")
    script = script.string
    script = script.split("const tridy")[1]
    script = script.replace(" ", "").replace("\n", "")[2:-2]
    script = script.split("newTrida")
    tridy = {}
    for i in script:
        if i == "":
            continue
        a = eval(i)
        if len(a) == 1:
            a = a[0]
        tridy[a[0]] = a[2]
    # print(max(tridy))
    return tridy


async def waitUntil(time):
    toWait = (time - datetime.datetime.now()).total_seconds()
    print(f"Waiting until {time} for {toWait} seconds")
    await asyncio.sleep(toWait)


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def covidDataEmbed(
    client: bdbf.Client,
    today,
    reinfectionsToday,
    lastDay,
    active,
    positivity,
    positivityBefore,
    testsToday,
    testsLastDay
):
    return client.embed(
        "Covid Data",
        fields=[
            ("Včera", "{:,}".format(today).replace(",", " ")),
            ("Z toho reinfekce", "{:,}".format(
                reinfectionsToday
            ).replace(",", " ")),
            ("Předevčírem", "{:,}".format(lastDay).replace(",", " ")),
            ("Aktivní", "{:,}".format(active).replace(",", " ")),
            ("Pozitivita", "{:.2%}".format(positivity)),
            ("Pozitivita předevčírem", "{:.2%}".format(positivityBefore)),
            ("Včera testů", f"{testsToday:,}".replace(",", " ")),
            ("Předevčírem testů", f"{testsLastDay:,}".replace(",", " ")),
        ]
    )


async def covidDataSend(
    channel: discord.TextChannel,
    covidData=None,
    testyData=None,
    reinfekceData=None,
):
    if covidData is None:
        # covidData = requests.get(
        #     "https://onemocneni-aktualne.mzcr.cz/api/v2/"
        #     "covid-19/zakladni-prehled.json"
        # ).json()
        covidData = oaAPI.getZakladniPrehled(os.environ["covidDataToken"])
    if testyData is None:
        # testyData = requests.get(
        #     "https://onemocneni-aktualne.mzcr.cz/api/v2/"
        #     "covid-19/testy-pcr-antigenni.min.json"
        # ).json()
        testyData = oaAPI.getTestyPcrAntigenni(
            os.environ["covidDataToken"],
            date_after=datetime.date.today() - datetime.timedelta(days=2)
        )
    if reinfekceData is None:
        reinfekceData = oaAPI.getPrehledReinfekceDate(
            os.environ["covidDataToken"],
            date=datetime.date.today()-datetime.timedelta(days=1)
        )

    await channel.send(
        embed=covidDataEmbed(
            client,
            covidData["potvrzene_pripady_vcerejsi_den"]
            + reinfekceData["60_dnu"],
            reinfekceData["60_dnu"],
            testyData[-2]["incidence_pozitivni"],
            covidData["aktivni_pripady"],
            (
                (covidData[
                    "potvrzene_pripady_vcerejsi_den"
                ] + reinfekceData["60_dnu"])
                /
                (
                    covidData[
                        "provedene_testy_vcerejsi_den"
                    ]
                    + covidData[
                        "provedene_antigenni_testy_vcerejsi_den"
                    ]
                )
            ),
            (
                testyData[-2][
                    "incidence_pozitivni"
                ]
                /
                (
                    testyData[-2][
                        "pocet_PCR_testy"
                    ]
                    + testyData[-2][
                        "pocet_AG_testy"
                    ]
                )
            ),
            (
                (
                    covidData[
                        "provedene_testy_vcerejsi_den"
                    ]
                    + covidData[
                        "provedene_antigenni_testy_vcerejsi_den"
                    ]
                )
            ),
            (
                (
                    testyData[-2][
                        "pocet_PCR_testy"
                    ]
                    + testyData[-2][
                        "pocet_AG_testy"
                    ]
                )
            )
        )
    )


async def covidDataTipsEval(
    channel,
    number,
    reinfections,
    twitter=True,
    discord=True
):
    from database import getCovidTipsDate
    sortedTips = sorted(
        getFullCovidTips(),
        key=lambda x: abs(x["number"] - number)
    )

    sortedDiscordTips = sorted(
        getCovidTipsDate(
            datetime.date.today() - datetime.timedelta(days=1)
        ),
        key=lambda x: abs(x["number"] - number)
    )

    if discord:
        await channel.send(
            embed=client.embed(
                "Tabulka tipů",
                description=f"{number}",
                fields=[
                    (
                        "Top 3 tips.",
                        "\n".join((
                            f"{p}. " + i["username"] + " "
                            + (
                                str(i["number"]) +
                                f" ({pm(i['number']-number)}"
                                f"{i['number']-number})"
                            )
                        ) for p, i in enumerate(sortedTips[:3]))
                        if len(sortedTips)
                        else
                        "No tips? WTF",
                        True
                    ),
                    (
                        "Discord tips.",
                        "\n".join((
                            f"{p}. ({sortedTips.index(i)}.) {i['username']} "
                            + (
                                str(i["number"]) +
                                f" ({pm(i['number']-number)}"
                                f"{i['number']-number})"
                            )
                        ) for p, i in enumerate(sortedDiscordTips))
                        if len(sortedDiscordTips)
                        else
                        "No discord tips yesterday 😢",
                        True
                    ),
                    (
                        "Celkem tipů:",
                        f"{len(sortedTips)}",
                        True
                    )
                ]
            )
        )
    if twitter:
        tweetCovidNumberAndWiner(
            number,
            reinfections,
            sortedTips[0]["username"] if len(sortedTips) else None,
            sortedTips[0]["number"] if len(sortedTips) else None,
            sortedTips[1:] if len(sortedTips) else None
        )


def getTwitterClient():
    return tweepy.Client(
        os.environ["bearerToken"],
        os.environ["consumerKey"],
        os.environ["consumerSecret"],
        os.environ["covidTipsToken"],
        os.environ["covidTipsSecret"]
    )


def tweetCovidNumberAndWiner(
    yesterday,
    reinfections,
    tipsWinner,
    tip,
    moreTips
):
    clientTW = getTwitterClient()

    winnerText = (
        f"Nejblíže byl {tipsWinner} - {nf(tip)} "
        f"({pm(tip-yesterday)} {nf(tip-yesterday)}).\n"
        "Gratuluji.\n"
    ) if tipsWinner is not None else ""

    tweetId = clientTW.create_tweet(
        text=(
            f"Včera přibylo {yesterday:,} nakažených covidem-19.\n".replace(
                ",", " "
            )
            +
            f"Z toho {reinfections:,} reinfekcí.\n\n".replace(",", " ")
            +
            winnerText
        )
    ).data["id"]

    clientTW.create_tweet(
        in_reply_to_tweet_id=tweetId,
        text=(
            "Tipy na dnešní den tweetujte jako odpověď na tento tweet "
            "nebo na jakýkoli jiný tweet, případně stačí označit @CovidTipsBot"
            "(např. 12 456), "
            "pokud bude tweet obsahovat písmena, nebude se počítat."
        )
    )

    if tipsWinner is None:
        return
    # print(moreTips)
    tweetListSize = 5
    moreTipsList = splitListSize(moreTips, tweetListSize)
    print(moreTipsList, moreTips)
    if moreTips:
        for t, tips in enumerate(moreTipsList):
            textMoreTips = "".join(
                f"{t*tweetListSize+i+2}. "
                f"{tip['username']} - {nf(tip['number'])} "
                f"({pm(tip['number']-yesterday)} "
                f"{nf(tip['number']-yesterday)})\n"
                for i, tip in enumerate(tips)
            )

            tweetId = clientTW.create_tweet(
                in_reply_to_tweet_id=tweetId,
                text=(
                    "Další v pořadí:\n"
                    f"{textMoreTips}"
                )
            ).data["id"]


def getTwitterTips(day=None, start=None, end=None):
    clientTW = getTwitterClient()

    if day is None and start is None and end is None:
        _start = datetime.datetime.combine(
            datetime.date.today() - datetime.timedelta(1),
            datetime.time(0, 0, 1)
        ).isoformat()+"Z"
        _end = datetime.datetime.combine(
            datetime.date.today(),
            datetime.time(0, 0, 1)
        ).isoformat()+"Z"
    elif start is None and end is None:
        _start = datetime.datetime.combine(
            day,
            datetime.time(0, 0, 1)
        ).isoformat()+"Z"
        _end = datetime.datetime.combine(
            day + datetime.timedelta(1),
            datetime.time(0, 0, 1)
        ).isoformat()+"Z"
    elif start is not None and end is not None:
        # print("THIS")
        _start = start
        _end = end

    next_token = None
    while True:
        if next_token is None:
            response: tweepy.Response = clientTW.get_users_mentions(
                1460632004509241349,
                end_time=_end,
                start_time=_start,
                user_fields=["username"],
                expansions=["author_id"],
                tweet_fields=["created_at"],
                max_results=100
            )
        else:
            response: tweepy.Response = clientTW.get_users_mentions(
                1460632004509241349,
                end_time=_end,
                start_time=_start,
                user_fields=["username"],
                expansions=["author_id"],
                tweet_fields=["created_at"],
                max_results=100,
                pagination_token=next_token
            )
        # print(response.data, response.includes)
        if response.data is not None:
            for tweet, user in zip(response.data, response.includes["users"]):
                try:
                    tweetText = str(tweet)
                    mentions = re.findall(r"@\w+", tweetText)
                    # print(mentions)
                    for mention in mentions:
                        tweetText = tweetText.replace(mention, "")
                    # print(tweetText)
                    tweetText = tweetText.replace(" ", "")
                    # print(tweetText)
                    if not tweetText.isnumeric():
                        continue
                    # num = "".join(re.findall(r'\b(\d| \d+)\b', str(tweet)))
                    # print(num)
                    # num = int(num.replace(" ", ""))
                    num = int(tweetText)
                    # num = int(
                    #     str(tweet).lower().replace(
                    #         "@covidtipsbot", ""
                    #     ).replace(" ", "")
                    # )
                    if (
                        day is not None
                        or
                        (
                            day is None
                            and
                            start is None
                            and
                            end is None
                        )
                    ):
                        yield {"number": num, "username": f"@{user}"}
                    else:
                        yield {
                            "date": tweet.created_at,
                            "number": num,
                            "username": f"@{user}"
                        }
                except ValueError:
                    continue
        if (
            response.meta["result_count"] == 0
            or
            "next_token" not in response.meta.keys()
        ):
            break
        # print(response.meta)
        next_token = response.meta["next_token"]


def getFullCovidTips(day=None):
    from database import getCovidTipsDate
    if day is None:
        day = datetime.date.today() - datetime.timedelta(days=1)
    tips = list(getCovidTipsDate(day))

    tips.extend(getTwitterTips(day))
    return tips


def pm(number):
    if number >= 0:
        return "+"
    else:
        return ""


def nf(number):
    return f"{number:,}".replace(",", " ")


def splitListSize(array, chunkSize):
    return [array[i:i + chunkSize] for i in range(0, len(array), chunkSize)]


def evalTips(month):
    from database import getCovidTips
    tips = [
        i for i in getCovidTips() if i["date"].isoformat().startswith(month)
    ]
    filteredTips = []
    filtered = set()
    for tip in tips:
        if ((tip["date"].date(), tip["userID"]) not in filtered):
            filteredTips.append(tip)
            filtered.add((tip["date"].date(), tip["userID"]))

    dateTips: dict[str, list] = {}
    for tip in filteredTips:
        dateTips.setdefault(
            tip["date"].date().isoformat(),
            []
        ).append(tip)

    dateNumbers = {
        i["datum"]: i["incidence_pozitivni"]
        for i in oaAPI.getTestyPcrAntigenni(
            os.environ["covidDataToken"],
            date_before=f"{month}-31",
            date_after=f"{month}-01"
        )
    }

    for key, value in dateTips.items():
        if key in dateNumbers:
            value.sort(key=lambda x: abs(x["number"] - dateNumbers[key]))
        else:
            value = []

    sumsOfPlaces = {}
    for tips in dateTips.values():
        for i, tip in enumerate(tips):
            sumsOfPlaces.setdefault(tip["userID"], 0)
            sumsOfPlaces[tip["userID"]] += len(tips) - i

    return sumsOfPlaces


def evalTwitterTips(start: datetime.datetime, end: datetime.datetime):
    tips = getTwitterTips(start=start.isoformat()+"Z", end=end.isoformat()+"Z")
    # print(tips)
    filteredTips = []
    filtered = set()
    for tip in tips:
        # print(tip)
        if ((tip["date"].date(), tip["username"]) not in filtered):
            filteredTips.append(tip)
            filtered.add((tip["date"].date(), tip["username"]))

    dateTips: dict[str, list] = {}
    for tip in filteredTips:
        dateTips.setdefault(
            tip["date"].date().isoformat(),
            []
        ).append(tip)

    dateNumbers = {
        i["datum"]: i["incidence_pozitivni"]
        for i in oaAPI.getTestyPcrAntigenni(
            os.environ["covidDataToken"],
            date_before=end.date().isoformat(),
            date_after=start.date().isoformat()
        )
    }

    for key, value in dateTips.items():
        if key in dateNumbers:
            value.sort(key=lambda x: abs(x["number"] - dateNumbers[key]))
        else:
            value = []

    sumsOfPlaces = {}
    for tips in dateTips.values():
        for i, tip in enumerate(tips):
            sumsOfPlaces.setdefault(tip["username"], 0)
            sumsOfPlaces[tip["username"]] += len(tips) - i

    return sumsOfPlaces


def tweetEvalTips(start, end, message):
    _start = datetime.datetime.combine(
        datetime.date.fromisoformat(start),
        datetime.time(0, 0, 1)
    )
    _end = datetime.datetime.combine(
        datetime.date.fromisoformat(end),
        datetime.time(23, 59, 59)
    )
    points = evalTwitterTips(
        _start, _end
    )

    sortedPeople = sorted(points, key=lambda x: points[x], reverse=True)

    clientTW = getTwitterClient()

    tweetId = clientTW.create_tweet(
        text=(
            message
            +
            "\n"
            +
            f"{sortedPeople[0]} s {nf(points[sortedPeople[0]])} body.\n"
            "Gratuluji."
        )
    ).data["id"]

    # print(moreTips)
    tweetListSize = 5
    morePointsList = splitListSize(sortedPeople, tweetListSize)
    for p, morePoints in enumerate(morePointsList):
        textMorePoints = "".join(
            f"{p*tweetListSize+i+2}. "
            f"{person} s {nf(points[person])} body\n"
            for i, person in enumerate(morePoints)
        )

        tweetId = clientTW.create_tweet(
            in_reply_to_tweet_id=tweetId,
            text=(
                "Další v pořadí:\n"
                f"{textMorePoints}"
            )
        ).data["id"]


def xorSum(arr):
    ans = 0
    for i in arr:
        ans ^= i
    return ans


def strTable(arr, cols, dir=1):
    colLen = max(map(len, arr))

    out = ""
    if dir == 1:
        for i, a in enumerate(arr):
            out += ("{:>"+f'{colLen+1}'+"}").format(a)
            print(i, i+1, cols, (i+1) % cols)
            if (i+1) % cols == 0:
                out += "\n"
    print(out)
    return "```"+out+"```"


def covidTipsEmbed(tips):
    return client.embed(
            "Aktuální tipy",
            # thumbnail=dict(
            #     url="https://pbs.twimg.com/profile_images/1461008360350924803/RltBFbNk_400x400.jpg"
            # ),
            fields=[(
                f"Pozice {ci*10} až {ci*10 + len(chunk)}",
                "\n".join(
                    f'**{i["username"]}** - {i["number"]}'
                    for i in chunk
                ),
                True
            ) for ci, chunk in enumerate(splitListSize(tips, 10))
            ]
        )
