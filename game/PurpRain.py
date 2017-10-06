from . import Engine
from . import Const

import threading
import logging
import time

class PurpRain():
    def __init__(self, step_mode=Const.TIMESTEP_AUTO, controller=Const.CONTROLLER_PLAYER):
        self.engine = Engine.Engine(step_mode, controller)

    # Begin normal gameplay if the engine is configured with an automatic timestep
    def start(self):
        if self.engine.step_mode == Const.TIMESTEP_MANUAL:
            pass
        else:
            self.engine.gameloop()

    # Returns True iff the hero is flagged as alive, and the engine scene is
    #       marked as in-game
    def is_in_game(self):
        if self.engine.scene == Const.SCENE_INGAME and self.engine.is_hero_alive == True:
            return True
        else:
            return False

    # Utility function to refresh the game screen
    def refresh_screen(self):
        self.engine.window.canvas.update()
        self.engine.window.canvas.update_idletasks()

    # Defines a method by which some controller may advance the game in time
    #       by some amount
    # Returns a tuple containing:
    #       The game state after stepping
    #       The reward for stepping through the game with the given inputs
    #       A boolean signaling whether the game is over (player lost)
    def step(self, dt=0.1):
        if self.engine.scene == Const.SCENE_INGAME and self.engine.is_hero_alive:
            step_update = self.engine.step(dt)
        else:
            step_update = (0, 0, True)

        return step_update
