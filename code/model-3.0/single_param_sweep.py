import numpy as np
import matplotlib.pyplot as plt
import single_magnetic_analysis as ma
from mpl_toolkits.mplot3d import Axes3D
import sys
from tqdm import tqdm

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def main(path, file, c0, a):
    eta = 8.9e-4
    rho = 5170
    r = 0.5e-6
    mu0 = 4 * np.pi * 10**-7
    Xs = -9.04e-6
    #initial_guess = [0.001, 0.5e-6]

    guesses = []
    chis = [1e-8, 8e-7, 6e-7, 4e-7, 2e-7,
            1e-7, 8e-6, 6e-6, 4e-6, 2e-6,
            1e-6, 8e-5, 6e-5, 4e-5, 2e-5,
            1e-5, 8e-4, 6e-4, 4e-4, 2e-4,
            1e-4, 8e-3, 6e-3, 4e-3, 2e-3,
            1e-3, 8e-2, 6e-2, 4e-2, 2e-2]
    rs =   [1e-9, 8e-8, 6e-8, 4e-8, 2e-8,
            1e-8, 8e-7, 6e-7, 4e-7, 2e-7,
            1e-7, 8e-6, 6e-6, 4e-6, 2e-6,
            1e-6, 8e-5, 6e-5, 4e-5, 2e-5,
            1e-5, 8e-4, 6e-4, 4e-4, 2e-4,
            1e-4]
    guesses = [0.001]


    bounds = ([0], [0.1])#([0, 0], [np.inf, np.inf])

    # Process data and fit model
    #file_paths = ['data/mjack005.txt', 'data/mjack006.txt', 'data/mjack007.txt', 'data/mjack008.txt', 'data/mjack009.txt']

    fitted_params = []

    save_path = '../../../../validation_data/model-3.0_results/single-param/'

    r_planeRange = np.linspace(1e-7, 1e-4, 50)
    X_p_planeRange = np.linspace(0.0001, 0.004, 50)

    print('init_chi\tinit_radius\tchi\t\tradius\t\tr_sq')

    #print(file_path)
    file_path = path + file
    file_name = file
    data_processor = ma.DataProcessor(file_path)
    conc = data_processor.calibration(c0)

    best_guess = guesses[0]
    best_r_sq = -np.inf

    for initial_guess in tqdm(guesses):
        model_fitter = ma.ModelFitter(file_path, data_processor.time, conc, c0, eta, rho, mu0, Xs, a, r, regularization=1)
        chi = model_fitter.fit(initial_guess, bounds)
        fitted_params.append((chi))
        r_squared, adj_r_squared, mse, rmse, mae = model_fitter.evaluate_fit()  # Print goodness-of-fit metrics
        # print(file_name + '\t' + str(chi) + '\t' + str(r) + '\t'
        #     + str(r_squared) + '\t' + str(adj_r_squared) + '\t' + str(mse)
        #     + '\t' + str(rmse) + '\t' + str(mae))

        if r_squared > best_r_sq:
            best_guess = initial_guess
            best_r_sq = r_squared
            print(str(initial_guess) + '\t' + str(chi) + '\t' + str(r) + '\t' + str(r_squared))
    # model_fitter.plot_residuals()  # Plot residuals for each file
    # model_fitter.plot_parameter_convergence()  # Plot parameter convergence for each file
    # model_fitter.plot_fit()
    #plt.savefig(save_path + 'fit-' + file_name.split('.')[0] + '.png', dpi=300)
    #model_fitter.plot_residuals_surface(X_p_planeRange, r_planeRange)

    model_fitter = ma.ModelFitter(file_path, data_processor.time, conc, c0, eta, rho, mu0, Xs, a, r, regularization=1)
    chi = model_fitter.fit(best_guess, bounds)
    fitted_params.append((chi))
    r_squared, adj_r_squared, mse, rmse, mae = model_fitter.evaluate_fit()  # Print goodness-of-fit metrics
    # print(file_name + '\t' + str(chi) + '\t' + str(r) + '\t'
    #     + str(r_squared) + '\t' + str(adj_r_squared) + '\t' + str(mse)
    #     + '\t' + str(rmse) + '\t' + str(mae))
    print("FINAL MODEL")
    print("file: " + str(file))
    print("chi\tradius\tr^2")
    print(str(chi) + '\t' + str(r) + '\t' + str(r_squared))

    # plot:
    fig = plt.figure()
    plt.plot(data_processor.time, conc, label='data')
    orig_model = model_fitter.model(data_processor.time, X_p=chi)
    plt.plot(data_processor.time, orig_model, label='original')
    plt.xlabel('time (s)')
    plt.ylabel('conc (mg/mL)')
    plt.legend()
    plt.tight_layout()
    plt.show()


    # NOTE: assume final magmitus obsidian system configuration
def command_line_interface():
        # parameters
        eta = 8.9e-4
        rho_p = 5200
        rho_s = 1000
        mu0 = 4 * np.pi * (10e-7)
        Xs = -9.04e-6

        # physical setup parameters
        sensor = [0.0130, 0.014] #TODO: enter sensor position
        z_low = sensor[0]
        z_high = sensor[1]
        h_window = 0.001
        a_window = 0.01 * 0.01
        v_window = a_window * h_window

        # magnet parameters
        l = 0.0254
        w = 0.0254
        in2m = 0.0254

        t_input = input('Which magnet are you using?\n[a] 3/16"\n[b] 1/4"\n[c] 3/8"\n[d] 1/2"\n')
        if t_input == 'a':
            t = 3/16 * in2m
            print('3/16" thickness, Grade N42 selected.')
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

        # TODO: eventually, replace this with the fit itself
        if t_input == 'a': # 3/16" thick, N42
            a = -6.677333
        elif t_input == 'b': #1/4" thick, N42
            a = -8.208740
        elif t_input == 'c' and grade =='a':
            a = -10.545907
        elif t_input == 'c' and grade =='b':
            a = -11.824199
        elif t_input == 'd':
            a = -13.655887
        print('a = ' + str(a))

        path = '../../../../test_data/paper_data/'

        print("\nCurrent path: " + path)
        path_append = input('Add to path? [enter to skip or start with "-" to enter fully new path]\n')
        if len(path_append) > 0 and path_append[0]=='-':
            path = path_append[1:]
        else:
            path += path_append

        print("\nNew path: " + path)

        file = input('Please enter file name: \n')

        if file[-4:] != '.txt':
            file += '.txt'

        c0_input = input('\nWhat is the initial concentration of the solution? [mg/mL]\n')
        try:
            c0 = float(c0_input)
        except:
            print("ENTRY ERROR: invalid initial concentration entered")

        ### CALIBRATION ###
        print("\nLoading file...")
        try:
            data = np.genfromtxt(path + file)
        except:
            print("ERROR: Could not load data file at:\n" + path + file)
        print("Successfully loaded " + file + '\n')


        main(path, file, c0, a)

if __name__ == "__main__":
    command_line_interface()
    #main_flip()
