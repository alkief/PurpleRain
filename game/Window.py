from tkinter import Canvas, Frame, Button, Label, BOTH
import tkinter as tk
import threading

from . import Const

class Window(tk.Frame):
    def __init__(self, master=None):
        self.root = tk.Frame.__init__(self, master, width=800, height=600)
        self.pack(fill=BOTH, expand=True)

        self.canvas = tk.Canvas(self, width=800, height=600, highlightthickness=0, bg='black')
        self.canvas.pack()
        self.canvas.focus_set() # Set window focus

        self.master.title('PurpRain') # Set the window title

        self.pack(fill=BOTH, expand=True)
        self.canvas.pack(fill=BOTH, expand=True)
        self.update()
        self.update_idletasks()

    def draw(self, transition):
        for t in transition:
            # For drawing the initial player rectangle
            # tuple is: (0, <rectangle bbox>)
            if t[0] == Const.DRAW_HERO:
                self.canvas.create_rectangle(t[1][0], t[1][1], t[1][2], t[1][3],
                                            fill='white', tags='hero')
            # Draw optimal square position
            # tuple is (5, <rectangle bbox>)
            if t[0] == Const.DRAW_OPTIMAL:
                self.canvas.create_rectangle(t[1][0], t[1][1], t[1][2], t[1][3],
                                            fill='green', tags='optimal')
            # Draw initial raindrops
            # tuple is: (1, <x>, <y>, vel_x, vel_y, length, id')
            elif t[0] == Const.DRAW_RAIN:
                self.canvas.create_line(t[1], t[2], t[1], t[2] + t[5], fill='purple', tags=(t[6], 'rain'))
            # # Move item with a given unique tag by specified distance
            # # tuple is: (2, tag, dx, dy)
            elif t[0] == Const.MOVE_ENTITY:
                entity = self.canvas.find_withtag(t[1])
                self.canvas.move(entity, t[2], t[3])
            # # Draw the initial score label
            # # tuple is: (3,)
            elif t[0] == Const.DRAW_SCORE:
                self.canvas.create_text(10, 10, anchor='nw', text='0', tags='score', fill='white')
            # # Update the score label
            # # tuple is: :(4, <updated-score>)
            elif t[0] == Const.UPDATE_SCORE:
                score_label = self.canvas.find_withtag('score')
                self.canvas.itemconfig(score_label, text=str(t[1]))

    # Display the main menu with 'Start' and 'Options' buttons
    # @Param start_game{function}: calls logic from engine to trigger game start
    def menu(self, start_game):
        self.clear()
        # Display the 'Start' button
        startBtn = Button(self, text='Start', command=start_game)
        startBtn.config(width='10', activebackground='#33B5E5')
        self.canvas.create_window((self.width()/2) - 100, self.height()/2, window=startBtn)

        # Display the 'Options' button
        optionBtn = Button(self, text='Options', command=None)
        optionBtn.config(width='10', activebackground='#33B5E5')
        self.canvas.create_window((self.width()/2) + 100, self.height()/2, window=optionBtn)

    def width(self):
        return self.master.winfo_width()

    def height(self):
        return self.master.winfo_height()

    def clear(self):
        self.canvas.delete('all')
