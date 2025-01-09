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
from scipy import stats

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

start_time = 30

# path = "../../../../test_data/paper_data/sys-cal/"
# file_list = ["m_nocuv1", "m_nocuv2", "m_nocuv3"]


def get_noise_level(lux, n_pts):
    lux_subset = lux[:n_pts]

    mean_lux = np.mean(lux_subset)
    std_dev_lux = np.std(lux_subset)

    return lux_subset, mean_lux, std_dev_lux

def plot_lux_hist(lux, ax, title_append=""):

    # use all datapoints in this given file
    lux_subset, noise_mean, noise_std_dev = get_noise_level(lux, len(time))
    title_str = "Noise level: " + str(file)

    mean_str = "Mean: {:.6f}".format(noise_mean)
    std_dev_str = "Std dev: {:.6f}".format(noise_std_dev)

    kde = stats.gaussian_kde(lux)

    ax.hist(lux_subset, edgecolor="black", bins=25, density=True)
    ticks = ax.get_xticks()
    min_tick = float(ticks[0])
    max_tick = float(ticks[-1])
    print("x: " + str(min_tick) + " to " + str(max_tick))
    kde_x = np.linspace(min_tick, max_tick, 1000)
    ax.plot(kde_x, kde(kde_x), color='red')

    # add lines for the mean, and std devs
    ax.axvline(noise_mean, color='k', label=mean_str)
    ax.axvline(noise_mean + noise_std_dev, color=grey, label=std_dev_str)
    ax.axvline(noise_mean - noise_std_dev, color=grey)
    ax.axvline(noise_mean - 2*noise_std_dev, color=grey)
    ax.axvline(noise_mean - 3*noise_std_dev, color=grey)
    ax.axvline(noise_mean + 2*noise_std_dev, color=grey)
    ax.axvline(noise_mean + 3*noise_std_dev, color=grey)

    ax.set_title(title_str + title_append)
    ax.set_xlabel("Lux")
    ax.set_ylabel("Frequency")
    #plt.ylim([0, 10])
    #plt.xlim([26800, 27200])
    ax.legend()


    return noise_mean, noise_std_dev

all_lux = None
mean_adj_lux = []

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

    ti = -1
    for i in range(len(time)):
        if time[i] >= start_time:
            ti = i
            break

    lux = lux[ti:]

    mean_lux = np.mean(lux)
    print("mean for " + file + ": " + "{:.3f}".format(mean_lux))
    lux = lux - mean_lux
    mean_adj_lux.append([time[ti:], lux])

    if all_lux is None:
        all_lux = lux
    else:
        all_lux = np.concatenate((all_lux, lux), axis=None)


fig, axes = plt.subplots(1, 2, figsize=(24, 6))

ax2 = axes[0]
for i in range(len(mean_adj_lux)):
    t = mean_adj_lux[i][0]
    l = mean_adj_lux[i][1]
    ax2.plot(t, l, label=file_list[i])
    ax2.legend(loc='upper right')
    ax2.set_xlabel('Time after 30 sec mark (s)')
    ax2.set_ylabel('Lux relative to mean lux')
    ax2.set_title('adjusted data')

noise_mean, noise_std_dev = plot_lux_hist(all_lux, ax=axes[1])
axes[1].set_title('noise distribution')



plt.tight_layout()
plt.show()
