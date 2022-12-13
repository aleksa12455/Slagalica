from PIL import ImageTk, Image
import tkinter

def get(name, size):
    return images[name].resize(size)

def open(path):
    return Image.open(path)

def getTkinterImage(path, size):
    img = open(path).resize(size)
    return ImageTk.PhotoImage(img)

def load():
    global images
    images = {
        'delete': getTkinterImage('images/buttons/delete.png', (80, 80)),
        'delete_small': getTkinterImage('images/buttons/delete.png', (50, 50)),
        'skocko': getTkinterImage('images/skocko/skocko.png', (80, 80)),
        'tref': getTkinterImage('images/skocko/tref.png', (80, 80)),
        'pik': getTkinterImage('images/skocko/pik.png', (80, 80)),
        'herc': getTkinterImage('images/skocko/herc.png', (80, 80)),
        'karo': getTkinterImage('images/skocko/karo.png', (80, 80)),
        'zvezda': getTkinterImage('images/skocko/zvezda.png', (80, 80)),
    }

images = {

}
