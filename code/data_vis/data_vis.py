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
from statistics import mean


# IMPORTANT VARIABLES
DATA_DIR = "../../../../test_data/"
BASELINE_PTS = 100 # number of datapoints used for baseline
CONC_PTS = 100 # number of datapoints averaged to calculate change in light transmission for concentration curve
# in the log of data files, the first two columns MUST be the file name and
# relative path to file (from the location of the log file).
file_col = 1
directory_col = 2

trial_col = 8
conc_col = 12

MEAS_PERIOD = 10 # number of seconds to average to get light transmission measurement

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

def main():
    ### SETUP ###
    # read in test log and sample key

    # check for correct number of arguments
    if len(sys.argv) < 2:
        print("ERROR: Not enough arguments.")
        print("Correct usage:")
        print("$ python3 data_vis.py <xlsx_file_path>")
        print("")
        file = input("Please enter the file path for the log file: ")
    else:
        # parse arguments
        file = sys.argv[1]

    df, sample_dict = load_data_log(file)

    to_plot = df.index.to_list() # track indices in the original dataframe of the files to plot
    current_filters = []

    #### FILE SELECTION STEP ###
    # apply filter to select specific files
    while True:
        # print selection options for filters
        # all columns are possible filters
        # filter numbers start at 1 for user convenience

        print("Filter options: [select via number]")
        for i in range(len(df.columns)):
            print("[" + str(i + 1) + "] " + str(df.columns[i]))
        print("[q] to quit")
        print("[r] to reset all filters")
        #print("Optional flags:")
        #print("-add to add to previous selection")
        #print("-rm to remove from previous selection")
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
        found, filtered_df, filter_label = apply_filter(df, to_plot, filter_num)

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

    ### PLOT SELECTION###
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

            plot_light_curve(df, sample_dict, to_plot, baseline_correction, no_legend, extra_big)
        elif plot_num == 2:
            plot_concentration_curve(df, sample_dict, to_plot)
        elif plot_num == 3:
            extra_stats = False
            if '-stats' in user_selection:
                extra_stats = True

            plot_reproducible(to_plot, extra_stats)
        else:
            print("Could not parse input. Please try again.")


def apply_filter(df, indices, filter_num):
    # create dataframe of current selection
    df = df.loc[indices]

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
            entries = df.loc[df[filter_type] == selection].index.to_list()

        else:
            try:
                selection_num = int(selection)
                options_index = options.index(sorted_options[selection_num])

                # get indices of the selected values where the selected filter
                # (filter_type) matches the selected value from the shown
                # list (options[options_index])
                entries = df.loc[df[filter_type] == options[options_index]].index.to_list()
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
        for e in entries:
            print(str(e) + ": " + df.loc[e]['File-name'])

        # create string indicating what was filtered
        filter_id = filter_type + ": " + selection

        # return the selected entries, and the filter string
        return True, entries, filter_id

def load_data_log(file):
    # read test log in to dataframe
    df = pd.read_excel(file, dtype='str')

    # read sample key
    # dictionary will contain sample info where the key is a sample label/name
    sample_dict = {}
    try:
        # assume that the sample key will be named 'sample-key'
        df_samples = pd.read_excel(file, sheet_name='sample-key', dtype='str')
        # set index to sample label (will be keys in sample_dict)
        df_samples.set_index('ID', inplace=True)
        sample_dict = df_samples.to_dict(orient='index') # make the dict
    except:
        print("Failed to find a sample key.")
        # TODO: actually handle this

    # process data
    df = pre_process(df, sample_dict)

    return df, sample_dict


#TODO: needs to be fixed since load_data was written
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

def pre_process(df, sample_dict):
    # sort data by date, system, sample, magnet, trial number
    df = df.sort_values(by=['Date', 'System', 'Sample', 'Magnet', 'Trial-num'])

    # ignore two columns (daily-num and user which are just record-keeping)
    df = df.drop(columns=['Daily-num', 'User'])

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

def load_data(df, sample_dict, selection):
    data_dict = {} # the dict with all file data that will be returned
    #DEBUG
    print("in load data")
    print("selection: ")
    print(selection)
    for i in selection:
        print("i: " + str(i))
        file_dict = {}

        # select row from the original log/dataframe
        row = df.loc[i]
        print(row)
        print("")

        # get directory and file name info
        directory = row['File-location']
        file_name = row['File-name']

        # create file path
        file_path = path.join(DATA_DIR, directory, file_name)

        # add .txt if not already at end of file path
        if file_path[:-4] != '.txt':
            file_path += '.txt'

        # read data file
        data = np.genfromtxt(file_path)

        # create dictionary for this file
        file_dict['file-path'] = file_path
        file_dict['time_data'] = data[:, 0]
        file_dict['lux_data'] = data[:, 1]

        # get info from the log
        file_dict['trial'] = row['Trial-num']
        file_dict['system'] = row['System']
        file_dict['magnet'] = row['Magnet']
        file_dict['sample'] = row['Sample'] # sample label

        # get info about the sample
        sample = sample_dict[file_dict['sample']] # get info for this sample

        # store sample info
        file_dict['concentration'] = sample['Concentration']
        file_dict['mnp'] = sample['MNP']
        file_dict['batch-date'] = sample['Batch-date']
        file_dict['solvent'] = sample['Solvent']

        # add to full data_dict using file name as key
        data_dict[file_name] = file_dict
        print("loaded i = " + str(i) + ": "+ file_name)

    return data_dict

def plot_light_curve(df, sample_dict, selection, baseline_correction=False, no_legend=False, extra_big=False):
    #fig = plt.figure()
    fig, ax = plt.subplots()

    # load selected data from dataframe
    data_dict = load_data(df, sample_dict, selection)

    # set title of plot
    title = input("Enter plot title (leave blank for default): ")
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
        print(str(curve_index) + ": " + file)

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
        plt.plot(t, l, label=file, linewidth=line_width, color=line_color) # TODO: add label

        curve_index += 1

    ax.set_title(title)

    # set axes label
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Light [lux]")

    # TODO: add legend
    if not no_legend:
        ax.legend()
    plt.tight_layout()
    plt.show()

# TODO: a work in progress but do i like this setup? questionable
def set_legend_format():
    print("What should be in the legend?")
    print("Use short form [captial letter] options for shorter entries")
    print("  [sys/S] System")
    print("  [con/C] Concentration")
    print("  [mag/M] Magnet")
    print("  [tri/T] Trial number")
    legend_format = input("Enter selection(s) separated by spaces: ")

    legend = ['', '', '', '', '', '', '', '']

    legend_splits = legend_format.split()
    i = 0
    for li in legend_splits:
        if li == 'sys':
            legend[i] = 'System: '
            legend[i + 1] = 'system'
        elif li == 'S':
            legend[i + 1] = 'system'
        elif li == 'con':
            legend[i] = 'Concentration [mg/mL]: '
            legend[i + 1] = 'concentration'
        elif li == 'C':
            legend[i + 1] = 'concentration'
        elif li == 'mag':
            legend[i] = 'Magnet: '
            legend[i + 1] = 'magnet'
        elif li == 'M':
            legend[i + 1] = 'magnet'
        elif li == 'tri':
            legend[i] = 'Trial #'

def plot_concentration_curve(df, sample_dict, selection):
    # make figure
    fig, ax = plt.subplots()

    # load selected data from dataframe
    data_dict = load_data(df, sample_dict, selection)

    colors = [colors_list[1], colors_list[6], colors_list[11], colors_list[0]]
    markers = ['o', 'v', 's', 'P']

    # set title of plot
    title = input("Enter plot title (leave blank for default): ")
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
        final_lux = mean(l[-CONC_PTS:])
        delta_lux = final_lux - init_lux

        trial = int(file_data['trial'])
        conc = float(file_data['concentration'])

        f_color = colors[trial - 1]
        f_marker = markers[trial - 1]

        plt.plot(conc, delta_lux, color=f_color, marker=f_marker)

    # set up legend
    for si in range(len(colors)):
        plt.plot([], [], color=colors[si], marker=markers[si], label=("Trial " + str(si + 1)))

    ax.set_title(title)
    ax.set_xlabel("Concentration [mg/mL]")
    ax.set_ylabel("Change in light [lux]")

    ax.legend()
    plt.show()


main()
