# plot files
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
from qc_formats import *
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


path = '../../../../test_data/paper_data/2025.09/'
file1_name = '2025.09/912_01.txt'
files = {
    1: dict(file_name='912_01.txt', r=3.7091e-07, chi=1.0412e+01, infl_pt=59.152, a=-2.05242069),
    2: dict(file_name='912_06.txt', chi=2.1446e+01, r=3.1924e-07, infl_pt=5.392, a=-14.04851482),
}

eta = 8.9e-4
rho_p = 5170
chi_s = -9.04e-6
mu0 = 4 * np.pi * 10**-7
c0 = 100

def working_model(t, chi_p, r):
    alpha = (9 * eta) / (2 * rho_p * r**2)
    beta = (2 * a**2 * chi_p) / (rho_p * mu0 * (1 + chi_s))
    delta1 = 0.5 * (-alpha + np.sqrt(alpha**2 - 4 * beta))
    delta2 = 0.5 * (-alpha - np.sqrt(alpha**2 - 4 * beta))
    k = delta2 * c0 / (delta2 - delta1)
    return k * np.exp(delta1 * t) + (c0 - k) * np.exp(delta2 * t)

for fkey in files:
    fig, axes = plt.subplots(1, 2, figsize=(6, 4))
    dfile = files[fkey]
    data = np.genfromtxt(path + dfile['file_name'])

    time = data[:, 0]
    lux = data[:, 1]
    conc = calibrate(lux, c0)
    for ax in axes:
        ax.plot(time, conc, color=green, label='Data')
    shifted_conc = conc[time >= dfile['infl_pt']]
    shifted_time = time[time >= dfile['infl_pt']]

    a = dfile['a']
    fit_y = working_model(shifted_time, dfile['chi'], dfile['r'])
    for ax in axes:
        ax.plot(shifted_time + dfile['infl_pt'], fit_y, linestyle=':',
            color=dark_blue, label='Best MSE Fit')

    fig.suptitle(dfile['file_name'])
    for ax in axes:
        ax.set_xlabel('Time (s)')
        ax.legend(loc='upper right')
    axes[0].set_ylabel('Concentration)')
    axes[1].set_ylabel('log(concentration)')
    axes[1].set_yscale('log')

    plt.tight_layout()
    plt.show()
