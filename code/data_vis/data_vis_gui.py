import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
from data_vis import *
from FileManagerClass import FileManager



class MapDA:
    def __init__(self):
        # create the main window
        self.root = tk.Tk()
        self.root.title("MAPDA")
        self.root.columnconfigure(0, weight=1) # vertical rescaling
        self.root.rowconfigure(0, weight=1) # horizontal rescaling

        # set up the notebook (tabs)
        self.notebook = ttk.Notebook(self.root)

        # set up a main frame to integrate themed widgets (esp. bkgd color)
        # add some padding
        self.main_frame = ttk.Frame(self.notebook, padding="3 3 12 12")
        self.notebook.add(self.main_frame, text="Selection")

        # TODO: fix second frame
        # add second dummy tab right now
        self.second_frame = ttk.Frame(self.notebook, padding="3 3 12 12")
        b1 = tk.Button(self.second_frame, text="hello!")
        b1.pack()
        self.notebook.add(self.second_frame, text="Plotter")

        self.notebook.pack(expand=1, fill="both")

        # stick to all sides
        #self.main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # TODO: fix this so it actually takes an input
        # save the data file

        self.file = "../../../../test_data/paper_data/MAP_test_log_data.xlsx"
        self.file_manager = FileManager(self.file)
        self.df = self.file_manager.get_df()
        self.filtered_list = self.df.index # start with ALL indices
        self.to_plot_list = [] # start with none

        # create things
        self.create_file_selection_screen()

    def run(self):
        self.root.mainloop()

    def create_file_selection_screen(self):
        # add a label
        self.tree_label = ttk.Label(self.main_frame, text='Log files:')
        self.tree_label.configure(font=("TkDefaultFont", 20, "bold"))
        self.tree_label.grid(row=0, column=0, sticky='w')

        ### SETUP FILE PREVIEW ###
        # set up file preview frame
        self.file_preview_frame = ttk.Frame(self.main_frame)
        self.file_preview_frame.grid(row=1, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.file_preview_frame.columnconfigure(0, weight=1)
        self.file_preview_frame.rowconfigure(0, weight=1)

        # view files from treeview
        cols = self.df.columns[1:-2]
        self.full_file_tree = self.create_tree(self.file_preview_frame)

        # add rows to tree from the dataframe (the file log)
        self.update_tree(self.full_file_tree, self.filtered_list,
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
        self.add_selection_button = ttk.Button(self.main_frame,
            text="Add Selected", command=self.add_selected)
        self.add_selection_button.grid(row=2, column=1)

        self.add_all_button = tk.Button(self.main_frame, text="Add All",
            command=self.add_all, bg='#2832c2', fg='#000000')
        self.add_all_button.grid(row=2, column=2)

        self.remove_selection_button = ttk.Button(self.main_frame,
            text="Remove Selected", command=self.remove_selected)
        self.remove_selection_button.grid(row=2, column=3)

        self.remove_all_button = tk.Button(self.main_frame, text="Remove All",
            command=self.remove_all, bg='#2832c2', fg='#000000')
        self.remove_all_button.grid(row=2, column=4)

        ### FILTERING ###
        # add a button to remove all filtering
        self.reset_filter_button = ttk.Button(self.main_frame,
            text="Reset filters", command=self.reset_filter)
        self.reset_filter_button.grid(row=3, column=4)

        # add dropdown menu for filtering
        # filter options are from the columns of the df
        self.filter_list = [''] + cols.to_list()

        self.filter_var = tk.StringVar()
        self.filter_optionmenu = ttk.OptionMenu(self.main_frame,
            self.filter_var, self.filter_list[0], *self.filter_list,
            command=self.display_filter_options) #TODO: set command , command=None)
        self.filter_optionmenu.config(width=10)
        self.filter_optionmenu.grid(row=3, column=1)

        # get actual options for filter
        self.filter_options = ['']
        self.filter_option_var = tk.StringVar()
        self.filteroptions_optionmenu = ttk.OptionMenu(self.main_frame,
            self.filter_option_var, self.filter_options[0],
            *self.filter_options, command=self.apply_filter) # TODO: fix command to actually show the filtered files (why doesn't this work?)
        self.filteroptions_optionmenu.config(width=15)
        self.filteroptions_optionmenu.grid(row=3, column=2)

        # add button to actually apply selected filter
        self.apply_button = ttk.Button(self.main_frame,
            text="Apply filter", command=self.apply_filter)
        self.apply_button.grid(row=3, column=3)

        # add label for second treeview
        self.queue_label = ttk.Label(self.main_frame,
            text='Files to be plotted:')
        self.queue_label.configure(font=("TkDefaultFont", 20, "bold"))
        self.queue_label.grid(row=4, column=0, sticky='w')

        # add second treeview with selected files to be plotted
        self.selection_preview_frame = ttk.Frame(self.main_frame)
        self.selection_preview_frame.grid(row=5, column=0, columnspan=6,
            sticky=tk.NSEW, padx=15)
        self.selection_preview_frame.columnconfigure(0, weight=1)
        self.selection_preview_frame.rowconfigure(0, weight=1)

        # create treeview to see selected files
        self.selection_preview_tree = self.create_tree(
            self.selection_preview_frame)

        # add rows to tree from the dataframe (the file log)
        self.update_tree(self.selection_preview_tree, self.to_plot_list)

    def create_tree(self, frame):
        cols = self.df.columns[1:-2]
        tree = ttk.Treeview(frame, columns=tuple(cols))
        tree.column('#0', width=120)
        tree.heading('#0', text='File-name')

        # set column widths
        # first "column" is file-location - should be longer
        tree.column(self.df.columns[1], width=200, anchor='w')
        tree.heading(self.df.columns[1], text=self.df.columns[1])

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
            row = self.df.loc[i]
            tree.insert('', 'end', id=i, text=row['File-name'],
                value=tuple(row[1:-2]))

            if highlight:
                if i in self.to_plot_list:
                    tree.item(i, tags=('selected'))

    def add_selected(self):
        selected_items = self.full_file_tree.selection()

        for item in selected_items:
            # change appearance of selected item via 'selected' tag
            self.full_file_tree.item(item, tags=("selected"))

            item_index = int(item)# convert item id to the index

            # add index from the list of files to be plotted
            if item_index not in self.to_plot_list:
                self.to_plot_list.append(item_index)

        # update the selection preview tree
        self.update_tree(self.selection_preview_tree, self.to_plot_list)


    def remove_selected(self):
        selected_items = self.full_file_tree.selection()

        for item in selected_items:
            # remove the 'selected' tag and change appearance in tree
            self.full_file_tree.item(item, tags=())

            item_index = int(item) # convert item id to the index

            # remove index from the list of files to be plotted
            if item_index in self.to_plot_list:
                self.to_plot_list.remove(item_index)

        # update the selection preview tree
        self.update_tree(self.selection_preview_tree, self.to_plot_list)

    def add_all(self):
        # add all shown files to the to_plot_list
        for i in self.filtered_list:
            if i not in self.to_plot_list:
                self.to_plot_list.append(i)
            # add highlight to file in full_file_tree
            self.full_file_tree.item(i, tags=('selected'))

        # update the selection preview tree
        self.update_tree(self.selection_preview_tree, self.to_plot_list)


    def remove_all(self):
        # remove all shown files from the to_plot_list
        for i in self.filtered_list:
            if i in self.to_plot_list:
                self.to_plot_list.remove(i)
            # remove highlight of file in full_file_tree
            self.full_file_tree.item(i, tags=())

        # update the selection preview tree
        self.update_tree(self.selection_preview_tree, self.to_plot_list)

    #TODO: fix the sort so that if they're numerical, then the sort by numbers
    def display_filter_options(self, event):
        # get options from dataframe for this filter type
        filter_type = self.filter_var.get()
        filter_options = self.df[filter_type].fillna("")
        self.filter_options = filter_options.unique().tolist()
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
        entries = self.df.loc[self.df[filter_type] == filter_selected]
        self.filtered_list = entries.index.to_list()
        print(entries)
        self.update_tree(self.full_file_tree, self.filtered_list,
            highlight=True)

    def reset_filter(self):
        self.filtered_list = self.df.index
        self.update_tree(self.full_file_tree, self.filtered_list,
            highlight=True)


app = MapDA()
app.run()
