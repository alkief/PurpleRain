from game.PurpRain import PurpRain
from game import Const

import threading
import sys

# Top level, define agent and game objects
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'random':
            from learn.RandomAgent import RandomAgent
            pr = PurpRain(Const.TIMESTEP_MANUAL, Const.CONTROLLER_OTHER)
            agent = RandomAgent(pr)
            agent.run()
        elif sys.argv[1] == 'serious':
            from learn.Agent import Agent
            pr = PurpRain(Const.TIMESTEP_MANUAL, Const.CONTROLLER_OTHER)
            agent = Agent(pr)
            agent.run()
    else:
        pr = PurpRain(Const.TIMESTEP_AUTO, Const.CONTROLLER_PLAYER)
        pr.start()
