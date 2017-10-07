from . import Const
from game import Transitions



class GameState():
    # @Param{game.Entities.Hero} hero: The initialized hero entity for the game
    # @Param{game.Entities.Rain[]} rain: The set of rain entities existing within the game
    def __init__(self, hero, rain=[]):
        self.hero = hero
        self.difficulty = 0
        self.rain = rain
        self.score = 0
        self.optimal = None

    def __str__(self):
        s = str(self.score) + '\n' + str(self.hero) + '\n'
        for r in self.rain:
            s += str(r) + '\n'
        return s

    # Return a tuple to tell the window to draw the hero at starting location
    # @Param{boolean} include_optimal: Boolean to control whether to add
    #       the optimal hero location widget to the screen
    def initial_transition(self, include_optimal):
        t = []
        # Draw initial hero on screen
        t.append(Transitions.DrawHeroTransition(Const.DRAW_HERO, (self.hero.bbox)))
        # Draw initial raindrops
        for r in self.rain:
            t.append(Transitions.DrawRainTransition(Const.DRAW_RAIN, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id))

        t.append(Transitions.DrawScoreTransition(Const.DRAW_SCORE))

        if include_optimal:
            self.optimal = self.hero.bbox
            t.append(Transitions.DrawOptimalHero(Const.DRAW_OPTIMAL, self.optimal))

        return t
