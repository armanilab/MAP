# error propagation for calculating chi

# created 01.31.24
# Lexie Scholtz

import sys
from os import path
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
import pandas as pd
import math
from statistics import mean

file = '../../../../test_data/paper_data/rs-conc/mag_sus_analysis_v2.1-rev.xlsx'

df = pd.read_excel(file, sheet_name='error-prop', dtype='str')

a_big = -9.040790524802906
var_a_big = 7.12482737e-5


row = 0
# print(df.iloc[row])
for row in range(6):
    delta1 = float(df.iloc[row]['delta1'])
    var_delta1 = float(df.iloc[row]['var_delta1'])
    delta2 = float(df.iloc[row]['delta2'])
    var_delta2 = float(df.iloc[row]['var_delta2'])
    chi = float(df.iloc[row]['chi'])

    std_a_big = math.sqrt(var_a_big)
    std_delta1 = math.sqrt(var_delta1)
    std_delta2 = math.sqrt(var_delta2)

    frac_error = math.sqrt((2 * std_a_big / a_big)**2
        + (std_delta1 / delta1)**2
        + (std_delta2 / delta2)**2)

    max_error = 2* std_a_big / a_big + std_delta1/delta1 + std_delta2/delta2

    err_chi = chi * frac_error

    print("for " + df.iloc[row]['file'] + ":")
    print("fractional error is {:.6f}".format(frac_error))
    print("error of chi is {:.6f}".format(err_chi))
    print("relative to chi of {:.6f}".format(chi))
    print("standard form: {:.6f} ± {:.6f}".format(chi, err_chi))
    print("max error is {:.4E}".format(max_error))
