import numpy as np

import sys
import numpy as np
from matplotlib import pyplot as plt

# parse arguments
path = input("Enter path of file(s): ")
files = input("Enter file names separated by spaces: ")
file_list = files.split()
#TODO: eventually change this to target lux value
scale_factor = input("Enter scale factor: ")

# make sure path is formatted properly
if path[-1] != '/':
    path += '/'

for file in file_list:
    file_name = file
    # error checking - make sure it is a .txt file
    if file[-4:] != ".txt":
        file += ".txt"

    file_path = path + file

    # get points from file
    data = np.genfromtxt(file_path)
    scaled_data = data[:, 1] * float(scale_factor)

    new_file_name = file_name + "_scaled_" + scale_factor + ".txt"
    with open(path + new_file_name, 'w') as f:
        f.write("# " + new_file_name + "\n")
        f.write("# Original file: " + file_name + "\n")
        f.write("# Scale Factor: " + scale_factor + "\n")
        for i in range(len(scaled_data)):
            f.write(str(data[i, 0]) + "\t" + str(scaled_data[i]) + "\n")

    plt.plot(data[:, 0], data[:, 1], label="original " + file_name)
    plt.plot(data[:, 0], scaled_data, label="scaled " + new_file_name)

plt.xlabel("Time (s)")
plt.ylabel("Lux")
plt.show()
