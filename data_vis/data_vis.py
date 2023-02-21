# Launches the data analysis pipeline
# Lexie Scholtz
# Created: 2022.12.27

import sys
from os import path
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import math


# IMPORTANT VARIABLES
DATA_DIR = "../../../test_data/"
# in the log of data files, the first two columns MUST be the file name and
# relative path to file (from the location of the log file).
file_col = 1
directory_col = 2

trial_col = 7
conc_col = 14

MEAS_PERIOD = 10 # number of seconds to average to get light transmission measurement


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
    df = pre_process(df)
    print(df.shape)

    to_plot = df
    current_filters = []

    while True:
        # print selection options for filters
        # all columns are possible filters
        # filter numbers start at 1 for user convenience

        print("Filter options: [select via number]")
        for i in range(len(df.columns)):
            print("[" + str(i + 1) + "] " + str(df.columns[i]))
        print("[q] to quit")
        print("[r] to reset all filters")
        filter_input = input("Enter filter number: ")
        try:
            filter_num = int(filter_input) - 1
        except ValueError:
            if filter_input == 'r':
                to_plot = df
                current_filters = []
                print("All filters reset.")
                continue
            elif filter_input == 'q':
                print("Ending data visualization.")
                return
            else:
                print("Could not select filter. Try again.")
                print("")
                continue

        # check the range of the filter
        if filter_num < 0 or filter_num > len(df.columns):
            print("Selected filter is out of range. Try again.")

        if filter_num == 5:
            to_plot, filter_label = filter_by_series(to_plot)
            current_filters.append(filter_label)

        # apply the filter
        found, filtered_df, filter_label = apply_filter(to_plot, filter_num)

        if found:
            current_filters.append(filter_label)
            to_plot = filtered_df


        print("Current filters applied: ")
        #print(current_filters)
        # TODO: fix this. currently prints each char on a separate line
        for i in range(len(current_filters)):
            print("  " + current_filters[i])
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
            # add value to specify legend entries and/or plot markers/colors, etc.
            print("any other key or just enter to continue")

            options = input("Enter options [multiple okay]: ")
            normalize = False
            if 'n' in options:
                normalize = True

            plot_light_curve(to_plot, normalize)
        elif plot_num == 2:
            print("")
            plot_concentration_curve(to_plot)
        else:
            break

def apply_filter(df, filter_num):
    print("")
    print("Filtering by ", end="")

    # find filter type
    filter_type = df.columns[filter_num]
    print(filter_type)

    # print out the options
    print("Options:")
    options = df[filter_type].unique().tolist()
    sorted_options = df[filter_type].unique().tolist()
    sorted_options.sort()

    if isinstance(options[0], str) and '' not in options:
        print("adding default to str")
        sorted_options.insert(0, '')
    if isinstance(options[0], int) or isinstance(options[0], float) and 0 not in options:
        print("adding default option to num")
        sorted_options.insert(0, 0)

    for i in range(len(sorted_options)):
            print("  [" + str(i) + "] "+ str(sorted_options[i]))

    while True:
        # prompt the user to select an option to filter
        prompt = "Enter " + filter_type + " [q to cancel]: "
        selection = input(prompt)

        # if user enters 'q', cancel
        if selection == 'q':
            return False, None, None

        # check if the entered id is in the list. if so, show the selected rows
        if selection in sorted_options:
            # find entries that fit this filter
            entries = df.loc[df[filter_type] == selection]

        else:
            try:
                selection_num = int(selection)
                options_index = options.index(sorted_options[selection_num])

                entries = df.loc[df[filter_type] == options[options_index]]
                selection = options[options_index]
            except ValueError:
                # if the selection could not be found, prompt user again
                print("Could not find " + filter_type + ": '" + selection + "'")
                print("Please try again.")
                continue

        # print a preview of the selected rows
        print("")
        print("Number of entries found: " + str(len(entries)))
        print("Preview of selected rows:")
        print(entries)

        # create string indicating what was filtered
        filter_id = filter_type + ": " + selection

        # return the selected entries, and the filter string
        return True, entries, filter_id


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
        directory = str(row[directory_col])
        file_name = str(row[file_col])
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

def plot_concentration_curve(df):
    # make plot fig
    fig, ax = plt.subplots()

    title_str = "Concentration curve\n"

    styles = [['r', 'o', 'Trial 1'],
              ['g', 'v', 'Trial 2'],
              ['b', 's', 'Trial 3'],
              ['k', '.', '']]

    for row in df.itertuples():
        # get the directory and file name from the dataframe
        directory = row[directory_col]
        file_name = row[file_col]
        conc = row[conc_col]

        # create file path
        file_path = path.join(DATA_DIR, directory, file_name)

        if file_path[:-4] != '.txt':
            file_path += '.txt'

        # read text file
        data = np.genfromtxt(file_path)

        # [color, marker type, marker size]
        trial_num = row[trial_col]
        plot_style = styles[(trial_num - 1) % len(styles)]

        # read and process data
        init_tot_lux = 0
        init_tot_pts = 0
        fin_tot_lux = 0
        fin_tot_pts = 0

        start_time = data[0, 0]
        end_time = data[-1, 0]
        print("processing file: " + file_name)
        print("start: " + str(start_time))
        print("end: " + str(end_time))
        print("num of data points: " + str(len(data[:, 0])))

        for i in range(len(data[:, 0])):
            t = float(data[i, 0]) # time stamp

            if t <= (start_time + MEAS_PERIOD):
                init_tot_lux += data[i, 1]
                init_tot_pts += 1
            if t >= (end_time - MEAS_PERIOD):
                print(t)
                fin_tot_lux += data[i, 1]
                fin_tot_pts += 1

        init_lux_avg = init_tot_lux / init_tot_pts
        fin_lux_avg = fin_tot_lux / fin_tot_pts
        delta_lux = fin_lux_avg - init_lux_avg
        print(str(conc) + ": " + str(delta_lux))

        plt.plot(conc, delta_lux, color=plot_style[0], marker=plot_style[1])

    ax.set_title(title_str)
    ax.set_xlabel("Concentration [mg/mL]")
    ax.set_ylabel("Change in lux")

    # set up legend
    for si in range(len(styles)-1):
        plt.plot([], [], color=styles[si][0], marker=styles[si][1], label=styles[si][2])

    ax.legend()
    plt.tight_layout()
    plt.show()

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

def pre_process(df):
    for ci in range(len(df.columns)):
        if isinstance(df.iloc[0, ci], str):
            df[df.columns[ci]] = df[df.columns[ci]].fillna("")
        if isinstance(df.iloc[0, ci], float) or isinstance(df.iloc[0, ci], int):
            df[df.columns[ci]] = df[df.columns[ci]].fillna(0)
        # if there is a column of dates, convert it to a string of format YYYY.MM.DD
        if isinstance(df.iloc[0, ci], pd.Timestamp):
            df[df.columns[ci]] = [date.strftime('%Y.%m.%d') for date in df[df.columns[ci]]]
    return df

main()
