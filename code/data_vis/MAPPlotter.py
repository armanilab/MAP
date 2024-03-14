import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
import pandas as pd
import math
from statistics import mean
from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})

BASELINE_PTS = 100 # number of datapoints used for baseline
CONC_PTS = 100 # number of datapoints averaged to calculate change in light transmission for concentration curve

colors_list = ['#67217e',   # purple
               '#3e3e90',   # dark blue
               '#4e65ae',   # mid blue
               '#6088be',   # blue
               '#709eaf',   # teal blue
               '#7eac99',   # teal
               '#92b875',   # green
               '#b6bc55',   # lime green
               '#ccab47',   # yellow
               '#d08d3e',   # yellow orange
               '#cb6433',   # orange
               '#ba2625',   # red
               '#945200',   # brown
               '#7f7f7f',   # grey`
               '#000000']   # black

markers_list = ['o', '^', 's', 'P']

class Plotter:
    def __init__(self, fig=None):
        if fig == None:
            fig = Figure()
        self.fig = fig

    def plot_light_curve(self, file_manager,
        baseline_correction=False, no_legend=False, extra_big=False):

        df = file_manager.get_df()
        sample_dict = file_manager.get_sample_dict()
        selection = file_manager.get_selected_list()
        ax = self.fig.axes[0]
        ax.clear()
        plt.tight_layout()

        # load selected data from dataframe
        data_dict = file_manager.load_data()

        # set title of plot
        title = ''
        if title == '':
            # default title
            title = "Light curves"
            if baseline_correction:
                title += "\nbaseline corrected"

        # set line properties
        line_width = 1
        if extra_big:
            line_width = 5

        # define variables used to set color of lines
        curve_index = 0
        num_rows = len(data_dict.keys())

        for file in data_dict.keys():
            file_data = data_dict[file]
            print(str(curve_index) + ": " + file_data['file_name'])

            # load data
            t = file_data['time_data']
            l = file_data['lux_data']

            if baseline_correction:
                # get average of first BASELINE_PTS number of points
                baseline_average = mean(l[0:BASELINE_PTS])
                # subtract average from all datapoints to offset data
                l = l - baseline_average

            # TODO: fix line label somehow?
            line_label = file_data['concentration'] + " mg/mL, " + 'trial #' + file_data['trial']
            line_color = colors_list[curve_index * int(len(colors_list) / num_rows) % len(colors_list)]
            ax.plot(t, l, label=file, linewidth=line_width, color=line_color) # TODO: add label

            curve_index += 1

        ax.set_title(title)

        # set axes label
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Light [lux]")

        # TODO: add legend
        if not no_legend:
            ax.legend()

        print("Plotted!")
        plt.tight_layout()

    # TODO: fix these bugs
    def plot_concentration_curve(self, file_manager):
        # get relevant variables from the file manager
        df = file_manager.get_df()
        sample_dict = file_manager.get_sample_dict()
        selection = file_manager.get_plot_list()
        # load selected data from dataframe
        data_dict = file_manager.load_data()

        # set up the axes
        ax = self.fig.axes[0]
        ax.clear()

        title = ''
        if title == '':
            # default title
            title = "Sensor response curve"

        for file in data_dict.keys():
            file_data = data_dict[file]

            # load data
            t = file_data['time_data']
            l = file_data['lux_data']

            # use first and last CONC_PTS to calculate the change in lux
            init_lux = mean(l[:CONC_PTS])
            final_lux = mean(l[-(CONC_PTS+1):])
            delta_lux = final_lux - init_lux

            trial = int(file_data['trial'])
            conc = float(file_data['concentration'])

            f_color = colors_list[trial - 1]
            f_marker = markers_list[trial - 1]

            plt.plot(conc, delta_lux, color=f_color, marker=f_marker)

        # set up legend
        for si in range(len(colors_list)):
            plt.plot([], [], color=colors_list[si], marker=markers_list[si],
                label=("Trial " + str(si + 1)))

        ax.set_title(title)
        ax.set_xlabel("Concentration [mg/mL]")
        ax.set_ylabel("Change in light [lux]")
        ax.legend()
        plt.tight_layout()
