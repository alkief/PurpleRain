import Const
# import json

class Serializer():
    def __init__(self):
        self.file = 'game_trial.dat'
        f = open(self.file, 'w')

    def write(self, state):
        with open(self.file, 'a') as f:
            f.write('#\n')
            f.write(str(state))
