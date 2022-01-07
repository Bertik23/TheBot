import asyncio
import bdbf
import random
import discord
from prettytable import PrettyTable
from botFunctions import waitUntil, xorSum
from variables import *


class Game2048:
    def __init__(self, player, gridSize):
        self.player = player
        self.grid = []
        for _ in range(gridSize):
            self.grid.append([0 for j in range(gridSize)])
        self.addNumber()
        self.addNumber()
        self.zeroInGrid = True
        self.playing = True

    async def startGame(self, msg):
        await msg.channel.send(
            "Welcome to 2048, the game where you move numbers around!")
        self.gameMSG = await msg.channel.send(self.printGrid())
        await self.playGame()

    async def playGame(self):
        while self.playing:
            # ⬆️⬅️⬇️➡️
            await self.gameMSG.clear_reactions()
            await self.gameMSG.add_reaction("⬆️")
            await self.gameMSG.add_reaction("⬅️")
            await self.gameMSG.add_reaction("⬇️")
            await self.gameMSG.add_reaction("➡️")

            def check(r, u):
                return u == self.player
            try:
                reaction, user = await client.wait_for("reaction_add",
                                                       timeout=60.0,
                                                       check=check)
            except asyncio.TimeoutError:
                await self.gameMSG.edit(
                    content=(f"{self.printGrid()}\n{self.player.mention}"
                             " your game was canceled after 60s of inactivity."
                             ))
                for i in bdbf.commands.cmds["all"]:
                    if str(i) == "game":
                        i.activeGame[self.player] = None
                self.playing = False
            else:
                await self.gameMSG.edit(content=self.makeMove(reaction.emoji))

    def addNumber(self):
        x = random.randint(0, len(self.grid) - 1)
        y = random.randint(0, len(self.grid[x]) - 1)
        # print(x,y)

        while self.grid[x][y] != 0:
            x = random.randint(0, len(self.grid) - 1)
            y = random.randint(0, len(self.grid[x]) - 1)
            # print(x,y)

        self.grid[x][y] = 2

    def move(self, direction):
        if direction == 0:  # up
            for _ in range(len(self.grid)):
                for j in range(len(self.grid[_])):
                    for i in range(len(self.grid)):
                        try:
                            if self.grid[i][j] == 0:
                                self.grid[i][j] = self.grid[i + 1][j]
                                self.grid[i + 1][j] = 0
                            if self.grid[i][j] == self.grid[i + 1][j]:
                                self.grid[i][j] += self.grid[i + 1][j]
                                self.grid[i + 1][j] = 0
                        except IndexError:
                            pass
        if direction == 1:  # left
            for i in range(len(self.grid)):
                for _ in range(len(self.grid[i])):
                    for j in range(len(self.grid[i])):
                        try:
                            if self.grid[i][j] == 0:
                                self.grid[i][j] = self.grid[i][j + 1]
                                self.grid[i][j + 1] = 0
                            if self.grid[i][j] == self.grid[i][j + 1]:
                                self.grid[i][j] += self.grid[i][j + 1]
                                self.grid[i][j + 1] = 0
                        except IndexError:
                            pass
        if direction == 3:  # right
            for i in range(len(self.grid)):
                for _ in range(len(self.grid[i])):
                    for j in range(-1, -len(self.grid[i]) - 1, -1):
                        # print(j)
                        try:
                            if self.grid[i][j] == 0:
                                self.grid[i][j] = self.grid[i][j - 1]
                                self.grid[i][j - 1] = 0
                            if self.grid[i][j] == self.grid[i][j - 1]:
                                self.grid[i][j] += self.grid[i][j - 1]
                                self.grid[i][j - 1] = 0
                        except IndexError:
                            pass
        if direction == 2:  # down
            for _ in range(len(self.grid)):
                for j in range(-1, -len(self.grid[_]) - 1, -1):
                    for i in range(len(self.grid)):
                        # print(j)
                        try:
                            if self.grid[i][j] == 0:
                                self.grid[i][j] = self.grid[i - 1][j]
                                self.grid[i - 1][j] = 0
                            if self.grid[i][j] == self.grid[i - 1][j]:
                                self.grid[i][j] += self.grid[i - 1][j]
                                self.grid[i - 1][j] = 0
                        except IndexError:
                            pass

    def printGrid(self):
        table = PrettyTable()
        table.field_names = [i for i in range(len(self.grid[0]))]
        for i, row in enumerate(self.grid):
            table.add_row(row)
        return "`" + str(table) + "`"

    def makeMove(self, direction=None):
        # ⬆️⬅️⬇️➡️

        if self.zeroInGrid:
            if direction is None:
                direction = int(input(""))
            elif direction == "⬆️":
                direction = 0
            elif direction == "⬅️":
                direction = 1
            elif direction == "⬇️":
                direction = 2
            elif direction == "⬇️":
                direction = 3
            moveDirection = direction
            self.move(moveDirection)
            self.checkForZeros()
            if self.zeroInGrid:
                self.addNumber()
            else:
                for i in bdbf.commands.cmds["all"]:
                    if str(i) == "game":
                        i.activeGame[self.player] = None
                self.playing = False
                return self.printGrid() + "\n" + f"{self.player.mention} lost"
            return self.printGrid()

    def checkForZeros(self):
        self.zeroInGrid = False
        for i in self.grid:
            for j in i:
                if j == 0:
                    self.zeroInGrid = True


class GameNim:
    def __init__(self, player1, player2, collums):
        self.player1 = player1
        self.player2 = player2
        self.collums = collums
        self.gameMessage = None
        self.currentPlayer = random.choice([player1, player2])
        # self.currentPlayer = player2

    async def startGame(self, msg: discord.Message):
        colsText = "\n\n".join(":orange_square: "*i for i in self.collums)
        self.gameMessage = await msg.channel.send(
            f"Welcome to the game of Nim\n{colsText}\n"
            f"Na tahu je {self.currentPlayer.mention}"
        )
        await self.playGame()

    async def playGame(self):
        if self.currentPlayer.id != client.user.id:
            msg = await client.wait_for(
                "message",
                check=lambda m: (
                    m.reference.message_id == self.gameMessage.id
                    and
                    m.author == self.currentPlayer
                )
            )
            play = msg.content.split(" ")
        else:
            s = xorSum(self.collums)
            for i, col in enumerate(self.collums):
                print(s, col, xorSum([s, col]))
                if (x := xorSum([s, col])) <= col:
                    play = [str(i), str(col - x)]
                    break
            else:
                play = [str(random.randint(0, len(self.collums)-1))]
                play.append(str(random.randint(1, self.collums[int(play[0])])))
            msg = self.gameMessage
        try:
            if len(play) != 2:
                await msg.reply("Neplatný tah")
            else:
                self.collums[int(play[0])] -= int(play[1])
                for i, col in enumerate(self.collums):
                    if col == 0:
                        del self.collums[i]
                colsText = "\n\n".join(
                    ":orange_square: "*i for i in self.collums
                )
                if self.currentPlayer == self.player1:
                    self.currentPlayer = self.player2
                else:
                    self.currentPlayer = self.player1
                self.gameMessage = await msg.reply(
                    colsText
                    + f"Na tahu je {self.currentPlayer.mention}"
                )
            if len(self.collums):
                await self.playGame()
            else:
                await msg.reply(f"{self.currentPlayer.mention} prohrál.")
                del self
        except Exception as e:
            await msg.reply(f"Neplatný tah\n{e}")
            await self.playGame()
