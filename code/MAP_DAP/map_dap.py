# MAP-DAP: MAgnetoPhotometer Data Analysis Program
#
# Written by: Lexie Scholtz
#             Jack Paulson
#
# Last Updated: 2025.04.08


import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import numpy as np
from FileManagerClass import FileManager
import map_dap_formats as mdf
import MAPPlotter as Plotter
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
        style.configure('Treeview.Heading', background='black')

        self.fm = FileManager()


        # --- FILE SELECTION PAGE ---
        # variables for file selection page

        # --- NOTEBOOK ---
        # set up notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill='both')

        page_padding = "3 3 12 12"

        # set up pages of the notebook
        # setup page - log file selection, other major parameters
        self.setup_page = SetupPage(self.notebook, self.fm,
            padding=page_padding)
        self.notebook.add(self.setup_page, text='Setup')

        # file selection page - select which files will be analyzed
        self.selection_page = SelectionPage(self.notebook, self.fm,
            padding=page_padding)#ttk.Frame(self.notebook, padding="3 3 12 12")
        self.notebook.add(self.selection_page, text='Selection')

        # plot page - allows visualization of data
        self.plot_page = PlotPage(self.notebook, self.fm, padding="3 3 12 12")
        self.notebook.add(self.plot_page, text="Visualization")

        self.notebook.bind('<<NotebookTabChanged>>', self.update_tab)

    def run(self):
        self.root.mainloop()

    def update_tab(self, event):
        tab = event.widget.tab('current')['text']
        print('changed tab to ' + tab)
        if self.setup_page.log_changed:
            print('log changed: update to selection page')
            self.selection_page.update()
            self.setup_page.log_changed = False
        if self.selection_page.selected_changed:
            print('selected changed: update to plot page')
            self.plot_page.update(self.selection_page.cols)
            self.selection_page.selected_changed = False

        # TODO: need to wipe selection if new log file loaded

class SetupPage(ttk.Frame):
    def __init__(self, parent, fm, **kwargs):
        super().__init__(parent, **kwargs)
        self.fm = fm

        # variables for setup page
        self.log_file_var = tk.StringVar(self, 'No file selected')
        self.log_file_fullpath = ''
        self.log_file_status_var = tk.StringVar(self, 'Unloaded')

        self.sample_from_log = tk.BooleanVar(value=True)
        self.sample_file_fullpath = ''
        self.sample_sheet_var = tk.StringVar(self, 'samples')
        self.sample_file_var = tk.StringVar(self, 'No file selected')
        self.sample_status_var = tk.StringVar(self, 'Unloaded')

        self.log_changed = False

        self.create_setup_page()

    def create_setup_page(self):

        self.setup_label = ttk.Label(self, text='SETUP',
            anchor='w')
        self.setup_label.configure(font=mdf.title_font)
        self.setup_label.grid(row=0, column=0)
        # to do: fix columns of each frame at some point

        # --- LOG FILE ---
        self.log_frame = ttk.Frame(self)
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
        self.sample_frame = ttk.Frame(self)
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
        self.magnet_frame = ttk.Frame(self)
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

        self.log_changed = True

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

    def set_sample_file(self, selected_file):
        self.sample_file_fullpath = selected_file
        self.fm.set_sample_file(self.sample_file_fullpath,
            self.sample_sheet_var.get())

        shortened_path = self.__shorten_path(self.log_file_fullpath)
        self.sample_file_var.set(shortened_path)
        self.sample_file_name_label.configure(text=self.sample_file_var.get())
        print('Sample file selected :' + self.sample_file_var.get())
        self.load_sample_file()

    def load_sample_file(self):
        self.fm.load_sample_dict()

class SelectionPage(ttk.Frame):
    def __init__(self, parent, fm, **kwargs):
        super().__init__(parent, **kwargs)
        self.fm = fm

        for i in range(6):
            self.columnconfigure(i, weight=1)

        # variables for selection page
        # default columns to display
        self.cols = self.get_default_cols()
        self.disp_rows = 10

        self.selected_changed = False

        # create page
        self.create_selection_page()

    def create_selection_page(self):
        # add a label
        self.tree_label = ttk.Label(self, text='Select files:')
        self.tree_label.configure(font=mdf.heading1_font)
        self.tree_label.grid(row=0, column=0, sticky='w')

        self.reload_button = ttk.Button(self, text='Reload log',
            command=self.create_full_file_tree)
        self.reload_button.grid(row=0, column=1, sticky='e')

        ### FILE LOG PREVIEW ###
        self.log_preview_frame = ttk.Frame(self)
        self.log_preview_frame.grid(row=1, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.log_preview_frame.columnconfigure(0, weight=1)
        self.log_preview_frame.rowconfigure(0, weight=1)

        # view files from tree view
        self.full_file_tree = ttk.Treeview(self.log_preview_frame,
            columns=self.cols, height=self.disp_rows)
        self.full_file_tree.grid(row=0, column=0, sticky=tk.NSEW)
        # set selected files to show up in blue text
        self.full_file_tree.tag_configure('selected', foreground='blue')
        self.create_full_file_tree() # TODO: implement

        # add scrollbar for file preview
        self.full_file_scrollbar = ttk.Scrollbar(self.log_preview_frame,
            orient=tk.VERTICAL, command=self.full_file_tree.yview)
        self.full_file_tree.configure(
            yscrollcommand=self.full_file_scrollbar.set) # attach to treeview
        self.full_file_scrollbar.grid(row=0, column=1, sticky='nse')

        # add a horizontal scrollbar??
        self.full_file_hscroll = ttk.Scrollbar(self.log_preview_frame,
            orient=tk.HORIZONTAL, command=self.full_file_tree.xview)
        self.full_file_tree.configure(xscrollcommand=self.full_file_hscroll.set)
        self.full_file_hscroll.grid(row=1, column=0, columnspan=2, sticky='sew')

        ### BUTTON MENU ###
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=2, column=0, columnspan=6, sticky=tk.NSEW,
            padx=15, pady=15)
        for i in range(5):
            self.button_frame.columnconfigure(i, weight=1)
        ## TODO: add sort options??

        ## FIRST ROW: filter options
        # add button to remove all filtering
        self.filter_label = ttk.Label(self.button_frame, text='Filter options:')
        self.filter_label.configure(font=mdf.heading2_font)
        self.filter_label.grid(row=0, column=0, sticky='w')

        ## SECOND ROW: selection buttons
        # TODO: add functions for all buttons still
        self.selections_label = ttk.Label(self.button_frame,
            text='Selection options:', font=mdf.heading2_font)
        self.selections_label.grid(row=1, column=0, sticky='w')

        # add button to add selected files
        self.add_selection_button = ttk.Button(self.button_frame,
            text='Add Selected', command=self.add_selected)
        self.add_selection_button.grid(row=1, column=1)

        # add button to add all files
        self.add_all_button = ttk.Button(self.button_frame, text='Add All',
            command=self.add_all)
        self.add_all_button.grid(row=1, column=2)

        # add button to remove selected files
        self.remove_selection_button = ttk.Button(self.button_frame,
            text='Remove Selected', command=self.remove_selected)
        self.remove_selection_button.grid(row=1, column=3)

        # add button to remove all files
        self.remove_all_button = ttk.Button(self.button_frame,
            text='Remove All', command=self.remove_all)
        self.remove_all_button.grid(row=1, column=4)

        ### SELECTED FILES PREVIEW ###
        self.selected_preview_frame = ttk.Frame(self)
        self.selected_preview_frame.grid(row=3, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.selected_preview_frame.columnconfigure(0, weight=1)
        self.selected_preview_frame.rowconfigure(0, weight=1)

        self.selected_file_tree = ttk.Treeview(self.selected_preview_frame,
            columns=self.cols, height=self.disp_rows)
        self.selected_file_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.create_selected_file_tree()

        self.selected_yscroll = ttk.Scrollbar(self.selected_preview_frame,
            orient=tk.VERTICAL, command=self.selected_file_tree.yview)
        self.selected_file_tree.configure(
            yscrollcommand=self.selected_yscroll.set) # attach to treeview
        self.selected_yscroll.grid(row=0, column=1, sticky='nse')

        self.selected_xscroll = ttk.Scrollbar(self.selected_preview_frame,
            orient=tk.HORIZONTAL, command=self.selected_file_tree.xview)
        self.selected_file_tree.configure(
            xscrollcommand=self.selected_xscroll.set) # attach to treeview
        self.selected_xscroll.grid(row=1, column=0, columnspan=2, sticky='sew')

    def create_full_file_tree(self):
        # get the data from the file manager
        print('creating full file tree')

        # configure columns
        self.full_file_tree.column('#0', width=0, stretch=tk.NO)
        #self.full_file_tree.heading('#0', text=self.cols[0])

        for i in range(0, len(self.cols)):
            self.full_file_tree.column(self.cols[i], width=70, anchor='w')
            self.full_file_tree.heading(self.cols[i], text=self.cols[i])

    def update_full_file_tree(self, filter_col=None, filter_value=None):
        # delete existing tree
        for item in self.full_file_tree.get_children():
            self.full_file_tree.delete(item)

        tree_data = self.fm.get_file_df(self.cols)

        if tree_data is None:
            print('no data found')
            return

        indices = tree_data.index.to_list()
        for i in indices:
            row = tree_data.loc[i]
            row_text = row[self.cols[0]]
            row_value = tuple(row[self.cols[1:]].fillna(''))
            #self.full_file_tree.insert('', 'end', id=i, text=row_text, value=row_value)
            self.full_file_tree.insert('', 'end', id=i, value=tuple(tree_data.loc[i].fillna('')))

    def create_selected_file_tree(self):
        print('Creating selected file tree')
        # TODO: finish
        self.selected_file_tree.column('#0', width=0, stretch=tk.NO)
        #self.full_file_tree.heading('#0', text=self.cols[0])

        for i in range(0, len(self.cols)):
            self.selected_file_tree.column(self.cols[i], width=70, anchor='w')
            self.selected_file_tree.heading(self.cols[i], text=self.cols[i])

    def add_selected(self):
        print('add selected')
        # get selected file
        selected_items = self.full_file_tree.selection()

        for item in selected_items:
            # tag the selected items to change appearance
            self.full_file_tree.item(item, tags=('selected'))
            self.fm.add_to_selected_list(item)
            self.selected_file_tree.insert('', 'end', id=item, value=tuple(self.fm.get_row(int(item), self.cols).fillna('')))

        self.selected_changed = True
        print(self.fm.get_selected_df(self.cols))

    def remove_selected(self):
        print('remove selected')
        selected_items = self.full_file_tree.selection()

        for item in selected_items:
            self.full_file_tree.item(item, tags=())
            self.fm.remove_from_selected_list(item)
            self.selected_file_tree.delete(item)

        self.selected_changed = True
        print(self.fm.get_selected_df(self.cols))

    def add_all(self):
        for item in self.full_file_tree.get_children():
            self.full_file_tree.item(item, tags=('selected'))
            self.fm.add_to_selected_list(item)
            self.selected_file_tree.insert('', 'end', id=item, value=tuple(self.fm.get_row(int(item), self.cols).fillna('')))

        print(self.fm.get_selected_df(self.cols))
        self.selected_changed = True
        print('add all')

    def remove_all(self):
        for item in self.selected_file_tree.get_children():
            self.full_file_tree.item(item, tags=())
            self.fm.remove_from_selected_list(item)
            self.selected_file_tree.delete(item)

        print(self.fm.get_selected_df(self.cols))
        self.selected_changed = True
        print('remove all')

    def update(self):
        self.update_full_file_tree()

        #TODO: eventually: reset filters, reset selected list
        self.remove_all()

    def get_default_cols(self):
        return ['File', 'Directory', 'Sample', 'Magnet']

class PlotPage(ttk.Frame):
    def __init__(self, parent, fm, **kwargs):
        super().__init__(parent, **kwargs)
        self.fm = fm

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        #TODO: eventually get this from the plotter class
        self.plot_types = ['Time vs. Intensity', 'Time vs. Concentration']
        self.plot_type_var = tk.StringVar()

        # TODO: get this from MAP_DAP
        self.cols = ['File', 'Directory', 'Sample', 'Magnet']
        self.disp_rows = 6
        self.check_box = '☑'
        self.box = '☐'

        self.create_page()

    def create_page(self):
        print("creating plot page")

        # add page label
        self.page_label = ttk.Label(self, text="Plotter",
            font=mdf.heading1_font)
        self.page_label.grid(row=0, column=0, sticky='w')

        ### PLOT TYPE SELECTION ###
        # dropdown menu to select plot type
        self.plot_type_label = ttk.Label(self, text="Select plot type:",
            font=mdf.bold_font)
        self.plot_type_label.grid(row=0, column=1, sticky='e')

        self.plot_type_menu = ttk.OptionMenu(self, self.plot_type_var,
            self.plot_types[0], *self.plot_types, command=self.set_plot_type)
        self.plot_type_menu.config(width=20)
        self.plot_type_menu.grid(row=0, column=2)

        self.plot_button = ttk.Button(self, text='Plot',
            command=self.generate_plot)
        self.plot_button.grid(row=0, column=3)

        ### FILE PREVIEW ###
        self.file_preview_frame = ttk.Frame(self)
        self.file_preview_frame.grid(row=1, column=0, columnspan=4,
            sticky='nsew', padx=15, pady=5)
        self.file_preview_frame.columnconfigure(0, weight=1)
        self.file_preview_frame.rowconfigure(0, weight=1)

        self.file_tree = ttk.Treeview(self.file_preview_frame,
            height=self.disp_rows)
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        self.create_file_tree()

        self.file_yscroll = ttk.Scrollbar(self.file_preview_frame,
            orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.config(yscrollcommand=self.file_yscroll.set)
        self.file_yscroll.grid(row=0, column=1, sticky='nse')

        self.file_xscroll = ttk.Scrollbar(self.file_preview_frame,
            orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.config(xscrollcommand=self.file_xscroll.set)
        self.file_xscroll.grid(row=1, column=0, columnspan=2, sticky='sew')

        ### MATPLOTLIB CANVAS ###
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.grid(row=2, column=1, columnspan=3, sticky='nswe',
            padx=5, pady=5)
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)

        self.canvas = FigureCanvasTkAgg(None, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def set_plot_type(self):
        # TODO: eventually set Plotter type
        print(self.plot_type_var.get())

    def create_file_tree(self):
        print('creating plot: file tree')
        self.file_tree.config(columns=[''] + self.cols)
        self.file_tree.column('#0', width=0, stretch=tk.NO)

        self.file_tree.column(0, width=25, stretch=tk.NO, anchor='center')
        self.file_tree.heading(0, text=self.check_box)

        for i in range(len(self.cols)):
            self.file_tree.column(i+1, minwidth=150, anchor='w')
            self.file_tree.heading(i+1, text=self.cols[i])

    def update_file_tree(self):
        print('updating file tree')
        tree_data = self.fm.get_selected_df(self.cols)

        if tree_data is None:
            print('no data found')
            return

        # remove old tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        indices = tree_data.index.to_list()
        for i in indices:
            row = [self.check_box] + tree_data.loc[i].fillna('').to_list()
            self.file_tree.insert('', 'end', id=i, value=tuple(row))

    def update(self, cols):
        self.cols = cols
        self.create_file_tree()
        self.update_file_tree()

    def generate_plot(self):
        # TODO; refine
        plotter = None
        # determine type of plot and generate Plotter object
        if self.plot_type_var.get() == 'Time vs. Intensity':
            plotter = Plotter.TimeVsIntensity(fm=self.fm)
        plotter.plot()
        self.canvas.figure = plotter.get_fig()
        self.canvas.draw()

app = MapDAP()
app.run()
