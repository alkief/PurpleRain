from game import Window
from game import GameState
from game import Entities
from game import Collision
from game import Const
from game import Transitions
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
        while self.scene == Const.SCENE_INGAME and self.is_hero_alive == True\
            and self.window.is_alive:
            self.step(0.1)
            time.sleep(0.0167) # 1/60 of a second

        # Exit loop
        if self.scene == Const.SCENE_EXIT_GAME:
            return
        elif self.is_hero_alive == False and self.scene == Const.SCENE_INGAME:
            self.serializer.write(self)
            self.state = None
            self.start() # Automatically restart on death
            # self.mainMenu() # Automatically go to menu on death
        elif self.scene == Const.SCENE_MAINMENU:
            self.mainMenu()
        elif self.scene == Const.SCENE_RESTART_GAME:
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
        try:
            self.window.canvas.update() # Display canvas changes
        except:
            pass

        # Calculate the reward for the change in state
        step_reward = self.calc_reward(initial_state, self.state, self.player_direction)

        done = False # Signal the end of the game
        if self.is_hero_alive != True or self.scene != Const.SCENE_INGAME:
            done = True

        if done == True:
            step_reward = -100 # Death is bad

        if self.optimal_shown == True:
            # print('updating optimal outline')
            x = self.update_optimal()
        # print('returning from step function')
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
        transition.append(Transitions.MoveEntityTransition(Const.MOVE_ENTITY, 'hero', dx, dy))

        # Move rain
        for r in state.rain:
            dx = dt * r.vel_x
            dy = dt * r.vel_y
            # If move is valid, update its object's stored position
            if self.collision.checkRainBounds(r, dx, dy) == True:
                r.move(dx, dy)
                t = Transitions.MoveEntityTransition(Const.MOVE_ENTITY, r.id, dx, dy)
                transition.append(t)
            # Or move it to a new starting position in the sky
            else:
                old_x = r.x
                old_y = r.y
                new_drop = self.create_drop(r)
                t = Transitions.MoveEntityTransition(Const.MOVE_ENTITY,
                                                    new_drop.id,
                                                    new_drop.x - old_x,
                                                    new_drop.y - old_y)
                transition.append(t)
                state.rain.remove(r)
                state.rain.append(new_drop)


        if self.collision.check_death(self):
            self.is_hero_alive = False # Trigger death
        else:
            state.score += 1 # Update score
            transition.append(Transitions.UpdateScoreTransition(Const.UPDATE_SCORE, state.score)) # Append the score update for graphics

            # Increase difficulty. Add a new drop of rain for every 200 score
            # if (state.score // 200) + 10 > len(state.rain):
            #     r = self.create_drop()
            #     t = Transitions.DrawRainTransition(Const.DRAW_RAIN, r.x, r.y, r.vel_x, r.vel_y, r.length, r.id)
            #     transition.append(t)
            #     state.rain.append(r)

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
        success = False
        # Get the optimal widget ID from the canvas
        # try:
        optimal_widget = self.window.canvas.find_withtag('optimal')
        # Calculate the optimal position for the current state
        new_optimal_x = self.find_optimal_position(self.state)
        # Get the coords of the current optimal outline
        current_optimal_x = self.window.canvas.coords(optimal_widget)[0]
        # Update the coords of the outline to the newly calculated position
        self.window.canvas.coords(optimal_widget,
                new_optimal_x - (Const.PLAYER_WIDTH // 2),
                self.state.hero.y - Const.PLAYER_HEIGHT,
                new_optimal_x + (Const.PLAYER_WIDTH // 2),
                self.state.hero.y)
        self.window.update() # Display changes
        success = True
        # except:
            # pass

        return success

    # Update the screen until the use swaps off the menu screen
    def wait_menu_input(self):
        while self.scene == Const.SCENE_MAINMENU and self.window.is_alive == True:
            try:
                self.window.canvas.update()
            except:
                pass

    # Display the main menu, set flags to store state and buffer until user input
    def mainMenu(self):
        self.scene = Const.SCENE_MAINMENU
        self.state = None
        try:
            self.window.menu(self.start)
            self.window.canvas.update()
        except:
            pass
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
        x_pos = random.randint(0, self.window.width() - 1)
        y_pos = random.randint(-100, 0)

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
        hero_y = state.hero.y
        lower = int(round(hero_x - 50))
        upper = int(round(hero_x + 50))

        # Set bounds for the range of X positions explored
        if upper > self.window.width() - (Const.PLAYER_WIDTH // 2):
            upper = self.window.width() - (Const.PLAYER_WIDTH // 2)
        if lower < 0 + (Const.PLAYER_WIDTH // 2):
            lower = (Const.PLAYER_WIDTH // 2)

        best_x = None
        best_x_score = 0
        for x in range(lower, upper):
            player_range = range(x - Const.PLAYER_WIDTH,
                                x + Const.PLAYER_WIDTH)
            # Find the total manhattan distance to each rain from the current X
            #       being evaluated
            total_dist = 0 # Score for the current x position
            has_rain_above = False # Whether rain is above player at position x
            for r in state.rain:
                dist_to_rain = abs(hero_y - r.y) + abs(x - r.x)
                total_dist += dist_to_rain # Add each distance to total_dist
                if r.x in player_range:
                    has_rain_above = True


            if has_rain_above == True:
                total_dist -= 1000
            else:
                total_dist += 1000

            # Update the coordinate of the best X position within search range
            if total_dist > best_x_score:
                # print('NEW BEST X FOUND AT ', x, 'WITH SCORE', total_dist)
                best_x = x
                best_x_score = total_dist

        # print('BEST X FOUND:', best_x)
        return best_x

    # Produce a reward for a given change in state based on the
    #       whether the hero increased, decreased or failed to change his/her
    #       distance to the calculated optimal hero position
    def calc_reward(self, initial_state, final_state, action):
        # Find the best position within +/- 50px
        optimal_x = self.find_optimal_position(initial_state)
        reward = 1 # Baseline bonus for staying alive
        # if action takes us closer to optimal position
        if abs((initial_state.hero.x + action) - optimal_x) < abs(initial_state.hero.x - optimal_x):
            reward += 1
        # player is at the optimal position
        elif final_state.optimal[0] == final_state.hero.bbox[0]:
            reward += 1

        # if action left us with rain over our head
        player_range = range(int(round(final_state.hero.x)) - (Const.PLAYER_WIDTH // 2),
                            int(round(final_state.hero.x)) + (Const.PLAYER_WIDTH // 2))
        has_rain_above = False
        for r in final_state.rain:
            if r.x in player_range:
                has_rain_above = True

        if has_rain_above == True:
            reward -= 1
        else:
            reward += 1

        return reward

    # Simple encoding of the hero's x position followed by N digits
    #       where N is the number of pixels on the screen
    #       N = 1 if there is rain, 0 if there is not
    def encode_state(self):
        # state = [[0 for y in range(self.window.height())] for x in range(self.window.width())],
        #
        # try:
        #     # Set player region as hero constant
        #     state[self.state.hero.bbox[0]:self.state.hero.bbox[2]]\
        #         [self.state.hero.bbox[1]:self.state.hero.bbox[3]] = Const.ENTITY_HERO
        #
        #     # Set rain pixels
        #     for r in self.state.rain:
        #         state[r.x][r.y:r.y+r.length] = Const.ENTITY_RAIN
        #
        # except:
        #     pass
        #
        # # print(state)
        # return state

        encoded_state = [self.state.hero.x]
        encoded_rain_state = [0 for x in range(self.window.width())]
        for r in self.state.rain:
            try:
                encoded_rain_state[int(r.x)-1] = 1
            except:
                pass

        return encoded_state + encoded_rain_state

    # Bind key-down and key-up functions to the canvas for player input
    def registerListeners(self):
        self.window.canvas.bind('<KeyPress>', self.keyDown)
        self.window.canvas.bind('<KeyRelease>', self.keyUp)
