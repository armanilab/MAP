import numpy as np
import matplotlib.pyplot as plt
import magnetic_analysis as ma
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import display, Math

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def display_chi_p_values(X_p_values, uncertainties):
    result = "\n".join([f"X_p = {X:.4f}, Uncertainty = {u:.4f}" for X, u in zip(X_p_values, uncertainties)])
    return result

def main():
    # Parameters
    L = 0.0254
    W = 0.0254
    T = 0.009525
    sensor_pos = 0.0447
    sensor_w = 0.001
    B_r = 1.32
    eta = 8.9e-4
    rho = 5200
    mu0 = 4 * np.pi * 10**-7
    Xs = -9.04e-6
    C0 =  0.1 #* (0.001 * 0.001 * 0.01) / (3.84e-22)#0.1 * (3 * 0.001 * 0.001 * 0.01) / (4e6 * np.pi * ((0.5e-6)**3) *rho)
    initial_guess = [1e-6, 0.001]
    bounds = ([0, 0], [0.1, 0.1])#([0, 0], [np.inf, np.inf])
    a3 = -9.0408
    #a3 = -26.195524 # 1/4" magnets, repelling
    # Instantiate classes
    # mag_field_model = ma.MagneticFieldModel(B_r, L, W, T)
    # a, b = mag_field_model.a_b_field_calc(sensor_pos, sensor_w)
    # print(a, b)

    # Process data and fit model
    file_paths = ['data/mjack005.txt', 'data/mjack006.txt', 'data/mjack007.txt', 'data/mjack008.txt', 'data/mjack009.txt']
    # path = '../../../../test_data/paper_data/magob/'
    # files = ['magob008.txt', 'magob009.txt']
    # file_paths = [path + f for f in files]
    fitted_params = []

    r_planeRange = np.linspace(1e-7, 3e-5, 50)
    X_p_planeRange = np.linspace(0.0001, 0.004, 50)

    for file_path in file_paths:
        data_processor = ma.DataProcessor(file_path)
        conc = data_processor.calibration(c0=0.1)
        model_fitter = ma.ModelFitter(file_path, data_processor.time, conc, C0, eta, rho, mu0, Xs, a3, regularization=1)
        fitted_params.append(model_fitter.fit(initial_guess, bounds))
        model_fitter.evaluate_fit()  # Print goodness-of-fit metrics
        # model_fitter.plot_residuals()  # Plot residuals for each file
        #model_fitter.plot_parameter_convergence()  # Plot parameter convergence for each file
        model_fitter.plot_fit()
        # model_fitter.plot_residuals_surface(r_planeRange, X_p_planeRange)

    X_ppms = 0.0016750985561811776
    # Print fitted parameters
    print(f"Reference parameter (PPMS): X_p={X_ppms:.4}")
    for i, params in enumerate(fitted_params):
        r_fit, X_p_fit = params
        print(f"Fitted parameters ({file_paths[i]}): r={r_fit:.3}, X_p={X_p_fit:.4}")

    def display_chi_p_values(X_p_values, uncertainties):
        for i, (X_p, uncertainty) in enumerate(zip(X_p_values, uncertainties), start=1):
            display(Math(rf'{i}: \chi_p = \, {X_p:.4f} \pm {uncertainty:.4f}'))

    def rel_error(true, pred):
        return abs(true - pred) / true

    X_p_values = []
    uncertainties = []
    for R, X in fitted_params:
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
    ax.set_xticklabels([f'Point {i+1}' for i in range(len(X_p_values))])
    ax.set_xlabel('Data Points')
    ax.set_ylabel('χ_p Values')
    ax.set_title(f'χ_p Values and Uncertainties\nχ_ppms = {X_ppms:.4f}')
    ax.legend()

    # Show the plot
    plt.grid(True)
    plt.tight_layout()

    plt.show()


def main_lexie():
    # Parameters
    L = 0.0254
    W = 0.0254
    T = 0.009525
    sensor_pos = 0.00905
    sensor_w = 0.00004
    B_r = 1.32
    eta = 8.9e-4
    rho = 5200
    mu0 = 4 * np.pi * 10**-7
    Xs = -9.04e-6
    C0 = 0.1 #* (3 * 0.001 * 0.001 * 0.01) / (4e6 * np.pi * ((0.5e-6)**3) *rho) #0.1 * (0.001 * 0.001 * 0.01) / (3.84e-22)
    initial_guess = [1e-6, 0.001]
    bounds = ([0, 0], [0.1, 0.1])#([0, 0], [np.inf, np.inf])
    #a3 = -9.0408
    #a3 = -26.195861 # 1/4" magnets, repelling
    a3 = -34.051553 #3/8" magnets, repelling

    file = '../../../../test_data/paper_data/noir2/noir2004.txt'
    results = []

    r_planeRange = np.linspace(1e-7, 3e-5, 50)
    X_p_planeRange = np.linspace(0.0001, 0.004, 50)

    r_range = np.linspace(1e-8, 1e-4, 20)
    x_range = np.linspace(1e-8, 1e-3, 20)

    data_processor = ma.DataProcessor(file)
    conc = data_processor.calibration(c0=0.1)
    model_fitter = ma.ModelFitter(file, data_processor.time, conc, C0, eta, rho, mu0, Xs, a3, regularization=1)
    max_r_sq = -np.inf
    max_result = []

    # counter = 0
    # for r in r_range:
    #     counter += 1
    #     print("# " + str(counter) + " of " + str(len(r_range)))
    #     for x in x_range:
    #         initial_guess = [r, x]
    #         print('initial- r: {:.4e}, chi: {:.4e}'.format(r, r))
    #         fitted_param = model_fitter.fit(initial_guess, bounds)
    #         r_fit, X_p_fit = fitted_param
    #         print('fit ---- r: {:.4e}, chi: {:.4e}'.format(r_fit, X_p_fit))
    #         y_pred = model_fitter.model(model_fitter.time, r_fit, X_p_fit)
    #         r_squared, adj_r_squared, mse, rmse, mae = ma.calculate_metrics(conc, y_pred, model_fitter.n, model_fitter.p)
    #         new_result = [x, r, fitted_param[0], fitted_param[1], r_squared, adj_r_squared, mse, rmse, mae]
    #         if r_squared > max_r_sq:
    #             max_result = new_result
    #         results.append(new_result)
    #         #print(new_result)
    #
    # print('max_result:')
    # print(max_result)
    #
    # print("analysis done; writing file")
    # with open('results.txt', 'w') as f:
    #     f.write(file + '\n')
    #     f.write('r_init, x_init, r_fit, x_fit, r_sq, adj_r_sq, mse, rmse, mae\n')
    #     for ri in range(len(results)):
    #         r = results[ri]
    #         f.write(str(r) + '\n')

    file_paths = ['../../../../test_data/paper_data/noir2/noir2011.txt',
        '../../../../test_data/paper_data/noir2/noir2012.txt',
        '../../../../test_data/paper_data/noir2/noir2013.txt']
    fitted_params = []

    for file_path in file_paths:
        data_processor = ma.DataProcessor(file_path)
        conc = data_processor.calibration(c0=0.1)
        model_fitter = ma.ModelFitter(file_path, data_processor.time, conc, C0, eta, rho, mu0, Xs, a3, regularization=1)
        fitted_params.append(model_fitter.fit(initial_guess, bounds))
        model_fitter.evaluate_fit()  # Print goodness-of-fit metrics
        # model_fitter.plot_residuals()  # Plot residuals for each file
        #model_fitter.plot_parameter_convergence()  # Plot parameter convergence for each file
        model_fitter.plot_fit()
        # model_fitter.plot_residuals_surface(r_planeRange, X_p_planeRange)

        plt.show()

    for i, params in enumerate(fitted_params):
        r_fit, X_p_fit = params
        print(f"Fitted parameters ({file_paths[i]}): r={r_fit:.3}, X_p={X_p_fit:.4}")


if __name__ == "__main__":
    main_lexie()
