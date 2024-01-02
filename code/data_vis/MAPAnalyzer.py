# Magnetic Suscepibility Analyzer for the MAPDAP

from Classes import MagFieldFit, ParamGuesser
import numpy as np
import matplotlib.pyplot as plt
import lightFunctions as lf
from scipy.optimize import curve_fit
import scipy.stats as stats
import warnings
import os
import random
import codecs
from tqdm import tqdm

# res - data resolution
class Analyzer:
    def __init__(self, res=1000, start_time=15):
        self.sensor_pos = 0.015115
        self.sensor_w = 0.001
        self.res = res
        self.z = np.linspace(self.sensor_pos-self.sensor_w,
            self.sensor_pos+self.sensor_w, self.res)
        self.start_time = start_time

        # TODO: this doesn't really belong here like this
        self.density = 5240 # intrinsic material density of the nanomaterial being analyzed

        # create dict of magnets
        self.magnets = {}
        self.create_magnets_dict()


    def create_magnets_dict(self):
        '''Adds the magnets to the Analyzer's dictionary.
        This function should be modified if different magnets are being used
        in the MAP.
        For each magnet, the following items are needed:
          - [str] a name that will show up in the menu
          - [float] the B_r value in Tesla
          - [list of floats] the dimensions of the magnet in m
                (order of arguments: Length, Width, Height)
        '''

        # default magnets - from K&J magnets
        #TODO: add part numbers
        # self.add_magnet('3', '3/8" - THE BIG KAHUNA', 1.32,
        #     [0.0254, 0.0254, 0.009525])
        # self.add_magnet('2', '1/4" - The Kahuna', 1.32,
        #     [0.0254, 0.0254, 0.006350])
        # self.add_magnet('1', '3/16" - the little kahuna', 1.32,
        #     [0.0254, 0.0254, 0.0047625])
        print("Importing magnets...")
        path = 'magnets/'
        for file in os.listdir(path):
            magnet_dict = self.import_magnet_file(path + file)

        print(self.magnets)

    def add_magnet(self, id, name, B_r, length, width, thickness):
        # create the magnet object
        mag = Magnet(name, B_r, length, width, thickness)

        # calculate magnet fit parameters
        [A, b] = mag.calculate_mag_fit(self.z)

        # add the magnet to the dictionary
        self.magnets[id] = {'mag': mag, 'name': name, 'A': A, 'b': b}

    # TODO: finish magnet import

    def import_magnet_file(self, file_name):
        """Import a single magnet file as a magnet dictionary

        Keyword arguments
        file_name - string, the name of the file
          - Any lines without a ':' in the line is ignored as a comment
        Returns: a dictionary representing the magnet
        """
        magnet = {}
        with open(file_name) as f:
            for line in f:
                # check if line is missing a colon - if so, ignore as a comment
                if ':' not in line:
                    continue

                (key, val) = line.split(":")
                # some post processing to remove any extra whitespace
                key = key.strip()
                val = val.strip()
                # add attributes to magnet dictionary
                magnet[key] = val

        self.add_magnet(magnet['id'], magnet['name'], magnet['B_r'],
            magnet['length'], magnet['width'], magnet['thickness'])


    #TODO: write function lol
    def analyze(self, file_manager):
        # get relevant variables from the file manager
        df = file_manager.get_df()
        sample_dict = file_manager.get_sample_dict()
        selection = file_manager.get_plot_list()
        # load selected data from dataframe
        data_dict = file_manager.load_data()

        # group files by sample and also sort by
        # sample > concentration > magnet > date > trial
        fg_keys, file_groups = self.group_files(data_dict)
        print("file groups:")
        self.print_groups(fg_keys, file_groups)

        # now for each group, actually analyze the samples
        for ki in range(len(fg_keys)):
            fg_k = fg_keys[ki]
            fg = file_groups[ki]

            #TODO: need to add status updates
            self.fit_file_group(data_dict, fg_k, fg)









    def group_files(self, data_dict):
        print('sorted data:')
        # Q: do i actually need to do this step??
        # sort the data given
        sorted_data_dict = sorted(data_dict.items(),
            key=lambda x: (x[1]['sample'], x[1]['concentration'],
                x[1]['magnet'], x[1]['date'], x[1]['trial']))
        #print(type(sorted_data_dict))
        #print(sorted_data_dict)
        # a list where is each entry is a tuple: (file_name, dict)

        file_groups = []
        fg_keys = []
        fi = -1
        for f in sorted_data_dict:
            file_name = f[0]
            f_sample = data_dict[file_name]['sample']
            f_conc = data_dict[file_name]['concentration']
            f_magnet = data_dict[file_name]['magnet']
            f_key = (f_sample, f_conc, f_magnet)
            if f_key not in fg_keys:
                fi += 1
                fg_keys.append(f_key)
                file_groups.append([])
                #TODO: fix the line below this
            file_groups[fi].append(file_name)

        return fg_keys, file_groups

    def print_groups(self, fg_keys, file_groups):
        for ki in range(len(fg_keys)):
            k = fg_keys[ki]
            print(k[0] + ", " + k[1] + ", " + k[2] + ": " + str(file_groups[ki]))

    # fg = list of file names
    def fit_file_group(self, data_dict, fg_k, fg):
        # get the linear fits from the magnet
        mag_id = fg_k[2]
        A = self.magnets[mag_id]['A']
        b = self.magnets[mag_id]['b']

        guesses = self.get_param_guesses(data_dict, fg)

        # analyze one file at a time
        for file_name in fg:
            time = data_dict[file_name]['time_data']
            lux = data_dict[file_name]['lux_data']
            print(file_name)
            print(self.analyze_file(time, lux, guesses, A, b, self.density))


    def preprocess_data(self, time_raw, lux_raw):
        # set the right starting point of the data
        time_trunc, lux_trunc = lf.trunc_low(self.start_time, time_raw, lux_raw)

        # check for negative values
        if np.any(lux_trunc <= 0):
            print("Negative values detected in dataset! That's no good mate.\n"
                + "Here is the problem child: " + test_file)

        # take log of inverse data to match exponential data
        lux_log = lf.matchEXP(lux_trunc)

        # translate data so that the starting point is t = 0, lux = 0
        time, lux = lf.set_data_origin(time_trunc, lux_log)
        return time, lux

    def get_param_guesses(self, data_dict, fg):
        warnings.filterwarnings("ignore")

        # set initial parameter scans
        s1_iter = np.linspace(-2000, -500, 40)
        s2_iter = np.linspace(-0.01, -1e-6, 40)
        total_iters = len(s1_iter) * len(s2_iter)

        # pick one file at random to test the parameter guesses
        test_file = fg[random.randint(0, len(fg) - 1)]
        print("parameters picked based on: " + test_file)

        # load the actual data
        time_raw = data_dict[test_file]['time_data']
        lux_raw = data_dict[test_file]['lux_data']

        time, lux = self.preprocess_data(time_raw, lux_raw)

        # dimensionality reduction function to help with fitting
        def transmOmega(t, eps, S1, S2):
            Omega = lux[-1]
            return lf.transm(t, eps, S1, S2, Omega)

        # define omega as the final lux value
        omega = lux[-1]
        print("omega: " + str(omega))

        # keep track of the mean values
        mean_matrix = np.zeros((total_iters, 3))

        print("\n")
        print("Scanning parameters")
        j = 0
        count = 0
        for s1 in s1_iter:
            k = 0
            for s2 in s2_iter:
                # define epsilon
                eps = s2 * omega / (s1 - s2)

                # set initial guesses
                guesses = eps, s1, s2

                # fit the curve
                (poptG, pcovG) = curve_fit(transmOmega, time, lux,
                    p0=guesses, maxfev=10000, bounds=(-np.inf, np.inf))

                # save the values
                mean_var = np.mean(np.diag(pcovG))
                mean_matrix[count] = [j, k, abs(mean_var)]

                # increment counting variables
                k += 1
                count += 1
            print(".", end="")
            j += 1

        print("\niterated " + str(count) + " times")

        # extract just the means from the saved data
        mean_var_array = lf.column(mean_matrix, 2)

        # find the index of the minimum mean
        index_min = np.argmin(mean_var_array)

        # extract the paramater guesses used in that run
        s1g_index, s2g_index, m = mean_matrix[index_min]
        s1g = s1_iter[int(s1g_index)] # find s1, s2 from initial array of params
        s2g = s2_iter[int(s2g_index)]
        epsg = s2g * omega / (s1g - s2g) # calculate epsilon

        guess_array = [epsg, s1g, s2g] # compile guesses
        print(guess_array)
        return guess_array

    def analyze_file(self, time_raw, lux_raw, guesses, A, b, density):
        # get processed data
        time, lux = self.preprocess_data(time_raw, lux_raw)

        # dimensionality reduction function to help with fitting
        def transmOmega(t, eps, S1, S2):
            Omega = lux[-1]
            return lf.transm(t, eps, S1, S2, Omega)

        # define omega as the final lux value
        omega = lux[-1]

        # fit the curve
        (popt, pcov) = curve_fit(transmOmega, time, lux, p0=guesses,
            maxfev=10000, bounds=(-np.inf,np.inf))

        # extract fit parameters
        eps, s1, s2 = popt

        # calculate additional model parameters
        alpha = lf.alpha(s1, s2)
        beta = lf.beta(s1, s2)
        X = lf.mag_sus(density, A, s1, s2)

        # create a dictionary with the results
        results = {}
        results['chi'] = X
        results['epsilon'] = eps
        results['delta1'] = s1
        results['delta2'] = s2
        results['omega'] = omega
        results['epsilon_init'] = guesses[0]
        results['delta1_init'] = guesses[1]
        results['delta2_init'] = guesses[2]
        return results


# B_r in T
# dims - (length, width, thickness) in [m]
class Magnet:
    def __init__(self, name, B_r, length, width, thickness):
        self.name = name
        self.B_r = float(B_r)
        self.L = float(length)
        self.W = float(width)
        self.T = float(thickness)

    def get_dims_str(self):
        return "Length: {} Width: {} Thickness: {}".format(self.L, self.W,
            self.T)

    # define the magnetic fit parameters
    # previously: get_magFitParams
    def calculate_mag_fit(self, z):
        #Creating mag field based on K&J Magnets, Inc. specs.
        B_s = lf.B_field(z, self.B_r, self.L, self.W, self.T)

        #Linear curve fit of magnetic field in sampling region
        (popt_B, pcov_B) = curve_fit(lf.B_LinFit, z, B_s, p0=None,
            sigma=None, bounds=(-np.inf,np.inf))

        # explicitly define actual parameters
        A, b = popt_B
        return [A, b]

    # TODO: write this
    def plot_mag_field(self, z):
        pass
