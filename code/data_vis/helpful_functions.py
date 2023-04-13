# additional functions that may be useful
import numpy as np
from matplotlib import pyplot as plt

def find_stats(file):
    data = np.genfromtxt(file)
    avg = np.mean(data[:, 1])
    stddev = np.std(data[:, 1])

    print(file + " stats:")
    print("average: " + str(avg))
    print("std dev: " + str(stddev))
