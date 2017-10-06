from . import Window
from . import GameState
from . import Entities
from . import Collision
from . import Const
from data import Serializer

import time
import random
import copy
import string

# TODO make controller default to keyboard controls if engine is self-updating
class Engine():
    # @Param{int} step_mode: Determine if the engine updates itself or is
    #       externally controlled
    # @Param{int} controller: The method of player control (keyboard or external input)
    #       Default is keyboard
    def __init__(self, step_mode=Const.TIMESTEP_AUTO, controller=Const.CONTROLLER_PLAYER):
        self.step_mode=step_mode

        self.state = None # Current copy of the game state
        self.player_direction = 0 # 1 for right, -1 for left, 0 for stand still

        # Engine controls for exiting main gameloop
        self.scene = None # Control for changing the currently displayed screen
        self.is_hero_alive = False

        self.optimal_shown = True # Toggle whether the optimal hero position is outlined

        # Self-defined modules
        self.window = Window.Window() # Create the game window
        self.collision = Collision.Collision(self.window.width(), self.window.height())
        self.serializer = Serializer.Serializer()

        # Set listeners for player controls
        if step_mode == Const.TIMESTEP_AUTO or controller != Const.CONTROLLER_OTHER:
            self.registerListeners()

        self.mainMenu() # Send the game to main menu on construction

    def __str__(self):
        return str(self.player_direction) + '\n' + str(self.state)

    # Automatically update hero position and graphics based on player input
    def gameloop(self):
        while self.scene == Const.SCENE_INGAME and self.is_hero_alive == True:
            self.step(0.1)
            time.sleep(0.0167) # 1/60 of a second

        # Exit loop
        if self.is_hero_alive == False:
            print('game lost with hero death, serializing state')
            self.serializer.write(self)
            self.state = None
            self.start() # Automatically restart on death
            # self.mainMenu() # Automatically go to menu on death
        elif self.scene == Const.SCENE_MAINMENU:
            self.mainMenu()
        elif self.scene == Const.SCENE_RESTART_GAME:
            self.start()
        else:
            self.start()

    # @Param{float} dt: the time amount to step forward with the given inputs
    # Returns a tuple of:
    #       The encoded game state after stepping
    #       The reward for the input action (player direction)
    #       A boolean signaling whether the game is over
    def step(self, dt):
        initial_state = copy.deepcopy(self.state) # Store the initial state

        # Update state, return the new state and the transitions used to get there
        stateUpdate = self.integrate(dt, self.state)
        # Update current window based on transitions
        self.window.draw(stateUpdate[1])
        # Store the new state
        self.state = stateUpdate[0]
        if self.is_hero_alive == False:
            if self.step_mode == Const.TIMESTEP_AUTO:
                self.start()

        self.serializer.write(self) # Write state to data file
        self.window.canvas.update() # Display canvas changes

        # Calculate the reward for the change in state
        step_reward = self.calc_reward(initial_state, self.state)

        done = False # Signal the end of the game
        if self.is_hero_alive != True or self.scene != Const.SCENE_INGAME:
            done = True

        if done == True:
            step_reward = -10 # Death is bad
        else:
            step_reward += 0.002 # Staying alive contributes to the reward received

        if self.optimal_shown == True:
            self.update_optimal()

        return (self.encode_state(), step_reward, done)

    # @Param{int} dt: The amount of time to integrate with respect to
    # @Param{game.GameState} state: The current state of the game to be updating
    # Returns:
    #       The new game state after integration
    #       The transitions used to achieve the new state
    #           Transitions are use to move existing canvas widgets rather than
    #           removing old ones and recreating new ones.
    #           TODO make transitions into formalized objects to improve readability
    def integrate(self, dt, state):
        # Set of actions to reach the new state (makes drawing much smoother)
        transition = []

        # Find initial player displacement
        dx = dt * state.hero.vel_x * self.player_direction
        dy = dt * state.hero.vel_y

        # Check bounds and return the max displacement allowed for the player
        dx, dy = self.collision.checkPlayerMove(self.state.hero, dx, dy)
        state.hero.move(dx, dy) # Update position stored in the hero object
        # Append the command for updating hero graphics to the transitions
        transition.append((2, 'hero', dx, dy))

        # Move rain
        for r in state.rain:
            dx = dt * r.vel_x
            dy = dt * r.vel_y
            # If move is valid, update its object's stored position
            if self.collision.checkRainBounds(r, dx, dy) == True:
                r.move(dx, dy)
                t = (2, r.id, dx, dy)
                transition.append(t)
            # Or move it to a new starting position in the sky
            else:
                old_x = r.x
                old_y = r.y
                new_drop = self.create_drop(r)
                transition.append((2, new_drop.id, new_drop.x - old_x, new_drop.y - old_y))
                state.rain.remove(r)
                state.rain.append(new_drop)


        if self.collision.check_death(self):
            self.is_hero_alive = False # Trigger death
        else:
            state.score += 1 # Update score
            transition.append((4, state.score)) # Append the score update for graphics

            # Increase difficulty. Add a new drop of rain for every 200 score
            if (state.score // 200) + 10 > len(state.rain):
                r = self.create_drop()
                transition.append((1, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id))
                state.rain.append(r)

        # Return game state and how we got there
        return (state, transition)

    # Resets all game data and displays the start menu
    def start(self):
        self.window.clear() # Clear window widgets

        # Set game controls
        self.scene = Const.SCENE_INGAME
        self.is_hero_alive = True

        # Create game state
        self.state = GameState.GameState(self.create_hero(), [self.create_drop() for i in range(10)])
        self.window.draw(self.state.initial_transition(self.optimal_shown)) # Draw the initial game

        if self.optimal_shown == True:
            self.update_optimal()

        self.serializer.write(self) # Write the initial game state

        if self.step_mode == Const.TIMESTEP_AUTO:
            self.gameloop()

    # TODO: make this more readable, use both X and Y coordinates in calculations
    # Update the display of the outline of the optimal hero positoin
    def update_optimal(self):
        # Get the optimal widget ID from the canvas
        optimal_widget = self.window.canvas.find_withtag('optimal')
        # Calculate the optimal position for the current state
        new_optimal_x = self.find_optimal_position(self.state)
        # Get the coords of the current optimal outline
        current_optimal_x = self.window.canvas.coords(optimal_widget)[0]

        # Update the coords of the outline to the newly calculated position
        self.window.canvas.coords(optimal_widget, new_optimal_x - 25, self.state.hero.y - 50, new_optimal_x + 25, self.state.hero.y)
        self.window.update() # Display changes

    # Update the screen until the use swaps off the menu screen
    def wait_menu_input(self):
        while self.scene == Const.SCENE_MAINMENU:
            self.window.canvas.update()

    # Display the main menu, set flags to store state and buffer until user input
    def mainMenu(self):
        self.scene = Const.SCENE_MAINMENU
        self.state = None
        self.window.menu(self.start)
        self.window.canvas.update()
        if self.step_mode == Const.TIMESTEP_AUTO:
            self.wait_menu_input()

    # @Param event{object} : holds information about KeyPress events
    def keyDown(self, event):
        if event.char == 'a':
            self.player_direction = -1
        elif event.char == 'd':
            self.player_direction = 1
        elif event.char == 't':
            self.scene = Const.SCENE_MAINMENU
        elif event.char == 'r':
            self.scene = Const.SCENE_RESTART_GAME

    # @Param event{object} : holds information about KeyPress events
    def keyUp(self, event):
        if event.char == 'a' and self.player_direction == -1:
            self.player_direction = 0
        elif event.char == 'd' and self.player_direction == 1:
            self.player_direction = 0

    # Default constructor for the hero within our game
    def create_hero(self):
        return Entities.Hero(self.window.width() // 2, self.window.height())

    # Default construction of rain or respawn rain in new position given an
    #       old rain object
    def create_drop(self, previous_drop=None):
        x_pos = random.randint(0, self.window.width())
        y_pos = random.randint(-500, 0)

        if previous_drop == None:
            drop_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            return Entities.Rain(drop_id, x_pos, y_pos)
        else:
            previous_drop.reset(x_pos, y_pos)
            return previous_drop

    # Use the current state to find ranges along the X axis of the hero bbox
    #       where rain doesn't exist, then calculate the center position
    #       of the largest range (largest span of pixels where rain doesn't exist)
    def find_optimal_position(self, state):
        hero_x = state.hero.x

        # Find x positions of rain which are on-screen and visible
        rain_x = []
        for r in state.rain:
            if r.y < 0 or r.y > self.window.height():
                pass
            else:
                rain_x += [r.x]

        rain_x = sorted(rain_x)
        ranges = []
        lower = 1
        # Find open X ranges using sorted rain locations
        for x in rain_x:
            ranges.append((lower, x-1))
            lower = x+1

        # Find the largest rain
        biggestRange = (0, 0)
        for r in ranges:
            if r[1] - r[0] > biggestRange[1] - biggestRange[0]:
                biggestRange = r

        # Calculate the middle pixel of the largest range
        bestPixel = biggestRange[0] + ((biggestRange[1] - biggestRange[0]) // 2)

        return bestPixel


    # Produce a reward for a given change in state based on the
    #       whether the hero increased, decreased or failed to change his/her
    #       distance to the calculated optimal hero position
    def calc_reward(self, initial_state, final_state):
        # Find the optimal x coordinate for the states before and after an action
        o1 = self.find_optimal_position(initial_state)
        o2 = self.find_optimal_position(final_state)

        # The distance the hero is from the optimal position for both states
        dist_state1 = abs(initial_state.hero.x - o1)
        dist_state2 = abs(final_state.hero.x - o2)

        # difference > 0 -> we closed the distance to the optimal position
        # difference < 0 -> we increased the distance
        # difference == 0 -> we stayed the same
        difference =  dist_state1 - dist_state2

        # Use the difference in hero distance from optimal position to contribute
        #       to the calculated reward
        if difference > 0:
            # print('WE\'RE MOVING TOWARDS THE OPTIMAL POSITION')
            return 0.2
        elif difference < 0:
            # print('WE\'RE MOVING AWAY FROM THE OPTIMAL POSITION')
            return -0.2
        else:
            return -0.00001 # Provide some negative stimulus for not moving to the reward

    # Simple encoding of the hero's x position followed by N digits
    #       where N is the number of pixels on the screen
    #       N = 1 if there is rain, 0 if there is not
    def encode_state(self):
        encoded_state = [self.state.hero.x]
        encoded_rain_state = [0 for x in range(self.window.width())]
        for r in self.state.rain:
            encoded_rain_state[int(r.x)] = 1

        return encoded_state + encoded_rain_state

    # Bind key-down and key-up functions to the canvas for player input
    def registerListeners(self):
        self.window.canvas.bind('<KeyPress>', self.keyDown)
        self.window.canvas.bind('<KeyRelease>', self.keyUp)
