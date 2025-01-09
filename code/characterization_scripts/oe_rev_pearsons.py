# pearson's correlation for MAP data in OE publication
# formatted for OE publication

# created 01.29.2024
# Lexie Scholtz

import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm
import seaborn as sns

# --- DATA ---
# VSM single value
vsm = [3.96e-4, 6.62e-6] # chi fit, error (1 std dev)

# concentration data
# [conc, trial1, trial2, trial3
conc_chi = [[0.5, 1.06e-3, 7.93e-4, 9.31e-4],
           [0.25, 7.8e-4, 5.41e-4, 5.66e-4],
           [0.125, 3.10e-4, 2.70e-4, 3.10e-4],
           [0.0625, 9.82e-4, 9.84e-4, 1.03e-3],
           [0.03125, 6.37e-4, 4.30e-4, 3.41e-4],
           [0.015625, 2.88e-4, 2.74e-4, 3.40e-4]]

# magnet data
# [surface field, trial1, trial2, trial3
mag_chi = [[3682, 1.06e-3, 7.93e-4, 9.31e-4], # 3/8"
           [2704, 1.20e-3, 1.06e-3, 1.06e-3], # 1/4"
           [2109, 9.67e-4, 9.34e-4, 1.32e-3]] # 3/16"

# --- ANALYSIS ---
# all concentrations
def analyze_all_conc():
    print("Analyzing all concentrations...")
    all_conc_list = []
    for c in conc_chi:
        for i in [1, 2, 3]:
            all_conc_list.append(c[i])
    print("list of chi values: " + str(all_conc_list))

    # reformat VSM to match
    vsm_list = []
    for i in range(len(all_conc_list)):
        vsm_list.append(vsm[0])
    print("list of vsm values: " + str(vsm_list))

    print("lists are equal: " + str(len(all_conc_list) == len(vsm_list)))

    r, p = pearsonr(all_conc_list, vsm_list)
    print("Pearson's r: " + str(r))
    print("p-value: " + str(p))

def linear_regression():
    print("Analyzing all concentrations...")
    all_conc_list = []
    all_chi_list = []
    for c in conc_chi:
        for i in [1, 2, 3]:
            all_conc_list.append(c[0])
            all_chi_list.append(c[i])

    print("pairs:")
    for i in range(len(all_chi_list)):
        print("(" + str(all_conc_list[i]) + ", " + str(all_chi_list[i])+ ")")

    x = np.array(all_conc_list).reshape((-1, 1))
    y = np.array(all_chi_list)
    # carry out linear regression
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)

    print("Linear regression model: ")
    print("intercept: " + str(model.intercept_))
    print("slope: " + str(model.coef_))
    print("r^2: " + str(r_sq))

# analyze_all_conc()
#linear_regression()

def correlate_matrix(chi_data, round_digit, title_str, axis_str):
    label_strs = []
    for row in chi_data:
        label_strs.append(str(round(row[0], round_digit)))
    print(label_strs)
    n = len(label_strs)

    corr_matrix = np.zeros((n, n))
    corr_p_matrix = np.zeros((n, n))
    for i in range(n):
        data_row1 = chi_data[i][1:]
        for j in range(n):
            data_row2 = chi_data[j][1:]
            r, p = pearsonr(data_row1, data_row2)
            corr_matrix[i, j] = r
            corr_p_matrix[i, j] = p

            print("r = {:.3f}".format(r) + " for " + label_strs[i] + " and " + label_strs[j])

    print(corr_matrix)
    # make heatmap
    plt.figure(figsize=(12, 8))

    fs = 30 # font-size
    ticks_fs = 24
    pfont = 'Avenir'
    lfont = fm.FontProperties(family='Avenir', size=24)

    ax = sns.heatmap(corr_matrix, annot=True, annot_kws = {'size':ticks_fs, 'fontname':pfont}, cmap='coolwarm', vmin=-1, vmax=1)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=ticks_fs, pad=10)
    # ax.set_xticks(np.arange(n))
    x_locs, _ = plt.xticks()
    plt.xticks(ticks=x_locs, labels=label_strs[::-1], fontname=pfont, fontsize=ticks_fs)
    # ax.set_yticks(np.arange(n))
    y_locs, _ = plt.yticks()
    plt.yticks(ticks=y_locs, labels=label_strs, rotation=0, fontname=pfont, fontsize=ticks_fs)

    plt.xlabel(axis_str, fontname=pfont, fontsize=fs)
    plt.ylabel(axis_str, fontname=pfont, fontsize=fs)
    #
    # plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    #
    # # add annotations
    # for i in range(n):
    #     for j in range(n):
    #         text = ax.text(j, i, corr_matrix[i, j], ha="center", va="center", color="w")

    plt.title(title_str, fontname=pfont, fontsize=fs+8)
    plt.tight_layout()
    plt.show()


correlate_matrix(conc_chi, 3, title_str="Correlations between Varying Concentrations",
   axis_str="Concentration (mg/mL)")
# correlate_matrix(mag_chi, 0,
#     title_str="Correlations between Varying Magnetic Fields",
#     axis_str="Magnetic Field (G)")
