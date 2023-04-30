import sys
import os
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
print("path given: " + path)
file_list = sys.argv[2:] # get the file names as arguments
print("file list: ")
for l in file_list:
    print(l)

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

if '-all' in file_list:
    print("found all")
    file_list = []
    for f in os.listdir(path):
        if '.txt' in f:
            file_list.append(f)
    print(file_list)


def plot_light_curve(file_list, baseline_correction=False, no_legend=False):
    # make plot fig
    fig, ax = plt.subplots()

    title_str = "Light curves\n"

    # TODO: add code to determine which variable to use as a label (the one that changes)
    # ignore the category that stays the same.
    # these could be: MNP, solvent, concentration, magnet
    # always include trial number
    for file in file_list:
        if file[-4:] != ".txt":
            file += ".txt"
        row_label = file[:-4]

        file_path = path + file
        print("plotting " + file_path)

        data = np.genfromtxt(file_path)

        x = data[:, 0]
        y = data[:, 1]

        if baseline_correction:
            total_l = 0
            total_pts = 0
            for i in range(len(data[:, 0])):
                t = data[i, 0]
                if t >= 0 and t <= 1:
                    if np.isnan(data[i, 1]):
                        total_l += 0
                    else:
                        total_l += data[i, 1]
                    total_pts += 1
            baseline = total_l / total_pts
            y = y - baseline
            # add label to title

        if extra_big:
            plt.plot(x, y, label=row_label, linewidth=5)
        else:
            plt.plot(x, y, label=row_label)

    if baseline_correction:
        title_str += "baseline corrected"

    ax.set_title(title_str)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Lux")

    if not no_legend:
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
        #ax.legend(ncol = 2, bbox_to_anchor=(0.5, -0.5), loc="upper center")
    plt.tight_layout()
    plt.show()


plot_light_curve(file_list, baseline_correction=True)
