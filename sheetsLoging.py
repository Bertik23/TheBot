import database
import time
import os

while True:
    logFiles = os.listdir("msgToLog")
    logFiles = sorted(logFiles, key=lambda x: int(x.split(".")[0]))
    toLog = []
    for logFile in logFiles:
        try:
            with open(f"msgToLog/{logFile}", "r", encoding="utf-8") as f:
                toLog.append(eval(f.read()))
            os.remove(f"msgToLog/{logFile}")
        except OSError:
            pass
    database.messageLog.append_rows(toLog)

    # Commands
    logFiles = os.listdir("cmdToLog")
    logFiles = sorted(logFiles, key=lambda x: int(x.split(".")[0]))
    toLog = []
    for logFile in logFiles:
        try:
            with open(f"cmdToLog/{logFile}", "r", encoding="utf-8") as f:
                toLog.append(eval(f.read()))
            os.remove(f"cmdToLog/{logFile}")
        except OSError:
            pass
    database.commandLog.append_rows(toLog)
    time.sleep(10)
