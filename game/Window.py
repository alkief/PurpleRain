from tkinter import Canvas, Frame, Button, Label, BOTH
import tkinter as tk
import threading

from . import Const

class Window(tk.Frame):
    def __init__(self):
        self.master = tk.Tk()
        self.master.protocol('WM_DELETE_WINDOW', self.quit)
        self.root = tk.Frame.__init__(self, self.master, width=300, height=300)
        self.pack(fill=BOTH, expand=True)

        self.canvas = tk.Canvas(self, width=300, height=300, highlightthickness=0, bg='black')
        self.canvas.pack()
        self.canvas.focus_set() # Set window focus

        self.master.title('PurpRain') # Set the window title

        self.pack(fill=BOTH, expand=True)
        self.canvas.pack(fill=BOTH, expand=True)
        self.update()
        self.update_idletasks()
        self.is_alive = True

    def draw(self, transition):
        try:
        # SEE: game.Transition for information on Transition structure
            for t in transition:
                # For drawing the initial player rectangle
                if t.type == Const.DRAW_HERO:
                    self.canvas.create_rectangle(t.bbox[0], t.bbox[1], t.bbox[2], t.bbox[3],
                                                fill='white', tags='hero')
                # Draw optimal square position
                elif t.type == Const.DRAW_OPTIMAL:
                    self.canvas.create_rectangle(t.bbox[0], t.bbox[1], t.bbox[2], t.bbox[3],
                                                fill='green', tags='optimal')
                # Draw initial raindrops
                elif t.type == Const.DRAW_RAIN:
                        self.canvas.create_line(t.x, t.y, t.x, t.y + t.length,
                                                fill='purple', tags=(t.rain_id, 'rain'))
                # Move item with a given unique tag by specified distance
                elif t.type == Const.MOVE_ENTITY:
                    entity = self.canvas.find_withtag(t.tag)
                    self.canvas.move(entity, t.dx, t.dy)
                # Draw the initial score label
                elif t.type == Const.DRAW_SCORE:
                        self.canvas.create_text(10, 10, anchor='nw', text='0', tags='score', fill='white')
                # Update the score label
                elif t.type == Const.UPDATE_SCORE:
                        score_label = self.canvas.find_withtag('score')
                        self.canvas.itemconfig(score_label, text=str(t.new_score))
                self.update()
        except:
            pass
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
        width = 1
        try:
            width = self.master.winfo_width()
        except:
            pass
        return width

    def height(self):
        height = 1
        try:
            height = self.master.winfo_height()
        except:
            pass
        return height

    def clear(self):
        try:
            self.canvas.delete('all')
        except:
            pass

    def quit(self):
        self.is_alive = False
        self.master.destroy()
