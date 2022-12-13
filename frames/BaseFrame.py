from tkinter import *
from abc import abstractmethod

frames = {}


class BaseFrame1:
    parent: Tk
    frame: Frame
    shownFrom: Frame

    def __init__(self, parent: Tk, frame: Frame):
        self.parent = parent
        self.frame = frame
        frames[self.__class__.__name__.replace('Frame', '').lower()] = self

    @abstractmethod
    def initialize(self):
        pass

    def createLabel(self, text=''):
        return Label(self.frame, text=text)

    def createEntry(self, variable: Variable = None, show=''):
        return Entry(self.frame, textvariable=variable, show=show)

    def hide(self):
        self.frame.pack_forget()
        self.frame.destroy()

    def show(self, shownFrom=None):
        self.shownFrom = shownFrom
        if shownFrom is not None:
            shownFrom.hide()
        self.frame.pack(fill=BOTH, side=BOTTOM, expand=True)
