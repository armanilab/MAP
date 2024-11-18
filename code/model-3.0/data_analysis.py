import numpy as np
import matplotlib.pyplot as plt
import magnetic_analysis as ma
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import display, Math
import sys

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def display_chi_p_values(X_p_values, uncertainties):
    result = "\n".join([f"X_p = {X:.4f}, Uncertainty = {u:.4f}" for X, u in zip(X_p_values, uncertainties)])
    return result

def main_flip():
    # Parameters
    # L = 0.0254
    # W = 0.0254
    # T = 0.009525
    # sensor_pos = 0.0447
    # sensor_w = 0.001
    #
    # B_r = 1.32
    eta = 8.9e-4
    rho = 5170
    mu0 = 4 * np.pi * (10**-7)
    Xs = -9.04e-6
    C0 =  1.0 #* (0.001 * 0.001 * 0.01) / (3.84e-22)#0.1 * (3 * 0.001 * 0.001 * 0.01) / (4e6 * np.pi * ((0.5e-6)**3) *rho)
    initial_guess = [0.001, 0.5e-6]
    bounds = ([0, 0], [0.1, 0.1])#([0, 0], [np.inf, np.inf])
    #a3 = -10.545907 #3/8", mag ob, N42
    #a3 = -8.208740 # 1/4" mag ob, N42
    a3 = -13.655887 # 1/2", N52
    #a3 = -11.824199 # 3/8", N52, mag ob
    #a3 = -6.677333 # 3/16", N42, mag ob
    # Instantiate classes
    # mag_field_model = ma.MagneticFieldModel(B_r, L, W, T)
    # a, b = mag_field_model.a_b_field_calc(sensor_pos, sensor_w)
    # print(a, b)

    # Process data and fit model
    #file_paths = ['data/mjack005.txt', 'data/mjack006.txt', 'data/mjack007.txt', 'data/mjack008.txt', 'data/mjack009.txt']
    path = '../../../../test_data/paper_data/magob/'
    #files = ['dyna0001.txt', 'dyna0002.txt', 'dyna0003.txt']
    # files = ['94_b1.txt', '94_b2.txt', '94_b3.txt', '94_si1.txt', '94_si2.txt', '94_si3.txt']
    files = ['magob147.txt', 'magob148.txt', 'magob149.txt', 'magob162.txt', 'magob163.txt', 'magob164.txt']
    file_paths = [path + f for f in files]
    fitted_params = []

    save_path = '../../../../validation_data/model-3.0_results/'

    r_planeRange = np.linspace(1e-7, 1e-4, 50)
    X_p_planeRange = np.linspace(0.0001, 0.004, 50)

    print('file\tchi\tradius\tr^2\tadj-r^2\tMSE\tRMSE\tMAE')
    for file_path in file_paths:
        #print(file_path)
        file_name = file_path.split('/')[-1]
        data_processor = ma.DataProcessor(file_path)
        conc = data_processor.calibration(c0=C0)
        model_fitter = ma.ModelFitter(file_path, data_processor.time, conc, C0, eta, rho, mu0, Xs, a3, regularization=1)
        chi, r = model_fitter.fit(initial_guess, bounds)
        fitted_params.append((chi, r))
        r_squared, adj_r_squared, mse, rmse, mae = model_fitter.evaluate_fit()  # Print goodness-of-fit metrics
        print(file_name + '\t' + str(chi) + '\t' + str(r) + '\t'
            + str(r_squared) + '\t' + str(adj_r_squared) + '\t' + str(mse)
            + '\t' + str(rmse) + '\t' + str(mae))
        # model_fitter.plot_residuals()  # Plot residuals for each file
        # model_fitter.plot_parameter_convergence()  # Plot parameter convergence for each file
        # model_fitter.plot_fit()
        #plt.savefig(save_path + 'fit-' + file_name.split('.')[0] + '.png', dpi=300)
        #model_fitter.plot_residuals_surface(X_p_planeRange, r_planeRange)

    X_ppms = 0.0016750985561811776
    # X_ppms = 5.9e-4 # rs particles
    # Print fitted parameters
    print(f"Reference parameter (PPMS): X_p={X_ppms:.4}")
    for i, params in enumerate(fitted_params):
        X_p_fit, r_fit = params
        print(f"Fitted parameters ({files[i][:-4]}): r={r_fit:.3}, X_p={X_p_fit:.4}")

    def display_chi_p_values(X_p_values, uncertainties):
        for i, (X_p, uncertainty) in enumerate(zip(X_p_values, uncertainties), start=1):
            display(Math(rf'{i}: \chi_p = \, {X_p:.4f} \pm {uncertainty:.4f}'))

    def rel_error(true, pred):
        return abs(true - pred) / true

    X_p_values = []
    uncertainties = []
    for X, R in fitted_params:
        X_p_values.append(X)
        uncertainties.append(rel_error(X_ppms, X))

    # display(Math(rf'\chi ppms = \, {X_ppms:.4f}'))
    # display_chi_p_values(X_p_values, uncertainties)

    X_p_avg = np.mean(X_p_values)
    X_p_std = np.std(X_p_values)

    fig, ax = plt.subplots()

    # Plot X_p values with uncertainties as error bars
    ax.errorbar(range(len(X_p_values)), X_p_values, yerr=None, fmt='o', color='b', capsize=5)
    ax.hlines(X_ppms, 0, len(X_p_values)-1, label='PPMS Reference')
    ax.fill_between(range(len(X_p_values)), X_p_avg - X_p_std, X_p_avg + X_p_std, color='green', alpha=0.2)
    ax.hlines(X_p_avg, 0, len(X_p_values)-1, color='green', label='Avg. X_p')
    ax.hlines(X_p_avg+X_p_std, 0, len(X_p_values)-1, color='green', linestyle='--', label=r'$\pm \sigma$')
    ax.hlines(X_p_avg-X_p_std, 0, len(X_p_values)-1, color='green', linestyle='--')

    # Set labels and title
    ax.set_xticks(range(len(X_p_values)))
    ax.set_xticklabels([f[:-4] for f in files])
    ax.set_xlabel('Data Points')
    ax.set_ylabel('χ_p Values')
    ax.set_title(f'χ_p Values and Uncertainties\nχ_ppms = {X_ppms:.4f}')
    ax.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()

    # plt.show()


    # NOTE: assume final magmitus obsidian system configuration
def command_line_interface():
    # parameters
    eta = 8.9e-4
    rho = 5200
    mu0 = 4 * np.pi * (10e-7)
    Xs = -9.04e-6

    # magnet parameters
    l = 0.0254
    w = 0.0254
    in2m = 0.0254

    if len(sys.argv) < 2:
        path = input('Enter path to directory containing data:\n')
    else:
        path = sys.argv[1]

    if len(path) < 1:
        sys.exit('ERROR: Directory path must be a non-empty string.')
    if path[-1] != '/':
        path += '/'

    file_prefix = input("Enter shared file prefix. If none, press enter.\n")

    file_names_str = input("Enter file names separated by commas:\n")
    file_names = [f.strip() for f in file_names_str.split(',')]

    print("\n")
    print("Files to analyze:")
    for f in file_names:
        print(f)
    print("\n")

    c0_input = input('\nWhat is the initial concentration of the solution? [mg/mL]\n')
    try:
        c0 = float(c0_input)
    except:
        sys.exit("ENTRY ERROR: invalid initial concentration entered")

    t_input = input('How thick is your magnet?\n[a] 3/16"\n[b] 1/4"\n[c] 3/8"\n[d] 1/2"\n')
    if t_input == 'a':
        t = 3/16 * in2m
        print('3/16" thickness selected.')
    elif t_input == 'b':
        t = 1/4 * in2m
        print('1/4" thickness selected.')
    elif t_input == 'c':
        t = 3/8 * in2m
        print('3/8" thickness selected.')
    elif t_input == 'd':
        t = 1/2 * in2m
        print('1/2" thickness selected.')
    else:
        print("ENTRY ERROR: invalid magnet thickness entered")
        return

    grade = input('\nWhat grade is your magnet?\n[a] N42\n[b] N52\n')
    if grade == 'a':
        B_r = 1.32
        print('Grade N42 selected.')
    elif grade == 'b':
        B_r = 1.48
        print('Grade N52 selected.')
    else:
        print("ENTRY ERROR: invalid magnet grade entered")
        return

    # select magnetic field model parameters based on the system
    if B_r == 1.48 and t_input == 'd': # 1/2" thick, grade N52
        a = -13.655887

    ### CALIBRATION ###


if __name__ == "__main__":
    # command_line_interface()
    main_flip()
