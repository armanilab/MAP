import numpy as np
from scipy.optimize import least_squares, curve_fit
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import display, Math

class MagneticFieldModel:
    def __init__(self, B_r, L, W, T):
        self.B_r = B_r
        self.L = L
        self.W = W
        self.T = T

    def B_field(self, z):
        """Returns the function for the magnetic field of a rectangular block
        magnet from K&J Magnets

        Parameters
        ----------
        z: float, or list/array of floats
            The distance from the surface of the magnet

        Returns
        -------
        The function modeling the magnetic field
        """

        return (self.B_r / np.pi) * (np.arctan((self.L * self.W) / (2 * z * np.sqrt(4 * z**2 + self.L**2 + self.W**2))) -
                                     np.arctan((self.L * self.W) / (2 * (z + self.T) * np.sqrt(4 * (z + self.T)**2 + self.L**2 + self.W**2))))

    @staticmethod
    def lin_fit(z, A, b):
        return A * z + b

    def a_b_field_calc(self, sensor_position, sensor_width):
        """Calculates the linear fit of the magnetic field equation within the
        sensor/smapling window

        Parameters
        ----------
        sensor_position: float
            The z-position of the midpoint of the sensor region
        sensor_width: float
            The full width of the sensor region

        Returns
        -------
        An array containing the slope and intercept of the linear fit, in that
        order
        """

        # define ends of sensing window
        upper = sensor_position + 0.5 * sensor_width
        lower = sensor_position - 0.5 * sensor_width

        z = np.linspace(0, 0.125, 1000)
        B = self.B_field(z)

        z_trunc = z[(z >= lower) & (z <= upper)]
        B_trunc = B[(z >= lower) & (z <= upper)]

        popt_b, _ = curve_fit(self.lin_fit, z_trunc, B_trunc)

        return popt_b

class DoubleMagModel(MagneticFieldModel):
    def __init__(self, B_r, L, W, T):
        super().__init__(B_r, L, W, T)

    def B_field(self, z):
        b1 = (self.B_r / np.pi) * (np.arctan((self.L * self.W) / (2 * z * np.sqrt(4 * z**2 + self.L**2 + self.W**2))) -
                                     np.arctan((self.L * self.W) / (2 * (z + self.T) * np.sqrt(4 * (z + self.T)**2 + self.L**2 + self.W**2))))
        b2 = np.flip(b1)
        return b1 + b2

class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.time, self.intensity = np.loadtxt(file_path, skiprows=3, unpack=True)

        # NEW: cutoff files at certain timepoint
        # cutoff = 180
        # print("cutoff time: " + str(cutoff))
        # self.intensity = self.intensity[self.time < cutoff]
        # self.time = self.time[self.time < cutoff]

        # the conversion factor between concentration and number of particles
        self.conc2num =(0.001 * 0.001 * 0.01) / (3.84e-22)

    def calibration(self, c0=0.1):
        """Performs calibration steps to turn intensity data into concentration

        Parameters
        ----------
        c_0: float
            Initial concentration

        Returns
        -------
        The transformed intensity data (now number of particles)
        """

        e_0 = np.average(self.intensity[-101:])
        T = self.intensity / e_0
        atten = np.log10(1 / T)
        att0 = atten[0]
        attf = np.average(atten[-5:])

        def att_to_conc(att, att0, attf, c0):
            return c0 / (att0 - attf) * att + attf * c0 / (attf - att0)

        conc = att_to_conc(atten, att0, attf, c0)
        return conc #* self.conc2num

class ParameterTracker:
    def __init__(self):
        self.history = []

    def update(self, params):
        self.history.append(np.copy(params))

    def get_history(self):
        return np.array(self.history)

    def get_path(self):
        return np.array(self.history)

def plot_convergence(history, param_names):
    history = np.array(history)
    n_params = len(param_names)

    plt.figure(figsize=(15, 5))

    for i in range(n_params):
        plt.subplot(1, n_params, i + 1)
        plt.plot(history[:, i], label=f'{param_names[i]}', marker='o', color='darkblue')
        plt.xlabel('Iteration')
        plt.ylabel('Parameter value')
        plt.title(f'{param_names[i]} Convergence')
        plt.legend()

    plt.tight_layout()
    # plt.show()

def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared

def calculate_adjusted_r_squared(r_squared, n, p):
    return 1 - (1 - r_squared) * (n - 1) / (n - p - 1)

def calculate_metrics(y_true, y_pred, n, p):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p - 1)
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(y_true - y_pred))
    return r_squared, adj_r_squared, mse, rmse, mae

class ModelFitter:
    def __init__(self, file_name, time, conc, C0, eta, rho, mu0, Xs, a, regularization=0.0):
        self.time = time
        self.conc = conc
        self.C0 = C0
        self.eta = eta
        self.rho = rho
        self.mu0 = mu0
        self.Xs = Xs
        self.a = a
        self.tracker = ParameterTracker()
        self.n = len(time)
        self.p = 2  # Number of parameters: r and X_p
        self.regularization = regularization
        self.file_name = file_name

    def model(self, t, X_p, r):
        #alpha = 9 * self.eta / (2 * self.rho * r**2)
        #lpha = 18 * self.eta / (np.pi * self.rho * r**2)
        #alpha = 4.50001 * self.eta / (self.rho * r**2)
        #alpha = .1 * self.eta / (2 * self.rho * r**2)
        #cd = 5589 10:1 aspect ratio
        #cd = 3384
        # cd = 31523 # dynabeads

        # stokes = 6 * np.pi * self.eta * r
        # alpha = stokes / (4 * np.pi * (r**3) * self.rho / 3)
        #alpha = (self.eta * cd) / (2 * r* self.rho) # new - lexie 10/26
        #print("stokes drag")
        #alpha = (0.375 * 1.2 * self.eta) / (r * self.rho) # cylinder
        alpha = (4.500001 * self.eta) / (r**2 * self.rho) # sphere (stokes)
        #alpha = (self.eta * 0.82) / (2 * r * self.rho)
        beta = 2 * self.a**2 * X_p / (self.rho * self.mu0 * (1 + self.Xs))

        discriminant = alpha**2 - 4 * beta

        if discriminant < 0:
            # Complex roots case: overdamped system
            real_part = -0.5 * alpha
            imaginary_part = 0.5 * np.sqrt(-discriminant)
            k1 = self.C0
            k2 = 0
            return np.exp(real_part * t) * (k1 * np.cos(imaginary_part * t) + k2 * np.sin(imaginary_part * t))
        else:
            delta1 = 0.5 * (-alpha - np.sqrt(discriminant))
            delta2 = 0.5 * (-alpha + np.sqrt(discriminant))

            if np.isclose(delta1, delta2):
                # Repeated roots case
                delta = delta1
                k1 = self.C0
                k2 = 0
                return (k1 + k2 * t) * np.exp(delta * t)
            else:
                # Distinct roots case
                k1 = self.C0 * delta2 / (delta2 - delta1)
                return k1 * np.exp(delta1 * t) + (self.C0 -k1) * np.exp(delta2 * t)

    def residuals(self, params):
        X_p, r = params
        residual = self.model(self.time, X_p, r) - self.conc
        # Add regularization term
        regularization = self.regularization * (r**2 + X_p**2)
        return residual + regularization

    def fit(self, initial_guess, bounds, verbose=0, convergence_method='trf', convergence_tol=1e-8):
        def objective_function(params):
            self.tracker.update(params)
            return self.residuals(params)

        result = least_squares(objective_function, initial_guess,
            method=convergence_method, tr_solver=None, loss='soft_l1',
            f_scale=0.1, x_scale=[1e-3, 1e-6], ftol=convergence_tol,
            gtol=convergence_tol, xtol=convergence_tol, bounds=bounds,
            verbose=verbose, max_nfev=10000)

        self.fitted_params = result.x
        return self.fitted_params

    def evaluate_fit(self):
        X_p_fit, r_fit = self.fitted_params
        y_pred = self.model(self.time, X_p_fit, r_fit)
        r_squared, adj_r_squared, mse, rmse, mae = calculate_metrics(self.conc, y_pred, self.n, self.p)
        # print(f"R²: {r_squared:.4f}")
        # print(f"Adjusted R²: {adj_r_squared:.4f}")
        # print(f"MSE: {mse:.4e}")
        # print(f"RMSE: {rmse:.4e}")
        # print(f"MAE: {mae:.4e}")
        return r_squared, adj_r_squared, mse, rmse, mae

    def plot_residuals(self):
        residuals = self.residuals(self.fitted_params)
        plt.figure()
        plt.plot(self.time, residuals, 'g.')
        plt.axhline(0, color='red', linestyle='--')
        plt.xlabel('Time')
        plt.ylabel('Residuals')
        plt.title('Residuals Plot')

    def plot_parameter_convergence(self):
        history = self.tracker.get_history()
        plot_convergence(history, ['X_p', 'r'])

    def plot_fit(self):
        X_p_fit, r_fit = self.fitted_params
        y_pred = self.model(self.time, X_p_fit, r_fit)

        plt.figure(figsize=(3.5, 3.5), dpi=300)
        plt.plot(self.time, self.conc, label='Experimental Data', markersize=5)
        plt.plot(self.time, y_pred, '--', label='Fitted Model', color='red')
        plt.xlabel('Time (s)')
        plt.ylabel('Concentration (mg/mL)')
        plt.title(self.file_name.split('/')[-1])
        plt.legend()
        plt.tight_layout()
        plt.grid(True)


    def plot_residuals_surface(self, param1_range, param2_range):
        param1_grid, param2_grid = np.meshgrid(param1_range, param2_range)
        residuals_grid = np.zeros_like(param1_grid)

        # Calculate residuals for each combination of parameters
        for i in range(param1_grid.shape[0]):
            for j in range(param1_grid.shape[1]):
                params = [param1_grid[i, j], param2_grid[i, j]]
                residuals_grid[i, j] = np.sum(self.residuals(params) ** 2)

        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Plot the surface with reduced opacity
        surf = ax.plot_surface(param1_grid, param2_grid, residuals_grid, cmap='viridis', alpha=0.6)

        # Plot the path of parameter values
        path = self.tracker.get_path()
        if path.shape[0] > 1:
            path_residuals = [np.sum(self.residuals(p) ** 2) for p in path]

            # Plot the line connecting all points in the path
            ax.plot(path[:, 0], path[:, 1], path_residuals, color='red', linestyle='-', linewidth=2, label='Path of Convergence', zorder=5)

            # Highlight the first and last points
            ax.scatter(path[0, 0], path[0, 1], path_residuals[0], color='blue', s=150, edgecolor='black', label='Start Point', zorder=10)
            ax.scatter(path[-1, 0], path[-1, 1], path_residuals[-1], color='green', s=150, edgecolor='black', label='End Point', zorder=10)

        # Plot the final convergence values

        X_p_fit, r_fit = self.fitted_params
        final_residuals = np.sum(self.residuals([X_p_fit, r_fit]) ** 2)
        ax.scatter(X_p_fit, r_fit, final_residuals, color='red', s=100, edgecolor='black', label='Final Convergence', zorder=10)

        ax.set_xlabel('r')
        ax.set_ylabel('X_p')
        ax.set_zlabel('Residuals Sum of Squares')
        ax.set_title('Residuals Surface')
        ax.legend()



def main():
    print('')

if __name__ == "__main__":
    main()
