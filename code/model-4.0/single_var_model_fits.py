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

ver = 2.0 # updated to read analysis files from txt file.
# to do: implement flags allowing usage: single_var_model_fits.py -single <log_file> <data file name>
# to do: also implement flag allowing radius + some std dev and radius - std dev
to_save = True

file_suffix = ''

### INITIALIZE PARAMETERS
# constants
mu0 = 4 * np.pi * 10**-7
in2m = 0.0254
n = 20 # num final points used for calibration

# pre-processing
min_n = 20
window_size = 50
poly_order = 3 # polynomial order
to_adj = True
num_guesses = 100000

# fit params
### INTIALIZE GUESSES & BOUNDS
chis = np.logspace(-9, 3, num=num_guesses) # chi only
guesses = []
for c in chis:
    guesses.append([c])

bounds = ([0], [np.inf])

# LOAD COMMAND LINE ARGUMENTS
if len(sys.argv) < 3:
    sys.exit('ERROR: too few arguments.\nExpected usage:\n>>> python model_fits.py <log_file> <list file>')
log_path = sys.argv[1]
to_run_file = sys.argv[2]
print('log input: ' + log_path)
print('list file: ' + to_run_file)

# define plot colors
purple = '#8645a3'
darker_blue = '#002e91'
dark_blue = '#0077bb'
cyan = '#33bbee'
teal = '#009988'
green = '#00dc79'
yellow = '#ffc800'
orange = '#ee7733'
red = '#cc3311'
maroon = '#a30011'
magenta = '#ee3377'
pink = '#ee85b7'
vib_grey = '#bbbbbb'
# rainbow_grey
black = '#000000'

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

def single_var_model(t, chi_p):
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

def fit_mag_field(window, b_r, l, w, t):
    def B_field(x, B_r, L, W, T):
       return (B_r/np.pi)*(np.arctan((L*W)/(2*x*np.sqrt(4*x**2+L**2+W**2)))-np.arctan((L*W)/(2*(x+T)*np.sqrt(4*(x+T)**2+L**2+W**2))))

    z_low = window[0] / 1000
    z_high = window[1] / 1000
    z_window = np.linspace(z_low, z_high, 1000)
    b_window = B_field(z_window, b_r, l, w, t)

    linreg = linregress(z_window, b_window)
    fit_str = 'B = {:0.8f} * z + {:0.8f}\n\tr^2 = {:0.4f}'.format(linreg.slope,
        linreg.intercept, linreg.rvalue**2)

    return linreg.slope, fit_str

### READ TEST PARAMETERS
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
for f in to_run_list:
    time_str = datetime.today().strftime('%H:%M')

    # reinitialize sample properties
    eta = 0 # water
    rho_p = 0
    chi_s = 0 #water
    c0 = 0

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
        optimize_radius = True
        if radius == 0:
            radius = 'Unknown'
            print('Radius: unknown')
            optimize_radius = False
    except:
        radius = 'Unknown'
        print('Radius: unknown')
        optimize_radius = False
        sys.exit('ERROR: Cannot proceed with unknown radius.')

    r = radius

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
    file_lines.append('Analyzed with single_var_model_fits.py ver 4.' + str(ver))

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

    ## update file lines
    file_lines.append('\n--- Fit parameters ---')
    file_lines.append('Guess ranges: [{:0.2e}, {:0.2e}] ({} values with log spacing)'.format(chis[0], chis[-1], num_guesses))
    file_lines.append('Fit bounds: [{:0.2e}, {:0.2e}]'.format(bounds[0][0], bounds[1][0]))
    # file_lines.append('All values: ' + str(chis))

    ### IMPORT DATA
    file_path = path + dir + file
    print('\nNow processing ' + str(file_path))

    data = np.genfromtxt(file_path)
    time = data[:, 0]
    lux = data[:, 1]
    print('Successfully loaded: ' + str(file))

    ### PRE-PROCESS DATA
    conc = calibrate(lux, c0)
    neg_count = (np.array(conc) < 0).sum()
    if neg_count == 0:
        print('successful calibration!')
    else:
        print('Calibrated with errors.')
        print('Found ' + str(neg_count) + ' negative concentration values. Continuing anyways.')

    # smooth data using the Savitzky-Golay filter
    if to_adj:
        # compute first derivative of data
        conc_prime = savgol_filter(conc, window_size, poly_order, deriv=1,
            delta=time[1]-time[0])
        conc_dbl_prime = savgol_filter(conc, window_size, poly_order, deriv=2,
            delta=time[1]-time[0])

        print('Minimum inflection point: ' + str(min_n))
        global_min_index = np.argmin(conc_prime[min_n:])+min_n
        print('Global minimum timepoint: ' + str(time[global_min_index]))

        time_shifted = time[global_min_index:] - time[global_min_index]
        conc_shifted = conc[global_min_index:]

        ## update file lines
        file_lines.append('\n--- File Processing Information ---')
        file_lines.append('Calibrated with {} negative concentration values.'.format(neg_count))
        file_lines.append('Smoothed with Savitzky-Golay filter with window size of {} and poly_order of {}.'.format(window_size, poly_order))
        file_lines.append('Global min timepoint (after min {} values) is {} s.'.format(min_n, time[global_min_index]))

    else:
        time_shifted = time
        conc_shifted = conc
        file_lines.append('\n--- File Processing Information ---')
        file_lines.append('Calibrated with {} negative concentration values.'.format(neg_count))
        file_lines.append('Data unadjusted.')
        conc_prime = conc_shifted
        global_min_index=0

    ### FIT OPTIMIZATION
    # fit the shifted data
    best_fits = {
        'r_sq': dict(guess=-1, chi=-1, fit_err=-1, r_sq=-np.inf, mse=-1, marker='^', print_list=[], color=purple),
        'mse': dict(guess=-1, chi=-1, fit_err=-1, r_sq=-1, mse=np.inf, marker='*', print_list=[], color=teal),
        'fit_err': dict( guess=-1, chi=-1, fit_err=np.inf, r_sq=-1, mse=-1, marker='~', print_list=[], color=cyan),
    }

    print_list = []
    c0 = conc_shifted[0]

    start_time = pytime.time()
    for init_guess in tqdm(guesses):
        try:
            (popt, pcov) = curve_fit(single_var_model, time_shifted, conc_shifted, p0=init_guess, bounds=bounds)
            adj_model_y = single_var_model(time_shifted, *popt)

            residuals = conc_shifted - adj_model_y
            ss_res = np.sum(residuals**2) # sum of square residuals
            ss_total = np.sum((conc_shifted - np.mean(conc_shifted)) ** 2) # total sum of squares

            # error metrics
            r_sq = 1 - ss_res / ss_total
            mse = ss_res / len(residuals)
            fit_err = pcov[0][0] ** (1/2)

            chi = popt[0]
            # check conditionals
            print_str = ''

            update_keys = []

            if fit_err < best_fits['fit_err']['fit_err']:
                update_keys.append('fit_err')
            if mse < best_fits['mse']['mse']:
                update_keys.append('mse')
            if r_sq > best_fits['r_sq']['r_sq']:
                update_keys.append('r_sq')

            for key in update_keys:
                best_fits[key]['guess'] = init_guess[0]
                best_fits[key]['chi'] = chi
                best_fits[key]['fit_err'] = fit_err
                best_fits[key]['mse'] = mse
                best_fits[key]['r_sq'] = r_sq
                print_str += best_fits[key]['marker']

            # add results to print strings
            print_str += '\t{guess:0.8e}\t{chi:0.8e}\t{fit_err:0.8e}\t{mse:0.8e}\t{r_sq:0.8e}'.format(
                guess=init_guess[0], chi=chi, fit_err=fit_err, mse=mse,
                r_sq=r_sq)
            print_list.append(print_str)
            for key in update_keys:
                best_fits[key]['print_list'].append(print_str)

        except ValueError:
            pass
        except RuntimeError:
            pass
        except ZeroDivisionError:
            pass

    end_time = pytime.time()
    duration = end_time - start_time

    print('time to fit: ' + str(duration) + ' s')

    print("\nTWO-PHASE MODEL")
    print("file: " + str(file))
    print('error metric\tchi\t\tfit_err\t\tmse\t\tr_sq')
    for key in best_fits:
        d = best_fits[key]
        print('best {metric}\t{chi:0.6e}\t{fit_err:0.8e}\t{mse:0.8e}\t{r_sq:0.8e}'.format(
            metric=key, chi=d['chi'], fit_err=d['fit_err'], mse=d['mse'],
            r_sq=d['r_sq']))

    ## update files
    file_lines.append('\n--- Model Results ---')
    file_lines.append('Time to fit: ' + str(duration) + ' s')

    file_lines.append('\nFINAL RESULTS')
    file_lines.append('\terror metric\tguess\t\tchi\t\tfit_err\t\tmse\t\tr_sq')
    for key in best_fits:
        d = best_fits[key]
        file_lines.append('best {metric}\t{guess:0.8e}\t{chi:0.8e}\t{fit_err:0.8e}\t{mse:0.8e}\t{r_sq:0.8e}'.format(
            metric=key, guess=d['guess'], chi=d['chi'], fit_err=d['fit_err'], mse=d['mse'],
            r_sq=d['r_sq']))

    marker_str = ''
    for key in best_fits:
        d = best_fits[key]
        marker_str += '{marker}new best by {metric}\n'.format(metric=key,
            marker=d['marker'])

    for key in best_fits:
        d = best_fits[key]
        file_lines.append('\nBEST {metric} RESULTS'.format(metric=key.upper()))
        file_lines.append(marker_str)
        file_lines.append('\terror metric\tguess\t\tchi\t\tfit_err\t\tmse\t\tr_sq')
        for l in d['print_list']:
            file_lines.append(l)

    file_lines.append('\nFULL RESULTS')
    file_lines.append(marker_str)
    file_lines.append('\terror metric\tguess\t\tchi\t\tfit_err\t\tmse\t\tr_sq')
    for s in print_list:
        file_lines.append(s)

    ### FORMAT FIG RESULTS
    # plot data
    f, (ax3) = plt.subplots(1, 1, figsize=(6, 4))
    grey = '#999999'
    f.suptitle(file)

    ax3.plot(time, conc, color=orange, label='Data')
    for key in best_fits:
        d = best_fits[key]
        ax3.plot(time_shifted, single_var_model(time_shifted, d['chi']),
            linestyle=':', color=d['color'], label='best ' + key)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Concentration (mg/mL)')
    ax3.legend(loc='upper right', handlelength=2)
    #
    # ax1.spines['top'].set_visible(False)   # Hide top spine
    # ax1.spines['right'].set_visible(False) # Hide right spine
    # ax1.spines['left'].set_visible(False)
    # ax1.spines['bottom'].set_visible(False)
    # ax1.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # grey = '#999999'
    # text_kwargs = {'fontproperties': label_font,
    #     'verticalalignment': 'top', 'horizontalalignment': 'left',
    #     'transform': ax1.transAxes}
    # labels = 'chi_i:\nchi:\n$r^2$'

    plt.tight_layout()

    ### SAVE RESULTS
    if to_save:
        with open(save_dir + file[:-4] + '-fit' + file_suffix + '.txt', 'w') as f:
            for l in file_lines:
                f.write(l + '\n')

        plt.savefig(save_dir + file[:-4] + '-fit' + file_suffix + '.png', dpi=600)
        print('Saved ' + save_dir + file[:-4] + '-fit' + file_suffix + ' as .txt and .png.')
    else:
        plt.show()
