import pandas as pd
import numpy as np
import sys
from os import path

DATA_DIR = "../../../../test_data/"

class FileManager:
    def __init__(self, file, preprocess=True):
        # initialize the FileManager by loading the test file
        self.file = file

        # load data and sample key from file
        self.df = self.load_data_log(self.file)

    def __str__(self):
        return 'File Manager object for file: ' + self.file

    def load_data_log(self, file):
        print("Loading data from: " + file + "...")

        # read test log in to dataframe
        try:
            df = pd.read_excel(file, dtype='str')
            print("Successfully read excel file.")
        except:
            print("ERROR: Failed to read excel file.")

        # check for required columns: file, directory, sample, magnet
        cols_found = [True, True, True, True]
        df.columns, cols_found[0] = self.__check_column(df.columns, 'File', 'File Name',
            ['filename', 'file_name', 'file name', 'file', 'name'])
        df.columns, cols_found[1] = self.__check_column(df.columns, 'Directory', 'Folder',
            ['directory', 'file directory', 'file_directory',
            'folder', 'file folder', 'file_folder',
            'location', 'file location', 'file_location'])
        df.columns, cols_found[2]= self.__check_column(df.columns, 'Sample', 'Sample ID',
            ['sample', 'sampleid', 'sample id', 'sample_id'])
        df.columns, cols_found[3] = self.__check_column(df.columns, 'Magnet', 'Magnet ID',
            ['magnet', 'magnetid', 'magnet id', 'magnet_id',
            'magnetic field', 'magnetic_field', 'magneticfield',
            'field', 'fieldid', 'field id', 'field_id'])

        # if one column wasn't found, exit with warning
        # TODO: how to exit?
        if False in cols_found:
            print("EXIT: Missing required column(s).")
            return None
        else:
            print("Found all required columns")
            return df

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
