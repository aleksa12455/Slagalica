from frames.BaseFrame import BaseFrame1
from tkinter import *
import frames.BaseFrame as BaseFrame


class LoginFrame(BaseFrame1):
    username = None
    password = None

    def __init__(self, parent, frame):
        super().__init__(parent, frame)
        print('login frame created')
        self.username = Variable(parent)
        self.password = Variable(parent)

    def initialize(self):
        usernameLabel = self.createLabel("Username:")
        passwordLabel = self.createLabel('Password:')
        usernameLabel.grid(row=0, column=0, sticky=W)
        passwordLabel.grid(row=1, column=0, sticky=W)

        usernameEntry = self.createEntry(self.username)
        usernameEntry.grid(row=0, column=1, padx=5, pady=2, sticky=E)

        passwordEntry = self.createEntry(self.password, show='*')
        passwordEntry.grid(row=1, column=1, padx=5, pady=2, sticky=E)

        button = Button(self.frame, text='Login', command=lambda: self.login(self.username.get(), self.password.get()))
        button.grid(row=3, column=1, pady=5, padx=10, sticky=E)

        registerButton = Button(self.frame, text='Register', command=self.register)
        registerButton.grid(row=3, column=0, pady=10, padx=5, sticky=W)

    def show(self, shownFrom=None):
        super().show(shownFrom)
        self.parent.geometry('280x120')

    def login(self, username, password):
        print(f'{username} {password}')
        BaseFrame.frames['startmenu'].show(self)

    def register(self):
        BaseFrame.frames['register'].show(self)
