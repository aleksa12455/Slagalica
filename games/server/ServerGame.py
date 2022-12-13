from abc import abstractmethod

import SlagalicaServer
from SlagalicaServer import PacketType


class ServerGame:

    server: SlagalicaServer = None
    name = None
    active = False
    color = None

    def __init__(self, name, server):
        self.name = name
        self.server = server
        self.initialize()

    def createPacket(self, packetType: PacketType, *values):
        packet = {
            'type': packetType.name,
            'game': self.name
        }
        for value in values:
            packet[value[0]] = value[1]
        return packet

    def sendTurnChangePacket(self, player, *values):
        packet = {
            'type': PacketType.TURN_CHANGE.name,
            'game': self.name,
            'player': str(player.id)
        }
        for value in values:
            packet[value[0]] = value[1]
        self.server.send_message(packet)

    def start(self, color):
        if self.color == 'RED' and color == 'RED':
            self.next()
        else: self.color = color

    def next(self):
        self.server.nextGame()
        self.server.getGame().start('BLUE')
        # print('starting ' + self.server.getGame())
        self.color = None

    @abstractmethod
    def initialize(self):
        pass

    def stop(self):
        pass

    @abstractmethod
    def handleTurnIn(self, player, packet):
        pass