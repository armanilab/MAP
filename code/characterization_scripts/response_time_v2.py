# calculates the statistics about the noise level for a given file
#
# Created: 2024.01.28
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

# Calculates response time based on tau and 5*tau

import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm

# # check for correct number of arguments
# if len(sys.argv) < 3:
#     print("ERROR: Not enough arguments.")
#     print("Correct usage:")
#     print("$ python3 simple_plot.py <path> <file_names>")
#     sys.exit()
#
# parse arguments
path = sys.argv[1]
file_list = sys.argv[2:] # get the file names as arguments

n_pts = 100
dark_grey = '#555555'
light_grey = '#c0c0c0'
grey = '#777777'

# path = "../../../../test_data/paper_data/rs-conc/rsi/"
# file_list = ["rsi31", "rsi32", "rsi33", "rsi21", "rsi22", "rsi23",
#     "rsi11", "rsi12", "rsi13"]
# file_list = ["rsi31"]
# path = "../../../../test_data/paper_data/rs-conc/rsj/"
# file_list = ["rsj31", "rsj32", "rsj33"]

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

print("--- RESPONSE TIME ANALYSIS ---")


for file in file_list:
    plt.figure(figsize=(12, 8))

    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    print("\nAnalyzing file: " + file_path)

    # get points from file
    data = np.genfromtxt(file_path)
    times = data[:, 0]
    lux = data[:, 1]

    lux = lux - np.min(lux)

    end_lux_subset = lux[-n_pts:]
    end_mean = np.mean(end_lux_subset)
    end_std_dev = np.std(end_lux_subset)

    # define "steady state" as first point within 3 std dev of the steady state
    # final value
    # TODO: first point or like x number of consecutive points?
    tau_threshold = end_mean * 0.632 # value for tau
    five_tau_threshold = end_mean * 0.993
    ninety_threshold = end_mean * 0.9

    plt.plot(times, lux, linewidth=3, color="#95211b")
    # plt.axhline(tau_threshold, linestyle='--', color='red',
    #     label="Tau Threshold")
    plt.axhline(ninety_threshold, linestyle='--', linewidth = 2, color=grey,
        label="90% Threshold")
    # plt.axhline(five_tau_threshold, linestyle='--', color='orange',
    #     label="5 Tau Threshold")

    tau = -1
    five_tau = -1
    ninety = -1

    for i in range(len(times)):
        t = times[i]
        l = lux[i]
        if l >= tau_threshold and tau < 0:
            tau = t
        if l >= ninety_threshold and ninety < 0:
            ninety = t
        if l >= five_tau_threshold and five_tau < 0:
            five_tau = t
            break

    # account for first 15 seconds before magnet is applied
    tau_adj = tau - 15
    ninety_adj = ninety - 15
    five_tau_adj = five_tau - 15

    print("Steady state: {:.3f} lux".format(end_mean))
    print("Tau (63.2% of final value): {:.3f} s".format(tau_adj))
    print("Tau threshold: {:.3f} lux".format(tau_threshold))
    print("T90 (90% of final value): {:.3f} s".format(ninety_adj))
    print("T90 threshold: {:.3f} lux".format(ninety_threshold))
    print("Five tau (99.3% of final value): {:.3f} s".format(five_tau_adj))
    print("Five Tau threshold: {:.3f} lux".format(five_tau_threshold))
    print("copy str:")
    print("{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f},{:.3f}".format(end_mean,
        tau_adj, tau_threshold, ninety_adj, ninety_threshold, five_tau_adj,
        five_tau_threshold))

    title_str = "Response time: " + str(file)

    tau_str = "Tau: {:.3f} s".format(tau_adj)
    ninety_str = "T90: {:.3f} s".format(ninety_adj)
    five_tau_str = "Five tau: {:.3f} s".format(five_tau_adj)

    # add lines for the mean, and std devs

    # plt.axvline(tau, color='k', label=tau_str)
    plt.axvline(ninety, linestyle='--', linewidth=2, color='black', label=ninety_str)
    # plt.axvline(five_tau, color=light_grey, label=five_tau_str)

    fs = 30 # font-size
    ticks_fs = 24
    pfont = 'Avenir'
    lfont = fm.FontProperties(family='Avenir', size=24)

    plt.title(title_str, fontname=pfont, fontsize=36)
    plt.xlabel("Time (min)", fontname=pfont, fontsize=fs)
    plt.ylabel("Change in Transmission (klx)", fontname=pfont, fontsize=fs)
    plt.xticks([0, 300, 600, 900, 1200, 1500], [0, 5, 10, 15, 20, 25],
       fontname=pfont, fontsize=ticks_fs)
    plt.yticks([0, 5000, 10000, 15000, 20000, 25000, 30000],
        [0, 5, 10, 15, 20, 25, 30], fontname=pfont, fontsize=ticks_fs)
    plt.ylim([0, 25000])
    #plt.ylim([0, np.ceil(np.max(lux) / 5000) * 5000])
    plt.xlim([0, 1500])
    #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    plt.legend(prop=lfont)
    plt.tight_layout()
    plt.show()
