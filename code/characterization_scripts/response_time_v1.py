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

n_pts = 100
grey = '#777777'
# grey = '#a0a0a0'

path = "../../../../test_data/paper_data/rs-conc/rsi/"
file_list = ["rsi31", "rsi32", "rsi33", "rsi21", "rsi22", "rsi23",
    "rsi11", "rsi12", "rsi13", "rsi01", "rsi02", "rsi03"]
file_list = ["rsi31"]

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

print("--- RESPONSE TIME ANALYSIS ---")

for file in file_list:
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    print("\nAnalyzing file: " + file_path)

    # get points from file
    data = np.genfromtxt(file_path)
    times = data[:, 0]
    lux = data[:, 1]

    # establish initial noise level (specifically std dev)
    noise_lux_subset = lux[:n_pts]
    noise_mean = np.mean(noise_lux_subset)
    noise_std_dev = np.std(noise_lux_subset)

    print("Noise std dev: " + str(noise_std_dev) + " lux")

    end_lux_subset = lux[-n_pts:]
    end_mean = np.mean(end_lux_subset)
    end_std_dev = np.std(end_lux_subset)

    print("Steady state mean: " + str(end_mean) + " lux")

    # define "steady state" as first point within 3 std dev of the steady state
    # final value
    # TODO: first point or like x number of consecutive points?
    steady_state_min = end_mean - 3 * noise_std_dev
    threshold_str = "within 3 std dev of steady state"
    print("Setting threshold to be " + threshold_str + ": " \
        + str(steady_state_min) + " lux.")

    plt.plot(times, lux)
    plt.axhline(steady_state_min, linestyle='--', color='orange',
        label="Steady State Threshold")
    plt.axvspan(-2, -1, alpha=0.75, color='orange', label='Data within threshold')

    first_steady_state = -1
    n_consec = 10
    consec_steady_state = -1

    span_tmin = -1
    span_tmax = -1

    n_above_min = 0
    for i in range(len(times)):
        t = times[i]
        l = lux[i]
        if l >= steady_state_min:
            if first_steady_state < 0:
                first_steady_state = t
            n_above_min += 1
            if span_tmin < 0:
                span_tmin = t
            span_tmax = t
        if l < steady_state_min:
            n_above_min = 0
            # plot previous span
            plt.axvspan(span_tmin, span_tmax, alpha=0.25, color='orange')
            span_tmin = -1
            span_tmax = -1
        if n_above_min >= n_consec and consec_steady_state < 0:
            consec_steady_state = t
            #break


    print("Timepoint until first point is " + threshold_str + ": " \
        + str(first_steady_state) + " s.")
    print("Timepoint until " + str(n_consec) + " consecutive points are " \
        + threshold_str + ": " + str(consec_steady_state) + " s.")

    title_str = "Response time: " + str(file) \
        + "\nSteady State Threshold : " + str(steady_state_min) \
        + "\n" + threshold_str

    first_str = "First: {:.3f} s".format(first_steady_state)
    consec_str = str(n_consec) + " consecutive: {:.3f} s".format(consec_steady_state)

    # add lines for the mean, and std devs

    plt.axvline(first_steady_state, color='k', label=first_str)
    plt.axvline(consec_steady_state, color=grey, label=consec_str)

    plt.title(title_str)
    plt.xlabel("Time (s)")
    plt.ylabel("Lux")
    plt.ylim([0, 30000])
    plt.xlim([0, 1500])
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    plt.tight_layout()
    plt.show()
