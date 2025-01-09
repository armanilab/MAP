# calculates the statistics about the noise level for a given file
#
# Created: 2024.01.27
#          Lexie Scholtz
#
# command line usage:
#     $ python3 temporal_resolution.py <path> <files_names>
#
#
# Multiple file names may be given as long as they are at the same path.
# For example: $ python3 simple_plot.py ../test_data/ file1.txt file2.txt
#
# For multiple paths, use ./ as the <path> and include the full path name in
# each entry of <file_names>
# For example: $ python3 simple_plot.py ./ dir1/file1.txt dir2/file2.txt

import sys
import numpy as np
from matplotlib import pyplot as plt

# # check for correct number of arguments
# if len(sys.argv) < 3:
#     print("ERROR: Not enough arguments.")
#     print("Correct usage:")
#     print("$ python3 simple_plot.py <path> <file_names>")
#     sys.exit()
#
# # parse arguments
# path = sys.argv[1]
# file_list = sys.argv[2:] # get the file names as arguments

full_file = False
n_pts = 100
grey = '#a0a0a0'

path = "../../../../test_data/paper_data/rs-conc/rsi/"
file_list = ["rsi31", "rsi32", "rsi33", "rsi21", "rsi22", "rsi23",
    "rsi11", "rsi12", "rsi13", "rsi01", "rsi02", "rsi03"]

path = "../../../../test_data/paper_data/rs-conc/w/"
file_list = ["w31", "w32", "w33"]
full_file = True

def get_noise_level(lux, n_pts):
    lux_subset = lux[:n_pts]

    mean_lux = np.mean(lux_subset)
    std_dev_lux = np.std(lux_subset)

    return lux_subset, mean_lux, std_dev_lux

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

for file in file_list:
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    print("\nAnalyzing file: " + file_path)

    # get points from file
    data = np.genfromtxt(file_path)
    time = data[:, 0]
    lux = data[:, 1]

    outliers = []

    for li in range(len(lux)):
        l = lux[li]
        t = time[li]

    # pull first n_pts data points to establish the noise level
    if full_file:
        lux_subset, noise_mean, noise_std_dev = get_noise_level(lux, len(time))
        title_str = "Noise level: " + str(file) +"\nfor all " + str(len(time)) \
            + " datapoints (t = 0 to t = " + str(time[-1]) + ")"
    else:
        lux_subset, noise_mean, noise_std_dev = get_noise_level(lux, n_pts)
        title_str = "Noise level: " + str(file) +"\nfor first " + str(n_pts) \
            + " datapoints (t = 0 to t = " + str(time[n_pts-1]) + ")"

    mean_str = "Mean: {:.6f}".format(noise_mean)
    std_dev_str = "Std dev: {:.6f}".format(noise_std_dev)

    plt.hist(lux_subset, edgecolor="black", bins=25)

    # add lines for the mean, and std devs
    plt.axvline(noise_mean, color='k', label=mean_str)
    plt.axvline(noise_mean + noise_std_dev, color=grey, label=std_dev_str)
    plt.axvline(noise_mean - noise_std_dev, color=grey)
    plt.axvline(noise_mean - 2*noise_std_dev, color=grey)
    plt.axvline(noise_mean - 3*noise_std_dev, color=grey)
    plt.axvline(noise_mean + 2*noise_std_dev, color=grey)
    plt.axvline(noise_mean + 3*noise_std_dev, color=grey)

    plt.title(title_str)
    plt.xlabel("Lux")
    plt.ylabel("Frequency")
    #plt.ylim([0, 10])
    #plt.xlim([26800, 27200])
    plt.legend()
    plt.tight_layout()
    plt.show()
