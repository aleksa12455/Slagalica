import json
import uuid
from abc import ABC

from games.client.Game import Game, PacketType
from tkinter import *

class Asocijacije(Game, ABC):

    buttons = {}
    confirmButton = None
    nextButton = None
    openedFields = []
    guessedEntries = []
    finalEntry = None
    entries = {}

    sFrame = None
    n = 0

    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def start(self, client):
        super().start(client)
        self.sFrame = Frame(self.frame, width=1000, height=1000)

        dY = 58
        dX = 40
        fieldWidth = 15
        startX = 200
        startY = 200
        endX = 800
        endY = 800

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['A'] = entry
                entry.place(x=startX + dX * i, y=startY + dY * i, anchor=CENTER)
                continue
            field = f'A{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'A{i+1}'] = button
            button.place(x=startX + dX*i, y=startY + dY*i, anchor=CENTER)

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['B'] = entry
                entry.place(x=endX - dX * i, y=startY + dY * i, anchor=CENTER)
                continue
            field = f'B{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'B{i+1}'] = button
            button.place(x=endX - dX*i, y=startY + dY*i, anchor=CENTER)

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['C'] = entry
                entry.place(x=startX + dX * i, y=endY - dY * i, anchor=CENTER)
                continue
            field = f'C{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'C{i+1}'] = button
            button.place(x=startX + dX*i, y=endY - dY*i, anchor=CENTER)

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['D'] = entry
                entry.place(x=endX - dX * i, y=endY - dY * i, anchor=CENTER)
                continue
            field = f'D{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'D{i+1}'] = button
            button.place(x=endX - dX*i, y=endY - dY*i, anchor=CENTER)

        self.finalEntry = Entry(self.sFrame, width=25, font=('Calibri', 22), justify=CENTER)
        self.finalEntry.place(x=500, y=500, anchor=CENTER)

        self.confirmButton = Button(self.sFrame, text='POTVRDI', command=self.confirm, width=7, font=('Calibri', 18))
        self.confirmButton.place(x=800, y=500, anchor=CENTER)
        self.nextButton = Button(self.sFrame, text='DALJE', command=self.next, width=7, font=('Calibri', 18))
        self.nextButton.place(x=200, y=500, anchor=CENTER)
        self.sFrame.grid(row=1, column=0, sticky=EW)
        self.setTurn(self.turn, None)

    def onClick(self, field):
        if self.turn != self.player: return
        if self.player.turnedIn: return
        if field in self.openedFields: return
        button = self.buttons[field]
        if button is None: return
        self.player.turnedIn = True
        self.client.connection.write_message(json.dumps(self.createPacket(PacketType.TURN_IN, ('fieldType', 'FIELD_OPEN'), ('field', field), ('answer', 'FIELD_OPEN'))))

    def next(self):
        if self.turn != self.player: return
        self.client.connection.write_message(json.dumps(self.createPacket(PacketType.TURN_IN, ('fieldType', 'FIELD_OPEN'), ('field', 'any'), ('answer', 'NEXT'))))

    def getName(self):
        return "Asocijacije"

    def getGameLength(self):
        return 25

    def handleGameEnd(self, packet):
        self.n += 1
        if self.n == 2:
            self.parent.after(5000, self.stopProgram)

        self.openedFields.clear()
        # self.drawCombination(packet['kombinacija'], 8)

    def stopProgram(self):
        self.client.stop()
        self.parent.destroy()


    def cleanup(self):
        super().cleanup()
        for button in self.buttons.values():
            button.destroy()
        for e in self.entries.values():
            e.destroy()
        self.buttons.clear()
        self.confirmButton.destroy()

    def setTurn(self, player, packet):
        super().setTurn(player, packet)
        player.turnedIn = False
        self.timeLeft = self.getGameLength()
        if self.client is None: return
        for b in self.buttons.values():
            b['state'] = NORMAL if self.client.player.name == player.name or b['text'] in self.openedFields else DISABLED

    def confirm(self):
        if self.turn != self.player: return
        for k, v in self.entries.items():
            if v in self.guessedEntries: continue
            value = v.get()
            if value is None or value == '': continue
            v.delete(0, END)
            self.client.connection.write_message(json.dumps(self.createPacket(PacketType.TURN_IN, ('fieldType', 'FIELD_ANSWER'), ('field', k), ('answer', value))))
            return
        if self.finalEntry.get() is None or self.finalEntry.get() == '': return
        self.client.connection.write_message(json.dumps(
            self.createPacket(PacketType.TURN_IN, ('fieldType', 'FIELD_ANSWER'), ('field', 'resenje'), ('answer', self.finalEntry.get()))))
        self.finalEntry.delete(0, END)
        return

    def handleTurnedIn(self, packet):
        player = self.client.getPlayerById(uuid.UUID(packet['player']))
        field = packet['field']
        if packet['fieldType'] == 'FIELD_OPEN':
            button = self.buttons[field]
            button['text'] = packet['value']
            self.openedFields.append(field)
        elif packet['fieldType'] == 'FIELD_ANSWER':
            if not packet['correct']:
                if field == 'resenje':
                    entry = self.finalEntry
                    entry.insert(0, packet['value'])
                    entry['bg'] = 'yellow'
                    entry['fg'] = 'black'
                    self.frame.master.after(3000, lambda: self.clearEntry(entry))
                else:
                    entry = self.entries[field]
                    entry.insert(0, packet['value'])
                    entry['disabledbackground'] = 'yellow'
                    entry['disabledforeground'] = 'black'
                    self.frame.master.after(3000, lambda: self.clearEntry(entry))
            else:
                if field != 'resenje':
                    entry = self.entries[field]
                    entry.delete(0, END)
                    entry.insert(0, packet['value'].upper())
                    entry['bg'] = player.color
                    entry['fg'] = 'white'
                    entry['disabledbackground'] = player.color
                    entry['disabledforeground'] = 'white'
                    entry['state'] = DISABLED
                    values = packet['values']
                    self.guessedEntries.append(entry)
                    for i in range(4):
                        f = f'{field}{i+1}'
                        b = self.buttons[f'{f}']
                        b['fg'] = 'white'
                        b['bg'] = player.color
                        b['text'] = values[i]
                        self.openedFields.append(f)
                else:
                    entry = self.finalEntry
                    entry.delete(0, END)
                    entry.insert(0, packet['value'])
                    entry['bg'] = player.color
                    entry['fg'] = 'white'
                    entry['disabledbackground'] = player.color
                    entry['disabledforeground'] = 'white'
                    for k, b in self.buttons.items():
                        if k in self.openedFields: continue
                        b['fg'] = 'white'
                        b['bg'] = player.color
                    entry['state'] = DISABLED

    def clearEntry(self, entry):
        entry.delete(0, END)
        entry['state'] = NORMAL
        entry['bg'] = 'white'
        entry['fg'] = 'black'



