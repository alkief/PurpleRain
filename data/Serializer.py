from game import Const

class Serializer():
    def __init__(self):
        self.file = 'data/game_trial.dat'
        f = open(self.file, 'w')

    def write(self, engine):
        with open(self.file, 'a') as f:
            f.write('#\n')
            f.write(str(engine))
