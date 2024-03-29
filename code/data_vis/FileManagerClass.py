import pandas as pd
import numpy as np
import sys
from os import path

DATA_DIR = "../../../../test_data/"

class FileManager:
    def __init__(self, file, preprocess=True):
        self.file = file
        # load data log and sample key from file
        self.df, self.sample_dict = self.load_data_log(self.file)
        # preprocess data
        if preprocess:
            self.df = self.pre_process(self.df)

        self.selected_list = [] # initialize to_plot list as empty list
        self.filtered_list = self.df.index.to_list()
        self.analyzed_files = {}

        # user indices
        # TODO: eventually, set these in a menu when file is imported
        self.file_loc_index = 1
        self.tree_col_start = 1
        self.tree_col_end = -2

    # read in the excel data log file, preprocess it,
    def load_data_log(self, file):
        print("loading data...")
        # read test log in to dataframe
        df = pd.read_excel(file, dtype='str')
        print("succesfully read excel file...")

        # read sample key
        # dictionary will contain sample info where the key is a sample label/name
        sample_dict = {}
        try:
            # assume that the sample key will be named 'sample-key'
            df_samples = pd.read_excel(file, sheet_name='sample-key', dtype='str')
            # set index to sample label (will be keys in sample_dict)
            df_samples.set_index('Label', inplace=True)
            sample_dict = df_samples.to_dict(orient='index') # make the dict
        except:
            print("Failed to find a sample key.")
            # TODO: actually handle this

        return df, sample_dict

    def get_df(self):
        return self.df

    def get_sample_dict(self):
        return self.sample_dict

    #TODO: does this actually need the sample dict?
    def pre_process(self, df):
        # sort data by date, system, sample, magnet, trial number
        df = df.sort_values(by=['Date', 'System', 'Sample', 'Magnet', 'Trial-num'])

        # ignore two columns (daily-num and user which are just record-keeping)
        df = df.drop(columns=['Daily-num', 'User'])

        # for ci in range(len(df.columns)):
        #     df[df.columns[ci]] = df[df.columns[ci]].fillna("")
            # if isinstance(df.iloc[0, ci], str):
            #     df[df.columns[ci]] = df[df.columns[ci]].fillna("")
            # if isinstance(df.iloc[0, ci], float) or isinstance(df.iloc[0, ci], int):
            #     df[df.columns[ci]] = df[df.columns[ci]].fillna(0)
            # if there is a column of dates, convert it to a string of format YYYY.MM.DD
            # if isinstance(df.iloc[0, ci], pd.Timestamp):
            #     df[df.columns[ci]] = [date.strftime('%Y.%m.%d') for date in df[df.columns[ci]]]

        # make label column strings (fix out of hardcoding later)
        if 'Label' in df.columns:
            df['Label'] = [str(x) for x in df['Label']]
        elif 'Sample' in df.columns:
            df['Sample'] = [str(x) for x in df['Sample']]
        df.fillna("")
        return df

    def load_data(self):
        data_dict = {} # the dict with all file data that will be returned
        #DEBUG
        for i in self.selected_list:
            #print("i: " + str(i))
            file_dict = {}

            # select row from the original log/dataframe
            row = self.df.loc[i]
            #print(row)
            #print("")

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
            file_dict['file_name'] = file_name
            file_dict['file_path'] = file_path
            file_dict['time_data'] = data[:, 0]
            file_dict['lux_data'] = data[:, 1]

            # get info from the log
            file_dict['trial'] = row['Trial-num']
            file_dict['system'] = row['System']
            file_dict['magnet'] = row['Magnet']
            file_dict['sample'] = row['Sample'] # sample label
            file_dict['date'] = row['Date']

            # get info about the sample
            sample = self.sample_dict[file_dict['sample']] # get info for this sample

            # store sample info
            file_dict['concentration'] = sample['Concentration']
            file_dict['mnp'] = sample['MNP']
            file_dict['batch-date'] = sample['Batch-date']
            file_dict['solvent'] = sample['Solvent']

            # add to full data_dict using file name as key
            data_dict[i] = file_dict
            print("loaded i = " + str(i) + ": "+ file_name)

        return data_dict

    # arguments:
    #  [int] file_index - the index of a file to be added to the selected_list
    def add_to_selected_list(self, file_index):
        if file_index not in self.selected_list:
            self.selected_list.append(file_index)

    # arguments:
    #   [int] file_index - the index of a file to be removed from the selected_list
    def remove_from_selected_list(self, file_index):
        if file_index in self.selected_list:
            self.selected_list.remove(file_index)

    # returns the to_selected_list (indices of files to be plotted)
    def get_selected_list(self):
        return self.selected_list

    def get_tree_cols(self):
        return self.df.columns[self.tree_col_start:self.tree_col_end]

    def get_file_loc_col(self):
        return self.df.columns[self.file_loc_index]

    # apply a filter to the dataframe
    # arguments:
    #
    def filter_df(self, filter_type=None, filter_selection=None):
        # if no filter is passed, then it is the unfiltered df
        if filter_type == None:
            self.filtered_list = self.df.index.to_list()
        else:
            entries = self.df.loc[self.df[filter_type] == filter_selection]
            self.filtered_list = entries.index.to_list()

    def get_filter_options(self, filter_type):
        filter_options = self.df[filter_type].fillna("")
        return filter_options.unique().tolist()

    # returns the filtered list
    def get_filtered_list(self):
        return self.filtered_list

    def get_tree_row(self, row_index):
        row = self.df.loc[row_index]
        row_text = row['File-name']
        # TODO: set nan to ""
        row_value = tuple(row[self.tree_col_start:self.tree_col_end].fillna(""))
        return row_text, row_value

    def update_analyzed_files(self):
        for file_index in self.selected_list:
            if file_index in self.analyzed_files.keys():
                # TODO: add a check where if the test settings are the same
                # if so, do nothing
                continue
            else:
                # eventually, the second item in this list should be a list of test settings for comparison
                file_name = self.df.at[file_index, 'File-name']
                self.analyzed_files[file_index] = [file_name, None, None]

    def add_analysis_results(self, file_index, file_name, results, test_info):
        self.analyzed_files[file_index] = [file_name, results, test_info]

    def get_analyzed_files(self):
        self.update_analyzed_files()
        return self.analyzed_files

    # group the files in the selected files list
    def group_files(self):
        print('Sorting and grouping data files...')
        # Q: do i actually need to do this step??
        # sort the data given
        sorted_data_dict = sorted(self.data_dict.items(),
            key=lambda x: (x[1]['sample'], x[1]['concentration'],
                x[1]['magnet'], x[1]['date'], x[1]['trial']))
        #print(type(sorted_data_dict))
        #print(sorted_data_dict)
        # a list where is each entry is a tuple: (file_name, dict)

        file_groups = {}
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
                file_groups[f_key] = []

            file_groups[f_key].append(file_name)
