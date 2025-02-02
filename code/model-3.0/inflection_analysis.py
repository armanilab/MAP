# inflection analysis

import numpy as np
import matplotlib.pyplot as plt
import single_magnetic_analysis as ma
from mpl_toolkits.mplot3d import Axes3D
import sys
from tqdm import tqdm
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter

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


# smooth data using the Savitzky-Golay filter
window_size = 21
poly_order = 7 # polynomial order

# compute first derivative of data
conc_smoothed = savgol_filter(conc, window_size, poly_order)
conc_prime = savgol_filter(conc, window_size, poly_order, deriv=1,
    delta=time[1]-time[0])
conc_dbl_prime = savgol_filter(conc, window_size, poly_order, deriv=2,
    delta=time[1]-time[0])
min_n = 30 # skip first 2 seconds
global_min_index = np.argmin(conc_prime[min_n:])+min_n
print('global min timepoint: ' + str(time[global_min_index]))

# plot data
f, (ax1, ax2) = plt.subplots(2, 1)
f.suptitle(file)
ax1.plot(time, conc)
ax1.plot(time, conc_smoothed, ":")
ax1.set_ylabel('conc (mg/mL)')
ax1.axvline(time[global_min_index], linestyle=':', color='r')
ax2.plot(time, conc_prime)
ax2.plot(time[global_min_index], conc_prime[global_min_index], 'o', color='r')
ax2.set_ylabel('change in conc (mg/mL per s)')
plt.tight_layout()
plt.show()
