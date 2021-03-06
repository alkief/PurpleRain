from . import Const
import random

class Entity():
    # @Param x{integer}: The starting x location of the entity
    # @Param y{integer}: The starting y location of the entity
    # @Param vel_x{integer}: The entity speed in the x direction
    # @Param vel_y{integer}: The starting x location of the entity
    # @Param velocity{integer}: Entity velocity
    def __init__(self, x=0, y=0, vel_x=0, vel_y=0):
        self.type = Const.ENTITY
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y

    def __str__(self):
        return str(self.type) + ' ' + str(self.x) + ' ' + str(self.y) + ' ' + str(self.vel_x) + ' ' + str(self.vel_y)

    # @Param dx{integer}: The change in x position including sign
    # @Param dy{integer}: The change in y position including sign
    def move(self, dx=None, dy=None):
        if dx==None and dy==None:
            pass
        elif dx==None:
            self.y = self.y + dy
        elif dy==None:
            self.x = self.x + dx
        else:
            self.x = self.x + dx
            self.y = self.y + dy

class Hero(Entity):
    # @Inherited{Entity} x
    # @Inherited{Entity} y
    # @Inherited{Entity} vel_x
    # @Inherited{Entity} vel_y
    def __init__(self, x=0, y=0, vel_x=50, vel_y=0):
        Entity.__init__(self, x, y, vel_x, vel_y)
        self.type = Const.ENTITY_HERO
        self.id = 'hero'

        self.bbox = ((self.x - (Const.PLAYER_WIDTH // 2)), (self.y - Const.PLAYER_HEIGHT),
                     (self.x + (Const.PLAYER_WIDTH // 2)), (self.y))

    def __str__(self):
        return super().__str__() + ' ' + str(self.bbox[0]) + ' ' + str(self.bbox[1]) + ' ' + str(self.bbox[2]) + ' ' + str(self.bbox[3])

     # @Inherited: Entity
    def move(self, dx=None, dy=None):
        super().move(dx, dy)
        self.bbox = ((self.bbox[0] + dx), (self.bbox[1] + dy), (self.bbox[2] + dx), (self.bbox[3] + dy))


class Rain(Entity):
    # @Inherited{Entity} x
    # @Inherited{Entity} y
    # @Inherited{Entity} vel_x
    # @Inherited{Entity} vel_y
    def __init__(self, drop_id=None, x=0, y=0, vel_x=0, vel_y=-1):
        Entity.__init__(self, x, y, vel_x, vel_y)
        self.type = Const.ENTITY_RAIN
        self.id = drop_id
        self.vel_y = random.randint(30, 40)
        self.length = random.randint(10, 30)

    def __str__(self):
        return super().__str__() + ' ' + str(self.length)

    def reset(self, x, y):
        self.x = x
        self.y = y

    # @Inherited: Entity
    def move(self, dx=None, dy=None):
        super().move(dx, dy)
