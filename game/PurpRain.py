
from . import Engine
from . import Const

import threading
import logging
import time

class PurpRain():
    def __init__(self, step_mode=Const.TIMESTEP_VARIABLE, step_func=None):
        self.engine = Engine.Engine(step_mode)
        if step_func == None:
            self.step_func = self.infinite_step
        else:
            self.step_func = step_func

    def start(self):
        if self.engine.step_mode == Const.TIMESTEP_MANUAL:
            t = threading.Thread(target=self.step_func, daemon=True)
            t.start()
            self.engine.window.mainloop()
            # self.engine.window.mainloop()
        else:
            self.engine.window.mainloop()

    # infinitely step through the game, display updates then sleep 1/60th of a second
    def infinite_step(self):
        while True:
            while self.engine.state == None:
                time.sleep(1)
                while self.engine.in_game == True:
                    self.engine.step(0.1)
                    time.sleep(0.0167) # 1/60 of a second


    def n_step(self, n):
        pass
