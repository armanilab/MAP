# fit data to new model
# model updated as of 2024.10.24
# Lexie Scholtz

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from tqdm import tqdm
from matplotlib import font_manager as fm
from lmfit import Model

def calibrate(lux, c0):
    n = 20
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

def plot_data(time, lux, conc, file):
    axes_font = {'family': 'avenir', 'size':16}
    title_font = {'family': 'avenir', 'size':20, 'weight':'bold',}
    labels_font = {'family': 'avenir', 'size':12}
    tick_font = fm.FontProperties(family='avenir', style='normal', size=12, weight='bold')

    fig, (lux_ax, conc_ax) = plt.subplots(1, 2, figsize=(12, 6))

    # plot data
    lux_ax.plot(time, lux)
    conc_ax.plot(time, conc)

    # format axes
    lux_ax.set_title('Raw data', fontdict=title_font)
    lux_ax.set_xlabel('Time (min)', fontdict=axes_font)
    lux_ax.set_ylabel('Intensity (klx)', fontdict=axes_font)

    lux_ax.set_title('Calibrated data', fontdict=title_font)
    conc_ax.set_xlabel('Time (min)', fontdict=axes_font)
    conc_ax.set_ylabel('Concentration (mg/mL)', fontdict=axes_font)

    for label in lux_ax.get_xticklabels() + lux_ax.get_yticklabels() + conc_ax.get_xticklabels() + conc_ax.get_yticklabels():
        label.set_fontproperties(tick_font)

    fig.suptitle(file, fontdict=title_font, fontsize=24, fontweight='black')
    plt.tight_layout()
    plt.show()

def model(t, chi, r):


def driver():
    # parameters
    eta = 8.9e-4
    rho = 5200
    mu0 = 4 * np.pi * (10e-7)
    Xs = -9.04e-6

    # magnet parameters
    l = 0.0254
    w = 0.0254
    in2m = 0.0254

    t_input = input('How thick is your magnet?\n[a] 3/16"\n[b] 1/4"\n[c] 3/8"\n[d] 1/2"\n')
    if t_input == 'a':
        t = 3/16 * in2m
        print('3/16" thickness selected.')
    elif t_input == 'b':
        t = 1/4 * in2m
        print('1/4" thickness selected.')
    elif t_input == 'c':
        t = 3/8 * in2m
        print('3/8" thickness selected.')
    elif t_input == 'd':
        t = 1/2 * in2m
        print('1/2" thickness selected.')
    else:
        print("ENTRY ERROR: invalid magnet thickness entered")
        return

    grade = input('\nWhat grade is your magnet?\n[a] N42\n[b] N52\n')
    if grade == 'a':
        B_r = 1.32
        print('Grade N42 selected.')
    elif grade == 'b':
        B_r = 1.48
        print('Grade N52 selected.')
    else:
        print("ENTRY ERROR: invalid magnet grade entered")
        return

    # set position of sensor relative to magnet
    system = input('\nWhich system are you using?\n[a] Magmitus-Obsidian\n[b] Noir\n[c] Silva\n')
    if system == 'a': # Mag-Ob
        sensor = [0.0130, 0.014] #TODO: enter sensor position
        print('Magmitus-Obsidian selected.')
    elif system == 'b': # Noir
        sensor = [0.00885, 0.00965]
        print('Noir selected.')
    elif system =='c': # Silva (modified though)
        sensor [0.0442, 0.0452]
        print('Silva selected.')
    else:
        print("ENTRY ERROR: invalid system entered")

    if t_input == 'c' and system == 'a':
        a = -10.545907

    path = '../../../../test_data/paper_data/'

    print("\nCurrent path: " + path)
    file = input('Please enter file name: \n')

    if file[-4:] != '.txt':
        file += '.txt'

    c0_input = input('\nWhat is the initial concentration of the solution? [mg/mL]\n')
    try:
        c0 = float(c0_input)
    except:
        print("ENTRY ERROR: invalid initial concentration entered")

    ### CALIBRATION ###
    print("\nLoading file...")
    try:
        data = np.genfromtxt(path + file)
    except:
        print("ERROR: Could not load data file at:\n" + path + file)
    print("Successfully loaded " + file + '\n')

    time = data[:, 0]
    lux = data[:, 1]

    conc = calibrate(lux, c0)
    print("\nData calibrated successfully!\n")

    toshow = input('Show the plot? [y/n] ')
    if toshow == 'y':
        plot_data(time, lux, conc, file)

    ### INITIAL PARAMETERS ###
    chi = 1.5e-3
    r = 0.5e-6
    print("\nCurrent Parameters:")
    print("Given chi: " + str(chi))
    print("Given r: " + str(r))

    alpha = 9 * eta / (2 * rho * (r**2))
    beta = -2 * (a**2) * chi * rho / (mu0 * (1+Xs))

    print("Alpha: " + str(alpha))
    print("Beta: " + str(beta))

    delta1 = (-alpha + np.sqrt((alpha**2) - 4 * beta)) / 2
    delta2 = (-alpha - np.sqrt((alpha**2) - 4 * beta)) / 2

    print("Delta1: " + str(delta1))
    print("Delta2: " + str(delta2))

    ### MODEL FIT ###





driver()
