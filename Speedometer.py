import tkinter as tk
from math import pi, cos, sin

OVAL_FILL = "#7796CB"
NEEDLE_FILL = "#C9CAD9"

class Speedometer(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = tk.Canvas(self, width = 210, height = 210, bg = "#C9CAD9")
        #self.canvas.place(relx=0.0, rely=0.0, fill)
        self.canvas.pack(fill="both", expand=True)
    
        self.oval = self.canvas.create_oval(10, 10, 210, 210, outline="black", fill=OVAL_FILL)
        #self.needle = self.canvas.create_line(110, 110, 110, 30, fill="red", width=2)
        self.needle = self.canvas.create_line(110, 110, 110, 30, fill=NEEDLE_FILL, width=10)
        self.center_point = self.canvas.create_line(110, 30, 110, 25, width = 5, fill="black")

    def erase_needle(self):
        #self.needle = self.canvas.create_line(xpos_from, ypos_from, xpos_to, xpos_to, fill=OVAL_FILL, width=2)
        self.canvas.itemconfigure(self.needle, fill=OVAL_FILL)
        self.needle.update()

    def update_needle_coords(self, new_x, new_y):
        self.canvas.coords(self.needle, 110, 110, new_x, new_y )
    # Here value = Deviation percentage
    def update_needle(self, value):
        #Modify for 50 being the center
        if (abs(value) <= 50):
            value = 50 + value
        else:
            if (value < 0):
                value = 0
            else:
                value = 100

        angle = (value / 100) * 180
        radians = angle * (pi / 180)
        x = 110 + 80 * cos(radians)
        y = 110 - 80 * sin(radians)
        self.update_needle_coords(x, y)
        self.update()
