# Makes a simple plot of the data
# Lexie Scholtz
# Created: 2022.11.02

# Usage:
# $ python3 simple_plot.py <path> <files_names>
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
    print("$ python3 normalized_plot.py <path> <file_names>")
    sys.exit()

# parse arguments
path = sys.argv[1]
file_list = sys.argv[2:] # get the file names as arguments

write_to_file = False
user_in = input("Write to file? [y/n]: ")
if 'y' in user_in:
    write_to_file = True


# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

for file in file_list:
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    # get points from file
    data = np.genfromtxt(file_path)

    # take baseline data from seconds 5-10
    total_l = 0
    total_pts = 0
    for i in range(len(data[:, 0])):
        t = data[i, 0]
        if t >= 0 and t <= 15:
            total_l += data[i, 1]
            total_pts += 1
    baseline = total_l / total_pts

    if write_to_file:
        new_file_name = file[:-4] + "_baseline_corrected.txt"

        with open(path + new_file_name, "w") as new_file:
            new_file.write("# Original file: " + file + "\n")
            new_file.write("# Baseline corrected by average value over first 15 seconds\n")
            for i in range(len(data[:, 0])):
                new_file.write(str(data[i, 0]) + "\t" + str(data[i, 1] - baseline) + "\n")
            print("Baseline corrected data successfully written to " + path + new_file_name)

    # plot data
    plt.plot(data[:, 0], data[:, 1] - baseline, label=file) #linestyle='None', marker = '+', markersize=0.25)

plt.title("QDM Data")
plt.xlabel("Time (s)")
plt.ylabel("Lux")
plt.legend(loc='lower right')
plt.show()
