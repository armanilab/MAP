import pandas as pd
import numpy as np
import sys
from os import path
import platform

DATA_DIR = "../../../../test_data/"

#TODO: known bug when file is reloaded -> need to wipe selected_list

class FileManager:
    def __init__(self):
        self.path = None
        self.log_file = None
        self.sample_file = None
        self.sample_sheet = ''

        if 'windows' in platform.system().lower():
            self.path_div = '\\' # for windows only
        else:
            self.path_div = '/' # for mac or linux

        #i initialize
        self.df = None
        self.sample_dict = None
        self.sample_df = None

        # load data and sample key from file
        # self.df = self.load_data_log(self.file)
        # self.sample_dict = self.load_sample_dict(self.file)

        self.selected_list = []

    def __str__(self):
        return 'File Manager object for file: ' + self.file

    def set_log_file(self, file):
        self.log_file = file
        print('Successfully set log file to: ' + self.log_file)

    def reset_selected_list(self):
        self.selected_list = []

    def set_sample_file(self, file, sample_sheet):
        self.sample_file = file
        self.path = file[:file.rfind(self.path_div)] + self.path_div # TODO: fix for windows

        print('Set new sample file: ' + str(self.sample_file))
        self.sample_sheet = sample_sheet
        print('Set new sample_sheet:' + str(self.sample_sheet))

    def load_data_log(self):
        print("Loading data from: " + self.log_file + "...")

        # read test log in to dataframe
        try:
            df = pd.read_excel(self.log_file, dtype='str')
            print("Successfully read excel file.")
            self.reset_selected_list()
        except:
            print("ERROR: Failed to read excel file.")
            return -1

        # check for required columns: file, directory, sample, magnet
        cols_found = [False, False, False, False]
        df.columns, cols_found[0] = self.__check_column(df.columns,
            'File', 'File Name',
            ['filename', 'file_name', 'file name', 'file', 'name'])
        df.columns, cols_found[1] = self.__check_column(df.columns,
            'Directory', 'Folder',
            ['directory', 'file directory', 'file_directory',
            'folder', 'file folder', 'file_folder',
            'location', 'file location', 'file_location'])
        df.columns, cols_found[2] = self.__check_column(df.columns,
            'Sample', 'Sample ID',
            ['sample', 'sampleid', 'sample id', 'sample_id'])
        df.columns, cols_found[3] = self.__check_column(df.columns,
            'Magnet', 'Magnet ID',
            ['magnet', 'magnetid', 'magnet id', 'magnet_id',
            'magnetic field', 'magnetic_field', 'magneticfield',
            'field', 'fieldid', 'field id', 'field_id'])

        # if one column wasn't found, exit with warning
        # TODO: how to exit?
        if False in cols_found:
            print("EXIT: Test log missing required column(s).")
            self.df = None
            return -1
        else:
            print("Found all required columns in test log.")
            # set all column names to be sentence case
            cols = []
            for c in df.columns:
                cols.append(self.__to_sentence_case(c))
            df.columns = cols
            self.df = df

            print(self.df.columns)
            return 0

    def load_sample_dict(self):
        sample_dict = {}
        print('Loading sample key...')
        print(self.sample_file)
        xl = pd.ExcelFile(self.sample_file)
        print(xl.sheet_names)

        try:
            # sample key must be named 'sample-key'
            print('Looking for sample sheet named: ' + self.sample_sheet + ' in file: ' + self.sample_file)
            df = pd.read_excel(self.sample_file, sheet_name=self.sample_sheet,
                dtype='str')
        except:
            print('ERROR: Failed to find a sample key.')
            self.sample_dict = None
            return -1

        # check dataframes for required columns
        cols_found = [False, False, False, False]
        df.columns, cols_found[0] = self.__check_column(df.columns,
            'Sample', 'ID', ['sample', 'sampleid', 'sample id', 'sample_id',
            'id', 'name', 'sample name', 'samplename', 'sample_name',
            'label', 'sample_label', 'sample label', 'samplelabel'])
        df.columns, cols_found[1] = self.__check_column(df.columns,
            'Material', 'Material ID',
            ['material', 'materialid', 'material_id', 'material id'])
        df.columns, cols_found[2] = self.__check_column(df.columns,
            'Solvent', 'Solvent Chemical',
            ['solvent', 'chemical',
            'solvent chemical', 'solvent_chemical', 'solventchemical'])
        df.columns, cols_found[3] = self.__check_column(df.columns,
            'Concentration', 'Conc',
            ['concentration', 'conc', 'nanoparticle concentration',
            'mnp concentration', 'nanoparticle_concentration',
            'mnp_concentration'])

        print(cols_found)
        print(df.columns)

        # TODO: how to exit?
        if False in cols_found:
            print("EXIT: Sample log missing required column(s).")
            self.sample_dict = None
            return -1

        print("Found all required columns in sample log.")

        # convert to sentence case
        cols = []
        for c in df.columns:
            cols.append(self.__to_sentence_case(c))
        df.columns = cols

        # set index to sample labels (which will be keys in the sample dict)
        df.set_index('Sample', inplace=True)

        # make a dict from the dataframe
        sample_dict = df.to_dict(orient='index')

        self.sample_df = df
        self.sample_dict = sample_dict
        self.merge_df()
        return 0

    def merge_df(self):
        print('Merging sample dataframe....')
        self.df = self.df.merge(self.sample_df, on='Sample', how='left')
        print('Successfully merged!')
        print('new dataframe:')
        print(self.df)

    def get_df(self):
        return self.df

    def get_sample_dict(self):
        return self.sample_dict

    def __check_column(self, cols, name, alt_name, possible_names):
        # make all columns lowercase to avoid dealing with different cases
        # strip all excess whitespace
        cols = [c.strip().lower() for c in cols]

        for n in possible_names:
            if n in cols:
                cols[cols.index(n)] = name
                return cols, True

        # failed to find required column
        print('ERROR: Log file missing required column: ' + name)
        print('Maybe it is misnamed? Column name should be: ' + name +
            ' or ' + alt_name)

        return cols, False

    def __to_sentence_case(self, s):
        return s[0].upper() + s[1:]

    def get_col_names(self):
        """Return names of all columns or -1 if no log file has been loaded"""
        if self.df is None:
            return -1

        return self.df.columns

    # cols is a list of columns
    def get_file_df(self, cols):
        if self.df is None:
            return None
        else:
            return self.df[cols]

    def add_to_selected_list(self, index):
        """Adds a given index of the df to the list of files that have been selected"""
        if index not in self.selected_list:
            self.selected_list.append(index)

    def remove_from_selected_list(self, index):
        """Removes a given index of the df to the list of files that have been selected"""
        if index in self.selected_list:
            self.selected_list.remove(index)

    def get_selected_list(self):
        return self.selected_list

    def get_selected_df(self, cols):
        """Returns only the dataframe of the files that have been selected,
           as specified from the self.selected_list variable.

           Keyword arguments:
           cols - the dataframe columns that should be included
           """
        if self.df is None:
            return None

        print(self.df.iloc[self.selected_list][cols])
        return self.df.iloc[self.selected_list][cols]

    def get_row(self, row, cols=None):
        if cols is None:
            cols = self.df.columns
        return self.df.iloc[int(row)][cols]

    def get_file_name(self, row):
        return self.df.iloc[int(row)]['File']

    def load_file(self, index, preprocess=False):
        """Returns the data from the file for a given row

        Keyword arguments:
        index - the index of the desired file
        preprocess - if additional pre-processing should be done on the file to
                     correct for MAP writing errors (defualt: True)
        """

        print('loading file for index: ' + str(index))
        row = self.df.iloc[int(index)]
        print(row)
        dir = row['Directory']
        if dir[-1] != self.path_div:
            dir += self.path_div

        file_path = self.path + row['Directory']

        file_name = row['File']
        if file_name [-4:] != '.txt':
            file_name += '.txt'

        data = np.genfromtxt(file_path + file_name)

        if preprocess:
            print('todo: implement pre-processing')

        print(data[0:5, :])
        return data
