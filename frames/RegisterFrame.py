import frames.BaseFrame as BaseFrame
from frames.BaseFrame import *


class RegisterFrame(BaseFrame1):
    username = None
    password = None
    repeatedPassword = None

    def __init__(self, parent, frame):
        super().__init__(parent, frame)
        print('register frame created')
        self.username = Variable(parent)
        self.password = Variable(parent)
        self.repeatedPassword = Variable(parent)

    def initialize(self):
        usernameLabel = self.createLabel("Username:")
        passwordLabel = self.createLabel('Password:')
        repeatPasswordLabel = self.createLabel('Repeat Password:')
        usernameLabel.grid(row=0, column=0, sticky=W)
        passwordLabel.grid(row=1, column=0, sticky=W)
        repeatPasswordLabel.grid(row=2, column=0, sticky=W)

        usernameEntry = self.createEntry(self.username)
        usernameEntry.grid(row=0, column=1, padx=5, pady=2, sticky=E)

        passwordEntry = self.createEntry(self.password, show='*')
        passwordEntry.grid(row=1, column=1, padx=5, pady=2, sticky=E)

        repeatPasswordEntry = self.createEntry(self.repeatedPassword, show='*')
        repeatPasswordEntry.grid(row=2, column=1, padx=5, pady=2, sticky=E)

        loginButton = Button(self.frame, text='Login',
                             command=self.login)
        loginButton.grid(row=3, column=0, pady=10, padx=5, sticky=W)

        registerButton = Button(self.frame, text='Register',
                                command=self.register)
        registerButton.grid(row=3, column=1, pady=5, padx=5, sticky=E)

    def show(self, shownFrom=None):
        self.parent.geometry('280x145')
        self.parent.title('Register')
        super().show(shownFrom)

    def register(self, username, password, repeatedPassword):
        print(f'{username} {password} {repeatedPassword}')

    def login(self):
        BaseFrame.frames['login'].show(self)
