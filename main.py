from tkinter import *

from frames.LoginFrame import LoginFrame
from frames.RegisterFrame import RegisterFrame
from frames.StartMenuFrame import StartMenuFrame
from frames.WaitingFrame import WaitingFrame
from games.client.Asocijacije import Asocijacije
from games.client.KoZnaZna import KoZnaZna
from games.client.MojBroj import MojBroj
from games.client.Slagalica import Slagalica
from games.client.Skocko import Skocko
from images import ImageProvider

parent = Tk()
parent.geometry('240x100')
parent.title("Login")

parent.columnconfigure(0, weight=1)
parent.columnconfigure(1, weight=3)

waitingFrame = Frame(parent, borderwidth=10)
waiting = WaitingFrame(parent, waitingFrame)
waiting.initialize()

startMenuFrame = Frame(parent, borderwidth=10)
startMenu = StartMenuFrame(parent, startMenuFrame)
startMenu.initialize()

registerFrame = Frame(parent, borderwidth=10)
register = RegisterFrame(parent, registerFrame)
register.initialize()

slagalicaFrame = Frame(parent, borderwidth=0)
slagalica = Slagalica(parent, slagalicaFrame)

mojBrojFrame = Frame(parent, borderwidth=0)
mojBroj = MojBroj(parent, mojBrojFrame)

skockoFrame = Frame(parent, borderwidth=0)
skocko = Skocko(parent, skockoFrame)

koZnaZnaFrame = Frame(parent, borderwidth=0)
koZnaZna = KoZnaZna(parent, koZnaZnaFrame)

asocijacijeFrame = Frame(parent, borderwidth=0)
asocijacije = Asocijacije(parent, asocijacijeFrame)

frameLogin = Frame(parent, borderwidth=10)
login = LoginFrame(parent, frameLogin)
login.initialize()
login.show()

ImageProvider.load()

parent.mainloop()
