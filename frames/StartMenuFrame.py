from tornado import ioloop
from PlayerClient import Client
from frames.BaseFrame import BaseFrame1
from tkinter import *
import asyncio


class StartMenuFrame(BaseFrame1):

    def __init__(self, parent, frame):
        super().__init__(parent, frame)

    def initialize(self):
        button = Button(self.frame, text='Igraj', command=self.play)
        button.place(x=140, y=60, anchor=CENTER)

    def show(self, shownFrom=None):
        super().show(shownFrom)
        self.parent.geometry('280x120')
        self.parent.title('Igraj')
        self.parent.resizable(False, False)

    def play(self):
        import threading
        t = threading.Thread(target=self.connect_to_socket)
        t.start()

    def connect_to_socket(self):
        from tornado.platform.asyncio import AnyThreadEventLoopPolicy
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
        io_loop = ioloop.IOLoop.current()
        client = Client(io_loop)
        io_loop.add_callback(client.start)
        io_loop.start()
        return