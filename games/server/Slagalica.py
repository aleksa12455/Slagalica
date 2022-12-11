import time
from abc import ABC

import numpy as np

from SlagalicaServer import PacketType, Player
from games.server.ServerGame import ServerGame

class Slagalica(ServerGame, ABC):

    recnikFile = None
    recnik = None
    endGameHandle = None

    slova = {
        'A': 11.3,
        'I': 9.3,
        'O': 8.9,
        'E': 8.8,
        'N': 5,
        'S': 4.7,
        'T': 4.5,
        'R': 4,
        'U': 3.9,
        'M': 4,
        'D': 3.9,
        'V': 3.7,
        'K': 3.6,
        'L': 3.3,
        'J': 3.1,
        'P': 2,
        'G': 2,
        'Z': 1.8,
        'B': 1.7,
        'Š': 1.5,
        'Č': 1.2,
        'Ć': 1,
        'C': 1,
        'Lj': 1,
        'Nj': 1,
        'H': 1,
        'Ž': 0.9,
        'Đ': 0.7,
        'F': 0.6,
        'Dž': 0.5
    }

    letters = []

    longestWord = ''

    def __init__(self, name, server):
        super().__init__(name, server)
        self.recnikFile = open('recnik.txt')
        self.recnik = self.recnikFile.read()

    def initialize(self):
        pass

    def generateLetters(self):
        letters = []
        chances = []
        for letter, chance in self.slova.items():
            letters.append(letter)
            chances.append(chance)
        chances = np.array(chances)
        chances /= chances.sum()
        return np.random.choice(letters, size=12, replace=False, p=chances)

    def validateWord(self, word: str, checkDictionary=True):
        letters = self.letters.tolist()
        i = 0
        skip = False
        validWord = ''
        for l in word:
            if skip:
                skip = False
                continue
            letter = l.upper()
            if (letter == 'N' or letter == 'L' or letter == 'D') and i < len(word) - 1:
                if word[i + 1] == 'j':
                    if (letter + 'j') not in letters: return ''
                    letters.remove(letter + 'j')
                    validWord += letter + 'j'
                    skip = True
                    i += 2
                    continue
                if word[i + 1] == 'ž':
                    if (letter + 'ž') not in letters: return ''
                    letters.remove(letter + 'ž')
                    validWord += letter + 'ž'
                    skip = True
                    i += 2
                    continue
            if letter.upper() not in letters:
                return ''
            letters.remove(letter)
            validWord += letter
            i += 1
        if checkDictionary:
            return validWord if (validWord.lower() in self.recnik) else ''
        return validWord

    def calculateLongestWord(self):
        print('calculating')
        start = time.time()
        words = self.recnik.split('\n')
        longest = ''
        for word in words:
            valid = self.validateWord(word, checkDictionary=False)
            if valid != '':
                if len(word) == 12:
                    print(valid)
                    return valid
                if len(word) > len(longest): longest = valid
        end = time.time()
        print(end - start)
        print(longest)
        return longest

    def start(self, color):
        super().start(color)
        if self.color is None: return
        for player in self.server.clients.values():
            player.turnedIn = None
        self.letters = self.generateLetters()
        self.active = True
        self.longestWord = self.calculateLongestWord()
        self.server.send_message(self.createPacket(PacketType.GAME_START, ('igra', 'slagalica'), ('slova', self.letters.tolist())))
        self.endGameHandle = self.server.getIOLoop().IOLoop.current().call_later(60, lambda: self.stop() if self.active else None)

    def stop(self):
        self.active = False
        self.endGameHandle.cancel()
        longerWord = None
        for player in self.server.clients.values():
            if player.turnedIn is None:
                player.turnedIn = ''
                continue
            wordLength = len(player.turnedIn)
            if longerWord is not None and wordLength == longerWord[1]:
                if longerWord[0].color == self.server.getCurrentGame().color: continue
                longerWord = (player, wordLength)
                continue
            if longerWord is None or wordLength > longerWord[1]:
                longerWord = (player, wordLength)
        words = {}
        for player in self.server.clients.values():
            player.score += len(player.turnedIn)*2
            if longerWord is not None and longerWord[0] == player:
                player.score = player.score + 6
            else:
                print(str(longerWord is not None) + ' ' + str(longerWord[0] == player))
            packet = self.createPacket(PacketType.UPDATE_SCORE, ('id', str(player.id)), ('score', player.score))
            words[str(player.id)] = player.turnedIn
            self.server.send_message(packet)
        self.server.send_message(self.createPacket(PacketType.GAME_END, ('najduza', self.longestWord), ('resenje', words)))
        self.server.getIOLoop().IOLoop.current().call_later(5, lambda: self.start('RED'))

    def handleTurnIn(self, player: Player, packet):
        word = packet['rec']
        player.turnedIn = word if self.validateWord(word) else ""
        for player in self.server.clients.values():
            if player.turnedIn is None: return
        self.stop()


