import json
import random
from abc import ABC
import time

from SlagalicaServer import PacketType, Player
from games.server.ServerGame import ServerGame

class Asocijacije(ServerGame, ABC):

    endGameHandle = None
    turnHandle = None
    player: Player = None
    opponent: Player = None
    opponentsTurn = False
    fields = []
    openedFields = []

    def __init__(self, name, server):
        super().__init__(name, server)
        self.startTime = None

    def initialize(self):
        pass

    def generate(self):
        self.fields.clear()
        with open('games/server/Asocijacije.json', 'r') as asocijacijeFile:
            if len(asocijacijeFile.readlines()) != 0:
                asocijacijeFile.seek(0)
                asocijacije = json.load(asocijacijeFile)['asocijacije']
                asocijacija = asocijacije[random.randint(0, len(asocijacije)-1)]
                self.fields = asocijacija['polja']
                self.fields['resenje'] = asocijacija['resenje']

    def start(self, color):
        super().start(color)
        if self.turnHandle is not None: self.turnHandle.cancel()
        if self.color is None: return
        self.openedFields.clear()
        for player in self.server.clients.values():
            player.turnedIn = None
            player.turn = 1
            if player.color == color:
                self.player = player
            else:
                self.opponent = player
        self.generate()
        self.startTime = self.getNow()
        self.generate()
        self.active = True
        self.opponentsTurn = False
        self.server.send_message(self.createPacket(PacketType.GAME_START, ('igra', 'asocijacije'), ('boja', color)))
        self.endGameHandle = self.server.getIOLoop().IOLoop.current().call_later(1000, lambda: self.stop() if self.active else None)
        self.turnHandle = self.server.getIOLoop().IOLoop.current().call_later(25, lambda: self.setPlayerTurn(self.getOtherPlayer(self.getCurrentTurnPlayer())))

    def stop(self):
        self.active = False
        self.endGameHandle.cancel()
        self.server.send_message(self.createPacket(PacketType.GAME_END))
        self.server.getIOLoop().IOLoop.current().call_later(5, lambda: self.start('RED'))

    def isCorrect(self, field: str, answer: str):
        if field not in self.fields: return False
        return self.fields[field] == answer.upper()

    def handleTurnIn(self, player: Player, packet):
        if self.getCurrentTurnPlayer() != player: return
        if 'answer' not in packet: return
        answer = packet['answer']
        field = packet['field']
        if answer == 'FIELD_OPEN':
            player.turnedIn = 'FIELD_OPEN'
            self.sendField(field, 'FIELD_OPEN', False, player)
            return
        if answer == 'NEXT':
            self.setPlayerTurn(self.getOtherPlayer(player))
            return
        correct = self.isCorrect(field, answer)
        self.sendField(field, 'FIELD_ANSWER', correct, player, playerAnswer=answer)
        stop = False
        if correct:
            if field == 'resenje':
                player.score += 15
                stop = True
            else: player.score += 5
            self.server.send_message(self.createPacket(PacketType.UPDATE_SCORE, ('id', str(player.id)), ('score', player.score)))
            if stop:
                self.stop()
                return
        self.setPlayerTurn(self.getOtherPlayer(player))

    def forceStop(self):
        super().forceStop()
        if self.endGameHandle is not None: self.endGameHandle.cancel()
        if self.turnHandle is not None: self.turnHandle.cancel()

    def sendField(self, field, type, correct, player, playerAnswer=''):
        values = ('values', {})
        self.openedFields.append(field)
        if correct:
            if len(field) == 1:
                for i in range(4):
                    values[1][f'{field}{i+1}'] = self.fields[f'{field}{i+1}']
            elif field == 'resenje':
                for k, v in self.fields.items():
                    values[1][k] = v
        self.server.send_message(self.createPacket(PacketType.TURNED_IN, ('fieldType', type), ('field', field), ('value', self.fields[field] if type == 'FIELD_OPEN' else playerAnswer), ('correct', correct), ('player', str(player.id)), values))

    def getNow(self):
        return time.time()

    def setPlayerTurn(self, player):
        self.turnHandle.cancel()
        self.sendTurnChangePacket(player)
        self.opponentsTurn = not self.opponentsTurn
        self.turnHandle = self.server.getIOLoop().IOLoop.current().call_later(25, lambda: self.setPlayerTurn(self.getOtherPlayer(self.getCurrentTurnPlayer())))

    def getCurrentTurnPlayer(self):
        if self.opponentsTurn: return self.opponent
        else: return self.player

    def getOtherPlayer(self, player):
        if self.player == player: return self.opponent
        return self.player

    def next(self):
        self.color = None