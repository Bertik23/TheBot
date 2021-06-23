import botFunctions
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime

# print(vars(botFunctions))

scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

with open("thebotdbCredentials-encrypted.nottxt", "rb") as f:
    with open("thebotdb-creds-decrypted.bsecret", "w") as f2:
        try:
            encryptionKey = int(os.environ.get("encrypt", 0))
            fr = f.read()
            f2.write(botFunctions.decrypt(fr.decode("utf-8"), encryptionKey))
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
