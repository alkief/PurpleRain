class Collision():
    def __init__(self, canvas):
        self.canvWidth = canvas.winfo_screenwidth()
        self.canvHeight = canvas.winfo_screenheight()

    def checkPlayerMove(self, hero, dx, dy):
        isValid = True

        if hero.bbox[0] + dx > self.canvWidth or hero.bbox[2] + dx > self.canvWidth:
            isValid = False
        elif hero.bbox[0] + dx < 0 or hero.bbox[2] + dx < 0:
            isValid = False
        elif hero.bbox[1] + dy > self.canvHeight or hero.bbox[3] + dy > self.canvHeight:
            isValid = False
        elif hero.bbox[1] + dy < 0 or hero.bbox[3] + dy < 0:
            isValid = False

        return isValid

    def check_death(self, canvas, state):
        isDead = False

        player_widget = canvas.find_withtag(state.hero.id)
        player_bbox  = canvas.bbox(player_widget)
        overlap = canvas.find_overlapping(player_bbox[0], player_bbox[1], player_bbox[2], player_bbox[3])

        if len(overlap) > 1:
            isDead = True

        return isDead

    def checkRainBounds(self, rain, dx, dy):
        isValid = True
        pass



        if rain.x + dx > self.canvWidth or rain.x + dx < 0:
            isValid = False
        elif rain.y + rain.length + dy > self.canvHeight:
            isValid = False

        return isValid
