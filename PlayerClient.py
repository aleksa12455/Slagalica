from enum import Enum

from tornado import websocket
import json
import games.client.Game
from frames import BaseFrame
import uuid


class Player:
    id = None
    score = 0
    name = ''
    color = None

    def __init__(self, name):
        self.name = name

class PlayerColor(Enum):
    RED = 0
    BLUE = 1

class Client:

    player = None
    opponent = None
    game = None
    turnedIn = False

    def __init__(self, io_loop):
        self.connection = None
        self.io_loop = io_loop
        self.num_successes = 0
        self.num_trials = 0

    def start(self):
        self.connect_and_read()

    def stop(self):
        self.io_loop.stop()

    def connect_and_read(self):
        print("Reading...")
        websocket.websocket_connect(
            url=f"ws://localhost:8888/websocket/",
            callback=self.maybe_retry_connection,
            on_message_callback=self.on_message,
            ping_interval=10,
            ping_timeout=30,
        )

    def maybe_retry_connection(self, future) -> None:
        try:
            self.connection = future.result()
        except:
            print("Could not reconnect, retrying in 3 seconds...")
            self.io_loop.call_later(3, self.connect_and_read)

    def on_message(self, m):
        if m is None or str(m) == 'None':
            print("Disconnected, reconnecting...")
            self.connect_and_read()
            pass

        print('received: ' + str(m))
        message = json.loads(m)
        packetType = message['type']
        if packetType == 'GAME_START':
            self.handleGameStart(message)
        elif packetType == 'PLAYER_CONNECT':
            if self.player is None:
                self.player = Player(message['name'])
                self.player.id = uuid.UUID(message['id'])
                self.player.color = message['color']
                protivnik = message['protivnik']
                if len(protivnik) > 0:
                    id = protivnik['id']
                    name = protivnik['name']
                    color = protivnik['color']
                    self.opponent = Player(name)
                    self.opponent.id = uuid.UUID(id)
                    self.opponent.color = color
                    BaseFrame.frames['waiting'].connect(self.opponent)
                BaseFrame.frames['waiting'].show(BaseFrame.frames['startmenu'])
            else:
                self.opponent = Player(message['name'])
                self.opponent.id = uuid.UUID(message['id'])
                self.opponent.color = message['color']
                BaseFrame.frames['waiting'].connect(self.opponent)
        elif packetType == "GAME_END":
            self.game.stop()
            self.game.handleGameEnd(message)
        elif packetType == "UPDATE_SCORE":
            score = message['score']
            player = self.getPlayerById(uuid.UUID(message['id']))
            player.score = score
            if player.color == 'BLUE':
                self.game.blueScore['text'] = score
                print('blue score')
            else:
                self.game.redScore['text'] = score
                print('red score')
        elif packetType == "TURNED_IN":
            self.game.handleTurnedIn(message)
        elif packetType == 'TURN_CHANGE':
            self.game.setTurn(self.getPlayerById(uuid.UUID(message['player'])), message)

    def handleGameStart(self, packet):
        game = packet['igra']
        match game:
            case 'slagalica':
                slagalica = games.client.Game.games['Slagalica']
                self.game = slagalica
                slagalica.start(self)
                slagalica.setLetters(packet['slova'])
                slagalica.show(BaseFrame.frames['waiting'])
            case 'moj_broj':
                print("starting moj broj")
                mojBroj = games.client.Game.games['Moj Broj']
                self.game = mojBroj
                mojBroj.start(self)
                mojBroj.setTarget(packet['rezultat'])
                mojBroj.setNumbers(packet['brojevi'])
                mojBroj.show(games.client.Game.games['Slagalica'])
            case 'skocko':
                print("starting skocko")
                skocko = games.client.Game.games['Skocko']
                color = packet['boja']
                self.game = skocko
                self.game.setTurn(self.getPlayer(PlayerColor[color]), packet)
                skocko.start(self)
                skocko.show(games.client.Game.games['Moj Broj'])
                # skocko.show(BaseFrame.frames['waiting'])
            case 'ko_zna_zna':
                print("starting skocko")
                kzz = games.client.Game.games['Ko Zna Zna']
                color = packet['boja']
                self.game = kzz
                self.game.setTurn(self.getPlayer(PlayerColor[color]), packet)
                kzz.start(self)
                kzz.show(games.client.Game.games['Skocko'])
                # kzz.show(BaseFrame.frames['waiting'])
            case 'asocijacije':
                print("starting asocijacije")
                asocijacije = games.client.Game.games['Asocijacije']
                color = packet['boja']
                self.game = asocijacije
                self.game.setTurn(self.getPlayer(PlayerColor[color]), packet)
                asocijacije.start(self)
                asocijacije.show(games.client.Game.games['Ko Zna Zna'])
                # asocijacije.show(BaseFrame.frames['waiting'])

    def handleGameEnd(self):
        if not self.turnedIn: self.connection.write_message(json.dumps(self.game.createTurnInPacket()))

    def getPlayer(self, color: PlayerColor):
        if self.player.color == color.name: return self.player
        return self.opponent

    def getPlayerById(self, id: uuid.UUID):
        if self.player.id == id: return self.player
        return self.opponent