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
        for i in range(self.df.shape[0]):
            row = self.df.loc[i]
            self.full_file_tree.insert('', 'end', id=i, text=row['File-name'],
                value=tuple(row[1:-2]))

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
        filter_options = [''] + cols.to_list()
        #filter_options.insert(0, ' ') # TODO: what is going on here?
        print(filter_options)
        self.filter_option_selected = tk.StringVar()
        self.filter_optionmenu = ttk.OptionMenu(self.main_frame,
            self.filter_option_selected, filter_options[0], *filter_options) #TODO: set command , command=None)
        self.filter_optionmenu.config(width=10)
        self.filter_optionmenu.grid(row=3, column=1)

    def run(self):
        self.root.mainloop()

    def add_selected(self):
        selected_items = full_file_tree.selection()
        # TODO: tag these items as selected and change appearance in tree
        for item in selected_items:
            full_file_tree.item(item, tags=("selected"))

    def remove_selected(self):
        selected_items = full_file_tree.selection()
        # remove the 'selected' tag and change appearance in tree
        for item in selected_items:
            full_file_tree.item(item, tags=())

    def select_filter(self):
        pass

app = MapDA()
app.create_file_selection_screen()
app.run()
