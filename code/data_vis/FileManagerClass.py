import pandas as pd
import numpy as np

class FileManager:
    def __init__(self, file, preprocess=True):
        self.file = file
        # load data log and sample key from file
        self.df, self.sample_dict = self.load_data_log(self.file)
        # preprocess data
        if preprocess:
            self.df = self.pre_process(self.df)

        self.plot_list = [] # initialize to_plot list as empty list

    # read in the excel data log file, preprocess it,
    def load_data_log(self, file):
        # read test log in to dataframe
        df = pd.read_excel(file, dtype='str')

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

    # arguments:
    #   files - a list of files to be added to the plot_list
    def add_to_plot_list(self, files):
        for f in files:
            if f not in self.plot_list:
                self.plot_list.append(int(f))

    # arguments:
    #   files - a list of files to be removed from the plot_list
    def remove_from_plot_list(self, files):
        for f in files:
            if f in self.plot_list:
                self.plot_list.remove(int(f))

    def get_plot_list(self):
        return self.plot_list
