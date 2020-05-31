import requests
from bs4 import BeautifulSoup
import discord
import bdbf

commandPrefix: str = None

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

def gymso():
    gymso = requests.get("https://www.gymso.cz")
    gymso = BeautifulSoup(gymso.text, features="html.parser")
    clanekDiv = gymso.find("div",attrs={"class":"blog-item"})
    clanekTitle = clanekDiv.find("h2", attrs={"class":"article-title"})
    clanekText = clanekDiv.find("section", attrs={"class":"article-intro"})
    return clanekTitle.a["title"], f"https://gymso.cz{clanekTitle.a['href']}", clanekText.text
