import datetime
import io
import json
import os
import pprint
import zlib
from datetime import date, datetime, timedelta, timezone, time

import bdbf
import discord
import numpy as np
import plotly.graph_objects as go
import requests
import tomd
import wolframalpha
from bs4 import BeautifulSoup
from prettytable import ALL, PrettyTable
import typing

import smaz

commandPrefix: str = None
wClient = wolframalpha.Client("TV7GVY-8YLJ26PPK9")
githubToken = os.environ.get("GithubToken", None)

def mostFrequent(List): 
    counter = 0
    num = List[0] 
      
    for i in List: 
        curr_frequency = List.count(i) 
        if(curr_frequency> counter): 
            counter = curr_frequency 
            num = i 
  
    return num 

def count(List):
    out = {}
    for i in List:
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
    rounded = time - (time - datetime.min) % timedelta(minutes=30)
    return rounded

def makeGithubIssue(title: str, body: str=None, labels: list=None):
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
    if response.status_code == 201:
        out= [eval(response.text.replace("false","False").replace("true","True").replace("null","None"))[i] for i in ("url", "title","body_html")]
        return f"Successfully created Issue `{title}`" , bdbf.embed(out[1], out[0].replace("api.","").replace("/repos/","/"), tomd.convert(out[2]))
    else:
        return f"Could not create Issue {title} Response: {response.content}", None

def makeSuggestion(title : str, body: str=None):
    title = title
    body = body
    labels = [
        "enhancement",
        "automated"
    ]
    suggestion = makeGithubIssue(title, body, labels)
    return suggestion[0].replace("Issue","suggestion"), suggestion[1]


def getZmena(parametr) -> str:
    zmeny = requests.get("https://bakalari.gymso.eu/next/zmeny.aspx")
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

def gymso() -> typing.Tuple[str, str, str]:
    gymso = requests.get("https://www.gymso.cz", timeout=10)
    gymso = BeautifulSoup(gymso.text, features="html.parser")
    clanekDiv = gymso.find("div",attrs={"class":"blog-item"})
    clanekTitle = clanekDiv.find("h2", attrs={"class":"article-title"})
    clanekText = clanekDiv.find("section", attrs={"class":"article-intro"})
    return clanekTitle.a["title"], f"https://gymso.cz{clanekTitle.a['href']}", clanekText.text

def newOnGymso() -> typing.List[dict]:
    clanky = []
    gymso = requests.get("https://www.gymso.cz", timeout=10)
    gymso = BeautifulSoup(gymso.text, features="html.parser")
    clankyDiv = gymso.findAll("div",attrs={"class":"blog-item"})
    for clanekDiv in clankyDiv:
        clanekTime = datetime.fromisoformat(clanekDiv.find("time")["datetime"])#.split("+")[0])
        if datetime.now(timezone(timedelta(hours=2))) - clanekTime < timedelta(minutes=15):
            clanekTitle = clanekDiv.find("h2", attrs={"class":"article-title"})
            clanekText = clanekDiv.find("section", attrs={"class":"article-intro"})
            clanky.append({"title": clanekTitle.a["title"], "url": f"https://gymso.cz{clanekTitle.a['href']}", "time": clanekTime, "text": clanekText.text})
    return clanky

def getJokeTxt() -> str:
    return requests.get("https://sv443.net/jokeapi/v2/joke/Any?format=txt").text

def getFact() -> str:
    return requests.get("https://uselessfacts.jsph.pl/random.txt?language=en").text

def wolframQuery(query):
    for pod in wClient.query(query):
        for subpod in pod.subpods:
            imgs = list(subpod.img)
            for img in imgs:
                yield bdbf.embed(f"{subpod.title}", image={"url": img.src})
        #yield bdbf.embed("")

def getTimetableUrl(query: str) -> str:
    tableSoup = BeautifulSoup(requests.get("https://bakalari.gymso.eu/timetable/public", timeout=10).text, features="html.parser")
    teachers = tableSoup.find("select", id="selectedTeacher").find_all("option")
    rooms = tableSoup.find("select", id="selectedRoom").find_all("option")
    classes = tableSoup.find("select", id="selectedClass").find_all("option")

    for teacher in teachers:
        if query in teacher.text:
            return "Teacher/"+teacher.get("value")

    for room in rooms:
        if query in room.text:
            return "Room/"+room.get("value")

    for c in classes:
        if query in c.text:
            return "Class/"+c.get("value")

    return None, query

def getTimetable(url: str, room=False):
    try:
        if url[0] == None:
            return f"{url[1]} doesn't have a timetable."
    except:
        pass
    tableSoup = BeautifulSoup(requests.get("https://bakalari.gymso.eu/Timetable/Public/Actual/"+url, timeout=10).text,features="html.parser")
    table = []
    days = tableSoup.find_all("div",class_="bk-timetable-row")
    dList = []
    field_names = ["Den","0.","1.","2.","3.","4.","5.","6.","7.","8.","9."]
    for day in days:
        row = []
        dList.append(day.find(class_="bk-day-day").text+"<br>"+day.find(class_="bk-day-date").text)
        for hour in day.find_all("div",class_="bk-timetable-cell"):
            try:
                row.append("<br>".join(f"<b>{h.text}</b>" for h in hour.find_all(class_="middle")))
                if room:
                    row[-1] = row[-1].split("<br>")
                    for i,h in enumerate(hour.find_all(class_="first")):
                        row[-1][i] += "<br>"+"<i>"+h.text+"</i>"

                    row[-1] = "<br>".join(row[-1])
            except:
                row.append("")
        table.append(row)

    table = np.array([np.array(t) for t in table])

    print(table)

    table = table.transpose()
    print(table)
    #table = rotateTable(table)
    #print(table)

    table = list(table)

    table.insert(0,dList)

    fig = go.Figure(data=[go.Table(header=dict(values=field_names),
                 cells=dict(values=table))
                     ])

    lines = []
    for column in table:
        lines.append(sum(map(len,[s.split("<br>") for s in column])))

    #print(lines)

    fig_bytes = fig.to_image(format="png", width=600, height=max(lines)*30+30+100)
    return io.BytesIO(fig_bytes)

def rotateTable(table):
    newTable = []
    for i in range(max(map(len,table))):
        newTable.append([])
        for i in range(len(table)):
            newTable[-1].append("")
    for i, row in enumerate(table):
        for ii, s in enumerate(row):
            newTable[ii][i] = s

    return newTable

def getLastInstaPost(user):
    instaResponse = requests.get(f"https://www.instagram.com/{user}/?__a=1", timeout=10)
    #print(instaResponse, instaResponse.text)
    
    instaJson = instaResponse.json()#json.loads(instaResponse.text)

    print("test")
    return instaJson["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]



def encrypt(text_to_encrypt, encryption_base):
    digits = []
    for i in range(48,48 + encryption_base):
        try:
            digits.append(bytes(chr(i),"utf-8").decode("utf-8"))
        except UnicodeEncodeError:
            pass
    text = smaz.compress(str(text_to_encrypt))
    if text == b"":
        text = zlib.compress(bytes(text_to_encrypt, encoding="utf-8"))
    textInts = [i for i in text]
    textNum = ""
    result = -1
    remainder = -1
    cipher = """"""
    for i in textInts:
        m = str(i)
        for _ in range(3-len(m)):
            m = f"0{m}"
        textNum = f"{textNum}{m}"

    try:
        result = int(textNum)
    except:
        result = 0
    while result != 0:
        remainder = result % len(digits)
        result = result // len(digits)
        cipher = f"{digits[remainder]}{cipher}"
    return cipher


def decrypt(text_to_decrypt, encryption_base):
    digits = []
    for i in range(48,48 + encryption_base):
        digits.append(bytes(chr(i),"utf-8").decode("utf-8"))
    cipher = text_to_decrypt
    num = 0
    power = len(cipher)-1
    text = ""
    for c in cipher:#[2:-1]:
        num += (digits.index(c) * (len(digits) ** power))
        power -= 1
    for i in range(3-(len(str(num))%3) if len(str(num))%3 != 0 else 0):
        num = f"0{num}"
    num = str(num)
    n = 3
    nums = [int(num[i:i+n]) for i in range(0, len(num), n)]
    try:
        texto = smaz.decompress(bytes(nums))
    except:
        texto = zlib.decompress(bytes(nums)).decode("utf-8")
    return texto

def deleteDuplicates(l):
    l2 = []
    for i in l:
        if i not in l2:
            l2.append(i)
    return l2

def checkMZCR(url):
    ts = requests.get(url)
    tsSoup = BeautifulSoup(ts.text, features="html.parser")
    articles = tsSoup.find_all("article", class_="post")
    articleLinks = [article.find("a") for article in articles]
    return [(article.get("id"), articleLinks[i].get("href"), articleLinks[i].get("title"), article.find("p", class_="summary").text) for i,article in enumerate(articles)]

def getCurrencyConversion(fromCurrency, toCurrency):
    rates = requests.get(f"https://v6.exchangerate-api.com/v6/1782af866122d90f03c1567c/latest/{fromCurrency}").json()

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
    
    areMessagesSame = True
    for i, m in enumerate(lastMessages):
        if m != lastMessages[i-1]:
            areMessagesSame = False

    if areMessagesSame:
        await message.delete()

def addZero(num):
    if num < 10:
        return "0"+str(num)
    return num

def nextHoursAreAndStartsIn():
    url = getTimetableUrl("7.A")

    now = datetime.utcnow()
    todayDate = date.today()
    hourDate = date.today()
    today = now.weekday() if now.hour <= 23 else now.weekday()+1
    now = (now.hour+1, now.minute)
    actualNow = now

    tableSoup = BeautifulSoup(requests.get("https://bakalari.gymso.eu/Timetable/Public/Actual/"+url, timeout=10).text,features="html.parser")

    hoursList = [i.text for i in tableSoup.find_all("span",class_="from")]
    hoursList = [(int(i.split(":")[0]),int(i.split(":")[1])) for i in hoursList]
    if hoursList[-1] < now:
        today += 1
        hourDate = hourDate.replace(day=hourDate.day+1)
        now = (0,0)

    days = tableSoup.find_all("div",class_="bk-timetable-row")
    dList = []
    # field_names = ["Den","0.","1.","2.","3.","4.","5.","6.","7.","8.","9."]
    day = days[today]
    row = []
    groups = []
    dList.append(day.find(class_="bk-day-day").text+"<br>"+day.find(class_="bk-day-date").text)
    for hour in day.find_all("div",class_="bk-timetable-cell"):
        row.append([h.text for h in hour.find_all(class_="middle")])
        groups.append([h.text.replace("\n","") for h in hour.find_all(class_="left") if h.text.replace("\n","") != ""])
    #print(groups)

    #print(row)

    modifiedHoursList = [h for i,h in enumerate(hoursList) if row[i] != []]
    modifiedGroups = [h for i,h in enumerate(groups) if row[i] != []]
    modifiedRow = [h for h in row if h != []]
    
    for i, item in enumerate(modifiedGroups):
        if item == []:
            modifiedGroups[i] = [""]

    #print(modifiedGroups)
    nextHour = [("","")]
    nextHourTime = (0,0)
    for i, (t, h) in enumerate(zip(modifiedHoursList, modifiedRow)):
        if t > now:
            #print(h, modifiedGroups[i])
            nextHour = zip(h, modifiedGroups[i])
            nextHourTime = t
            break

    for h, g in nextHour:
        yield datetime.combine(hourDate, time(nextHourTime[0], nextHourTime[1]))-datetime.combine(todayDate, time(actualNow[0], actualNow[1])), h, g if g != "" else None



