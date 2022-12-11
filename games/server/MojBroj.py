import random
from abc import ABC

from SlagalicaServer import PacketType, Player
from games.server.ServerGame import ServerGame

class MojBroj(ServerGame, ABC):

    endGameHandle = None

    small = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    medium = [10, 20, 25]
    large = [50, 75, 100]

    operations = ['+', '-', '*', '/', '(', ')']

    numbers = []

    result: int = None

    def __init__(self, name, server):
        super().__init__(name, server)

    def initialize(self):
        pass

    def generate(self):
        self.numbers.clear()
        for i in range(4):
            self.numbers.append(random.choice(self.small))
        self.numbers.append(random.choice(self.medium))
        self.numbers.append(random.choice(self.large))
        self.result = random.randint(1, 999)
        return self.result

    def validateResult(self, expression: str):
        if len(expression) == 0: return False
        for i in expression:
            if not i.isdigit() and i not in self.operations:
                return False
        return True

    def start(self, color):
        super().start(color)
        for player in self.server.clients.values():
            player.turnedIn = None
        self.generate()
        self.active = True
        self.server.send_message(self.createPacket(PacketType.GAME_START, ('igra', 'moj_broj'), ('rezultat', self.result), ('brojevi', self.numbers)))
        self.server.game = self
        self.endGameHandle = self.server.getIOLoop().IOLoop.current().call_later(60, lambda: self.stop() if self.active else None)

    def stop(self):
        self.active = False
        self.endGameHandle.cancel()
        winner = None
        results = {}
        for player in self.server.clients.values():
            if player.turnedIn is None or player.turnedIn == -9999:
                results[player.color] = '???'
                continue
            try:
                result = eval(player.turnedIn)
            except SyntaxError:
                results[player.color] = '???'
                continue
            results[player.color] = player.turnedIn
            difference = self.result - result
            if winner is not None and difference == winner[1]:
                if winner[0].color == self.server.getCurrentGame().color: continue
                winner = (player, difference)
            if winner is None or difference < winner[1]:
                winner = (player, difference)
        if winner is not None:
            winner[0].score += 10
            scorePacket = self.createPacket(PacketType.UPDATE_SCORE, ('id', str(winner[0].id)), ('score', winner[0].score))
            self.server.send_message(scorePacket)
        self.server.send_message(self.createPacket(PacketType.GAME_END, ('resenja', results)))
        self.server.getIOLoop().IOLoop.current().call_later(5, lambda: self.start('RED'))

    def handleTurnIn(self, player: Player, packet):
        expression = packet['expression']
        player.turnedIn = expression if self.validateResult(expression) else -9999
        for player in self.server.clients.values():
            if player.turnedIn is None: return
        self.stop()


