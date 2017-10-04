from . import Window
from . import GameState
from . import Entities
from . import Collision
from . import Const
from data import Serializer

import threading
import time
import random
import string

class Engine():
    def __init__(self, step_mode=Const.TIMESTEP_VARIABLE):
        self.step_mode=step_mode

        self.state = None # Current copy of the game state
        self.player_direction = 0

        self.steps = [] # (state, transition)

        # Engine controls for exiting main gameloop
        self.in_game = False
        self.is_hero_alive = False

        # Self-defined modules
        self.window = Window.Window() # Create the window class
        self.collision = Collision.Collision(self.window.canvas)
        self.serializer = Serializer.Serializer()

        self.registerListeners() # Set listeners for keybindings

        self.window.canvas.after(100, self.mainMenu) # Display the main menu

        # The main game loop. Responsible for making performing calculations for
        #       graphics changes, collision detection, scoring, difficulty
    def gameloop(self):
        # Set time-step controls
        dt = 0.01
        frame_rate = 30
        frameMS = 100 / frame_rate
        startTime = time.time()
        endTime = time.time()

        while self.in_game == True and self.is_hero_alive == True:
            if dt < 0.000001 and self.step_mode == 0:
                startTime = time.time()
                time.sleep(0.000001)
                endTime = time.time()
                dt = endTime - startTime

            startTime = time.time()

            # Check for and trigger difficulty increase

            self.step(dt)

            endTime = time.time()

            if self.step_mode == 0:
                dt = endTime - startTime
            self.serializer.write(self.state)


        # Exit loop
        if self.in_game == False:
            self.state = None
            self.mainMenu() # Return to the main menu after game exits
        elif self.is_hero_alive == False:
            print('game lost with hero death, serializing state')
            self.serializer.write(self.state)
            self.state = None
            self.start()
        else:
            self.start()

    def step(self, dt):
        # Update state, return the new state and the transitions used to get there
        stateUpdate = self.integrate(dt, self.state)
        # Update current window based on transitions
        self.window.draw(stateUpdate[1])
        # Store the new state
        self.state = stateUpdate[0]
        if self.is_hero_alive == False:
            self.start()

    def integrate(self, dt, state):
        transition = [] # Set of actions to reach the new state (makes drawing much smoother)

        # Move player
        dx = dt * state.hero.vel_x * self.player_direction
        dy = dt * state.hero.vel_y

        if self.collision.checkPlayerMove(state.hero, dx, dy):
            state.hero.move(dx, dy)
            transition.append((2, 'hero', dx, dy))
        # Move rain
        for r in state.rain:
            dx = dt * r.vel_x
            dy = dt * r.vel_y
            # If move is valid, update its position with the entity
            if self.collision.checkRainBounds(r, dx, dy) == True:
                r.move(dx, dy)
                t = (2, r.id, dx, dy)
                transition.append(t)

            else:
                old_x = r.x
                old_y = r.y
                new_drop = self.create_drop(r)
                transition.append((2, new_drop.id, new_drop.x - old_x, new_drop.y - old_y))
                state.rain.remove(r)
                state.rain.append(new_drop)


        if self.collision.check_death(self.window.canvas, state):
            pass
            # trigger death
            self.is_hero_alive = False
        else:
            state.score += 1
            transition.append((4, state.score))

            if state.score // 50 > len(state.rain):
                r = self.create_drop()
                transition.append((1, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id))
                state.rain.append(r)


        # Return game state
        return (state, transition)

    # Resets all game data and displays the start menu
    def start(self):
        self.window.clear()

        # Create game state
        self.state = GameState.GameState(self.create_hero(), [self.create_drop() for i in range(10)])
        self.window.draw(self.state.initial_transition()) # Draw the initial game

        self.serializer.write(self.state)

        # Set game controls
        self.in_game = True
        self.is_hero_alive = True

        if self.step_mode != Const.TIMESTEP_MANUAL:
            print('starting gameloop thread')
            t = threading.Thread(target=self.gameloop, daemon=True)
            t.start()


    def mainMenu(self):
        self.window.menu(self.start)

        # @Param event{object} : holds information about KeyPress events
    def keyDown(self, event):
        if event.char == 'a':
            self.player_direction = -1
        elif event.char == 'd':
            self.player_direction = 1
        elif event.char == 't':
            self.in_game = False
        elif event.char == 'r':
            self.in_game = 2

        # @Param event{object} : holds information about KeyPress events
    def keyUp(self, event):
        if event.char == 'a' and self.player_direction == -1:
            self.player_direction = 0
        elif event.char == 'd' and self.player_direction == 1:
            self.player_direction = 0

    def create_hero(self):
        return Entities.Hero(self.window.width() // 2, self.window.height())

    def create_drop(self, previous_drop=None):
        x_pos = random.randint(0, self.window.width())
        y_pos = random.randint(-500, 0)

        if previous_drop == None:
            drop_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            return Entities.Rain(drop_id, x_pos, y_pos)
        else:
            previous_drop.reset(x_pos, y_pos)
            return previous_drop

    def registerListeners(self):
        self.window.canvas.bind('<KeyPress>', self.keyDown)
        self.window.canvas.bind('<KeyRelease>', self.keyUp)
        pass
