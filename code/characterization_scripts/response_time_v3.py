# calculates the statistics about the noise level for a given file
#
# Created: 2024.12.23
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

    # print("\nAnalyzing file: " + file_path)

    # get points from file
    data = np.genfromtxt(file_path)
    times = data[:, 0]
    lux = data[:, 1]

    lux = lux - np.min(lux)

    end_lux_subset = lux[-n_pts:]
    end_mean = np.mean(end_lux_subset)
    end_std_dev = np.std(end_lux_subset)

    ninety_threshold = end_mean * 0.9

    plt.plot(times, lux, linewidth=3, color="#95211b")
    plt.axhline(ninety_threshold, linestyle='--', linewidth = 2, color=grey,
        label="90% Threshold")

    ninety = -1

    for i in range(len(times)):
        t = times[i]
        l = lux[i]
        if l >= ninety_threshold and ninety < 0:
            ninety = t
            break

    # print("Steady state: {:.3f} lux".format(end_mean))
    # print("T90 (90% of final value): {:.3f} s".format(ninety))
    # print("T90 threshold: {:.3f} lux".format(ninety_threshold))
    # print("copy str:")
    print(file + ",{:.3f},{:.3f},{:.3f}".format(end_mean,
        ninety, ninety_threshold))

    title_str = "Response time: " + str(file)

    ninety_str = "T90: {:.3f} s".format(ninety)

    # # add lines for the mean, and std devs
    #
    # plt.axvline(ninety, linestyle='--', linewidth=2, color='black', label=ninety_str)
    #
    # fs = 30 # font-size
    # ticks_fs = 24
    # pfont = 'Avenir'
    # lfont = fm.FontProperties(family='Avenir', size=24)
    #
    # plt.title(title_str, fontname=pfont, fontsize=36)
    # plt.xlabel("Time (min)", fontname=pfont, fontsize=fs)
    # plt.ylabel("Change in Transmission (klx)", fontname=pfont, fontsize=fs)
    # plt.xticks([0, 300, 600, 900, 1200, 1500], [0, 5, 10, 15, 20, 25],
    #    fontname=pfont, fontsize=ticks_fs)
    # plt.yticks([0, 5000, 10000, 15000, 20000, 25000, 30000],
    #     [0, 5, 10, 15, 20, 25, 30], fontname=pfont, fontsize=ticks_fs)
    # plt.ylim([0, 25000])
    # #plt.ylim([0, np.ceil(np.max(lux) / 5000) * 5000])
    # plt.xlim([0, 1500])
    # #plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    # plt.legend(prop=lfont)
    # plt.tight_layout()
    # plt.show()
