import json
import uuid
from abc import ABC

from games.client.Game import Game, PacketType
from tkinter import *

class KoZnaZna(Game, ABC):

    questionWidget = None
    answers = []
    answerButtons = []
    nextButton = None

    sFrame = None
    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def start(self, client):
        super().start(client)
        self.sFrame = Frame(self.frame, width=1000, height=1000)
        self.questionWidget = Text(self.frame, width=30, height=5, wrap=WORD, font=('Calibri', 20))
        self.questionWidget.place(x=500, y=300, anchor=CENTER)
        self.questionWidget.tag_configure("center", justify='center')
        self.questionWidget.tag_add("center", 1.0, "end")
        for i in range(4):
            button = Button(self.sFrame, height=1, width=15, command=lambda c=i: self.onClick(c), text='', font=('Calibri', 20))
            button.place(x=500, y=500+50*i, anchor=CENTER)
            self.answerButtons.append(button)

        self.nextButton = Button(self.sFrame, text='DALJE', command=self.dalje, width=7, bg='yellow', activebackground='#65FF72', font=('Calibri', 20))
        self.nextButton.place(x=500, y=800, anchor=CENTER)
        self.sFrame.place(x=0, y=100)
        self.setTurn(self.turn, None)

    def onClick(self, index):
        if self.client.turnedIn: return
        button = self.answerButtons[index]
        answer = self.answers[index]
        self.setButtonColor(button, self.player.color)
        self.client.turnedIn = True
        for b in self.answerButtons:
            if b == button: continue
            b['state'] = DISABLED
        self.client.connection.write_message(json.dumps(self.createPacket(PacketType.TURN_IN, ('odgovor', answer))))

    def dalje(self):
        if self.client.turnedIn: return
        self.client.turnedIn = True
        self.client.connection.write_message(self.createPacket(PacketType.TURN_IN, ('odgovor', 'DALJE')))
        for b in self.answerButtons:
            b['state'] = DISABLED

    def getName(self):
        return "Ko Zna Zna"

    def getGameLength(self):
        return 10

    def createTurnInPacket(self):
        pass

    def handleGameEnd(self, packet):
        pass

    def cleanup(self):
        super().cleanup()
        for button in self.answerButtons:
            button.destroy()
        self.nextButton.destroy()
        self.questionWidget.destroy()
        self.answers.clear()

    def setTurn(self, player, packet):
        super().setTurn(player, packet)
        if self.client is None or packet is None: return
        self.setQuestion(packet['pitanje'])
        self.setAnswers(packet['odgovori'])

    def setQuestion(self, question):
        self.questionWidget['state'] = NORMAL
        self.questionWidget.delete('1.0', END)
        self.questionWidget.insert(END, question)
        self.questionWidget['state'] = DISABLED

    def setAnswers(self, answers):
        counter = 0
        self.answers = answers.copy()
        for a in answers:
            print(a)
            button = self.answerButtons[counter]
            self.setButtonColor(button, None)
            button['text'] = a
            button['state'] = NORMAL
            counter += 1
        self.client.turnedIn = False
        self.timeLeft = 10

    def handleTurnedIn(self, packet):
        for a in packet['odgovori']:
            id = uuid.UUID(a['playerId'])
            player = self.client.getPlayerById(id)
            button = self.buttonByText(a['answer'])
            if button is not None: self.setButtonColor(button, player.color)
        button = self.buttonByText(packet['tacanOdgovor'])
        if button is not None: self.setButtonColor(button, 'lime')

    def buttonByText(self, text):
        for b in self.answerButtons:
            if b['text'] == text: return b
        return None

    def setButtonColor(self, button, color):
        if color is None:
            button['bg'] = '#f0f0f0'
            button['fg'] = '#000000'
            button['activebackground'] = '#f0f0f0'
            button['activeforeground'] = '#000000'
        else:
            button['bg'] = color
            button['fg'] = 'white'
            button['activebackground'] = color
            button['activeforeground'] = 'white'