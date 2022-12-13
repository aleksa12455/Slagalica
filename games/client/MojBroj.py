import json
from abc import ABC

from games.client.Game import Game, PacketType
from tkinter import *

from images import ImageProvider


class MojBroj(Game, ABC):

    expression = ''
    expressionWidget = None
    opponentExpressionWidget = None
    target = None

    redResult = None
    blueResult = None

    deleteButton = None
    confirmButton = None

    buttons = []
    clickedButtons = []

    mbFrame = None

    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def start(self, client):
        super().start(client)
        self.mbFrame = Frame(self.frame, width=1000, height=1000)
        self.expressionWidget = Entry(self.mbFrame, disabledbackground='white', disabledforeground='black', state=DISABLED, justify=LEFT, width=25, font=('Calibri', 32))
        self.target = Entry(self.mbFrame, disabledbackground='white', disabledforeground='black', state=DISABLED, justify=CENTER, width=5, font=('Calibri', 32))
        self.target.place(x=500, y=100, anchor=CENTER)
        self.expressionWidget.place(x=500, y=400, anchor=CENTER)
        self.redResult = Entry(self.mbFrame, disabledbackground='red', disabledforeground='white', state=DISABLED, justify=CENTER, fg='white', width=5, font=('Calibri', 32), bg='#FF0000')
        self.blueResult = Entry(self.mbFrame, disabledbackground='blue', disabledforeground='white', state=DISABLED, justify=CENTER, fg='white', width=5, font=('Calibri', 32), bg='#0000FF')
        self.blueResult.place(x=100, y=200, anchor=CENTER)
        self.redResult.place(x=900, y=200, anchor=CENTER)
        for i in range(4):
            button = Button(self.mbFrame, text='', height=1, width=2, font=('Calibri', 24), command=lambda b=i: self.onNumberClick(b))
            button.place(x=366 + i*24*2.8, y=550)
            self.buttons.append(button)

        self.buttons.append(self.createButton(1, 8, 4, x=385, y=650, text='', center=True))
        self.buttons.append(self.createButton(1, 11, 5, x=600, y=650, text='', center=True))
        self.buttons.append(self.createButton(1, 2, 6, x=350-52, y=750, text='+'))
        self.buttons.append(self.createButton(1, 2, 7, x=417-52, y=750, text='-'))
        self.buttons.append(self.createButton(1, 2, 8, x=484-52, y=750, text='*'))
        self.buttons.append(self.createButton(1, 2, 9, x=552-52, y=750, text='/'))
        self.buttons.append(self.createButton(1, 2, 10, x=619-52, y=750, text='('))
        self.buttons.append(self.createButton(1, 2, 11, x=686-52, y=750, text=')'))
        #
        img = ImageProvider.images['delete_small']
        self.deleteButton = Button(self.mbFrame, image=img, borderwidth=0, bd=0, highlightthickness=0, command=self.onDeleteClick, text='image', bg='#FFFFFF')
        self.deleteButton.image = img
        self.deleteButton.place(x=775, y=400, anchor=CENTER)
        self.confirmButton = Button(self.mbFrame, text='POTVRDI', command=self.confirm, bg='#07FC1C', activebackground='#65FF72', font=('Calibri', 20))
        self.confirmButton.place(x=500, y=475, anchor=CENTER)
        self.mbFrame.place(x=0, y=100)

    def setTarget(self, target):
        self.target['state'] = NORMAL
        self.target.delete(0, END)
        self.target.insert(0, target)
        self.target['state'] = DISABLED

    def setNumbers(self, numbers):
        for i in range(6):
            self.buttons[i]['text'] = numbers[i]

    def onNumberClick(self, index):
        if self.client.turnedIn: return
        button: Button = self.buttons[index]
        clickedValue = str(button['text'])
        lastClickedValue = None if len(self.clickedButtons) == 0 else str(self.clickedButtons[0]['text'])
        if lastClickedValue is not None:
            if clickedValue == '(':
                if lastClickedValue.isdigit() or lastClickedValue == ')': return
            elif clickedValue == ')':
                if not lastClickedValue.isdigit() and lastClickedValue != ')': return
            elif (clickedValue.isdigit() and lastClickedValue.isdigit()) or (not clickedValue.isdigit() and not lastClickedValue.isdigit()):
                return
        if clickedValue.isdigit(): button['state'] = DISABLED
        self.expression += str(button['text'])
        self.updateText()
        self.clickedButtons.insert(0, button)

    def updateText(self):
        self.expressionWidget['state'] = NORMAL
        self.expressionWidget.delete(0, END)
        self.expressionWidget.insert(END, self.expression)
        self.expressionWidget['state'] = DISABLED

    def onDeleteClick(self):
        if len(self.clickedButtons) <= 0:
            return
        button: Button = self.clickedButtons[0]
        self.clickedButtons.pop(0)
        self.expression = self.expression[:-len(str(button['text']))]
        self.updateText()
        button['state'] = NORMAL

    def createButton(self, height, width, index, text='', x=0, y=0, center=False):
        button = Button(self.mbFrame, text=text, height=height, width=width, font=('Calibri', 24),
                        command=lambda: self.onNumberClick(index))
        if center:
            button.place(x=x, y=y, anchor=CENTER)
        else:
            button.place(x=x, y=y)
        return button

    def getName(self):
        return "Moj Broj"

    def getGameLength(self):
        return 60

    def createTurnInPacket(self):
        self.client.turnedIn = True
        return self.createPacket(PacketType.TURN_IN, ("expression", self.expression))

    def handleGameEnd(self, packet):
        self.client.turnedIn = False
        if not self.client.turnedIn:
            self.updateText()
            for button in self.buttons:
                button.destroy()
            self.buttons.clear()
            self.deleteButton.destroy()
            self.confirmButton.destroy()
        for color, result in packet['resenja'].items():
            try:
                evaluated = str(eval(result))
            except Exception:
                evaluated = '???'
            if color == 'BLUE':
                self.blueResult['state'] = NORMAL
                self.blueResult.insert(0, evaluated)
                self.blueResult['state'] = DISABLED
            else:
                self.redResult['state'] = NORMAL
                self.redResult.insert(0, evaluated)
                self.redResult['state'] = DISABLED
        self.opponentExpressionWidget = Text(self.mbFrame, state=NORMAL, wrap='none', height=1, width=25,
                                             font=('Calibri', 32))
        self.opponentExpressionWidget.insert(END, packet['resenja'][str(self.client.opponent.color)])
        self.opponentExpressionWidget.place(x=500, y=650, anchor=CENTER)
        self.opponentExpressionWidget['state'] = DISABLED

    def cleanup(self):
        super().cleanup()
        self.expression = ''
        self.expressionWidget.destroy()
        self.redResult.destroy()
        self.blueResult.destroy()
        self.target.destroy()
        self.expressionWidget.destroy()
        self.client.turnedIn = False

    def confirm(self):
        if self.client.turnedIn: return
        self.client.connection.write_message(json.dumps(self.createTurnInPacket()))
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        self.deleteButton.destroy()
        self.confirmButton.destroy()
        self.clickedButtons.clear()
