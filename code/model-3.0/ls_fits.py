import numpy as np
import matplotlib.pyplot as plt
import single_magnetic_analysis as ma
from mpl_toolkits.mplot3d import Axes3D
import sys
from tqdm import tqdm
from scipy.optimize import curve_fit

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

### START SCRIPT
path = '../../../../test_data/paper_data/'

print("\nCurrent path: " + path)
path_append = input('Add to path? [enter to skip or start with "-" to enter fully new path]\n')
if len(path_append) > 0 and path_append[0]=='-':
    path = path_append[1:]
else:
    path += path_append

if path[-1] != '/':
    path += '/'

print("\nNew path: " + path)

file = input('Please enter file name: \n')

if file[-4:] != '.txt':
    file += '.txt'

c0_input = input('\nWhat is the initial concentration of the solution? [mg/mL]\n')
try:
    c0 = float(c0_input)
except:
    print("ENTRY ERROR: invalid initial concentration entered")
    sys.exit()

# magnet parameters
l = 0.0254
w = 0.0254
in2m = 0.0254

m_input = input('Which MNP are you using?\n[a] pure iron oxide\n[b] Dynabeads\n')
if m_input == 'a':
    rho_p = 5170
    guesses = [[0.001, 0.5e-6]]
elif m_input == 'b':
    rho_p = 1400
    guesses = [[0.0001, 1.4e-6]]
else:
    print('ENTRY ERROR: invalid MNP material entered')
    sys.exit()

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
elif t_input == 'e':
    B_r = 0
    a = 0
else:
    print("ENTRY ERROR: invalid magnet thickness entered")
    sys.exit()

grade = input('\nWhat grade is your magnet?\n[a] N42\n[b] N52\n')
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

#initial_guess = [0.001, 0.5e-6]

# guesses = []
# chis = [1e-8, 8e-7, 6e-7, 4e-7, 2e-7,
#         1e-7, 8e-6, 6e-6, 4e-6, 2e-6,
#         1e-6, 8e-5, 6e-5, 4e-5, 2e-5,
#         1e-5, 8e-4, 6e-4, 4e-4, 2e-4,
#         1e-4, 8e-3, 6e-3, 4e-3, 2e-3,
#         1e-3, 8e-2, 6e-2, 4e-2, 2e-2]
# rs =   [1e-9, 8e-8, 6e-8, 4e-8, 2e-8,
#         1e-8, 8e-7, 6e-7, 4e-7, 2e-7,
#         1e-7, 8e-6, 6e-6, 4e-6, 2e-6,
#         1e-6, 8e-5, 6e-5, 4e-5, 2e-5,
#         1e-5, 8e-4, 6e-4, 4e-4, 2e-4,
#         1e-4]
# #guesses = [0.0001]
# guesses = []
# for i in range(len(chis)):
#     for j in range(len(rs)):
#         guesses.append([chis[i], rs[j]])
# guesses = [[0.0001, 1.4e-6]]
print("total number of guesses: " + str(len(guesses)))

bounds = ([0, 1e-9], [0.01, 1e-4])#([0, 0], [np.inf, np.inf])

#print('init_chi\tinit_radius\tchi\t\tradius\t\tr_sq')

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

best_guess = guesses[0]
best_r_sq = -np.inf
best_results = best_guess

print('\n* indicates new best found')
print('init_chi\tinit_radius\tchi\t\tradius\t\tr_sq')

for init_guess in tqdm(guesses):
    # iterate over guesses
    model = working_model
    try:
        (popt, pcov) = curve_fit(working_model, time, conc, p0=init_guess, bounds=bounds)
    except ValueError:
        print("ValueError encountered at chi_init {chi:0.4f}, r_init {r:0.4f}".format(chi=init_guess[0], r=init_guess[1]))
        pass
    except RuntimeError:
        print("RuntimeError encountered at chi_init {chi:0.4f}, r_init {r:0.4f}".format(chi=init_guess[0], r=init_guess[1]))
        pass

    model_y = working_model(time, *popt)

    residuals = conc - model_y
    ss_res = np.sum(residuals**2) # sum of square residuals
    ss_total = np.sum((conc - np.mean(conc)) ** 2) # total sum of squares
    r_sq = 1 - ss_res / ss_total

    if r_sq > best_r_sq:
        best_r_sq = r_sq
        best_results = popt
        best_guess = init_guess
        print('*', end='')

    print('{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{r_sq:0.4f}'.format(
        chi_guess=init_guess[0], r_guess=init_guess[1], chi=popt[0],
        r=popt[1], r_sq=r_sq))

print("\nFINAL MODEL")
print("file: " + str(file))
print('init_chi\tinit_radius\tchi\t\tradius\t\tr_sq')
print('{chi_guess:0.4e}\t{r_guess:0.4e}\t{chi:0.4e}\t{r:0.4e}\t{r_sq:0.4f}'.format(
    chi_guess=best_guess[0], r_guess=best_guess[1], chi=best_results[0],
    r=best_results[1], r_sq=best_r_sq))

model_y = model(time, *best_results)

# plot:
fig = plt.figure()
plt.plot(time, conc, label='data')
plt.plot(time, model_y, ':', label='fit')
plt.xlabel('time (s)')
plt.ylabel('conc (mg/mL)')
plt.legend()
plt.tight_layout()
plt.show()
