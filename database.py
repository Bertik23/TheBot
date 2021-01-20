import botFunctions
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# print(vars(botFunctions))

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

with open("thebotdbCredentials-encrypted.nottxt", "rb") as f:
	with open("thebotdb-creds-decrypted.bsecret", "w") as f2:
		try:
			encryptionKey = int(os.environ.get("encrypt",0))
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
	creds = ServiceAccountCredentials.from_json_keyfile_name("thebotdb-creds-decrypted.bsecret", scope)
except:
	creds = ServiceAccountCredentials.from_json_keyfile_name("TheBotBD-credentials.bsecret", scope)

sheetClient = gspread.authorize(creds)

#print(sheetClient.open("TheBotDB").worksheets())

commandLog = sheetClient.open("TheBotDB").worksheet("Command Log")

messageLog = sheetClient.open("TheBotDB").worksheet("Message Log")

dataLog = sheetClient.open("TheBotDB").worksheet("Database")

advantniKalendar = sheetClient.open("TheBotDB").worksheet("AK")

#print(advantniKalendar.get_all_values())