# test zero magnet case to see if we can fit radius better
#
# Lexie Scholtz
# created 2024.10.22
ver = 1.0   # version num.

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm
from lmfit import Model

# path = '../../../../test_data/paper_data/magob/'
# files = ['magob138.txt', 'magob139.txt', 'magob140.txt']
path = '../../../../test_data/paper_data/dyna-20241020/'
files = ['dbnm0001.txt', 'dbnm0002.txt', 'dbnm0003.txt']
colors = ['blue', 'red', 'green']
c0 = (0.125 *1e-6)/(1 * 1e-6) # convert to kg/m^3 (from mg/mL)

# physical parameters
v_sol = 1e-6 # mL
h_sol = 0.01 # m (10 mm)
v_window = 1e-7 # m^3
rho_p = 1400 #5200 # g/m^3
g = 9.8 # m/s^2
rho_s = 1000 # kg/m^3
eta = 8.9e-4

# print('pre-r variable: ' =  + str((c0 * v_sol * (rho_p - rho_s) * g) / (6 * np.pi * v_window * h_sol * eta * rho_p)))
k = 2 * (rho_p - rho_s) * g / (9 * v_window * eta)
d = (3 * c0 * v_sol) / (4 * np.pi * rho_p * h_sol) *0.1
print('k: ' + str(k))
print('d: ' + str(d))
print('d * k: ' + str(d * k))
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

def lin_f(t, r):
    #return (c0 * v_sol * (rho_p - rho_s) * g) / (6 * np.pi * v_window * h_sol * eta * (rho_p**3) * r) * t + c0
    return r * t + c0

def fit_file(file, color):
    print("fitting file: " + file)
    file_path = path + file

    data = np.genfromtxt(file_path)
    time = data[:, 0]
    lux = data[:, 1]

    conc = calibrate(lux, c0)
    plt.plot(time, conc, color=color, label=file)

    # fit file
    model = Model(lin_f)
    params = model.make_params(r=1e-6)
    result = model.fit(conc, params, t=time)
    print(result.fit_report())
    plt.plot(time, result.best_fit, '-', color=color)

for fi in range(len(files)):
    file = files[fi]
    color = colors[fi]
    fit_file(file, color)

plt.xlabel('time (s)')
plt.ylabel('concentration (kg/mL)')
plt.legend()
plt.tight_layout()
plt.show()
