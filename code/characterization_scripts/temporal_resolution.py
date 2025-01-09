# calculates the statistics about the temporal resolution for a given file
#
# Created: 2024.01.26
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

# check for correct number of arguments
if len(sys.argv) < 3:
    print("ERROR: Not enough arguments.")
    print("Correct usage:")
    print("$ python3 simple_plot.py <path> <file_names>")
    sys.exit()

# parse arguments
path = sys.argv[1]
file_list = sys.argv[2:] # get the file names as arguments

# file_list = ["rsi31", "rsi32", "rsi33", "rsi21", "rsi22", "rsi23",
#     "rsi11", "rsi12", "rsi13", "rsi01", "rsi02", "rsi03"]

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

for file in file_list:
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    print("Analyzing file: " + file_path)

    # get points from file
    data = np.genfromtxt(file_path)

    # analyze data
    times = data[:, 0]
    delta_times = []
    t_init = times[0]
    for ti in range(1, len(times)):
        delta_times.append(times[ti] - t_init)
        t_init = times[ti]

    mean_delta = np.mean(delta_times)
    median_delta = np.median(delta_times)
    std_dev_delta = np.std(delta_times)
    max_delta = np.max(delta_times)
    min_delta = np.min(delta_times)
    median_count = np.count_nonzero(delta_times == median_delta)

    mean_str = "Mean: {:.6f} s".format(mean_delta)
    median_str = "Median: {:.6f} s".format(median_delta)
    std_dev_str = "Std Dev: {:.6f} s".format(std_dev_delta)
    min_str = "Min: {:.3f} s".format(min_delta)
    max_str = "Max: {:.3f} s".format(max_delta)
    median_count_str = "Median counts: n = {:d}".format(median_count)
    total_count_str = "Total counts: n = {:d}".format(len(delta_times))

    print("Time between measurements")
    print(file + ": ")
    print(mean_str)
    print(median_str)
    print(std_dev_str)
    print(min_str)
    print(max_str)
    print(median_count_str)
    print(total_count_str)

    plt.plot(0.15, 0.15, linestyle='None', label=mean_str)
    plt.plot(0.15, 0.15, linestyle='None', label=median_str)
    plt.plot(0.15, 0.15, linestyle='None', label=std_dev_str)

    plt.hist(delta_times, color='orange')
    plt.title("Temporal Resolution: " + str(file))
    plt.xlabel("Delta time [s]")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    #plt.show()
