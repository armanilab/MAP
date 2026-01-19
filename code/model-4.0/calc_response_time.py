import sys
import numpy as np

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

def plot_data(time, lux, conc, label):
    lux_ax.plot(time, lux, label=label)
    conc_ax.plot(time, conc, label=label)

def calculate_resp_time(file_path):
    data = np.genfromtxt(file_path)
    time = data[:, 0]
    lux = data[:, 1]

    rel_lux = lux - np.min(lux)
    end_mean = np.mean(rel_lux[-20:])
    #end_std_dev = np.std(re_lux[-20:])
    ninety_threshold = end_mean * 0.9
    above_times = time[rel_lux >= ninety_threshold]

    return above_times[0] # return first time above threshold

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

for file in file_list:
    if file[-4:] != '.txt':
        file += '.txt'

    file_path = path + file

    print('{f}\t{resp_time:0.3f}'.format(f=file[:-4], resp_time=calculate_resp_time(file_path)))
