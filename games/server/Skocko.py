import random
import uuid
from abc import ABC

from SlagalicaServer import PacketType, Player
from games.server.ServerGame import ServerGame

class Skocko(ServerGame, ABC):

    endGameHandle = None

    symbols = ['SKOCKO', 'TREF', 'PIK', 'HERC', 'KARO', 'ZVEZDA']
    defaultCombination = ['SKOCKO', 'SKOCKO', 'SKOCKO', 'SKOCKO']

    combination = []
    player: Player = None
    opponent: Player = None
    opponentsTurn = False

    def __init__(self, name, server):
        super().__init__(name, server)

    def initialize(self):
        pass

    def generate(self):
        self.combination.clear()
        for i in range(4):
            self.combination.append(random.choice(self.symbols))
        print(self.combination)
        return self.combination

    def validateCombination(self, combination):
        if len(combination) != 4: return False
        for symbol in combination:
            if symbol not in self.symbols: return False
        return True

    def forceStop(self):
        super().forceStop()
        if self.endGameHandle is not None: self.endGameHandle.cancel()

    def start(self, color):
        super().start(color)
        if self.color is None: return
        for player in self.server.clients.values():
            player.turnedIn = None
            player.turn = 1
            if player.color == color: self.player = player
            else: self.opponent = player
        self.generate()
        self.active = True
        self.opponentsTurn = False
        self.server.send_message(self.createPacket(PacketType.GAME_START, ('igra', 'skocko'), ('boja', self.color)))
        self.endGameHandle = self.server.getIOLoop().IOLoop.current().call_later(60, lambda: self.stop() if self.active else None)

    def stop(self):
        self.active = False
        self.endGameHandle.cancel()
        self.server.send_message(self.createPacket(PacketType.GAME_END, ('kombinacija', self.combination)))
        self.server.getIOLoop().IOLoop.current().call_later(5, lambda: self.start('RED'))

    def checkCombination(self, combination):
        red = 0
        yellow = 0
        exceptions = []
        exceptions2 = []
        print(self.combination)
        for i in range(4):
            if combination[i] == self.combination[i]:
                exceptions.append(i)
                exceptions2.append(i)
                red += 1
        for i in range(4):
            if i in exceptions: continue
            for j in range(4):
                if j in exceptions2: continue
                if combination[i] != self.combination[j]: continue
                yellow += 1
                exceptions2.append(j)
                break
        player = self.opponent if self.opponentsTurn else self.player
        packet = self.createPacket(PacketType.TURNED_IN, ('player', str(player.id)), ('kombinacija', combination),
                                   ('crveni', red), ('zuti', yellow), ('potez', self.player.turn + 1))
        self.server.send_message(packet)
        if red == 4:
            player.score += self.calculateScore()
            print(player.score)
            self.server.send_message(self.createPacket(PacketType.UPDATE_SCORE, ('id', str(player.id)), ('score', player.score)))
            self.stop()

    def calculateScore(self):
        if self.player.turn <= 4: return 20
        return 20 - 5 * (4 - self.player.turn)

    def handleTurnIn(self, player: Player, packet):
        player = uuid.UUID(packet['player'])
        if self.opponentsTurn:
            if player != self.opponent.id: return
        elif player != self.player.id: return
        combination = packet['kombinacija']
        self.player.turnedIn = combination if self.validateCombination(combination) else self.defaultCombination.copy()
        self.checkCombination(combination)
        self.player.turn += 1
        if self.opponentsTurn:
            if self.active: self.stop()
        elif self.player.turn > 6:
            self.opponentsTurn = True
            self.sendTurnChangePacket(self.opponent)


