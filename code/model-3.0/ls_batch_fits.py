import numpy as np
import matplotlib.pyplot as plt
import single_magnetic_analysis as ma
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import font_manager as fm
import sys
from tqdm import tqdm
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# fit params
eta = 8.9e-4
# rho_p = 5170
rho_p = 0
mu0 = 4 * np.pi * 10**-7
chi_s = -9.04e-6
c0 = 0

n = 20

def working_model(t, chi_p, r):
    alpha = (9 * eta) / (2 * rho_p * r**2)
    beta = (2 * a**2 * chi_p) / (rho_p * mu0 * (1 + chi_s))
    delta1 = 0.5 * (-alpha + np.sqrt(alpha**2 - 4 * beta))
    delta2 = 0.5 * (-alpha - np.sqrt(alpha**2 - 4 * beta))
    k = delta2 * c0 / (delta2 - delta1)
    return k * np.exp(delta1 * t) + (c0 - k) * np.exp(delta2 * t)

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

def fit_data(time, conc, init_guess):
    popt = (init_guess[0], init_guess[1])
    try:
        (popt, pcov) = curve_fit(working_model, time, conc, p0=init_guess, bounds=bounds)
    except ValueError:
        #print("ValueError encountered at chi_init {chi:0.4f}, r_init {r:0.4f}".format(chi=init_guess[0], r=init_guess[1]))
        pass
    except RuntimeError:
        #print("RuntimeError encountered at chi_init {chi:0.4f}, r_init {r:0.4f}".format(chi=init_guess[0], r=init_guess[1]))
        pass

    model_y = working_model(time, *popt)

    residuals = conc - model_y
    ss_res = np.sum(residuals**2) # sum of square residuals
    ss_total = np.sum((conc - np.mean(conc)) ** 2) # total sum of squares
    r_sq = 1 - ss_res / ss_total
    return popt, r_sq

### START SCRIPT
orig_path = '../../../../test_data/paper_data/'

# dir, file, c0, type, mag, grade, init_chi, init_r
batches = [['magob', 'magob123', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['magob', 'magob124', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['magob', 'magob125', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['magob', '0423_001', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['magob', '0423_002', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['magob', '0423_003', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['armando', '94_b1', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['armando', '94_b2', 0.1, 'a', 'd', 'b', 6, 5e-7],
           ['armando', '94_b3', 0.1, 'a', 'd', 'b', 6, 5e-7]
]

dyna_r = 1.4e-6
dynabeads = [['2025.01.17', '0117_05', 0.1, 'b', 'd', 'b', 5, dyna_r],
             ['2025.01.17', '0117_06', 0.1, 'b', 'd', 'b', 5, dyna_r],
             ['2025.01.17', '0117_07', 0.1, 'b', 'd', 'b', 5, dyna_r]
]

multiconc = [['0418-series3', '1201_05', 0.5, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_06', 0.5, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_07', 0.5, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_08', 0.25, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_09', 0.25, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_10', 0.25, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_11', 0.125, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_12', 0.125, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_13', 0.125, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_14', 0.063, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_15', 0.063, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_16', 0.063, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_17', 0.031, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_18', 0.031, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_19', 0.031, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_20', 0.016, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_21', 0.016, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_22', 0.016, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_23', 0.008, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_24', 0.008, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_25', 0.008, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_26', 0.004, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_27', 0.004, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_28', 0.004, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_29', 0.002, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_30', 0.002, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_31', 0.002, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_32', 0.001, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_33', 0.001, 'a', 'd', 'b', 6, 5e-7],
             ['0418-series3', '1201_34', 0.001, 'a', 'd', 'b', 6, 5e-7],
]

multimag = [['magob', 'magob123', 0.1, 'a', 'd', 'b', 6, 5e-7],
            ['magob', 'magob124', 0.1, 'a', 'd', 'b', 6, 5e-7],
            ['magob', 'magob125', 0.1, 'a', 'd', 'b', 6, 5e-7],
            ['magob', 'magob126', 0.1, 'a', 'c', 'b', 6, 5e-7],
            ['magob', 'magob127', 0.1, 'a', 'c', 'b', 6, 5e-7],
            ['magob', 'magob128', 0.1, 'a', 'c', 'b', 6, 5e-7],
            ['magob', 'magob129', 0.1, 'a', 'c', 'a', 6, 5e-7],
            ['magob', 'magob130', 0.1, 'a', 'c', 'a', 6, 5e-7],
            ['magob', 'magob131', 0.1, 'a', 'c', 'a', 6, 5e-7],
            ['magob', 'magob132', 0.1, 'a', 'b', 'a', 6, 5e-7],
            ['magob', 'magob133', 0.1, 'a', 'b', 'a', 6, 5e-7],
            ['magob', 'magob134', 0.1, 'a', 'b', 'a', 6, 5e-7],
            ['magob', 'magob135', 0.1, 'a', 'a', 'a', 6, 5e-7],
            ['magob', 'magob136', 0.1, 'a', 'a', 'a', 6, 5e-7],
            ['magob', 'magob137', 0.1, 'a', 'a', 'a', 6, 5e-7],
]

selection = input('which series do you want to analyze?\n' + \
    '[a] multi-batch\n[b] dynabeads\n[c] multi-concentration\n' + \
    '[d] multi_magnet\n')
if selection == 'a':
    series = batches
elif selection == 'b':
    series = dynabeads
elif selection == 'c':
    series = multiconc
elif selection == 'd':
    series = multimag
else:
    print('ERROR: invalid selction\n')
    sys.exit()


for s in series:
    path_append = s[0]
    file = s[1]
    c0_input = s[2]
    m_input = s[3]
    t_input = s[4]
    grade = s[5]
    chi_init = s[6]
    r_init = s[7]

    path = orig_path
    if len(path_append) > 0 and path_append[0]=='-':
        path = path_append[1:]
    else:
        path += path_append

    if path[-1] != '/':
        path += '/'

    print("\nNew path: " + path)

    if file[-4:] != '.txt':
        file += '.txt'

    try:
        c0 = float(c0_input)
    except:
        print("ENTRY ERROR: invalid initial concentration entered")
        sys.exit()

    # magnet parameters
    l = 0.0254
    w = 0.0254
    in2m = 0.0254

    if m_input == 'a':
        print('iron oxide selected.')
        rho_p = 5170
        # guesses = [[0.001, 0.5e-6]]
    elif m_input == 'b':
        rho_p = 1400
        # guesses = [[0.0001, 1.4e-6]]
    else:
        print('ENTRY ERROR: invalid MNP material entered')
        sys.exit()

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
    elif t_input == 'e':
        B_r = 0
        a = 0
    else:
        print("ENTRY ERROR: invalid magnet thickness entered")
        sys.exit()

    if grade == 'a':
        B_r = 1.32
        print('Grade N42 selected.')
    elif grade == 'b':
        B_r = 1.48
        print('Grade N52 selected.')
    else:
        print("ENTRY ERROR: invalid magnet grade entered")
        sys.exit()

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

    bounds = ([0, 1e-9], [100, 5e-6])#([0, 0], [np.inf, np.inf])

    file_path = path + file
    print('\nnow processing ' + str(file_path))

    data = np.genfromtxt(file_path)
    time = data[:, 0]
    lux = data[:, 1]

    print('successfully loaded: ' + str(file))

    conc = calibrate(lux, c0)
    neg_count = (np.array(conc) < 0).sum()
    if neg_count == 0:
        print('successful calibration!')
    else:
        print('calibrated with errors.')
        print('found ' + str(neg_count) + ' negative concentration values. Continuing anyways.')

    # fit unadjusted data
    selected_popt, r_sq = fit_data(time, conc, (chi_init, r_init))

    print("\nUNADJUSTEDMODEL")
    print("file: " + str(file))
    print('init_chi\tinit_radius\tchi\t\tradius\t\tr_sq')
    print('{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{r_sq:0.4f}'.format(
        chi_guess=chi_init, r_guess=r_init, chi=selected_popt[0],
        r=selected_popt[1], r_sq=r_sq))

    model_y = working_model(time, *selected_popt)

    # smooth data using the Savitzky-Golay filter
    window_size = 50
    poly_order = 3 # polynomial order

    # compute first derivative of data
    conc_prime = savgol_filter(conc, window_size, poly_order, deriv=1,
        delta=time[1]-time[0])
    conc_dbl_prime = savgol_filter(conc, window_size, poly_order, deriv=2,
        delta=time[1]-time[0])
    min_n = 40
    # print('min n: ' + str(min_n))
    global_min_index = np.argmin(conc_prime[min_n:])+min_n
    # print('global min timepoint: ' + str(time[global_min_index]))

    time_shifted = time[global_min_index:] - time[global_min_index]
    conc_shifted = conc[global_min_index:]
    c0 = conc_shifted[0]

    # fit the shifted data
    adj_selected_popt, adj_r_sq = fit_data(time_shifted, conc_shifted, (chi_init, r_init))

    print("\nTWO-PHASE MODEL")
    print("file: " + str(file))
    print('init_chi\tinit_radius\tchi\t\tradius\t\tr_sq')
    print('{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{r_sq:0.4f}'.format(
        chi_guess=chi_init, r_guess=r_init, chi=adj_selected_popt[0],
        r=adj_selected_popt[1], r_sq=adj_r_sq))

    two_model_y = working_model(time_shifted, *adj_selected_popt)

    # plot data
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 6))
    f.suptitle(file)
    ax3.plot(time, conc, label='data')
    ax3.plot(time, model_y, ':', label='fit')
    ax3.set_xlabel('time (s)')
    ax3.set_ylabel('conc (mg/mL)')
    ax2.plot(time, conc_prime)
    ax2.plot(time[global_min_index], conc_prime[global_min_index], 'o', color='r')
    ax2.set_xlabel('time (s)')
    ax2.set_ylabel('change in conc (mg/mL per s)')
    ax4.plot(time_shifted, conc_shifted, label='data')
    ax4.plot(time_shifted, two_model_y, ':', label='fit')
    ax4.set_xlabel('shifted time (s)')
    ax4.set_ylabel('shifted conc (mg/mL)')

    ax1.spines['top'].set_visible(False)   # Hide top spine
    ax1.spines['right'].set_visible(False) # Hide right spine
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # add results as text in ax 1
    results = 'initial guesses:\n     chi = {chi_guess:0.0e}    rad = {r_guess:0.0e}\n'.format(chi_guess=chi_init, r_guess=r_init) + \
        'bounds:\n     chi = ({cl:0.0e}, {ch:0.0e})\n     rad = ({rl:0.0e}, {rh:0.0e})\n'.format(
            cl=bounds[0][0], ch=bounds[1][0], rl=bounds[0][1], rh=bounds[1][1]) + \
        'inflection point: ' + str(time[global_min_index]) + ' s\n\n' + \
        '        unadjusted       adjusted\n' + \
        'chi:    {chi_unadj:0.6e}     {chi_adj:0.6e}\n'.format(chi_unadj=selected_popt[0], chi_adj=adj_selected_popt[0]) + \
        'rad:    {r_unadj:0.6e}     {r_adj:0.6e}\n'.format(r_unadj=selected_popt[1], r_adj=adj_selected_popt[1]) + \
        'r^2:    {rsq_unadj:0.6f}         {rsq_adj:0.6f}\n'.format(rsq_unadj=r_sq, rsq_adj=adj_r_sq)
    ax1.text(0.05, 0.9, results, transform=ax1.transAxes, fontproperties=fm.FontProperties(family='Monaco',size=10),
        verticalalignment='top', horizontalalignment='left')

    plt.legend()
    plt.tight_layout()
    # plt.show()
    save_dir = '../../../../validation_data/model-3.0_results/2025.02.02/'
    plt.savefig(save_dir + file + '.png', dpi=600)
