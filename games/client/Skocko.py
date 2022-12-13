import json
import time
import uuid
from abc import ABC

import PIL
from PIL import ImageTk

from games.client.Game import Game, PacketType
from tkinter import *

from images import ImageProvider


class Skocko(Game, ABC):

    currentCombination = []
    results = []

    canvas: Canvas = None
    deleteButton = None
    confirmButton = None

    buttons = []

    symbols = ['SKOCKO', 'TREF', 'PIK', "HERC", 'KARO', 'ZVEZDA']
    canvasSymbols = []

    sFrame = None
    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def start(self, client):
        super().start(client)
        self.sFrame = Frame(self.frame, width=1000, height=1000)

        self.canvas = Canvas(self.sFrame, height=900, width=950)
        self.canvas.place(x=50, y=50)
        for i in range(9):
            if i == 6: continue
            if i < 6:
                self.canvas.create_rectangle(820, 5+80*i, 900, 5+80+80*i, fill='#FFFFFF', outline='red')
                x = 820+50+40
                y = 5+80+85*i+50-40
                button = Button(self.sFrame, image=self.getImage(i), command=lambda c=i: self.onClick(c), state=DISABLED)
                button.place(x=x, y=y, anchor=CENTER)
                self.buttons.append(button)
            for j in range(4):
                pass
                self.canvas.create_rectangle(5+80*j, 5+80*i, 5+80+80*j, 5+80+80*i, fill='#FFFFFF')

        self.deleteButton = Button(self.sFrame, text='OBRISI', command=self.onDeleteClick, width=7, bg='#07FC1C', activebackground='#65FF72', font=('Calibri', 20))
        self.deleteButton.place(x=900, y=750, anchor=CENTER)
        self.confirmButton = Button(self.sFrame, text='POTVRDI', command=self.confirm, width=7, bg='#07FC1C', activebackground='#65FF72', font=('Calibri', 20), state=DISABLED)
        self.confirmButton.place(x=900, y=700, anchor=CENTER)
        self.sFrame.place(x=0, y=100)
        self.setTurn(self.turn, None)

    def onDeleteClick(self):
        if len(self.currentCombination) == 0: return
        del self.currentCombination[-1]
        self.canvas.delete(self.canvasSymbols[-1])
        del self.canvasSymbols[-1]
        self.confirmButton['state'] = DISABLED

    def onClick(self, index):
        if self.turn != self.player or len(self.currentCombination) >= 4: return
        symbol = self.getSymbol(index)
        self.currentCombination.append(symbol)
        self.draw(symbol, self.getImage(index))
        if len(self.currentCombination) >= 4:
            self.confirmButton['state'] = NORMAL
        else:
            self.confirmButton['state'] = DISABLED

    def draw(self, symbol, image):
        column = len(self.currentCombination)
        gameTurn = self.gameTurn
        if gameTurn >= 7: gameTurn = self.gameTurn+1
        self.canvasSymbols.append(self.canvas.create_image(5+80*column-40, 5+80*gameTurn-40, image=image))

    def drawCombination(self, combination, row):
        print(combination)
        realRow = row
        if realRow >= 7: realRow = row+1
        for i in range(4):
            self.canvas.create_image(5 + 80 * (i+1) - 40, 5 + 80 * realRow - 40, image=self.getImage(self.getIndex(combination[i])))

    def getIndex(self, symbol):
        for i in range(len(self.symbols)):
            if self.symbols[i] == symbol: return i
        return 0

    def getName(self):
        return "Skocko"

    def getGameLength(self):
        return 60

    def createTurnInPacket(self):
        return self.createPacket(PacketType.TURN_IN, ("kombinacija", self.currentCombination))

    def handleGameEnd(self, packet):
        self.drawCombination(packet['kombinacija'], 8)

    def cleanup(self):
        super().cleanup()
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        self.deleteButton.destroy()
        self.confirmButton.destroy()

    def setTurn(self, player, packet):
        super().setTurn(player, packet)
        if self.client is None: return
        for b in self.buttons:
            b['state'] = NORMAL if self.client.player.name == player.name else DISABLED

    def confirm(self):
        if len(self.currentCombination) != 4: return
        self.client.connection.write_message(json.dumps(self.createTurnInPacket()))
        self.currentCombination.clear()
        self.confirmButton['state'] = DISABLED

    def drawCircle(self, x, y, color):
        r = 40
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1, fill=color)

    def getSymbol(self, row):
        return self.symbols[row]

    def getImage(self, row):
        return ImageProvider.images[self.getSymbol(row).lower()]

    def handleTurnedIn(self, packet):
        left = 4
        counter = 0
        gameTurn = self.gameTurn
        if gameTurn >= 7: gameTurn = self.gameTurn+1
        for i in range(packet['crveni']):
            self.drawCircle(25 + 80*5 + 5 + 80 * counter - 40, 5+80*gameTurn-40, color='red')
            counter += 1
            left -= 1
        for i in range(0, packet['zuti']):
            self.drawCircle(25 + 80*5 + 5 + 80 * counter - 40, 5+80*gameTurn-40, color='yellow')
            counter += 1
            left -= 1
        for i in range(0, left):
            self.drawCircle(25 + 80*5 + 5 + 80 * counter - 40, 5+80*gameTurn-40, color='gray')
            counter += 1
        self.gameTurn = packet['potez']
        if uuid.UUID(packet['player']) != self.player.id:
            self.drawCombination(packet['kombinacija'], self.gameTurn-1)
        print(counter)
        print(self.gameTurn)

