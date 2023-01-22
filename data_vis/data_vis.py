# Launches the data analysis pipeline
# Lexie Scholtz
# Created: 2022.12.27

import sys
from os import path
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import math

DATA_DIR = "../../../test_data/"

def main():
    # check for correct number of arguments
    if len(sys.argv) < 2:
        print("ERROR: Not enough arguments.")
        print("Correct usage:")
        print("$ python3 data_vis.py <xlsx_file_path>")
        sys.exit()

    # parse arguments
    file = sys.argv[1]

    df = pd.read_excel(file)
    print(df.shape)

    to_plot = df
    current_filters = ""

    while True:
        # TODO: finish selection options
        print("Filter options:")
        print("[1] Date")
        print("[2] File Location")
        print("[3] File Name")
        print("[4] Series ID")
        print("[5] Sample ID")
        print("[r] to reset all filters")
        print("[q] to quit")

        filter_input = input("Enter filter number: ")
        try:
            filter_num = int(filter_input)
        except ValueError:
            print(filter_num)
            if filter_input == 'r':
                to_plot = df
                current_filters = ""
                print("All filters reset.")
                continue
            elif filter_input == 'q':
                print("Ending data visualization.")
                return

        if filter_num == 3:
            # to_plot, filter_applied = filter_by_name(to_plot)
            pass

        if filter_num == 4:
            to_plot, filter_applied = filter_by_series(to_plot)


        print("Current filters applied: " + current_filters)
        again = input("Filter further? [y/n] ")
        if again == 'n':
            break

    # now actually plot these
    while True:
        print("Select a plot type:")
        print("[1] Time vs. light")
        print("[2] Concentration vs. change in light")
        print("[b] to go back")
        print("Any other key to end program")

        try:
            plot_num = int(input("Enter plot number: "))
        except ValueError:
            break

        # TODO: add customizations

        if plot_num == 1:
            print("")
            print("Add additional options? Include all letters at once")
            print("[n] Normalize curve")
            print("any other key or just enter to continue")

            options = input("Enter (multiple) options: ")
            normalize = False
            if 'n' in options:
                normalize = True

            plot_light_curve(to_plot, normalize)
        else:
            break

# TODO: add title label
def plot_light_curve(df, normalized=False):
    # make plot fig
    fig, ax = plt.subplots()

    title_str = "Light curves\n"

    # TODO: add code to determine which variable to use as a label (the one that changes)
    # ignore the category that stays the same.
    # these could be: MNP, solvent, concentration, magnet
    # always include trial number

    # plot each curve
    for row in df.itertuples():
        directory = row[3]
        file_name = row[4]
        file_path = path.join(DATA_DIR, directory, file_name)
        if file_path[:-4] != '.txt':
            file_path += '.txt'
        data = np.genfromtxt(file_path)

        # TODO: change this out of hard coded later
        magnet = row[13]
        trial_num = row[6]
        row_label = str(magnet) + '\" magnet, trial #' + str(trial_num)[:-2]

        x = data[:, 0]
        y = data[:, 1]

        if normalized:
            total_l = 0
            total_pts = 0
            for i in range(len(data[:, 0])):
                t = data[i, 0]
                if t >= 5 and t <= 10:
                    total_l += data[i, 1]
                    total_pts += 1
            baseline = total_l / total_pts
            y = y - baseline
            # add label to title
            title_str += 'normalized'

        plt.plot(x, y, label=row_label)

    ax.set_title(title_str)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Lux")
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    #ax.legend(ncol = 2, bbox_to_anchor=(0.5, -0.5), loc="upper center")
    plt.tight_layout()
    plt.show()

def filter_by_name(df):
    print("")
    print("Filtering by name")
    file = input("Enter file name [q to cancel]: ")

    # some correction if they don't include .txt
    if (file[-4:] != '.txt'):
        file += '.txt'

# Filter the selected data by a series ID
#   input:
def filter_by_series(df):
    print("")
    print("Filtering by series")
    print("Options:")
    series_list = df['Series-ID'].unique()
    for i in series_list:
        if isinstance(i, str):
            print("   " + str(i))

    while True:
        series_id = input("Enter series ID [q to cancel]: ")

        # if user enters 'q', cancel
        if series_id == 'q':
            return None, None

        # check if id in list. if so, show the selected rows
        if series_id in series_list:
            # find entries in this series
            series = df.loc[df['Series-ID'] == series_id]

            # print selected series
            print("Preview of selected rows:")
            print(series)

            # create string indicating what was used to filter
            filter_id = "Series-ID: " + series_id
        else:
            # could not find
            print("Could not find '" + series_id + "' series.")
            print("Please try again.")

    return series, filter_id
main()
