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

for file in file_list:
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    # get points from file
    data = np.genfromtxt(file_path)

    # plot data
    #plt.plot(data[:, 0], data[:, 1], label=file[-12:], marker='.', markersize=2, linestyle='None', alpha=0.75)
    plt.plot(data[:, 0], data[:, 1]-min(data[:, 1]), marker='.', markersize=2, linestyle='None', label=file.split('/')[-1])
    print(file.split('/')[-1])
    print(min(data[:, 1]))
    print(data[-101:-1, 1].mean())
    #plt.plot(data[:, 0], data[:, 1]-data[0, 1], label=file[-10:]) #linestyle='None', marker = '+', markersize=0.25)
    ax = plt.subplot(111)
    #ax.legend(loc='center left')

plt.title("MAP Light curve")
plt.xlabel("Time (s)")
plt.ylabel("Lux")


plt.legend()
plt.show()
