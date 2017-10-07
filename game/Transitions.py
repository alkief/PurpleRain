from game import Const

# Class used to respresent updates made to the tkinter Canvas in place of
#       destroying and recreating widgets each update to the frame

class Transition():
    # @Param{int} type: The type of change being made to the canvas. Can be:
    #       Integers for each transition type are defined in game.Const
    def __init__(self, t):
        self.type = t

class DrawHeroTransition(Transition):
    # @Inherited{t} Transition
    def __init__(self, t, bbox):
        super().__init__(t)
        self.bbox = bbox

class DrawRainTransition(Transition):
    # @Inherited{t} Transition
    def __init__(self, t, x, y, vel_x, vel_y, length, rain_id):
        super().__init__(t)
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.length = length
        self.rain_id = rain_id

class DrawScoreTransition(Transition):
    # @Inherited{t} Transition
    def __init__(self, t):
        super().__init__(t)

class DrawOptimalHero(Transition):
    # @Inherited{t} Transition
    def __init__(self, t, bbox):
        super().__init__(t)
        self.bbox = bbox

class MoveEntityTransition(Transition):
    # @Inherited{t} Transition
    def __init__(self, t, tag, dx, dy):
        super().__init__(t)
        self.tag = tag
        self.dx = dx
        self.dy = dy

class UpdateScoreTransition(Transition):
    # @Inherited{t} Transition
    def __init__(self, t, new_score):
        super().__init__(t)
        self.new_score = new_score
