from enum import Enum

from frames.BaseFrame import BaseFrame1
from tkinter import *
from abc import abstractmethod

games = {

}

class Game(BaseFrame1):

    player = None
    client = None
    timeLeft = -1
    timerLabel = None
    scoreboardFrame = None
    blueScore = None
    redScore = None
    active = False
    needsCleanup = False
    turn = None
    gameTurn = 1

    def __init__(self, parent, frame):
        super().__init__(parent, frame)
        self.initialize()

    def initialize(self):
        games[self.getName()] = self
        self.onInitialize()

    def show(self, shownFrom=None):
        super().show(shownFrom)
        self.parent.geometry('1000x1000')
        self.parent.title(self.getName())
        self.parent.resizable(False, False)
        self.frame.grid_propagate(False)

    def update(self):
        if not self.active: return
        if self.timeLeft > 0: self.timeLeft -= 1
        self.timerLabel['text'] = self.timeLeft
        self.parent.after(1000, self.update)

    def start(self, client):
        from PlayerClient import PlayerColor
        if self.needsCleanup:
            self.cleanup()
            self.needsCleanup = False
        self.gameTurn = 1
        self.client = client
        self.player = client.player
        self.timeLeft = self.getGameLength()
        self.scoreboardFrame = Frame(self.frame, width=1000, height=100)
        self.timerLabel = Label(self.scoreboardFrame, text=self.timeLeft, font=('Calibri', 15))
        self.timerLabel.place(x=500, y=50, anchor=CENTER)
        self.scoreboardFrame.grid_rowconfigure(0, weight=1)
        self.scoreboardFrame.columnconfigure(0, weight=1)
        self.scoreboardFrame.grid(row=0, column=0, rowspan=1, columnspan=20, sticky=EW)
        self.scoreboardFrame.grid_propagate(False)
        self.blueScore = Label(self.scoreboardFrame, text=self.client.getPlayer(PlayerColor.BLUE).score, fg='blue', font=('Calibri', 15))
        self.redScore = Label(self.scoreboardFrame, text=self.client.getPlayer(PlayerColor.RED).score, fg='red', font=('Calibri', 15))
        self.blueScore.place(x=50, y=50, anchor=CENTER)
        self.redScore.place(x=950, y=50, anchor=CENTER)
        self.client.turnedIn = False
        self.active = True
        self.parent.after(1000, self.update)

    def stop(self):
        self.active = False
        self.needsCleanup = True

    def createPacket(self, packetType, *values):
        packet = {
            'player': str(self.player.id),
            'type': packetType.name,
            'game': self.getName()
        }
        for value in values:
            packet[value[0]] = value[1]
        return packet

    def cleanup(self):
        self.blueScore.destroy()
        self.redScore.destroy()
        self.timerLabel.destroy()
        self.timeLeft = self.getGameLength()
        self.client.turnedIn = False

    def setTurn(self, player, packet):
        self.turn = player

    def handleTurnedIn(self, packet):
        pass

    @abstractmethod
    def getName(self):
        pass

    @abstractmethod
    def onInitialize(self):
        pass

    @abstractmethod
    def getGameLength(self):
        pass

    @abstractmethod
    def createTurnInPacket(self):
        pass

    @abstractmethod
    def handleGameEnd(self, packet):
        pass

class PacketType(Enum):
    TURN_IN = 0