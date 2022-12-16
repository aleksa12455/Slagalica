import ast
import json
import random
from abc import ABC
import time

from SlagalicaServer import PacketType, Player
from games.server.ServerGame import ServerGame


class Answer:

    def __init__(self, playerId, answer, time):
        self.playerId = playerId
        self.answer = answer
        self.time = time

class KoZnaZna(ServerGame, ABC):

    endGameHandle = None
    checkAnswersHandle = None

    allQuestions = None
    chosenQuestions = []
    currentQuestion = 0

    def __init__(self, name, server):
        super().__init__(name, server)
        self.startTime = None
        with open('games/server/Pitanja.json', 'r') as questionsFile:
            if len(questionsFile.readlines()) != 0:
                questionsFile.seek(0)
                self.allQuestions = json.load(questionsFile)['pitanja']

    def initialize(self):
        pass

    def generate(self):
        self.chosenQuestions.clear()
        for i in range(5):
            # n = random.randint(0, len(self.allQuestions)-1)
            self.chosenQuestions.append(self.allQuestions[i])
        return self.chosenQuestions

    def start(self, color):
        super().start(color)
        if self.color is None: return
        self.startTime = self.getNow()
        for player in self.server.clients.values():
            player.turnedIn = None
        self.generate()
        self.active = True
        self.server.send_message(self.createPacket(PacketType.GAME_START, ('igra', 'ko_zna_zna'), ('boja', color)))
        self.endGameHandle = self.server.getIOLoop().IOLoop.current().call_later(120, lambda: self.stop() if self.active else None)
        self.nextQuestion()

    def forceStop(self):
        super().forceStop()
        if self.endGameHandle is not None: self.endGameHandle.cancel()
        if self.checkAnswersHandle is not None: self.checkAnswersHandle.cancel()

    def stop(self):
        self.active = False
        self.endGameHandle.cancel()
        self.server.send_message(self.createPacket(PacketType.GAME_END))
        self.next()

    def nextQuestion(self):
        print(self.currentQuestion)
        if self.currentQuestion >= 5:
            self.stop()
            return
        self.currentQuestion += 1
        for player in self.server.clients.values():
            player.turnedIn = None
        question = self.chosenQuestions[self.currentQuestion-1]
        self.startTime = self.getNow()
        self.checkAnswersHandle = self.server.getIOLoop().IOLoop.current().call_later(10, lambda: self.checkAnswers())
        self.server.send_message(self.createPacket(PacketType.TURN_CHANGE, ('player', str(list(self.server.clients.keys())[0])), ('pitanje', question['pitanje']), ('odgovori', question['odgovori'])))



    def checkAnswers(self):
        self.checkAnswersHandle.cancel()
        answers = []
        winner = None
        losers = []
        for player in self.server.clients.values():
            answer = player.turnedIn
            if answer is None or answer.answer == 'DALJE': continue
            answers.append(Answer(str(player.id), answer.answer, answer.time).__dict__)
            if not self.isCorrect(answer):
                losers.append(player)
                continue
            if winner is None:
                winner = (player, answer)
                continue
            else:
                if answer.time < winner[1].time:
                    winner = (player, answer)
        if winner is not None:
            winner[0].score += 6
            self.server.send_message(self.createPacket(PacketType.UPDATE_SCORE, ('id', str(winner[0].id)), ('score', winner[0].score)))
        for loser in losers:
            loser.score = loser.score-3
            self.server.send_message(self.createPacket(PacketType.UPDATE_SCORE, ('id', str(loser.id)), ('score', loser.score)))
        self.server.send_message(self.createPacket(PacketType.TURNED_IN, ('odgovori', answers), ('tacanOdgovor', self.chosenQuestions[self.currentQuestion-1]['tacanOdgovor'])))
        self.server.getIOLoop().IOLoop.current().call_later(5, lambda: self.nextQuestion() if self.currentQuestion <= 10 else self.stop())

    def isCorrect(self, answer):
        if answer.time > 10: return False
        return answer.answer == self.chosenQuestions[self.currentQuestion-1]['tacanOdgovor']

    def handleTurnIn(self, player: Player, packet):
        if player.turnedIn is not None: return

        answer = Answer(player, packet['odgovor'], (self.getNow()-self.startTime))
        player.turnedIn = answer
        for player in self.server.clients.values():
            if player.turnedIn is None: return
        self.checkAnswers()

    def getNow(self):
        return time.time()