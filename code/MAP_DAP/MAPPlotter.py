import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import math
from statistics import mean
from matplotlib import rcParams
from abc import ABC, abstractmethod

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

class Plotter(ABC):
    def __init__(self, fig=None):
        if fig == None:
            fig = Figure()
        self.fig = fig

    @abstractmethod
    def plot(self):
        """Generates the figure of the plot"""
        pass

    def get_fig(self):
        """Returns the figure"""
        return self.fig

class TimeVsIntensity(Plotter):
    def __init__(self, fm, fig=None):
        self.fig = fig
        self.axes = None
        self.fm = fm
        self.files = {}

    # for now, we're going to ignore visibility
    # TODO: implement toggling / set visibiility
    def plot(self):
        selected_list = self.fm.get_selected_list()
        self.fig, self.axes = plt.subplots(1, 1)

        for index in selected_list:
            data = self.fm.load_file(index)
            line = self.axes.plot(data[:, 0], data[:, 1], linewidth=2,
                label=self.fm.get_file_name(index))

            self.files[index] = {'index': index,
                'data': self.fm.load_file(index), 'line': line}

            self.axes.set_xlabel('Time (s)')
            self.axes.set_ylabel('Intensity (lux)')

            self.axes.legend()
            plt.tight_layout()

    def get_fig(self):
        return self.fig
