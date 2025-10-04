import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
from tqdm import tqdm
from scipy.optimize import curve_fit
from scipy.stats import linregress
from scipy.signal import savgol_filter
from matplotlib import font_manager as fm
from datetime import datetime
import os
import time as pytime
import pandas as pd
import warnings

ver = 2.2 # updated to include data truncation
to_save = True

file_suffix = ''

# load files to run from script
if len(sys.argv) < 3:
    sys.exit('ERROR: too few arguments.\nExpected usage:\n>>> python model_fits.py <log_file> <list file>')
log_path = sys.argv[1]
to_run_file = sys.argv[2]
print('log input: ' + log_path)
print('list file: ' + to_run_file)

# option to add suffix to file names to allow for duplicate runs
if len(sys.argv) > 3:
    file_suffix = sys.argv[3]

if log_path[-5:] != '.xlsx':
    log_path += '.xlsx'

if to_run_file[-4:] != '.txt':
    to_run_file += '.txt'

with open(to_run_file, 'r') as f:
    to_run_list = f.readlines()

### START SCRIPT
path = '../../../../test_data/paper_data/'

# set up folder
# save_dir_base = '../analysis/fits/'
save_dir_base = '../../../../validation_data/model-4.0_results/'
# check for and make a dated folder  if not found
date_dir = datetime.today().strftime('%Y.%m.%d')
save_dir = save_dir_base + date_dir + file_suffix + '/'
if not os.path.isdir(save_dir):
    os.mkdir(save_dir)

label_font = fm.FontProperties(family='Avenir', size=10)
subtitle_font = fm.FontProperties(family='Avenir', size=12)
title_font = fm.FontProperties(family='Avenir', size=16)

plt.rcParams.update({'font.family': 'Avenir', 'figure.titlesize': 16,
    'figure.titleweight': 'bold', 'axes.titlesize': 12, 'axes.labelsize': 12,
    'xtick.labelsize': 10, 'ytick.labelsize': 10})

file_lines = []

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
        pass
    except RuntimeError:
        pass

    model_y = working_model(time, *popt)

    residuals = conc - model_y
    ss_res = np.sum(residuals**2) # sum of square residuals
    ss_total = np.sum((conc - np.mean(conc)) ** 2) # total sum of squares
    MSE = 1 - ss_res / ss_total
    return popt, MSE

def fit_mag_field(window, b_r, l, w, t):
    def B_field(x, B_r, L, W, T):
       return (B_r/np.pi)*(np.arctan((L*W)/(2*x*np.sqrt(4*x**2+L**2+W**2)))-np.arctan((L*W)/(2*(x+T)*np.sqrt(4*(x+T)**2+L**2+W**2))))

    z_low = window[0] / 1000
    z_high = window[1] / 1000
    z_window = np.linspace(z_low, z_high, 1000)
    b_window = B_field(z_window, b_r, l, w, t)

    linreg = linregress(z_window, b_window)
    # y_fit = lin_fit(z_window, linreg.slope, linreg.intercept)
    fit_str = 'B = {:0.8f} * z + {:0.8f}\n\tMSE = {:0.4f}'.format(linreg.slope,
        linreg.intercept, linreg.rvalue**2)

    return linreg.slope, fit_str

### READ LOG FILE
try:
    log_df = pd.read_excel(path + log_path, sheet_name='log',
        dtype={'Magnet': str})
    print('\nLog file {:s} loaded.'.format(log_path.split('/')[-1]))
except:
    print('\nERROR: Invalid log file.')
    sys.exit()

try:
    sample_df = pd.read_excel(path + log_path, sheet_name='samples')
    print('Sample sheet loaded.')
except:
    print('ERROR: Could not load sample sheet.')
    sys.exit()

try:
    mag_df = pd.read_excel(path + log_path, sheet_name='magnets',
        dtype={'ID': str, 'Grade': float})
    print('Magnets sheet loaded.')
except:
    print('ERROR: Could not load magnet sheet.')
    sys.exit()

### LOOP THROUGH ALL FILES
num_files = len(to_run_list)
file_counter = 0
for f in to_run_list:
    file_counter += 1
    print('\n\nnow processing file {:d}/{:d}'.format(file_counter, num_files))
    time_str = datetime.today().strftime('%H:%M')

    # reinitialize all variables
    # fit params
    eta = 0 # water
    rho_p = 0
    mu0 = 4 * np.pi * 10**-7
    chi_s = 0 #water
    c0 = 0

    n = 20
    in2m = 0.0254

    file_lines = []

    # process file name
    f = f.strip()
    file_key = f
    file = f

    if file_key[-4:] == '.txt':
        file_key = file_key[:-4]
    else:
        file += '.txt'

    try:
        entry = log_df.loc[log_df['File'] == file_key].iloc[0]
        print('Entry for {} successfully found.'.format(file_key))
    except:
        sys.exit('ERROR: Could not find file {} in log.'.format(file))

    try:
        dir = str(entry['Directory'])
        if dir[-1] != '/':
            dir += '/'
        if 'paper_data/' in dir:
            dir = dir.replace('paper_data/', '') # fix duplicate
        print('Directory: ' + dir)
    except:
        sys.exit('ERROR: Invalid directory: {}.'.format(entry['Directory']))

    sample = str(entry['Sample'])
    magnet = str(entry['Magnet'])

    try:
        sample_entry = sample_df.loc[sample_df['ID'] == sample].iloc[0]
        print('\nSample: ' + sample)
    except:
        print('ERROR: Could not find sample {} in sample log'.format(sample))
        sys.exit()

    try:
        material = str(sample_entry['Material'])
    except:
        print('ERROR: Invalid sample material.')
        sys.exit()

    try:
        rho_p = float(sample_entry['Density'])
        print('Density: {} kg/m^3'.format(rho_p))
    except ValueError:
        print('ERROR: Invalid density - should be a numerical value with units kg/m^3')
        sys.exit()

    try:
        solvent = sample_entry['Solvent']
        if solvent.lower() == 'water':
            solvent_type = 'Water'
            eta = 8.9e-4
            chi_s = -9.04e-6
        elif solvent.lower() == 'dpbs':
            solvent_type = 'DPBS'
            eta = 0.89e-3
            chi_s = -9.05e-6
        else:
            print('ERROR: Unknown solvent.')
            sys.exit()
        print('Solvent: ' + solvent_type)
    except:
        print('ERROR: Solvent could not be found.')
        sys.exit()

    try:
        radius = float(sample_entry['Radius'])
        print('Radius: {} m'.format(radius))
        radius_std = float(sample_entry['Radius-std'])
        print('Radius std dev: {} m'.format(radius_std))
        optimize_radius = True
        if radius == 0:
            radius = 'Unknown'
            print('Radius: unknown')
            optimize_radius = False
    except:
        radius = 'Unknown'
        print('Radius: unknown')
        optimize_radius = False

    try:
        batch = str(sample_entry['Batch-date/Lot'])
    except:
        print('ERROR: Could not find Batch date/Lot')
        sys.exit()

    try:
        c0 = float(sample_entry['Conc.\n[mg/mL]'])
    except:
        print('ERROR: Invalid initial concentration')
        sys.exit()

    # magnet parameters
    try:
        mag_entry = mag_df.loc[mag_df['ID'] == magnet].iloc[0]
        print('\nMagnet: ' + magnet)
    except:
        print('ERROR: Could not find magnet {} in magnet log.'.format(magnet))
        sys.exit()

    try:
        mag_name = str(mag_entry['K&J magnet'])
        print('K&J Magnet: ' + str(mag_name))
    except:
        sys.exit('ERROR: Could not find name of magnet.')

    try:
        l_in = float(mag_entry['Length']) # inches
        print('Length: {}"'.format(l_in))
    except:
        sys.exit('ERROR: Invalid length.')

    try:
        w_in = float(mag_entry['Width']) # inches
        print('Width: {}"'.format(w_in))
    except:
        sys.exit('ERROR: Invalid width.')

    try:
        t_in = float(mag_entry['Height']) # inches
        print('Thickness: {}"'.format(t_in))
    except:
        sys.exit('ERROR: Invalid height.')

    try:
        grade = int(mag_entry['Grade'])
        print('Grade: N{:d}'.format(grade))
    except:
        sys.exit('ERROR: Invalid grade: {}.'.format(mag_entry['Grade']))

    try:
        dist = float(mag_entry['Distance']) # mm
        window = [dist - 0.5, dist + 0.5]
    except:
        sys.exit('ERROR: Invalid distance.')

    # magnet params
    l = l_in * in2m
    w = w_in * in2m
    t = t_in * in2m
    if grade == 52:
        b_r = 1.48
    elif grade == 42:
        b_r = 1.32
    else:
        print('Unknown magnet grade of {}'.format(grade))
        sys.exit()

    a, fit_str = fit_mag_field(window, b_r, l, w, t)
    print('Fit magnetic field: a = {}'.format(a))
    print(fit_str)

    ## update file lines
    file_lines.append(str(file))
    file_lines.append('\n--- Analysis Information ---')
    file_lines.append('Analyzed on ' + date_dir + ' at ' + time_str)
    file_lines.append('Analyzed with model.py ver 4.' + str(ver))

    file_lines.append('\n--- File Information ---')
    path_str = path
    while path_str[:3] == '../':
        path_str = path_str[3:]
    file_lines.append('File directory: ' + str(path_str))
    file_lines.append('File: ' + str(file))

    file_lines.append('\n--- Sample + Test Information ---')
    file_lines.append('Type: ' + material)
    file_lines.append('\tDensity: ' + str(rho_p) + ' kg/m^3')
    file_lines.append('Batch Date/Lot: ' + str(batch))
    file_lines.append('\tRadius: ' + str(radius) + ' m')
    file_lines.append('Initial concentration: ' + str(c0) + ' mg/mL')
    file_lines.append('Solvent: ' + solvent_type)
    file_lines.append('\tDynamic viscosity: ' + str(eta) + ' Pa·s')
    file_lines.append('\tMagnetic susceptibility: ' + str(chi_s))

    file_lines.append('Magnet: K&J ' + mag_name)
    file_lines.append('\tSize: {}" x {}" x {}"'.format(l_in, w_in, t_in))
    file_lines.append('\tGrade: N{}'.format(grade))
    file_lines.append('Distance to optical path: ' + str(dist))
    file_lines.append('\tWindow: [{}, {}]'.format(window[0], window[1]))
    file_lines.append('Magnetic field fit:\n' + fit_str)

    ### IMPORT DATA
    file_path = path + dir + file
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

    #### MULTI-MODAL ANALYSIS
    # smooth data using the Savitzky-Golay filter
    window_size = 100
    poly_order = 2 # polynomial order

    # compute first derivative of data
    conc_prime = savgol_filter(conc, window_size, poly_order, deriv=1,
        delta=time[1]-time[0])
    conc_dbl_prime = savgol_filter(conc, window_size, poly_order, deriv=2,
        delta=time[1]-time[0])
    min_n = 20
    print('Minimum inflection point: ' + str(min_n))
    global_min_index = np.argmin(conc_prime[min_n:])+min_n
    print('Global minimum timepoint: ' + str(time[global_min_index]))

    # truncate the data
    trunc_i = len(conc_prime)-1
    threshold = -1
    consec_vals = 50
    counter = 0
    # for i in range(global_min_index, len(conc_prime)):
    #     if np.abs(conc_prime[i]) < threshold:
    #         counter +=1
    #     else:
    #         counter = 0
    #     if counter > consec_vals:
    #         trunc_i = i
    #         break

    print('Truncated at: {:0.3f} (n={:d}) with threshold {:e}'.format(time[trunc_i], trunc_i, threshold))

    time_shifted = time[global_min_index:trunc_i] - time[global_min_index]
    conc_shifted = conc[global_min_index:trunc_i]

    ## update file lines
    file_lines.append('\n--- File Processing Information ---')
    file_lines.append('Calibrated with {} negative concentration values.'.format(neg_count))
    file_lines.append('Smoothed with Savitzky-Golay filter with window size of {} and poly_order of {}.'.format(window_size, poly_order))
    file_lines.append('Global min timepoint (after min {} values) is {} s.'.format(min_n, time[global_min_index]))
    file_lines.append('Truncation threshold: {:0.2e} with {:d} consecutive values.'.format(threshold, consec_vals))
    file_lines.append('Truncated at: {:0.3f} (n={:d}).'.format(time[trunc_i], trunc_i))

    ### INTIALIZE GUESSES & BOUNDS
    low_r_bound = radius-radius_std
    high_r_bound = radius+radius_std
    bounds = ([1e-5, low_r_bound], [np.inf, high_r_bound])#([0, 0], [np.inf, np.inf])
    num_chi_guesses = 500
    num_r_guesses = 25
    chis = np.logspace(-6, 2, num=num_chi_guesses) # changed from -6 to -2
    rs = np.linspace(low_r_bound, high_r_bound, num=num_r_guesses)
    guesses = []

    for i in range(len(chis)):
        for j in range(len(rs)):
            guesses.append([chis[i], rs[j]])
    print("total number of guesses: " + str(len(guesses)))

    ## update file lines
    file_lines.append('\n--- Fit parameters ---')
    file_lines.append('Guess ranges:')
    file_lines.append('\tChi: [{:0.2e}, {:0.2e}] ({:d} values with log spacing)'.format(chis[0], chis[-1], num_chi_guesses))
    file_lines.append('\tRadius: [{:0.6e}, {:0.6e} ({:d} values with lin spacing)]'.format(rs[0], rs[-1], num_r_guesses))
    file_lines.append('Bounds: ')
    file_lines.append('\tChi: [{:0.2e}, {:0.2e}]'.format(bounds[0][0], bounds[1][0]))
    file_lines.append('\tRadius: [{:0.2e}, {:0.2e}]'.format(bounds[0][1], bounds[1][1]))
    # file_lines.append('All values:')
    # file_lines.append('\tChi: ' + str(chis))
    # file_lines.append('\tRadius: ' + str(rs))


    ### FIT OPTIMIZATION --- UPDATED TO MEAN SQUARE ERROR (BUT MSE LABELS ARE UNCHANGED FOR NOW)
    # fit the shifted data
    best_MSE_guess = guesses[0]
    best_MSE = np.inf
    best_MSE_result = [0, 0]
    best_MSE_r_sq = -np.inf
    best_dist_guess = guesses[0]
    best_dist = np.inf
    best_dist_MSE = -np.inf
    best_dist_r_sq = -np.inf
    best_dist_result = [0, 0]
    c0 = conc_shifted[0]

    print_list = []

    start_time = pytime.time()
    for init_guess in tqdm(guesses):
        # iterate over guesses
        # popt, MSE = fit_data(time_shifted, conc_shifted, init_guess)

        model = working_model
        try:
            (popt, pcov) = curve_fit(working_model, time_shifted, conc_shifted, p0=init_guess, bounds=bounds)

            adj_model_y = working_model(time_shifted, *popt)

            residuals = conc_shifted - adj_model_y
            ss_res = np.sum(residuals**2) # sum of square residuals
            mse = ss_res / len(residuals)
            MSE = mse
            ss_total = np.sum((conc_shifted - np.mean(conc_shifted)) ** 2) # total sum of squares
            r_sq = 1 - ss_res / ss_total
            chi_err = (pcov[0][0]) * (1/2)
            rad_err = (pcov[1][1]) * (1/2)
            # check conditionals
            to_print = False
            print_str = ''

            if MSE < best_MSE:
                best_MSE = MSE
                best_MSE_result = popt
                best_MSE_guess = init_guess
                best_MSE_r_sq = r_sq
                to_print = True
                print_str += '^'

            if optimize_radius:
                r_result = popt[1]
                distance = np.abs(radius - r_result)

                if distance <= best_dist:
                    best_dist_guess = init_guess
                    best_dist_result = popt
                    best_dist = distance
                    best_dist_MSE = MSE
                    best_dist_r_sq = r_sq
                    to_print = True
                    print_str += '*'

            if to_print:
                print_str += '{chi_guess:0.6e}\t{r_guess:0.6e}\t{chi:0.6e}\t{r:0.6e}\t{MSE:0.12f}\t{r_sq:0.12f}'.format(
                    chi_guess=init_guess[0], r_guess=init_guess[1], chi=popt[0],
                    r=popt[1], MSE=MSE, r_sq=r_sq)
                print_list.append(print_str)

        except ValueError:
            #print("ValueError encountered at chi_init {chi:0.4f}, r_init {r:0.4f}".format(chi=init_guess[0], r=init_guess[1]))
            pass
        except RuntimeError:
            #print("RuntimeError encountered at chi_init {chi:0.4f}, r_init {r:0.4f}".format(chi=init_guess[0], r=init_guess[1]))
            pass
        except ZeroDivisionError:
            pass

    end_time = pytime.time()
    duration = end_time - start_time

    print('time to fit: ' + str(duration) + ' s')

    print("\nFINAL MODEL")
    print("file: " + str(file))
    print('fit:\tinit_chi\tinit_radius\tchi\t\tradius\t\tMSE\t\tr_sq')
    print('MSE:\t{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{MSE:0.12e}\t{r_sq:0.12f}'.format(
        chi_guess=best_MSE_guess[0], r_guess=best_MSE_guess[1], chi=best_MSE_result[0],
        r=best_MSE_result[1], MSE=best_MSE, r_sq=best_MSE_r_sq))
    if optimize_radius:
        print('rad:\t{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{MSE:0.12e}\t{r_sq:0.12f}'.format(
            chi_guess=best_dist_guess[0], r_guess=best_dist_guess[1], chi=best_dist_result[0],
            r=best_dist_result[1], MSE=best_dist_MSE, r_sq=best_dist_r_sq))

    best_MSE_y = working_model(time_shifted, *best_MSE_result)

    if optimize_radius:
        best_dist_y = working_model(time_shifted, *best_dist_result)

    file_lines.append('\nFINAL RESULTS')
    file_lines.append('Opt. param.:\tinit_chi\tinit_radius\tchi\t\tradius\t\tMSE')
    file_lines.append('Best MSE:\t{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{MSE:0.12e}\t{r_sq:0.12f}'.format(
        chi_guess=best_MSE_guess[0], r_guess=best_MSE_guess[1], chi=best_MSE_result[0],
        r=best_MSE_result[1], MSE=best_MSE, r_sq=best_MSE_r_sq))
    if optimize_radius:
        file_lines.append('Best rad:\t{chi_guess:0.6e}\t{r_guess:0.6e}\t{chi:0.6e}\t{r:0.6e}\t{MSE:0.12e}\t{r_sq:0.12f}'.format(
            chi_guess=best_dist_guess[0], r_guess=best_dist_guess[1], chi=best_dist_result[0],
            r=best_dist_result[1], MSE=best_dist_MSE, r_sq=best_dist_r_sq))

    ## update files
    file_lines.append('\n--- Full Results ---')
    file_lines.append('Time to fit: ' + str(duration) + ' s')
    file_lines.append('^new best by MSE')
    if optimize_radius:
        file_lines.append('*new best by radius\n')
    file_lines.append('init_chi\tinit_radius\tchi\t\tradius\t\tMSE\t\tr_sq')
    for s in print_list:
        file_lines.append(s)

    ### FORMAT FIG RESULTS
    # plot data
    f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 4))
    f.suptitle(file)
    ax2.plot(time, conc_prime * 1000, color='green', label='Data', zorder=2)
    ax2.plot(time[global_min_index], conc_prime[global_min_index] * 1000, 'o', markersize=5, color='r', label='Inflection point', zorder=3)
    ax2.axvline(time[trunc_i], color='#777777', zorder=1, label='Truncation')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Conc. gradient (µg/mL per s)')
    ax2.legend(loc='lower right', handlelength=2)

    ax3.plot(time, conc, color='green', label='Data')
    ax3.plot(time_shifted + time[global_min_index], best_MSE_y, '--', color='blue', label='Best MSE fit')
    if optimize_radius:
        ax3.plot(time_shifted + time[global_min_index], best_dist_y, ':', color='red', label='Best radius fit')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Concentration (mg/mL)')
    ax3.legend(loc='upper right', handlelength=2)

    ax1.spines['top'].set_visible(False)   # Hide top spine
    ax1.spines['right'].set_visible(False) # Hide right spine
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    grey = '#999999'
    text_kwargs = {'fontproperties': label_font,
        'verticalalignment': 'top', 'horizontalalignment': 'left',
        'transform': ax1.transAxes}
    labels = 'chi_i:\nrad_i:\nchi:\nrad:\n$MSE$'
    MSE_str = '{chi_i:0.2e}\n{r_i:0.2e}\n{chi:0.2e}\n{rad:0.2e}\n{MSE:0.2e}'.format(
        chi_i=best_MSE_guess[0], r_i=best_MSE_guess[1], chi=best_MSE_result[0],
        rad=best_MSE_result[1], MSE=best_MSE)
    rad_str = '{chi_i:0.2e}\n{r_i:0.2e}\n{chi:0.2e}\n{rad:0.2e}\n{MSE:0.2e}'.format(
        chi_i=best_dist_guess[0], r_i=best_dist_guess[1], chi=best_dist_result[0],
        rad=best_dist_result[1], MSE=best_dist_MSE)

    ax1.text(0.02, 0.44, labels, **text_kwargs)
    ax1.text(0.24, 0.54, 'Best $MSE$', **text_kwargs, fontsize=12)
    ax1.text(0.24, 0.44, MSE_str, **text_kwargs)
    if optimize_radius:
        ax1.text(0.65, 0.54, 'Best radius', **text_kwargs, fontsize=12)
        ax1.text(0.65, 0.44, rad_str, **text_kwargs)
    ax1.set_xlim([0, 1])
    ax1.set_ylim([0, 1])
    ax1.plot([0.2, 0.2], [0.1, 0.560], color='grey', linewidth=1, linestyle=':')
    ax1.plot([0.2, 1.0], [0.465, 0.465], color='grey', linewidth=1, linestyle=':')

    chi_param_str = 'chi_init range'
    chi_params = '[{:0.4e}, {:0.4e}]'.format(chis[0], chis[-1])
    r_param_str = 'r_init range'
    r_params = '[{:0.4e}, {:0.4e}]'.format(rs[0], rs[-1])
    bounds_str = 'bounds'
    bounds_chi_str = 'chi: '
    bounds_chi = '{:0.4e} - {:0.4e}'.format(bounds[0][0], bounds[0][1])
    bounds_rad_str = 'rad: '
    bounds_rad = '{:0.4e} - {:0.4e}'.format(bounds[1][0], bounds[1][1])

    ax1.text(0.02, 0.97, 'Fit parameters', **text_kwargs, fontsize=12)
    ax1.text(0.02, 0.87, chi_param_str, **text_kwargs)
    ax1.text(0.4, 0.87, chi_params, **text_kwargs)
    ax1.text(0.02, 0.81, r_param_str, **text_kwargs)
    ax1.text(0.4, 0.81, r_params, **text_kwargs)
    ax1.text(0.02, 0.72, bounds_str, **text_kwargs)
    ax1.text(0.24, 0.75, bounds_chi_str, **text_kwargs)
    ax1.text(0.4, 0.75, bounds_chi, **text_kwargs)
    ax1.text(0.24, 0.69, bounds_rad_str, **text_kwargs)
    ax1.text(0.4, 0.69, bounds_rad, **text_kwargs)
    ax1.plot([0.0, 1.0], [0.6, 0.6], color=grey, linewidth=1)
    ax1.plot([0.0, 1.0], [0.89, 0.89], color=grey, linewidth=1, linestyle=':')
    ax1.plot([0.35, 0.35], [0.63, 0.9], color=grey, linewidth=1, linestyle=':')

    plt.tight_layout()

    ### SAVE RESULTS
    if to_save:
        with open(save_dir + file[:-4] + '-fit' + file_suffix + '.txt', 'w') as f:
            for l in file_lines:
                f.write(l + '\n')

        plt.savefig(save_dir + file[:-4] + '-fit' + file_suffix + '.png', dpi=600)
        plt.close()
    else:
        plt.show()
        plt.close()
