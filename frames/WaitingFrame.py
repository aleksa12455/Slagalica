from frames.BaseFrame import BaseFrame1
from tkinter import *


class WaitingFrame(BaseFrame1):

    label = None

    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def initialize(self):
        self.label = Label(self.frame, text='Cekamo drugog igraca...')
        self.label.grid(pady=475)

    def show(self, shownFrom=None):
        super().show(shownFrom)
        self.parent.geometry('1000x1000')
        self.parent.title('Cekamo drugog igraca')
        self.parent.resizable(False, False)

    def connect(self, player):
        if self.label is not None: self.label['text'] = 'Drugi igrac je usao. Igra pocinje za 5 sekundi...'
        else: print('label is none')
