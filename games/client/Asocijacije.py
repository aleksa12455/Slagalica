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
        startY = 50
        endX = 800
        endY = 700

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, state=DISABLED, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['A'] = entry
                entry.place(x=startX + dX * i, y=startY + dY * i, anchor=CENTER)
                continue
            field = f'A{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'A{i+1}'] = button
            button.place(x=startX + dX*i, y=startY + dY*i, anchor=CENTER)

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, state=DISABLED, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['B'] = entry
                entry.place(x=endX - dX * i, y=startY + dY * i, anchor=CENTER)
                continue
            field = f'B{i+1}'
            button = Button(self.sFrame, state=DISABLED, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'B{i+1}'] = button
            button.place(x=endX - dX*i, y=startY + dY*i, anchor=CENTER)

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, state=DISABLED, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['C'] = entry
                entry.place(x=startX + dX * i, y=endY - dY * i, anchor=CENTER)
                continue
            field = f'C{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'C{i+1}'] = button
            button.place(x=startX + dX*i, y=endY - dY*i, anchor=CENTER)

        for i in range(5):
            if i == 4:
                entry = Entry(self.sFrame, state=DISABLED, width=fieldWidth, font=('Calibri', 22), justify=CENTER)
                self.entries['D'] = entry
                entry.place(x=endX - dX * i, y=endY - dY * i, anchor=CENTER)
                continue
            field = f'D{i+1}'
            button = Button(self.sFrame, text=field, command=lambda f=field: self.onClick(f), width=fieldWidth, font=('Calibri', 22))
            self.buttons[f'D{i+1}'] = button
            button.place(x=endX - dX*i, y=endY - dY*i, anchor=CENTER)

        self.finalEntry = Entry(self.sFrame, width=25, font=('Calibri', 22), justify=CENTER)
        self.finalEntry.place(x=500, y=endY - dY * 6 + 60/2, anchor=CENTER)

        self.confirmButton = Button(self.sFrame, text='POTVRDI', command=self.confirm, width=7, font=('Calibri', 18))
        self.confirmButton.place(x=800, y=endY - dY * 6 + 60/2, anchor=CENTER)
        self.nextButton = Button(self.sFrame, text='DALJE', command=self.next, width=7, font=('Calibri', 18))
        self.nextButton.place(x=200, y=endY - dY * 6 + 60/2, anchor=CENTER)
        self.sFrame.place(x=0, y=100)
        self.setTurn(self.turn, None)

    def onClick(self, field):
        if self.turn != self.player: return
        if self.player.turnedIn: return
        if field in self.openedFields: return
        button = self.buttons[field]
        if button is None: return
        self.player.turnedIn = True
        self.client.connection.write_message(json.dumps(self.createPacket(PacketType.TURN_IN, ('fieldType', 'FIELD_OPEN'), ('field', field), ('answer', 'FIELD_OPEN'))))
        entryName = field[0]
        if entryName not in self.entries: return
        entry = self.entries[entryName]
        entry['state'] = NORMAL

    def isOpen(self, entry):
        if entry in self.guessedEntries: return False
        fieldName = entry
        if len(fieldName) != 1:
            return False
        field = fieldName[0]
        for i in range(4):
            f = f'{field}{i+1}'
            if f in self.openedFields:
                return True
        return False

    def next(self):
        if self.turn != self.player or not self.player.turnedIn: return
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
        self.client.connection.close()
        self.parent.destroy()


    def cleanup(self):
        super().cleanup()
        for button in self.buttons.values():
            button.destroy()
        for e in self.entries.values():
            e.destroy()
        self.buttons.clear()
        self.confirmButton.destroy()
        self.entries.clear()
        self.guessedEntries.clear()
        self.openedFields.clear()

    def setTurn(self, player, packet):
        super().setTurn(player, packet)
        player.turnedIn = False
        self.timeLeft = self.getGameLength()
        if self.client is None: return
        for b in self.buttons.values():
            b['state'] = NORMAL if self.client.player.name == player.name or b['text'] in self.openedFields else DISABLED
        for e in self.entries:
            if self.entries[e] in self.guessedEntries:
                self.entries[e]['state'] = DISABLED
                continue
            if self.isOpen(e):
                self.entries[e]['state'] = NORMAL

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
            if len(self.guessedEntries) > 0:
                self.finalEntry['state'] = NORMAL
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
                    entry['state'] = NORMAL
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
                        b['text'] = values[f]
                        self.openedFields.append(f)
                else:
                    entry = self.finalEntry
                    entry.delete(0, END)
                    entry.insert(0, packet['value'])
                    entry['bg'] = player.color
                    entry['fg'] = 'white'
                    entry['disabledbackground'] = player.color
                    entry['disabledforeground'] = 'white'
                    entry['state'] = DISABLED
                    for k, b in self.buttons.items():
                        if b['bg'] == 'BLUE' or b['bg'] == 'RED': continue
                        b['fg'] = 'white'
                        b['bg'] = player.color
                    for k, v in packet['values'].items():
                        if len(k) == 1:
                            e = self.entries[k]
                            if e in self.guessedEntries: continue
                            e['state'] = NORMAL
                            e.delete(0, END)
                            e.insert(0, v)
                            e['bg'] = player.color
                            e['fg'] = 'white'
                            e['disabledbackground'] = player.color
                            e['disabledforeground'] = 'white'
                            e['state'] = DISABLED
                        elif len(k) == 2:
                            self.buttons[k]['text'] = v
                    entry['state'] = DISABLED

    def clearEntry(self, entry):
        entry.delete(0, END)
        entry['state'] = NORMAL
        entry['bg'] = 'white'
        entry['fg'] = 'black'



