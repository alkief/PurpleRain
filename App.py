from game.PurpRain import PurpRain
from game import Const
from tkinter import Tk

import threading

if __name__ == '__main__':
    app = PurpRain(Const.TIMESTEP_MANUAL)
    app.start()
