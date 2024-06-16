#!/usr/bin/env python3

# Grabs raw data from the Pico's UART and plots it as received

# Install dependencies:
# python3 -m pip install pyserial matplotlib

# Usage: python3 plotter <port>
# eg. python3 plotter /dev/ttyACM0

# see matplotlib animation API for more: https://matplotlib.org/stable/api/animation_api.html

import serial
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from collections import deque
import time

# disable toolbar
plt.rcParams['toolbar'] = 'None'

class Plotter:
    def __init__(self, ax):
        self.ax = ax
        self.maxt = 30  # Set the maximum time span to display in seconds
        self.maxlen = 120  # Set the maximum number of data points to keep
        self.tdata = deque([0], maxlen=self.maxlen)
        self.ydata = deque([0], maxlen=self.maxlen)
        self.line = Line2D(self.tdata, self.ydata)

        self.ax.add_line(self.line)
        self.ax.set_ylim(0, 250)
        self.ax.set_xlim(0, self.maxt)  # Set initial x-axis limits

    def update(self, y):
        # Update time
        t = self.tdata[-1] + 1
        self.tdata.append(t)

        # Update data
        self.ydata.append(y)

        # Update x-axis limits to show only the last 'maxt' seconds
        if t > self.maxt:
            self.ax.set_xlim(t - self.maxt, t)

        # Update line data
        self.line.set_data(self.tdata, self.ydata)

        return self.line,

def serial_getter():
    while True:
        for i in range(5):
            line = ser.readline()
            try:
                line = float(line)
            except ValueError:
                continue
            break
        yield line

if len(sys.argv) < 2:
    raise Exception("Ruh roh..no port specified!")

print(sys.argv[1])
ser = serial.Serial(sys.argv[1], 9600, timeout=1)

fig, ax = plt.subplots()
plotter = Plotter(ax)

ani = animation.FuncAnimation(fig, plotter.update, serial_getter, interval=1,
                              blit=True, cache_frame_data=False)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Temperature (°C)")
fig.canvas.manager.set_window_title('PCR Thermal Profile')
fig.tight_layout()
plt.show()
