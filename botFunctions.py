import requests
from bs4 import BeautifulSoup
import discord
import bdbf
from datetime import datetime, timedelta, timezone
import wolframalpha
import pprint
import os
import json
import tomd

commandPrefix: str = None
wClient = wolframalpha.Client("TV7GVY-8YLJ26PPK9")
githubToken = os.environ.get("GithubToken", None)

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

def gymso() -> (str, str, str):
    gymso = requests.get("https://www.gymso.cz")
    gymso = BeautifulSoup(gymso.text, features="html.parser")
    clanekDiv = gymso.find("div",attrs={"class":"blog-item"})
    clanekTitle = clanekDiv.find("h2", attrs={"class":"article-title"})
    clanekText = clanekDiv.find("section", attrs={"class":"article-intro"})
    return clanekTitle.a["title"], f"https://gymso.cz{clanekTitle.a['href']}", clanekText.text

def newOnGymso() -> [dict]:
    clanky = []
    gymso = requests.get("https://www.gymso.cz")
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

print(wolframQuery("adam"))