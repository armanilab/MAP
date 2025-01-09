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


def driver():
    # parameters
    eta = 8.9e-4
    rho_p = 5200
    rho_s = 1000
    mu0 = 4 * np.pi * (10e-7)
    Xs = -9.04e-6

    # physical setup parameters
    sensor = [0.0130, 0.014] #TODO: enter sensor position
    z_low = sensor[0]
    z_high = sensor[1]
    h_window = 0.001
    a_window = 0.01 * 0.01
    v_window = a_window * h_window

    # magnet parameters
    l = 0.0254
    w = 0.0254
    in2m = 0.0254

    t_input = input('Which magnet are you using?\n[a] 3/16"\n[b] 1/4"\n[c] 3/8"\n[d] 1/2"\n')
    if t_input == 'a':
        t = 3/16 * in2m
        print('3/16" thickness, Grade N42 selected.')
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

    # TODO: eventually, replace this with the fit itself
    if t_input == 'a': # 3/16" thick, N42
        a = -6.677333
    elif t_input == 'b': #1/4" thick, N42
        a = -8.208740
    elif t_input == 'c' and grade =='a':
        a = -10.545907
    elif t_input == 'c' and grade =='b':
        a = -11.824199
    elif t_input == 'd':
        a = -13.655887
    print('a = ' + str(a)) 

    shape = input('\nWhat shape are you expecting your particles to be?\n[a] Spherical clusters\n[b] Oblong clusters\n'
        + '[c] spherical - Re=0.86 (mag 5)\n[d] spherical - Re=0.26 (mag 1)\n')
    if shape == 'a':
        cd = 0.47
    elif shape == 'b':
        cd = 0.04
    elif shape == 'c':
        cd = 5988.85#27.91
    elif shape =='d':
        cd = 92.31
    else:
        cd = 0.5

    print('cd = ' + str(cd))
    path = '../../../../test_data/paper_data/'

    print("\nCurrent path: " + path)
    path_append = input('Add to path? [enter to skip or start with "-" to enter fully new path]\n')
    if len(path_append) > 0 and path_append[0]=='-':
        path = path_append[1:]
    else:
        path += path_append

    print("\nNew path: " + path)

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
    alpha = (eta * cd) / (2 * r * rho_p)
    beta = (2 * (a**2) * chi) / (mu0 * rho_p * (1 + Xs))
    delta1 = 0.5 * (-alpha + np.sqrt((alpha**2) - 4 * beta))
    delta2 = 0.5 * (-alpha - np.sqrt((alpha**2) - 4 * beta))


    print("Alpha: " + str(alpha))
    print("Beta: " + str(beta))
    print((alpha**2) - 4 * beta)
    print("Delta1: " + str(delta1))
    print("Delta2: " + str(delta2))

    ### MODEL FIT ###
    def model_eqn(t, chi, r):
        alpha = (eta * cd) / (2 * r * rho_p)
        beta = (2 * (a**2) * chi) / (mu0 * rho_p * (1 + Xs))
        delta1 = 0.5 * (-alpha + np.sqrt((alpha**2) - 4 * beta))
        delta2 = 0.5 * (-alpha - np.sqrt((alpha**2) - 4 * beta))

        k1 = delta2 / (delta2 - delta1)
        k2 = -delta1 / (delta2 - delta1)
        return c0 / (k1 * np.exp(delta1 * t) + k2 * np.exp(delta2 * t))
        #k = (3 * c0 * v_window) / (rho_p * 4 * np.pi * (r**2) * (z_high - z_low))
        #deltas = delta2 - delta1
        #return k * (z_low + z_high) / (delta2 / deltas * np.exp(delta1 * t) - delta1 / (deltas) * np.exp(delta2 * t))

    model = Model(model_eqn)
    params = model.make_params(chi=chi, r=r)
    result = model.fit(conc, params, t=time)
    print(result.fit_report())



driver()
