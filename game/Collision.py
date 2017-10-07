from game import Const

class Collision():
    # @Param{int} width: The width of the game canvas
    # @Param{int} height: The height of the game canvas
    def __init__(self, width, height):
        self.canvWidth = width
        self.canvHeight = height

    # @Param{game.Entities.Hero} hero: The hero object within the game
    # @Param{int} dx: The attempted change in x position of the hero
    # @Param{int} dy: The attempted change in y position of the hero
    def checkPlayerMove(self, hero, dx, dy):
        if hero.bbox[2] + dx > self.canvWidth:
            dx = self.canvWidth - hero.bbox[2]
        if hero.bbox[0] + dx < 0:
            dx = hero.bbox[0]
        if hero.bbox[1] + dy > self.canvHeight or hero.bbox[3] + dy > self.canvHeight:
            isValid = False
        if hero.bbox[1] + dy < 0 or hero.bbox[3] + dy < 0:
            isValid = False

        valid_move = (dx, dy)
        return valid_move

    # @Param{game.Engine} engine: The current engine context of the game
    def check_death(self, engine):
        isDead = False
        if engine.is_hero_alive == True and engine.scene == Const.SCENE_INGAME:
            canv = engine.window.canvas
            try:
                player_widget = canv.find_withtag(engine.state.hero.id)
                player_bbox  = canv.bbox(player_widget)
                overlap = canv.find_overlapping(player_bbox[0], player_bbox[1], player_bbox[2], player_bbox[3])
                for x in overlap:
                    if 'rain' in canv.gettags(x):
                        isDead = True
            except:
                pass

        return isDead


    # @Param{game.Entities.Rain} rain: The rain entity being moved
    # @Param{int} dx: The attempted change in X position of the rain entity
    # @Param{int} dy: The attempted change in Y position of the rain entity
    def checkRainBounds(self, rain, dx, dy):
        isValid = True

        if rain.x + dx > self.canvWidth or rain.x + dx < 0:
            isValid = False
        elif rain.y + rain.length + dy > self.canvHeight:
            isValid = False

        return isValid
