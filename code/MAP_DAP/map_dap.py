# MAP-DAP: MAgnetoPhotometer Data Analysis Program
#
# Written by: Lexie Scholtz
#             Jack Paulson
#
# Last Updated: 2025.01.09


import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import numpy as np
from FileManagerClass import FileManager
import map_dap_formats as mdf
# from MAPPlotter import Plotter
# from MAPAnalyzer import Analyzer

import matplotlib
matplotlib.use('TkAgg')
# to embed the plot
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# default Matplotlib key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from datetime import datetime

DATA_DIR = "../../../../test_data/"

class MapDAP:
    def __init__(self):
        # create the main window
        self.root = tk.Tk()
        self.root.title("MAP-DAP")
        self.root.geometry("1000x800")
        self.root.columnconfigure(0, weight=1) # vertical rescaling
        self.root.rowconfigure(0, weight=1) # horizontal rescaling

        style = ttk.Style()
        style.theme_use('aqua')
        style.configure('TButton', font=mdf.text_font, foreground='black')
        style.configure('TLabel', font=mdf.text_font)
        style.configure('TCheckbutton', font=mdf.text_font)
        style.configure('TEntry', font=mdf.text_font)

        self.fm = FileManager()

        # --- SETUP PAGE ---
        # variables for setup page
        self.log_file_var = tk.StringVar(self.root, 'No file selected')
        self.log_file_fullpath = ''
        self.log_file_status_var = tk.StringVar(self.root, 'Unloaded')

        self.sample_from_log = tk.BooleanVar(value=True)
        self.sample_file_fullpath = ''
        self.sample_sheet_var = tk.StringVar(self.root, 'samples')
        self.sample_file_var = tk.StringVar(self.root, 'No file selected')
        self.sample_status_var = tk.StringVar(self.root, 'Unloaded')

        # --- NOTEBOOK ---
        # set up notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill='both')

        # set up pages of the notebook
        # setup page - log file selection, other major parameters
        self.setup_page = ttk.Frame(self.notebook, padding="3 3 12 12")
        self.notebook.add(self.setup_page, text='Setup')
        self.create_setup_page()


    def run(self):
        self.root.mainloop()

    def create_setup_page(self):
        self.setup_label = ttk.Label(self.setup_page, text='SETUP',
            anchor='w')
        self.setup_label.configure(font=mdf.title_font)
        self.setup_label.grid(row=0, column=0)

        # to do: fix columns of each frame at some point

        # --- LOG FILE ---
        self.log_frame = ttk.Frame(self.setup_page)
        self.log_frame.grid(row=1, column=0, sticky='wens', pady=20)
        for i in range(8):
            self.log_frame.columnconfigure(i, weight=1)

        # log file section label
        self.log_sec_label = ttk.Label(self.log_frame, text='Test Log',
            font=mdf.heading1_font)
        self.log_sec_label.grid(row=0, column=0, sticky='w', padx=20)

        # log file select button
        self.select_log_button = ttk.Button(self.log_frame, text='Select',
            command=self.select_log_file)
        self.select_log_button.grid(row=1, column=1, sticky='e')

        # log file load button
        self.log_load_button = ttk.Button(self.log_frame, text='Load',
            command=self.load_log_file)
        self.log_load_button.grid(row=1, column=2, sticky='e')

        # log file preview button
        self.log_preview_button = ttk.Button(self.log_frame, text='Preview',
            command=self.preview_log)
        self.log_preview_button.grid(row=1, column=3, sticky='e')

        # log file file 'name' label
        self.log_file_label = ttk.Label(self.log_frame, text='File: ',
            font=mdf.bold_font)
        self.log_file_label.grid(row=2, column=1, sticky='w')

        # log file actual name of file
        self.log_label = ttk.Label(self.log_frame, text=self.log_file_var.get())
        self.log_label.grid(row=2, column=2, columnspan=3, sticky='w')

        # log file status label
        self.log_file_status_static_label = ttk.Label(self.log_frame,
            text='Status: ', font=mdf.bold_font)
        self.log_file_status_static_label.grid(row=2, column=5, sticky='w',
            padx=(20, 0))

        # log file actual status label
        self.log_file_status_label = ttk.Label(self.log_frame,
            text=self.log_file_status_var.get())
        self.log_file_status_label.grid(row=2, column=6, columnspan=2,
            sticky='w')

        # --- SAMPLE FILE ---
        self.sample_frame = ttk.Frame(self.setup_page)
        self.sample_frame.grid(row=2, column=0, sticky='wens', pady=20)

        for i in range(6):
            self.sample_frame.columnconfigure(i, weight=1)

        # sample file section label
        self.sample_sec_label = ttk.Label(self.sample_frame,
            text='Samples', font=mdf.heading1_font)
        self.sample_sec_label.grid(row=0, column=0, sticky='w', padx=20)

        # sample file select button
        self.select_sample_button = ttk.Button(self.sample_frame,
            text='Select', command=self.select_sample_dict)
        self.select_sample_button.grid(row=1, column=1, sticky='e')

        # sample dict checkbox: from log file
        self.from_log_file_checkbox = ttk.Checkbutton(self.sample_frame,
            text='load from log file', variable=self.sample_from_log)
        self.from_log_file_checkbox.grid(row=2, column=1, columnspan=2,
            sticky='w')

        # sample dict sheet name label
        self.sheet_name_label = ttk.Label(self.sample_frame,
            text='Sheet name: ', font=mdf.bold_font)
        self.sheet_name_label.grid(row=2, column=3, sticky='w')

        # sample dict text field
        self.sample_sheet_entry = ttk.Entry(self.sample_frame,
            textvariable=self.sample_sheet_var)
        self.sample_sheet_entry.grid(row=2, column=4, columnspan=2,
            sticky='we')

        # sample dict file label
        self.sample_file_label = ttk.Label(self.sample_frame, text='File:')
        self.sample_file_label.grid(row=3, column=1, sticky='w')

        # sample dict file
        self.sample_file_name_label = ttk.Label(self.sample_frame,
            text=self.sample_file_var.get())
        self.sample_file_name_label.grid(row=3, column=2, columnspan=3,
            sticky='w')

        # TODO: link sample dict to log file selection

        # --- MAGNETS LIBRARY ---
        self.magnet_frame = ttk.Frame(self.setup_page)
        self.magnet_frame.grid(row=3, column=0, sticky='wens', pady=20)

        # magnets file section label
        self.magnet_sec_label = ttk.Label(self.magnet_frame,
            text='Magnets', font=mdf.heading1_font)
        self.magnet_sec_label.grid(row=0, column=0, sticky='w', padx=20)

        # magnet file select button


    def select_log_file(self):
        filetypes = (
            ('Excel files', '*.xlsx'),
            ('csv files', '*.csv'),
            ('text files', '*.txt'),
            ('all files', '*.*')
        )

        selected_file = tk.filedialog.askopenfilename(title='Select Log File',
            initialdir='./', filetypes=filetypes)
        if selected_file == '':
            return

        shortened_path = self.__shorten_path(self.log_file_fullpath)

        self.log_file_fullpath = selected_file
        self.fm.set_log_file(self.log_file_fullpath)
        print(self.log_file_fullpath)

        # shorten full path for display and update label
        self.log_file_var.set(shortened_path)
        self.log_label.configure(text=self.log_file_var.get())
        print('Selected :' + self.log_file_var.get())

        # automatically load selected file
        self.load_log_file()

        # if checkbox for loading sample dict from same file is checked:
        # set the sample dict file as well
        if self.sample_from_log.get():
            self.set_sample_file(selected_file)

    def __shorten_path(self, path):
        # show less than the last n characters, but cut it off at the first
        # full directory name and prepend ....
        n = 50
        return '...' + path[-n:][path[-n:].find('/'):]

    def load_log_file(self):
        # TOOD: add actual file loading process
        is_loaded = self.fm.load_data_log()
        if is_loaded == 0:
            print('successfully loaded')

            # update the status
            status_str = 'Loaded at ' + \
                datetime.now().strftime('%m/%d/%y %H:%M:%S')
            self.log_file_status_var.set(status_str)
        else:
            print('error in loading log file')
            status_str = 'Error: code ' + str(is_loaded)

        print(status_str)
        self.log_file_status_label.configure(
            text=self.log_file_status_var.get())

    def preview_log(self):
        print("todo: implement preview log file")

    def select_sample_dict(self):
        filetypes = (
            ('Excel files', '*.xlsx'),
            ('csv files', '*.csv'),
            ('text files', '*.txt'),
            ('all files', '*.*')
        )

        selected_file = tk.filedialog.askopenfilename(
            title='Select Sample File', initialdir='./', filetypes=filetypes)
        if selected_file == '':
            return

        self.set_sample_file(selected_file)

    def set_sample_file(self, selected_file, ):

        self.sample_file_fullpath = selected_file
        self.fm.set_sample_file(self.sample_file_fullpath,
            self.sample_sheet_var.get())

        shortened_path = self.__shorten_path(self.log_file_fullpath)
        self.sample_file_var.set(shortened_path)
        self.sample_file_name_label.configure(text=self.sample_file_var.get())
        print('Sample file selected :' + self.sample_file_var.get())


app = MapDAP()
app.run()
