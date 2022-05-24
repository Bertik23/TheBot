import bdbf
import os
import ksoftapi
import praw
import datetime

version = (2, 2, 17)
changelog = {
    "2.2.17": "Better logging system",
    "2.2.16": "Now sending covid data in the morning.",
    "2.2.15": "Added ~birthdays and notifying of next birthdays.",
    "2.2.14": "Next hour now displays rooms and upgraded `rozvrh` command",
    "2.2.13": "Updated to discord.py 1.7.2 and added some hlášky.",
    "2.2.12": "Removed spamming and fixed info command.",
    "2.2.11": "Command CKS",
    "2.2.10": "Multiple timers now possible",
    "2.2.9": "Timer overhaul",
    "2.2.8": "Added day command",
    "2.2.7": "Added rotate command",
    "2.2.6": "PEP 8 tified code",
    "2.2.5": "Added the makeEmbed command",
    "2.2.4": "Upgraded to bdbf 1.1.1",
    "2.2.3": "Small fix in versioning",
    "2.2.2": "Small backend fixes",
    "2.2.1": ("Started versioning and making a changelog.\n"
              "Better stats command.")
}

heroku = os.environ.get("isHeroku", False)
if not heroku:
    logging = False
    try:
        with open(
                "C:\\Users\\alber\\OneDrive\\Plocha\\discordBotSecrets.txt",
                "r") as f:
            kclient = eval(f.readline())
            token = eval(f.readline())
            reddit = eval(f.readline())
            githubToken = eval(f.readline())
    except Exception:
        with open("/home/bertik23/Plocha/discordBotSecrets.txt", "r") as f:
            kclient = eval(f.readline())
            token = eval(f.readline())
            reddit = eval(f.readline())
            githubToken = eval(f.readline())

else:
    kclient = ksoftapi.Client(os.environ.get("ksoft_token", None))

    reddit = praw.Reddit(client_id=os.environ.get(
                            "reddit_client_id",
                            None),
                         client_secret=os.environ.get(
                             "reddit_client_secret",
                             None),
                         user_agent=os.environ.get(
                             "reddit_user_agent",
                             None))

    token = os.environ.get('TOKEN', None)
    logging = True

botId = 540563812890443794
# 84032 permissions int
# https://discordapp.com/oauth2/authorize?client_id=540563812890443794&scope=bot&permissions=8

# DEBUG ONLY!!!
# logging = True
# END DEBUG ONLY!!!

client = bdbf.Client(
    commandPrefix="~",
    embedFooter={
        "text": "Powered by Bertik23",
        "icon_url": "https://cdn.discordapp.com/avatars/452478521755828224/92f95d857438843f22ca480d65d7baeb.webp"
    },
    embedColor=(37, 217, 55),
    botName="TheBot",
    logging=logging,
    createTaskCommands=False
    )


(
    klubik, obecne, choco_afroAnouncements,
    korona_info, hodinyUpozorneni, botspam
) = (
    None, None, None, None, None, None
)
botStartTime = datetime.datetime.utcnow()
botReadyTimes = []

userTimers = {}


class Dummy:
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])
