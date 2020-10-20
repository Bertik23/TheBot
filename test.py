from database import *
from botFunctions import *
from random import randint
import math
import plotly.graph_objects as go

commandCountTotaly = len(commandLog.col_values(1))-1
commandsList = commandLog.col_values(2)[1:]
# commandCountGuild = len([g for g in commandLog.col_values(7) if g == str(msg.channel.guild.id)])
# commandCountChannel = len([g for g in commandLog.col_values(5) if g == str(msg.channel.id)])
mostActiveCommandor = mostFrequent(commandLog.col_values(4))
mostUsedCommand = mostFrequent(commandsList)

commandTimes = commandLog.col_values(1)[1:]

commandTimeUsage = {}
for i, t in enumerate(commandTimes):
    if t[:10] not in commandTimeUsage.keys():
        commandTimeUsage[t[:10]] = []
    commandTimeUsage[t[:10]].append(commandsList[i])

for key in commandTimeUsage.keys():
    commandTimeUsage[key] = count(commandTimeUsage[key])

print(commandTimeUsage)

commandCounts = count(commandsList)

commandTimes = [time.isoformat() for time in map(roundToTheLast30min,map(datetime.fromisoformat, commandTimes))]
commandTimesUno = deleteDuplicates(commandTimes)
commandTimeCounts = [commandTimes.count(t) for t in commandTimesUno]

fig = go.Figure(data=[go.Pie(labels=list(commandCounts.keys()), values=list(commandCounts.values()), textinfo="value+percent")])

fig_bytes = fig.to_image(format="png", width=1200, height=1200)

with open("test.png", "wb") as t:
    t.write(fig_bytes)
