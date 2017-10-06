from . import Const

class GameState():
    # @Param{game.Entities.Hero} hero: The initialized hero entity for the game
    # @Param{game.Entities.Rain[]} rain: The set of rain entities existing within the game
    def __init__(self, hero, rain=[]):
        self.hero = hero
        self.difficulty = 0
        self.rain = rain
        self.score = 0
        self.optimal = -1000

    def __str__(self):
        s = str(self.score) + '\n' + str(self.hero) + '\n'
        for r in self.rain:
            s += str(r) + '\n'
        return s

    # Return a tuple to tell the window to draw the hero at starting location
    # @Param{boolean} include_optimal: Boolean to control whether to add
    #       the optimal hero location widget to the screen
    def initial_transition(self, include_optimal):
        raindrops = [(Const.DRAW_RAIN, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id) for r in self.rain]
        score = [(Const.DRAW_SCORE,)]

        if include_optimal:
            self.optimal = self.hero.bbox
            score += [(Const.DRAW_OPTIMAL, self.hero.bbox)]

        return [(Const.DRAW_HERO, self.hero.bbox)] + raindrops + score
