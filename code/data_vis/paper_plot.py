# Plots data with formatting for the paper/conference
# Lexie Scholtz
# Created: 2023.08.28

# Usage:
# $ python3 paper_plot.py <path> <files_names>
#
# Multiple file names may be given as long as they are at the same path.
# For example: $ python3 paper_plot.py ../test_data/ file1.txt file2.txt
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
    print("$ python3 paper_plot.py <path> <file_names>")
    sys.exit()

# parse arguments
path = sys.argv[1]
file_list = sys.argv[2:] # get the file names as arguments

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

# size figure properly
plt.figure(figsize=(3.4, 3.4))

markers = [('+', 'b'), ('x', 'r'), ('D', 'k')]

file_num = 0
for file in file_list:
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    # get points from file
    data = np.genfromtxt(file_path)
    raw_time = data[:, 0]
    raw_lux = data[:, 1]

    # find the index of the first time point > 15 sec
    i = 0
    while True:
        if raw_time[i] >= 15:
            break
        i += 1

    # shift data so that zero point is t = 15
    shift_time = raw_time[i]
    time = raw_time[i:] - shift_time

    # baseline correct the lux data
    shift_lux = min(raw_lux[:i])
    lux = raw_lux[i:] - shift_lux

    # plot data
    m = markers[file_num]
    plt.plot(time, lux, linewidth=2, #label='Run #' + str(file_num + 1),
        linestyle='None', markersize=2, marker=m[0], markeredgecolor=m[1],
        markerfacecolor='None')
    ax = plt.subplot(111)
    #ax.legend(loc='center left')
    file_num += 1

# populate legend
for mi in range(len(markers)):
    plt.plot([], [], color=markers[mi][1], marker=markers[mi][0],
        linestyle='None', label="Run #" + str(mi + 1))

fs = 16 # font-size
#pfont = {'fontname': 'Arial'}
pfont = 'Arial'
plt.title("Sample Iron Oxide NP", fontsize=fs, fontname=pfont)
#plt.text(1025, 5700, 'Chi = 2.05e-4', fontsize=fs-6)
plt.xlabel("Time (min)", fontsize=fs, fontname=pfont)
plt.ylabel("Lux", fontsize=fs, fontname=pfont)
plt.xticks([0, 600, 1200, 1800], [0, 10, 20, 30], fontsize=fs, fontname=pfont)
plt.yticks([0, 10000, 20000, 30000, 40000, 50000],
    ['0', '10k', '20k', '30k', '40k', '50k'], fontsize=fs, fontname=pfont)
plt.xlim([0, 1200])
plt.ylim([0, 50000])
plt.legend(loc='lower right', fontsize=fs-4)
plt.tight_layout()
plt.show()
