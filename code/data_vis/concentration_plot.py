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
    print("$ python3 simple_plot.py <path> <file_names>")
    sys.exit()

# parse arguments
path = sys.argv[1]
file_list = sys.argv[2:] # get the file names as arguments

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

for f in file_list:
     # shortcut stuff, remove later and change f to file
    for i in range(30):
        file = f
        if i < 9:
            file += str(0) + str(i + 1)
        else:
            file += str(i + 1)
        # error checking - make sure it is a .txt file
        if file[-4:] != ".txt":
            file += ".txt"

        file_path = path + file

        data = np.genfromtxt(file_path)

        # take baseline data from seconds 5-10
        total_l = 0
        total_pts = 0
        final_l = 0
        final_pts = 0
        for i in range(len(data[:, 0])):
            t = data[i, 0]
            if t >= 5 and t <= 10:
                total_l += data[i, 1]
                total_pts += 1
            if t >= 590 and t <= 600:
                final_l += data[i, 1]
                final_pts += 1
        baseline = total_l / total_pts
        final = final_l / final_pts

        print(file + ", " + str(baseline) + ", " + str(final))
        # plot data
        plt.plot(data[:, 0], data[:, 1]) #linestyle='None', marker = '+', markersize=0.25)


plt.title("QDM Data")
plt.xlabel("Time (s)")
plt.ylabel("Lux")
plt.legend(loc='lower right')
plt.show()
