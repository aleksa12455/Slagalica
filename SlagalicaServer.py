import uuid
from typing import Any

import tornado.ioloop
import tornado.web
import tornado.websocket
import json
from enum import Enum
from tornado import httputil

class Player:
    client = None
    id = None
    name = None
    score = 0
    turnedIn = None
    color = None

    def __init__(self, client, id, name, color):
        self.turn = 1
        self.client = client
        self.id = id
        self.name = name
        self.color = color

class Server(tornado.websocket.WebSocketHandler):

    class Game(Enum):
        SLAGALICA = 0
        MOJ_BROJ = 1
        SKOCKO = 2
        KO_ZNA_ZNA = 3
        ASOCIJACIJE = 4

    clients = {

    }

    games = []

    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)

        from games.server.Slagalica import Slagalica
        from games.server.MojBroj import MojBroj
        from games.server.Skocko import Skocko
        from games.server.KoZnaZna import KoZnaZna
        from games.server.Asocijacije import Asocijacije

        self.games.append(Slagalica('Slagalica', self))
        self.games.append(MojBroj('MojBroj', self))
        self.games.append(Skocko('Skocko', self))
        self.games.append(KoZnaZna('KoZnaZna', self))
        self.games.append(Asocijacije('Asocijacije', self))

        self.game = self.games[0]

    def open(self):
        if len(self.clients) >= 2:
            self.close()
            return
        name = f'player{len(self.clients)+1}'
        playerId = uuid.uuid4()
        protivnik = {}
        color = 'BLUE'
        if len(self.clients) > 0:
            for id, player in self.clients.items():
                protivnik['id'] = str(id)
                protivnik['name'] = player.name
                protivnik['color'] = 'BLUE'
                color = 'RED'
                break
        self.clients[playerId] = Player(self, playerId, name, color)
        self.send_message(createPacket(PacketType.PLAYER_CONNECT, ('id', str(playerId)), ('name', name), ('color', color), ('protivnik', protivnik)))
        if len(self.clients) == 2:
            self.getCurrentGame().start('BLUE')

    def on_close(self):
        toRemove = None
        for id, player in self.clients.items():
            if player.client == self:
                toRemove = id
                break
        if toRemove is not None:
            self.clients.pop(toRemove)
            self.sendForceStop()
            self.reloadGames()

    @classmethod
    def send_message(cls, packet, client=None):
        message = json.dumps(packet)
        print(f"Sending message {message} to {len(cls.clients)} client(s).")
        if client is not None:
            client.write_message(message)
            pass
        else:
            for player in cls.clients.values():
                player.client.write_message(message)

    def on_message(self, message: str):
        try:
            packet = json.loads(message)
        except:
            return
        if packet is None: return
        if packet['type'] == 'TURN_IN':
            self.handleTurnIn(packet)

    def nextGame(self):
        g = 0
        for i in range(len(self.games)):
            if self.game == self.games[i]:
                g = i
                break
        game = self.games[g+1]
        self.game = game
        print(f'setting game to {game}')

    def getGame(self):
        return self.game

    def handleTurnIn(self, packet):
        player = self.clients[uuid.UUID(packet['player'])]
        if player is None: return
        game = packet['game']
        if game == 'Slagalica':
            self.games[0].handleTurnIn(player, packet)
        elif game == 'Moj Broj':
            self.games[1].handleTurnIn(player, packet)
        elif game == 'Skocko':
            self.games[2].handleTurnIn(player, packet)
        elif game == 'Ko Zna Zna':
            self.games[3].handleTurnIn(player, packet)
        elif game == 'Asocijacije':
            self.games[4].handleTurnIn(player, packet)


    def getCurrentGame(self):
        return self.getGame()

    def getIOLoop(self):
        return tornado.ioloop

    def reloadGames(self):
        for game in self.games:
            game.forceStop()
        from games.server.Slagalica import Slagalica
        from games.server.MojBroj import MojBroj
        from games.server.Skocko import Skocko
        from games.server.KoZnaZna import KoZnaZna
        from games.server.Asocijacije import Asocijacije

        self.games.clear()
        self.games.append(Slagalica('Slagalica', self))
        self.games.append(MojBroj('MojBroj', self))
        self.games.append(Skocko('Skocko', self))
        self.games.append(KoZnaZna('KoZnaZna', self))
        self.games.append(Asocijacije('Asocijacije', self))

        self.game = self.games[0]

    def sendForceStop(self):
        self.send_message(createPacket(PacketType.FORCE_STOP))

class PacketType(Enum):
    PLAYER_CONNECT = 0
    GAME_START = 1
    GAME_END = 2
    UPDATE_SCORE = 3
    TURNED_IN = 4
    TURN_CHANGE = 5
    FORCE_STOP = 6

def createPacket(packetType, *values):
    packet = {
        'type': packetType.name
    }
    for value in values:
        packet[value[0]] = value[1]
    return packet


def main():
    app = tornado.web.Application(
        [(r"/websocket/", Server)],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
    )
    app.listen(43110)

    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()


if __name__ == "__main__":
    main()
