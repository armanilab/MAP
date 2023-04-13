# Launches the data analysis pipeline
# Lexie Scholtz
# Created: 2022.12.27

import sys
from os import path
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
import pandas as pd
import math


# IMPORTANT VARIABLES
DATA_DIR = "../../../../test_data/"
# in the log of data files, the first two columns MUST be the file name and
# relative path to file (from the location of the log file).
file_col = 1
directory_col = 2

trial_col = 8
conc_col = 12

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

    df = pd.read_excel(file, dtype='str')
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
        print("Optional flags:")
        print("-add to add to previous selection")
        print("-rm to remove from previous selection")
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
        print("  [-bc] baseline correction")
        print("  [-nl] no legend")
        print("  [-xbig] extra big text")
        print("[2] Concentration vs. change in light")
        print("[3] Light change vs. file number")
        print("  [-stats] add average and standard deviation")
        print("[b] to go back")
        print("Any other key to end program")

        user_selection = input("Enter plot number with flags, if any: ")

        # parse output
        user_selection = user_selection.split()
        if user_selection[0] == 'q':
            break

        # if user_selection[0] == 'b':
        #     break

        try:
            plot_num = int(user_selection[0])
        except:
            print("Could not determine plot number. Please enter an int.")
            continue

        if plot_num == 1:
            baseline_correction = False
            if '-bc' in user_selection:
                baseline_correction = True
            no_legend = False
            if '-nl' in user_selection:
                no_legend = True
            extra_big = False
            if '-xbig' in user_selection:
                extra_big = True

            plot_light_curve(to_plot, baseline_correction, no_legend, extra_big)
        elif plot_num == 2:
            plot_concentration_curve(to_plot)
        elif plot_num == 3:
            extra_stats = False
            if '-stats' in user_selection:
                extra_stats = True

            plot_reproducible(to_plot, extra_stats)
        else:
            print("Could not parse input. Please try again.")


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
def plot_light_curve(df, baseline_correction=False, no_legend=False, extra_big=False):
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
        print("plotting " + file_name)
        data = np.genfromtxt(file_path)

        # TODO: change this out of hard coded later
        magnet = row[6]
        trial_num = row[7]
        #row_label = str(magnet) + '\" magnet, trial #' + str(trial_num)
        row_label = file_name

        x = data[:, 0]
        y = data[:, 1]

        if baseline_correction:
            total_l = 0
            total_pts = 0
            for i in range(len(data[:, 0])):
                t = data[i, 0]
                if t >= 0 and t <= 15:
                    if np.isnan(data[i, 1]):
                        total_l += 0
                    else:
                        total_l += data[i, 1]
                    total_pts += 1
            baseline = total_l / total_pts
            y = y - baseline
            # add label to title

        if extra_big:
            plt.plot(x, y, label=row_label, linewidth=5)
        else:
            plt.plot(x, y, label=row_label)

    if baseline_correction:
        title_str += "baseline corrected"

    if extra_big:
        ax.xaxis.label.set_size(20)
        ax.xaxis.set_tick_params(width=3.5, length=8)
        ax.yaxis.label.set_size(20)
        ax.yaxis.set_tick_params(width=3.5, length=8)
        [x.set_linewidth(3.5) for x in ax.spines.values()]

        #mpl.rcParams['axes.linewidth'] = 5
        plt.xticks([0, 100, 200, 300, 400, 500, 600], labels=[], fontsize=16)
        plt.yticks([0, 10000, 20000, 30000, 40000], labels = [], fontsize=16)
    else:
        ax.set_title(title_str)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Lux")

    if not no_legend:
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
        plot_style = styles[(int(trial_num) - 1) % len(styles)]

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

def plot_reproducible(df, extra_stats=False):
    df_data = []

    # process files
    for row in df.itertuples():
        # get the directory and file name from the dataframe
        directory = row[directory_col]
        file_name = row[file_col]
        conc = row[conc_col]
        trial_num = row[trial_col]

        # create file path
        file_path = path.join(DATA_DIR, directory, file_name)

        # append .txt if necessary
        if file_path[:-4] != 'txt':
            file_path += '.txt'

        # read text file
        print("processing file: " + file_name)
        data = np.genfromtxt(file_path)
        # read and process data
        delta_lux, start_lux, end_lux = calculate_concentration(data)

        df_data.append([trial_num, delta_lux, start_lux, end_lux])

    print(df_data) #to do make this nicer

    if extra_stats:
        # calculate mean and standard deviation of deltas
        sum_deltas = 0
        deltas = []
        num_deltas = len(df_data)
        for data_pt in df_data:
            delta = data_pt[1]
            deltas.append(delta)
            sum_deltas += delta
        avg_delta = sum_deltas / num_deltas

        sum_dev = 0
        for d in deltas:
            sum_dev += (avg_delta - d) ** 2
        std_dev_delta = (sum_dev / num_deltas) ** (0.5)

        print("Mean: %f" % avg_delta)
        print("Std. dev: %f" % std_dev_delta)

    # make plot
    fig, ax = plt.subplots()
    try:
        title_str = "Reproducibility plot\nConcentration: %0.6f mg/mL" % conc
    except:
        title_str = "Reproducibility plot"
    # TODO: plot mean as line and std dev as faded rectangle
    if extra_stats:
        rec_bottom = avg_delta - std_dev_delta
        rec_top = avg_delta + std_dev_delta

        plt.plot([0, len(df_data)+1], [avg_delta, avg_delta], color='orangered', label="Average change in lux")
        ax.add_patch(Rectangle((0, rec_bottom), len(df_data)+1, 2*std_dev_delta,
            fill=True, color='orangered', alpha=0.3))

    for file in df_data:
        [trial_num, delta_lux, start_lux, end_lux] = file
        plt.plot([trial_num, trial_num], [start_lux, end_lux], color='gainsboro')
        plt.plot(trial_num, delta_lux, marker='o', color='dodgerblue')

    # make legend entries
    plt.plot([], [], color='gainsboro', label="Range of lux values")
    plt.plot([], [], color='dodgerblue', marker='o', label="Change in lux")
    ax.legend()

    ax.set_title(title_str)
    ax.set_xlabel("Trial number")
    ax.set_ylabel("Change in lux")

    # TODO: FIX THE AXES LIMITS
    ax.set_xlim([0, len(df)+1])
    plt.show()

def calculate_concentration(data):
    init_tot_lux = 0
    init_tot_pts = 0
    fin_tot_lux = 0
    fin_tot_pts = 0

    start_time = data[0, 0]
    end_time = data[-1, 0]

    for i in range(len(data[:, 0])):
        t = float(data[i, 0]) # time stamp

        if t <= (start_time + MEAS_PERIOD):
            init_tot_lux += data[i, 1]
            init_tot_pts += 1
        if t >= (end_time - MEAS_PERIOD):
            fin_tot_lux += data[i, 1]
            fin_tot_pts += 1

    init_lux_avg = init_tot_lux / init_tot_pts
    fin_lux_avg = fin_tot_lux / fin_tot_pts
    delta_lux = fin_lux_avg - init_lux_avg
    return delta_lux, init_lux_avg, fin_lux_avg

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
        df[df.columns[ci]] = df[df.columns[ci]].fillna("")
        # if isinstance(df.iloc[0, ci], str):
        #     df[df.columns[ci]] = df[df.columns[ci]].fillna("")
        # if isinstance(df.iloc[0, ci], float) or isinstance(df.iloc[0, ci], int):
        #     df[df.columns[ci]] = df[df.columns[ci]].fillna(0)
        # if there is a column of dates, convert it to a string of format YYYY.MM.DD
        if isinstance(df.iloc[0, ci], pd.Timestamp):
            df[df.columns[ci]] = [date.strftime('%Y.%m.%d') for date in df[df.columns[ci]]]

    # make label column strings (fix out of hardcoding later)
    if 'Label' in df.columns:
        df['Label'] = [str(x) for x in df['Label']]
    elif 'Sample' in df.columns:
        df['Sample'] = [str(x) for x in df['Sample']]
    df.fillna("")
    return df

main()
