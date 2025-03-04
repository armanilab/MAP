# Simple script to plot the MAP data
# Will display the raw data on the left subplot and calibrated concentration
# data on the right subplot
#
# Usage: python3 plot_data.py <path> <file(s)>
#   path will be added as a prefix to all files
#
# Written by: Lexie Scholtz
#   First version: 2025.01.09


import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm

n = 20

def calibrate(lux, c0):
    # convert to transmission
    e_0 = np.average(lux[-n:]) # "water" value
    transmission = lux / e_0
    # convert from transmission to attenuation
    att = -np.log10(transmission)

    # determine c vs. att linear relationship
    att0 = att[0]
    attf = np.average(att[-n:])

    # convert attenuation to concentration
    return c0 / (att0 - attf) * att + attf * c0 / (attf - att0)

def plot_data(time, lux, conc, label):
    lux_ax.plot(time, lux, label=label)
    conc_ax.plot(time, conc, label=label)

axes_font = {'family': 'avenir', 'size':16}
title_font = {'family': 'avenir', 'size':20, 'weight':'bold',}
labels_font = {'family': 'avenir', 'size':12}
tick_font = fm.FontProperties(family='avenir', style='normal', size=12, weight='bold')

# parse arguments
path = sys.argv[1]
file_list = sys.argv[2:] # get the file names as arguments

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

# check for flags
flags = []
for f in file_list:
    if '-' in f:
        flags.append(f)
        file_list.remove(f)

# get user input about concentration
try:
    c_i = float(input("What is the concentration of the solution? [mg/mL] "))
except ValueError:
    "Error: invalid concentration"
    c_i = 0

# plot data
fig, (lux_ax, conc_ax) = plt.subplots(1, 2, figsize=(12, 6))

for file in file_list:
    if file[-4:] != '.txt':
        file += '.txt'

    file_path = path + file

    data = np.genfromtxt(file_path)
    time = data[:, 0] / 60 # convert to min
    lux = data[:, 1] / 1000 # convert to klux
    conc = calibrate(lux, c_i)

    lux_ax.plot(time, lux)
    conc_ax.plot(time, conc, label=file)

    print(file + ": success!")

# format plot
lux_ax.set_xlabel('Time (min)', fontdict=axes_font)
lux_ax.set_ylabel('Intensity (klx)', fontdict=axes_font)

conc_ax.set_xlabel('Time (min)', fontdict=axes_font)
conc_ax.set_ylabel('Concentration (mg/mL)', fontdict=axes_font)

for label in lux_ax.get_xticklabels() + lux_ax.get_yticklabels() + conc_ax.get_xticklabels() + conc_ax.get_yticklabels():
    label.set_fontproperties(tick_font)

title_str = input('What should this plot be titled?\n')
fig.suptitle(title_str, fontdict=title_font)

handles = []
labels = []
for ax in [lux_ax, conc_ax]:
    for handle, label in zip(*ax.get_legend_handles_labels()):
        handles.append(handle)
        labels.append(label)

plt.legend(handles, labels, loc='center left', bbox_to_anchor=(1.05, 0.5),
   prop=tick_font)

plt.tight_layout()
plt.show()
