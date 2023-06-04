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

        # set up a main frame to integrate themed widgets (esp. bkgd color)
        # add some padding
        self.main_frame = ttk.Frame(self.root, padding="3 3 12 12")
        # stick to all sides
        self.main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # TODO: fix this so it actually takes an input
        # save the data file

        self.file = "../../../../test_data/paper_data/MAP_test_log_data.xlsx"
        self.file_manager = FileManager(self.file)
        self.df = self.file_manager.get_df()

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
        self.full_file_tree = ttk.Treeview(self.file_preview_frame,
            columns=tuple(cols))
        self.full_file_tree.column('#0', width=120)
        self.full_file_tree.heading('#0', text='File-name')
        # set column widths
        # first "column" is file-location - should be longer
        self.full_file_tree.column(self.df.columns[1], width=200, anchor='w')
        self.full_file_tree.heading(self.df.columns[1], text=self.df.columns[1])
        # set all other columns to width of 100
        for i in (range(len(cols[1:]))):
            i += 1
            self.full_file_tree.column(cols[i], width=100, anchor='center')
            self.full_file_tree.heading(cols[i], text=cols[i])
        self.full_file_tree.grid(row=0, column=0, sticky=tk.NSEW)

        # add rows to tree from the dataframe (the file log)
        self.update_file_tree(self.df.index.to_list())

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

        self.remove_selection_button = ttk.Button(self.main_frame,
            text="Remove Selected", command=self.remove_selected)
        self.remove_selection_button.grid(row=2, column=3)

        ### FILTERING ###
        # add dropdown menu for filtering
        # filter options are from the columns of the df
        self.filter_list = [''] + cols.to_list()
        #filter_options.insert(0, ' ') # TODO: what is going on here?
        print(self.filter_list)
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
            *self.filter_options, command=self.apply_filter) # TODO: set command to actually show the filtered files
        self.filteroptions_optionmenu.config(width=15)
        self.filteroptions_optionmenu.grid(row=3, column=2)

        self.apply_button = ttk.Button(self.main_frame,
            text="Apply filter", command=self.apply_filter)
        self.apply_button.grid(row=3, column=3)


    def run(self):
        self.root.mainloop()

    # TODO: might need to change the row slicing values eventually, esp
    # if i add in feature to view/hide certain columns
    def update_file_tree(self, indices):
        # clear old tree
        for item in self.full_file_tree.get_children():
            self.full_file_tree.delete(item)

        # add new entries from given dataframe
        for i in indices:
            row = self.df.loc[i]
            print(str(i) + ": " + row['File-name'])
            self.full_file_tree.insert('', 'end', id=i, text=row['File-name'],
                value=tuple(row[1:-2]))

    def add_selected(self):
        selected_items = self.full_file_tree.selection()
        # TODO: tag these items as selected and change appearance in tree
        for item in selected_items:
            self.full_file_tree.item(item, tags=("selected"))

    def remove_selected(self):
        selected_items = self.full_file_tree.selection()
        # remove the 'selected' tag and change appearance in tree
        for item in selected_items:
            self.full_file_tree.item(item, tags=())

    #TODO: fix the sort so that if they're numerical, then the sort by numbers
    def display_filter_options(self, event):
        # get options from dataframe for this filter type
        filter_type = self.filter_var.get()
        filter_options = self.df[filter_type].fillna("")
        self.filter_options = filter_options.unique().tolist()
        self.filter_options.sort()
        self.filter_options.append("<None>") # for empty cells. #TODO: rename this?
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

    def apply_filter(self):
        print("applying filter:")
        # get the two selected filter variables
        filter_type = self.filter_var.get()
        filter_selected = self.filter_option_var.get()
        print("col: " + filter_type)
        print("value: " + filter_selected)

        # select the subset of the dataframe
        entries = self.df.loc[self.df[filter_type] == filter_selected]
        entries_indices = entries.index.to_list()
        print(entries)
        self.update_file_tree(entries_indices)


app = MapDA()
app.create_file_selection_screen()
app.run()
