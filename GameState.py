import Const

class GameState():
    # @Param window{tuple}: of type (window_width{int}, window_height{int})
    def __init__(self, hero, rain=[]):
        self.player_direction = 0
        self.hero = hero
        self.difficulty = 0
        self.rain = rain
        self.score = 0

    def __str__(self):
        s = str(self.score) + '\n' + str(self.hero) + '\n'
        # s += 'Rain:\n'
        for r in self.rain:
            s += str(r) + '\n'

        return s
    def reset(self):
        self.player_direction = 0
        self.hero = Hero(window[0] // 2, window[1])
        self.rain = []
        self.score = 0

        # @Param direction {integer}: 0 for no input, -1 for left, 1 for right movement
    def setPlayerDirection(self, direction):
        self.player_direction = direction

        # Return a tuple to tell the window to draw the hero at starting location
    def initial_transition(self):
        raindrops = [(Const.DRAW_RAIN, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id) for r in self.rain]
        score = [(Const.DRAW_SCORE,)]
        return [(Const.DRAW_HERO, self.hero.bbox)] + raindrops + score
