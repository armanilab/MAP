import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
#from data_vis import *
import numpy as np
from FileManagerClass import FileManager
from MAPPlotter import Plotter
from MAPAnalyzer import Analyzer

import matplotlib
matplotlib.use('TkAgg')
# to embed the plot
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# default Matplotlib key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class MapDAP:
    def __init__(self):
        # create the main window
        self.root = tk.Tk()
        self.root.title("MAP-DAP")
        self.root.columnconfigure(0, weight=1) # vertical rescaling
        self.root.rowconfigure(0, weight=1) # horizontal rescaling

        # set up the notebook (tabs)
        self.notebook = ttk.Notebook(self.root)

        # set up a main frame to integrate themed widgets (esp. bkgd color)
        # add some padding
        self.selection_page = ttk.Frame(self.notebook, padding="3 3 12 12")
        self.notebook.add(self.selection_page, text="Selection")

        # TODO: finish plotting frame
        self.plot_page = ttk.Frame(self.notebook, padding="3 3 12 12")
        self.notebook.add(self.plot_page, text="Plotter")

        # TODO: fnish analysis code
        self.mag_page = ttk.Frame(self.notebook, padding="3 3 12 12")
        self.notebook.add(self.mag_page, text="Analysis")

        self.notebook.pack(expand=1, fill="both")

        # TODO: fix this so it actually takes an input
        # save the data file

        self.file = "../../../../test_data/paper_data/MAP_test_log_data.xlsx"
        #self.file = "../../../../test_data/paper_data/test_log.xlsx"
        #self.file = "../../../../test_data/MAP_test_log_slit.xlsx"
        self.fm = FileManager(self.file)
        print("Successfully imported test log: " + self.file)

        self.df = self.fm.get_df()
        #self.filtered_list = self.df.index # start with ALL indices
        #self.to_selected_list = [] # start with none

        # TODO: did this even do anything?? set button styles
        s = ttk.Style()
        s.configure('main.TButtton', font=('Calibri', 20))

        # create things
        self.create_file_selection_page()
        self.create_plot_page()

        self.analyzer = Analyzer()
        self.create_mag_page()

        self.plot_type = 'Time vs. Lux'
        self.plotter = Plotter(self.fig)



    def run(self):
        self.root.mainloop()

    def create_file_selection_page(self):
        # add a label
        self.tree_label = ttk.Label(self.selection_page, text='Log files:')
        self.tree_label.configure(font=("TkDefaultFont", 20, "bold"))
        self.tree_label.grid(row=0, column=0, sticky='w')

        ### SETUP FILE PREVIEW ###
        # set up file preview frame
        self.file_preview_frame = ttk.Frame(self.selection_page)
        self.file_preview_frame.grid(row=1, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.file_preview_frame.columnconfigure(0, weight=1)
        self.file_preview_frame.rowconfigure(0, weight=1)

        # view files from treeview
        cols = self.fm.get_tree_cols()
        self.full_file_tree = self.create_tree(self.file_preview_frame)

        # add rows to tree from the dataframe (the file log)
        self.update_tree(self.full_file_tree, self.fm.get_filtered_list(),
            highlight=True)

        # set appearance for selected items
        self.full_file_tree.tag_configure("selected", background="yellow")

        # add scrollbar for file_preview
        self.full_file_scrollbar = ttk.Scrollbar(self.file_preview_frame,
            orient=tk.VERTICAL, command=self.full_file_tree.yview)
        self.full_file_tree.configure(
            yscrollcommand=self.full_file_scrollbar.set)
        self.full_file_scrollbar.grid(row=0, column=1, sticky='nse')

        ### ADD BUTTONS ###
        self.add_selection_button = ttk.Button(self.selection_page,
            text="Add Selected", command=self.add_selected)
        self.add_selection_button.grid(row=2, column=1)

        self.add_all_button = tk.Button(self.selection_page, text="Add All",
            command=self.add_all, bg='#2832c2', fg='#000000')
        self.add_all_button.grid(row=2, column=2)

        self.remove_selection_button = ttk.Button(self.selection_page,
            text="Remove Selected", command=self.remove_selected)
        self.remove_selection_button.grid(row=2, column=3)

        self.remove_all_button = tk.Button(self.selection_page, text="Remove All",
            command=self.remove_all, bg='#2832c2', fg='#000000')
        self.remove_all_button.grid(row=2, column=4)

        ### FILTERING ###
        # add a button to remove all filtering
        self.reset_filter_button = ttk.Button(self.selection_page,
            text="Reset filters", command=self.reset_filter)
        self.reset_filter_button.grid(row=3, column=4)

        # add dropdown menu for filtering
        # filter options are from the columns of the df
        self.filter_list = [''] + cols.to_list()

        self.filter_var = tk.StringVar()
        self.filter_optionmenu = ttk.OptionMenu(self.selection_page,
            self.filter_var, self.filter_list[0], *self.filter_list,
            command=self.display_filter_options) #TODO: set command , command=None)
        self.filter_optionmenu.config(width=10)
        self.filter_optionmenu.grid(row=3, column=1)

        # get actual options for filter
        self.filter_options = ['']
        self.filter_option_var = tk.StringVar()
        self.filteroptions_optionmenu = ttk.OptionMenu(self.selection_page,
            self.filter_option_var, self.filter_options[0],
            *self.filter_options, command=self.apply_filter) # TODO: fix command to actually show the filtered files (why doesn't this work?)
        self.filteroptions_optionmenu.config(width=15)
        self.filteroptions_optionmenu.grid(row=3, column=2)

        # add button to actually apply selected filter
        self.apply_button = ttk.Button(self.selection_page,
            text="Apply filter", command=self.apply_filter)
        self.apply_button.grid(row=3, column=3)

        # add label for second treeview
        self.queue_label = ttk.Label(self.selection_page,
            text='Files to be plotted:')
        self.queue_label.configure(font=("TkDefaultFont", 20, "bold"))
        self.queue_label.grid(row=4, column=0, sticky='w')

        # add second treeview with selected files to be plotted
        self.selection_preview_frame = ttk.Frame(self.selection_page)
        self.selection_preview_frame.grid(row=5, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.selection_preview_frame.columnconfigure(0, weight=1)
        self.selection_preview_frame.rowconfigure(0, weight=1)

        # create treeview to see selected files
        self.selection_preview_tree = self.create_tree(
            self.selection_preview_frame)

        # add rows to tree from the dataframe (the file log)
        self.update_tree(self.selection_preview_tree, self.fm.get_selected_list())

        # TODO: connect command to navigate to plot screen
        self.plotter_button = ttk.Button(self.selection_page, text="Plot",
            style="main.TButton", command=self.change_to_plot_page)
        self.plotter_button.grid(row=6, column=3, rowspan=2, columnspan=2)

    def create_tree(self, frame, ht=10):
        cols = self.fm.get_tree_cols()
        tree = ttk.Treeview(frame, columns=tuple(cols), height=ht)
        tree.column('#0', width=120)
        tree.heading('#0', text='File-name')

        # set column widths
        # first "column" is file-location - should be longer
        tree.column(self.fm.get_file_loc_col(), width=200, anchor='w')
        tree.heading(self.fm.get_file_loc_col(),
            text=self.fm.get_file_loc_col())

        # set all other columns to width of 100
        for i in (range(len(cols[1:]))):
            i += 1
            tree.column(cols[i], width=100, anchor='center')
            tree.heading(cols[i], text=cols[i])

        # add to grid and fill space in frame
        tree.grid(row=0, column=0, sticky=tk.NSEW)

        return tree

    # TODO: might need to change the row slicing values eventually, esp
    # if i add in feature to view/hide certain columns
    def update_tree(self, tree, indices, highlight=False):
        # clear old tree
        for item in tree.get_children():
            tree.delete(item)

        # add new entries from given dataframe
        for i in indices:
            row_text, row_value = self.fm.get_tree_row(i)
            tree.insert('', 'end', id=i, text=row_text, value=row_value)
            #row = self.df.loc[i]
            #tree.insert('', 'end', id=i, text=row['File-name'],
            #    value=tuple(row[1:-2]))

            if highlight:
                if i in self.fm.get_selected_list():
                    tree.item(i, tags=('selected'))

    def add_selected(self):
        selected_items = self.full_file_tree.selection()

        for item in selected_items:
            # change appearance of selected item via 'selected' tag
            self.full_file_tree.item(item, tags=("selected"))

            item_index = int(item)# convert item id to the index

            # add index from the list of files to be plotted
            self.fm.add_to_selected_list(item_index)
            #if item_index not in self.to_selected_list:
            #    self.to_selected_list.append(item_index)
            self.update_selected_trees()

    def update_selected_trees(self):
        self.update_tree(self.selection_preview_tree, self.fm.get_selected_list())
        self.update_tree(self.file_list_tree, self.fm.get_selected_list())
        self.update_tree(self.mag_file_list_tree, self.fm.get_selected_list())
        self.update_results_tree()
        # TODO: add updates to the selected files lists on the plot and analysis pages

    def remove_selected(self):
        selected_items = self.full_file_tree.selection()

        for item in selected_items:
            # remove the 'selected' tag and change appearance in tree
            self.full_file_tree.item(item, tags=())

            item_index = int(item) # convert item id to the index

            # remove index from the list of files to be plotted
            self.fm.remove_from_selected_list(item_index)
            #if item_index in self.to_selected_list:
            #    self.to_selected_list.remove(item_index)

        # update the selection preview tree
        self.update_selected_trees()

    def add_all(self):
        # add all shown files to the to_selected_list
        for i in self.fm.get_filtered_list():
            self.fm.add_to_selected_list(i)
            # add highlight to file in full_file_tree
            self.full_file_tree.item(i, tags=('selected'))

        # update the selection preview tree
        self.update_selected_trees()

    def remove_all(self):
        # remove all shown files from the to_selected_list
        for i in self.fm.get_filtered_list():
            self.fm.remove_from_selected_list(i)
            # remove highlight of file in full_file_tree
            self.full_file_tree.item(i, tags=())

        # update the selection preview tree
        self.update_selected_trees()

    #TODO: fix the sort so that if they're numerical, then the sort by numbers
    def display_filter_options(self, event):
        # get options from dataframe for this filter type
        filter_type = self.filter_var.get()
        self.filter_options = self.fm.get_filter_options(filter_type)
        self.filter_options.sort()
        self.filter_options.append("<Blank>") # for empty cells. #TODO: rename this?

        # remove 'extra' options
        if 'nan' in self.filter_options:
            self.filter_options.remove('nan')
        if 'none' in self.filter_options:
            self.filter_options.remove('none')

        # now actually update the option menu
        menu = self.filteroptions_optionmenu['menu']
        menu.delete(0, "end")
        # add new options to the mneu
        for s in self.filter_options:
            menu.add_command(label=s,
                command=lambda value=s: self.filter_option_var.set(value))

    def apply_filter(self, event):
        self.apply_filter()

    def apply_filter(self):
        print("applying filter:")
        # get the two selected filter variables
        filter_type = self.filter_var.get()
        filter_selected = self.filter_option_var.get()
        print("col: " + filter_type)
        print("value: " + filter_selected)

        # select the subset of the dataframe
        self.fm.filter_df(filter_type, filter_selected)

        self.update_tree(self.full_file_tree, self.fm.get_filtered_list(),
            highlight=True)

    def reset_filter(self):
        self.fm.filter_df()
        self.update_tree(self.full_file_tree, self.fm.get_filtered_list(),
            highlight=True)

    def create_plot_page(self):
        # add a label
        self.plot_label = ttk.Label(self.plot_page, text="Magic Plotter")
        self.plot_label.configure(font=("TkDefaultFont", 20, "bold"))
        self.plot_label.grid(row=0, column=0, sticky='w')

        self.plot_type_label = ttk.Label(self.plot_page, text="Select plot type:")
        self.plot_type_label.grid(row=0, column=2, sticky='e')

        # TODO: create dropdown menu to select plot type
        self.plot_types = ['Time vs. Lux', 'Concentration vs. Change in lux',
            'Trial Number vs. Lux range']
        self.plot_type_var = tk.StringVar()
        self.plot_type_menu = ttk.OptionMenu(self.plot_page, self.plot_type_var,
            self.plot_types[0], *self.plot_types, command=self.set_plot_type)
        self.plot_type_menu.config(width=20)
        self.plot_type_menu.grid(row=0, column=3, columnspan=2)

        # add treeview with selected files to be plotted
        self.file_list_frame = ttk.Frame(self.plot_page)
        self.file_list_frame.grid(row=1, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.file_list_frame.columnconfigure(0, weight=1)
        self.file_list_frame.rowconfigure(0, weight=1)

        # create treeview to see selected files
        self.file_list_tree = self.create_tree(self.file_list_frame, ht=5)
        self.update_tree(self.file_list_tree, self.fm.get_selected_list())

        # TODO: add scrollbar to treeview
        self.file_list_scrollbar = ttk.Scrollbar(self.file_list_frame,
            orient=tk.VERTICAL, command=self.file_list_tree.yview)
        self.file_list_tree.configure(
            yscrollcommand=self.file_list_scrollbar.set)
        self.file_list_scrollbar.grid(row=0, column=1, sticky='nse')

        # create button to plot things
        self.plot_button = ttk.Button(self.plot_page, text="Plot!",
            command=self.generate_plot)
        self.plot_button.grid(row=0, column=5, columnspan=2)

        # create frame for plot
        self.canvas_frame = ttk.Frame(self.plot_page)
        self.canvas_frame.grid(row = 2, column=2, rowspan=6, columnspan=5,
            sticky=tk.NSEW, pady=15, padx=15)
        #self.canvas_frame.columnconfigure(0, weight=1)
        #self.canvas_frame.rowconfigure(0, weight=1)

        #TODO: fix why won't this show the whole plot??
        self.fig = Figure(figsize=(4, 3), dpi=150)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)

        # create the toolbar
        #toolbar = NavigationToolbar2Tk(figure_canvas, self.canvas_frame)
        #toolbar.update()

        self.axes = self.fig.add_subplot()

        # create the barchart
        self.axes.plot([0, 1, 2, 3, 4, 5], [5, 4, 3, 2, 1, 0])
        self.axes.set_title('test')
        self.axes.set_ylabel('y axis')

        self.figure_canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH,
            expand=True)

        self.save_button = ttk.Button(self.plot_page, text="Save",
            command = self.save_fig)
        self.save_button.grid(row=2, column=0)

    def change_to_plot_page(self):
        self.generate_plot() # generate plot for selected files
        self.notebook.select(1) # actually change notebook tab

    def set_plot_type(self, event):
        self.plot_type = self.plot_type_var.get()
        print("changed plot type to " + self.plot_type)

    def generate_plot(self):
        if self.plot_type == 'Time vs. Lux':
            self.fig = self.plotter.plot_light_curve(self.fm,
                baseline_correction=False)
        elif self.plot_type == 'Concentration vs. Change in lux':
            self.fig = self.plotter.plot_concentration_curve(self.fm)
        self.figure_canvas.draw()
        print("canvas redrawn")

    def save_fig(self):
        self.fig.savefig('plot.svg', format='svg', dpi=1200)

    def create_mag_page(self):
        # add a label
        self.analysis_label = ttk.Label(self.mag_page,
            text="Magnetic Analysis")
        self.analysis_label.configure(font=("TkDefaultFont", 20, "bold"))
        self.analysis_label.grid(row=0, column=0, columnspan=3, sticky='w')

        # add treeview with selected files to be plotted
        self.mag_file_list_frame = ttk.Frame(self.mag_page)
        self.mag_file_list_frame.grid(row=1, column=0, columnspan=5,
            sticky=tk.NSEW, padx=15, pady=(0, 15))
        self.mag_file_list_frame.columnconfigure(0, weight=1)
        self.mag_file_list_frame.rowconfigure(0, weight=1)

        # create treeview to see selected files
        self.mag_file_list_tree = self.create_tree(self.mag_file_list_frame, ht=5)
        self.update_tree(self.mag_file_list_tree, self.fm.get_selected_list())

        # TODO: add scrollbar to treeview
        self.mag_file_list_scrollbar = ttk.Scrollbar(self.mag_file_list_frame,
            orient=tk.VERTICAL, command=self.mag_file_list_tree.yview)
        self.mag_file_list_tree.configure(
            yscrollcommand=self.mag_file_list_scrollbar.set)
        self.mag_file_list_scrollbar.grid(row=0, column=1, sticky='nse')

        # frame for analysis
        self.analysis_frame = ttk.Frame(self.mag_page, padding="3 3 12 12")
        self.analysis_frame.grid(row=2, column=0, columnspan=2, rowspan=4,
            sticky=tk.EW)

        self.analysis_frame_label = ttk.Label(self.analysis_frame,
            text="Analysis Options")
        self.analysis_frame_label.configure(font=("TkDefaultFont", 16, "bold"))
        self.analysis_frame_label.grid(row=0, column=0, columnspan=3,
            sticky=tk.W)

        self.analysis_type_label = ttk.Label(self.analysis_frame,
            text="Analysis Type")
        self.analysis_type_label.grid(row=1, column=0, columnspan=3)
        self.analysis_type_var = tk.IntVar()

        # individual analysis button
        self.analysis_type_indiv = ttk.Radiobutton(self.analysis_frame,
            text="Individual", variable=self.analysis_type_var,
            value=0)
        self.analysis_type_indiv.grid(row=1, column=3)
        # grouped analysis button
        self.analysis_type_group = ttk.Radiobutton(self.analysis_frame,
            text="Grouped", variable=self.analysis_type_var,
            value=1)
        self.analysis_type_group.grid(row=1, column=4)

        self.density_label = ttk.Label(self.analysis_frame,
            text="Intrinsic Material Density:")
        self.density_label.grid(row=2, column=0, columnspan=3)

        # TODO: add validation function to entry
        self.density_var = tk.StringVar(self.root, "5150")
        self.density_entry = ttk.Entry(self.analysis_frame,
            textvariable=self.density_var, justify=tk.LEFT)
        self.density_entry.grid(row=2, column=3)

        self.density_units_label = ttk.Label(self.analysis_frame,
            text = "mg/cm^3")
        self.density_units_label.grid(row=2, column=4, sticky=tk.W)

        # TODO: add validation function to entry
        self.start_time_label = ttk.Label(self.analysis_frame,
            text = "Start time:")
        self.start_time_label.grid(row=3, column=0, columnspan=3)

        self.start_time_var = tk.StringVar(self.root, "0")
        self.start_time_entry = ttk.Entry(self.analysis_frame,
            textvariable=self.start_time_var, justify=tk.LEFT)
        self.start_time_entry.grid(row=3, column=3)

        self.start_time_units_label = ttk.Label(self.analysis_frame,
            text = "sec")
        self.start_time_units_label.grid(row=3, column=4, sticky=tk.W)

        self.analyze_button = ttk.Button(self.mag_page, text="Analyze!",
            command=self.start_analysis)
        self.analyze_button.grid(row=0, column=4, columnspan=2)

        self.results_frame = ttk.Frame(self.mag_page, padding="3 3 12 12")
        self.results_frame.grid(row=2, column=2, columnspan=2, rowspan=6,
            sticky=tk.EW)

        self.results_frame_label = ttk.Label(self.results_frame,
            text="Results")
        self.results_frame_label.configure(font=("TkDefaultFont", 16, "bold"))
        self.results_frame_label.grid(row=0, column=0, columnspan=2,
            sticky=tk.W)

        self.results_tree = self.create_results_tree()
        self.update_results_tree()

        self.results_scrollbar = ttk.Scrollbar(self.results_frame,
            orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=self.results_scrollbar.set)
        self.results_scrollbar.grid(row=1, column=1, sticky='nse')

    def create_results_tree(self):
        cols = ['file-name', 'chi']
        tree = ttk.Treeview(self.results_frame, columns=cols)
        tree.heading('#0', text='File-name')
        tree.heading('#1', text='Chi')
        tree.grid(row=1, column=0, sticky=tk.NSEW)
        return tree

    def update_results_tree(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        results = self.fm.get_analyzed_files()
        selected_files = self.fm.get_selected_list()

        for f in selected_files:
            row_text = str(results[f][0])
            if results[f][1] is None:
                row_value = ''
            else:
                row_value = "{:0.3e}".format(results[f][1]['chi'])
            self.results_tree.insert('', 'end', id=f, text=row_text, value=row_value)


    def create_analyzed_files_tree(self, frame, ht=10):
        cols = []
        tree = ttk.Treeview(frame, columns=tuple(cols), height=ht)
        tree.column('#0', width=120)
        tree.heading('#0', text='File-name')

        # set column widths
        # first "column" is file-location - should be longer
        tree.column(self.fm.get_file_loc_col(), width=200, anchor='w')
        tree.heading(self.fm.get_file_loc_col(),
            text=self.fm.get_file_loc_col())

        # set all other columns to width of 100
        for i in (range(len(cols[1:]))):
            i += 1
            tree.column(cols[i], width=100, anchor='center')
            tree.heading(cols[i], text=cols[i])

        # add to grid and fill space in frame
        tree.grid(row=0, column=0, sticky=tk.NSEW)

    def start_analysis(self):
        print("Starting analysis...")

        self.analyzer.update_start_time(self.start_time_var.get())
        self.analyzer.update_density(self.density_var.get())
        self.analyzer.analyze_v2(self.fm)

        print("finished updating mag page")
        self.update_results_tree()




app = MapDAP()
app.run()
