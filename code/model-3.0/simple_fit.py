import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm
from scipy.optimize import curve_fit

n = 20

# fit params
eta = 8.9e-4
rho_p = 1400
mu0 = 4 * np.pi * 10**-7
a = -13.655887
Xs = -9.04e-6

def og_model(t, k1, d1, k2, d2):
    return k1 * np.exp(d1*t) + k2 * np.exp(d2 * t)

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

# FOR NOW: assume same concentration
# get concentration data for calibration steps
# same_conc = lower(input("Are all files the same concentration? [y/n]"))
# if same_conc == 'y':
#
try:
    c0 = float(input("What is the concentration of the solution? [kg/mL] "))
except ValueError:
    "Error: invalid concentration"
    c0 = 0

# plot data
fig, (lux_ax, conc_ax) = plt.subplots(1, 2, figsize=(12, 6))


for file in file_list:
    if file[-4:] != '.txt':
        file += '.txt'

    file_path = path + file

    print(file)

    data = np.genfromtxt(file_path)
    time = data[:, 0] # convert to min
    lux = data[:, 1]  # convert to klux
    conc = calibrate(lux, c0)

    if min(conc) < 0:
        print('*@#!')

    lux_ax.plot(time, lux)

    # fit model
    (popt, pcov) = curve_fit(og_model, time, conc, p0=[-1.93e-13, -1.5e7, 0.1, -2.9e-5]) #p0=[0, 0.1, 0, 0.1], bounds=([-1, 0, -1, 0], [1, 0.1, 1, 0.1]))
    k1, d1, k2, d2 = popt
    model_y = og_model(time, k1, d1, k2, d2)

    conc_ax.plot(time, conc, label=file + ' data')
    conc_ax.plot(time, model_y, '--', label=file + ' fit')

    print('k1: ' + str(k1))
    print('d1: ' + str(d1))
    print('k2: ' + str(k2))
    print('d2: ' + str(d2))

    chi = rho_p * mu0 * (1 + Xs) / (2 * a**2) * d1 * d2
    r = (9 * eta / (2 * rho_p * (d1 + d2))) ** 0.5
    print('chi: ' + str(chi))
    print('r: ' + str(r))

    print('')


# format plot
lux_ax.set_xlabel('Time (min)', fontdict=axes_font)
lux_ax.set_ylabel('Intensity (klx)', fontdict=axes_font)

conc_ax.set_xlabel('Time (min)', fontdict=axes_font)
conc_ax.set_ylabel('Concentration (mg/mL)', fontdict=axes_font)

for label in lux_ax.get_xticklabels() + lux_ax.get_yticklabels() + conc_ax.get_xticklabels() + conc_ax.get_yticklabels():
    label.set_fontproperties(tick_font)

title_str = input('What should this plot be titled?\n')
# fig.suptitle(title_str, fontdict=title_font) #, fontweight='black')

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
