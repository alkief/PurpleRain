from Window import Window
from GameState import GameState
from Entities import Hero, Rain
from Collision import Collision
from Serializer import Serializer
import Const

import threading
import time
import random
import string

class Engine():
    def __init__(self):
        self.state = None # Current copy of the game state

        # Engine controls for exiting main gameloop
        self.in_game = False
        self.is_hero_alive = False

        # Self-defined modules
        self.window = Window() # Create the window class
        self.collision = Collision(self.window.canvas)
        self.serializer = Serializer()

        self.registerListeners() # Set listeners for keybindings

        self.window.canvas.after(100, self.mainMenu) # Display the main menu
        self.window.mainloop()


        # The main game loop. Responsible for making performing calculations for
        #       graphics changes, collision detection, scoring, difficulty
    def gameloop(self):
        # Create game state
        self.state = GameState(self.create_hero(), [self.create_drop() for i in range(0)])
        self.window.draw(self.state.initial_transition()) # Draw the initial game

        self.serializer.write(self.state)

        # Set game controls
        self.in_game = True
        self.is_hero_alive = True

        col = threading.Thread(target=self.collision_detection, daemon=True)
        col.start()

        # Set time-step controls
        time_step_mode = 0
        dt = 0.01
        frame_rate = 30
        frameMS = 100 / frame_rate
        startTime = time.time()
        endTime = time.time()

        while self.in_game == True and self.is_hero_alive == True:
            if dt < 0.000001 and time_step_mode == 0:
                startTime = time.time()
                time.sleep(0.000001)
                endTime = time.time()
                dt = endTime - startTime

            startTime = time.time()

            # Check for and trigger difficulty increase

            # Update state, return the new state and the transitions used to get there
            stateUpdate = self.integrate(dt, self.state)

            # Update current window based on transitions
            self.window.draw(stateUpdate[1])

            # Store the new state
            self.state = stateUpdate[0]

            endTime = time.time()

            if time_step_mode == 0:
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

    def integrate(self, dt, state):
        transition = [] # Set of actions to reach the new state (makes drawing much smoother)

        # Move player
        dx = dt * state.hero.vel_x * state.player_direction
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

        state.score += 1
        transition.append((4, state.score))

        if state.score // 50 > len(state.rain):
            r = self.create_drop()
            transition.append((1, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id))
            state.rain.append(r)

        # Return game state
        return (state, transition)

    def collision_detection(self):
        while self.in_game and self.is_hero_alive:
            # print('checking for death')
            time.sleep(0.001)
            if self.collision.checkDeath(self.window.canvas, self.state) == True:
                self.is_hero_alive = False


    # Resets all game data and displays the start menu
    def start(self):
        self.window.clear()
        t = threading.Thread(target=self.gameloop, daemon=True)
        t.start()

    def mainMenu(self):
        self.window.menu(self.start)

        # @Param event{object} : holds information about KeyPress events
    def keyDown(self, event):
        if event.char == 'a':
            self.state.setPlayerDirection(-1)
        elif event.char == 'd':
            self.state.setPlayerDirection(1)
        elif event.char == 't':
            self.in_game = False
        elif event.char == 'r':
            self.in_game = 2
        # @Param event{object} : holds information about KeyPress events
    def keyUp(self, event):
        if event.char == 'a' and self.state.player_direction == -1:
            self.state.setPlayerDirection(0)
        elif event.char == 'd' and self.state.player_direction == 1:
            self.state.setPlayerDirection(0)

    def create_hero(self):
        return Hero(self.window.width() // 2, self.window.height())

    def create_drop(self, previous_drop=None):
        x_pos = random.randint(0, self.window.width())
        y_pos = random.randint(-500, 0)

        if previous_drop == None:
            drop_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            return Rain(drop_id, x_pos, y_pos)
        else:
            previous_drop.reset(x_pos, y_pos)
            return previous_drop

    def registerListeners(self):
        self.window.canvas.bind('<KeyPress>', self.keyDown)
        self.window.canvas.bind('<KeyRelease>', self.keyUp)
        pass
