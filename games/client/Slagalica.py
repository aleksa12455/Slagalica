import json
from abc import ABC

from games.client.Game import Game, PacketType
from tkinter import *


class Slagalica(Game, ABC):
    text = None
    buttons = []
    word: str = ''
    clickedButtons = []
    wordChecker = None
    opponentWord = None
    computerWord = None
    deleteButton = None
    confirmButton = None
    recnikFile = None
    recnik = None
    slagalicaFrame = None

    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def onInitialize(self):
        self.recnikFile = open('recnik.txt', encoding="utf8")
        self.recnik = self.recnikFile.read()

    def start(self, client):
        super().start(client)
        self.slagalicaFrame = Frame(self.frame, width=1000, height=1000)
        self.text = Text(self.slagalicaFrame, state=DISABLED, wrap='none', height=1, width=30, font=('Calibri', 30))
        self.text.place(x=500, y=250, anchor=CENTER)
        self.wordChecker = Label(self.slagalicaFrame, justify=CENTER, anchor=CENTER, text='Rec nije pronadjena.', fg='red', font=('Calibri', 16))
        self.wordChecker.place(x=500, y=315, anchor=CENTER)
        for i in range(12):
            button = Button(self.slagalicaFrame, text='', height=2, width=4, font=('Calibri', 16), command=lambda b=i: self.onLetterClick(b))
            button.place(x=160+37.5+80 + 90*(i%6), y=400 + (0 if i < 6 else 85), anchor=CENTER)
            self.buttons.append(button)
        self.deleteButton = Button(self.slagalicaFrame, text='OBRISI', command=self.onDeleteClick, bg='#E78587', height=2, width=12, font=('Calibri', 16))
        self.deleteButton.place(x=680, y=585, anchor=CENTER)
        self.confirmButton = Button(self.slagalicaFrame, text='POTVRDI', command=self.onConfirmWord, bg='#07FC1C', height=2, width=12, activebackground='#65FF72', font=('Calibri', 16))
        self.confirmButton.place(x=160+86+80, y=585, anchor=CENTER)
        self.slagalicaFrame.place(x=0, y=100)

    def setLetters(self, letters):
        for i in range(12):
            self.buttons[i]['text'] = letters[i]

    def onConfirmWord(self):
        if self.client.turnedIn: return
        self.client.connection.write_message(json.dumps(self.createTurnInPacket()))
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        self.deleteButton.destroy()
        self.confirmButton.destroy()
        self.opponentWord = Text(self.slagalicaFrame, state=NORMAL, wrap='none', height=1, width=30, font=('Calibri', 30))
        self.opponentWord.insert(END, 'Protivnik resava...')
        self.opponentWord.place(x=500, y=400, anchor=CENTER)
        self.opponentWord['state'] = DISABLED

    def onLetterClick(self, index):
        if self.client.turnedIn: return
        button: Button = self.buttons[index]
        button['state'] = DISABLED
        self.word += button['text']
        self.updateText()
        self.clickedButtons.insert(0, button)

    def onDeleteClick(self):
        if len(self.clickedButtons) <= 0 or len(self.word) <= 0:
            return
        button: Button = self.clickedButtons[0]
        self.clickedButtons.pop(0)
        self.word = self.word[:-len(button['text'])]
        self.updateText()
        button['state'] = NORMAL

    def updateText(self):
        self.text['state'] = NORMAL
        self.text.delete('1.0', END)
        self.text.insert(END, self.word)
        if len(self.word) > 1 and self.word.lower() in self.recnik:
            self.wordChecker['text'] = 'Rec je pronadjena.'
            self.wordChecker['fg'] = 'green'
        else:
            self.wordChecker['text'] = 'Rec nije pronadjena.'
            self.wordChecker['fg'] = 'red'
        self.text['state'] = DISABLED


    def getName(self):
        return "Slagalica"

    def getGameLength(self):
        return 60

    def createTurnInPacket(self):
        self.client.turnedIn = True
        return self.createPacket(PacketType.TURN_IN, ('rec', self.word))

    def handleGameEnd(self, packet):
        if self.client.turnedIn:
            self.opponentWord['state'] = NORMAL
            self.opponentWord.delete('1.0', END)
            self.opponentWord.insert(END, packet['resenje'][str(self.client.opponent.id)])
            self.opponentWord['state'] = DISABLED
        else:
            self.word = ''
            self.updateText()
            for button in self.buttons:
                button.destroy()
                button.destroy()
            self.buttons.clear()
            self.deleteButton.destroy()
            self.confirmButton.destroy()
            self.opponentWord = Text(self.slagalicaFrame, state=NORMAL, wrap='none', height=1, width=30, font=('Calibri', 30))
            self.opponentWord.insert(END, packet['resenje'][str(self.client.opponent.id)])
            self.opponentWord.place(x=500, y=400, anchor=CENTER)
            self.opponentWord['state'] = DISABLED

        self.computerWord = Text(self.slagalicaFrame, state=NORMAL, wrap='none', height=1, width=30, font=('Calibri', 30))
        self.computerWord.insert(END, packet['najduza'])
        self.computerWord.place(x=500, y=550, anchor=CENTER)
        self.computerWord['state'] = DISABLED

    def cleanup(self):
        super().cleanup()
        self.opponentWord.destroy()
        self.computerWord.destroy()
        self.word = ''
        self.opponentWord = None
        self.computerWord = None
        self.text = None