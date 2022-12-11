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
        self.recnikFile = open('recnik.txt')
        self.recnik = self.recnikFile.read()

    def start(self, client):
        super().start(client)
        self.slagalicaFrame = Frame(self.frame)
        self.text = Text(self.slagalicaFrame, state=NORMAL, wrap='none', height=1, width=30, font=('Calibri', 30))
        self.text.grid(column=0, row=0, pady=0, sticky='N', columnspan=8, rowspan=2)
        self.wordChecker = Label(self.slagalicaFrame, justify=CENTER, anchor=CENTER, text='Rec nije pronadjena.', fg='red', font=('Calibri', 16))
        self.wordChecker.grid(row=2, column=0, columnspan=8, rowspan=1, pady=30, sticky=N)
        for i in range(12):
            button = Button(self.slagalicaFrame, text='', height=2, width=2, font=('Calibri', 16), command=lambda b=i: self.onLetterClick(b))
            button.grid(row=5 if i < 6 else 6, column=1 + (i % 6), columnspan=1, padx=0, sticky=EW)
            self.buttons.append(button)
        self.deleteButton = Button(self.slagalicaFrame, text='OBRISI', command=self.onDeleteClick, bg='#E78587', height=3, width=3, font=('Calibri', 14))
        self.deleteButton.grid(column=1, columnspan=2, rowspan=2, row=8, pady=15, sticky=NSEW)
        self.confirmButton = Button(self.slagalicaFrame, text='POTVRDI', command=self.onConfirmWord, bg='#07FC1C', activebackground='#65FF72', font=('Calibri', 14))
        self.confirmButton.grid(column=5, columnspan=2, rowspan=2, row=8, pady=15, sticky=NSEW)
        self.slagalicaFrame.grid(row=2, column=0, sticky=N)

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
        self.opponentWord.grid(row=3, column=0, columnspan=8, rowspan=1, pady=30, sticky=N)

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
        self.text.delete('1.0', END)
        self.text.insert(END, self.word)
        if len(self.word) > 1 and self.word.lower() in self.recnik:
            self.wordChecker['text'] = 'Rec je pronadjena'
            self.wordChecker['fg'] = 'green'
        else:
            self.wordChecker['text'] = 'Rec nije pronadjena'
            self.wordChecker['fg'] = 'red'


    def getName(self):
        return "Slagalica"

    def getGameLength(self):
        return 60

    def createTurnInPacket(self):
        self.client.turnedIn = True
        return self.createPacket(PacketType.TURN_IN, ('rec', self.word))

    def handleGameEnd(self, packet):
        if self.client.turnedIn:
            self.opponentWord.delete('1.0', END)
            self.opponentWord.insert(END, packet['resenje'][str(self.client.opponent.id)])
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
            self.opponentWord.grid(row=3, column=0, columnspan=8, rowspan=1, pady=30, sticky=N)

        self.computerWord = Text(self.slagalicaFrame, state=NORMAL, wrap='none', height=1, width=30, font=('Calibri', 30))
        self.computerWord.insert(END, packet['najduza'])
        self.computerWord.grid(row=4, column=0, columnspan=8, rowspan=1, pady=30, sticky=N)

    def cleanup(self):
        super().cleanup()
        self.opponentWord.destroy()
        self.computerWord.destroy()
        self.word = ''
        self.opponentWord = None
        self.computerWord = None
        self.text = None