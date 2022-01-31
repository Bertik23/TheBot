from botFunctions import decrypt
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime
import re

# print(vars(botFunctions))


class Dummy:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

with open("thebotdbCredentials-encrypted.nottxt", "rb") as f:
    with open("thebotdb-creds-decrypted.bsecret", "w") as f2:
        try:
            encryptionKey = int(os.environ.get("encrypt", 0))
            fr = f.read()
            f2.write(decrypt(fr.decode("utf-8"), encryptionKey))
        except Exception as e:
            print(e)

# with open("thebotdbCredentials-encrypted.nottxt", "wb") as f:
# 	with open("TheBotBD-credentials.bsecret", "r") as f2:
# 		#print(f2.read())
# 		fr = f2.read()
# 		encrypted = botFunctions.encrypt(fr,key)
# 		print(encrypted)
# 		f.write(bytes(botFunctions.encrypt(fr,key),"utf-8"))

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "thebotdb-creds-decrypted.bsecret", scope)
except Exception:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "TheBotBD-credentials.bsecret", scope)

sheetClient = gspread.authorize(creds)

# print(sheetClient.open("TheBotDB").worksheets())

commandLog = sheetClient.open("TheBotDB").worksheet("Command Log")

messageLog = sheetClient.open("TheBotDB").worksheet("Message Log")

dataLog = sheetClient.open("TheBotDB").worksheet("Database")

advantniKalendar = sheetClient.open("TheBotDB").worksheet("AK")

timers = sheetClient.open("TheBotDB").worksheet("Timers")

birthdays = sheetClient.open("TheBotDB").worksheet("BDays")

iedb = sheetClient.open("TheBotDB").worksheet("IEBot")

covidTipsSheet = sheetClient.open("TheBotDB").worksheet("CovidTips")


def getBDays():
    values = birthdays.get_all_values()
    captions = values[0]
    values = values[1:]
    bDicts = [dict(zip(captions, v)) for v in values]
    for i in bDicts:
        for k in i:
            if k in ["GuildIDs", "ChannelIDs"]:
                i[k] = list(map(int, i[k].split(",")))
            if k == "Birthdate":
                i[k] = datetime.date.fromisoformat(i[k])
    return bDicts


def getTodayBDays(today=None):
    if today is None:
        today = datetime.date.today()
    bDays = getBDays()
    for i in bDays:
        if (
            i["Birthdate"].month == today.month
            and i["Birthdate"].day == today.day
        ):
            yield i


def getGuildBDays(guild):
    for i in getBDays():
        if guild in i["GuildIDs"]:
            yield i


def lastCheckedBDay():
    lastDateStr = dataLog.cell(2, 4).value
    return datetime.date.fromisoformat(lastDateStr)


def updateLastCheckedBDay(today=None):
    if today is None:
        today = datetime.date.today()
    dataLog.update_cell(2, 4, today.isoformat())


def getIEData():
    values = iedb.get_all_values()
    captions = values[0]
    values = values[1:]
    ieDicts = [dict(zip(captions, v)) for v in values]
    for i in ieDicts:
        for k in i:
            if k == "time":
                i[k] = datetime.datetime.fromisoformat(i[k])
            if k == "eventIndex":
                i[k] = int(i[k])
    return ieDicts


def addIEData(time, text, index):
    if time in getIEDataTimes():
        return False
    iedb.append_row([time.isoformat(), text, index])
    return True


def getIEDataT(time):
    for i in getIEData():
        if i["time"] == time:
            return i


def deleteIEData(time):
    indexes = [i for i, t in enumerate(getIEDataTimes()) if t == time]
    for i in indexes:
        iedb.delete_row(i+1)


def getIEDataTimes():
    return ["time"]+[
        datetime.datetime.fromisoformat(i) for i in iedb.col_values(1)[1:]
    ]


def getLastCovidTime():
    return dataLog.cell(2, 5).value


def setLastCovidTime(time):
    return dataLog.update_cell(2, 5, time)


def getCovidTips():
    values = covidTipsSheet.get_all_values()
    captions = values[0]
    values = values[1:]
    covidTipsData = [dict(zip(captions, v)) for v in values]
    for i in covidTipsData:
        for k in i:
            if k == "date":
                i[k] = datetime.datetime.fromisoformat(i[k])
            if k == "userID":
                i[k] = int(i[k])
            if k == "number":
                i[k] = int(i[k])
    return covidTipsData


def getCovidTipsDate(date):
    covidTips = getCovidTips()
    covidTips = [i for i in covidTips if i["date"].date() == date]
    users = set()
    for tip in covidTips:
        if tip["userID"] not in users:
            users.add(tip["userID"])
            yield tip


def setCovidTip(date: datetime.date, tip, user, twitterUsername=""):
    isTwitterUsername = re.match(r"(\b[A-Za-z0-9]+\b)", twitterUsername)
    if isTwitterUsername and isTwitterUsername.groups()[0] == twitterUsername:
        twitterUsername = "@" + twitterUsername[:15]
    else:
        twitterUsername = twitterUsername[:25]
    covidTipsSheet.append_row([
        date.isoformat(),
        str(user)
        if not twitterUsername
        else twitterUsername,
        str(user.id),
        str(tip)
    ])
