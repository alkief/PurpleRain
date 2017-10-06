import random
from game import Const
class RandomAgent():
    def __init__(self, app):
        self.app = app

    def run(self):
        while True:
            if self.app.is_in_game():
                self.app.engine.player_direction = random.choice([0, 1, -1])
                self.app.step()
            elif self.app.engine.scene == Const.SCENE_MAINMENU: # At menu screen
                self.app.engine.wait_menu_input()
            self.app.refresh_screen()

            if self.app.engine.is_hero_alive == False:
                self.app.engine.start()
