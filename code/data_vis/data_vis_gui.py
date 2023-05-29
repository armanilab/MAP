import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
from data_vis import *

def add_selected():
    selected_items = full_file_tree.selection()
    # TODO: tag these items as selected and change appearance in tree
    for item in selected_items:
        full_file_tree.item(item, tags=("selected"))

def remove_selected():
    selected_items = full_file_tree.selection()
    # remove the 'selected' tag and change appearance in tree
    for item in selected_items:
        full_file_tree.item(item, tags=())



# Create the main window
root = tk.Tk()
root.title("MAPDA")

# set up a main frame to smoothly integrate themed widgets (esp. bkgd color)
main_frame = ttk.Frame(root, padding="3 3 12 12") # add some padding
main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S)) # stick to all sides
root.columnconfigure(0, weight=1) # vertical rescaling
root.rowconfigure(0, weight=1) # horizontal rescaling

# load data log
file = "../../../../test_data/paper_data/MAP_test_log_data.xlsx"
df, sample_dict = load_data_log(file)

# add a label above the file viewer
tree_label = ttk.Label(main_frame, text='Log files:')
tree_label.configure(font=("TkDefaultFont", 20, "bold"))
tree_label.grid(row=0, column=0, sticky='w')

### SETUP FILE PREVIEW ###
# set up file preview frame
file_preview_frame = ttk.Frame(main_frame)
file_preview_frame.grid(row=1, column=0, columnspan=6, sticky=tk.NSEW, padx=15)
file_preview_frame.columnconfigure(0, weight=1)
file_preview_frame.rowconfigure(0, weight=1)

# view files from treeview
cols = df.columns[1:-2]
full_file_tree = ttk.Treeview(file_preview_frame, columns=tuple(cols))
full_file_tree.column('#0', width=120)
full_file_tree.heading('#0', text='File-name')
full_file_tree.column(df.columns[1], width=200, anchor='w')
full_file_tree.heading(df.columns[1], text=df.columns[1])
for i in (range(len(cols[1:]))):
    i += 1
    full_file_tree.column(cols[i], width=100, anchor='center')
    full_file_tree.heading(cols[i], text=cols[i])

full_file_tree.grid(row=0, column=0, sticky=tk.NSEW)

for i in range(df.shape[0]):
    row = df.iloc[i]
    full_file_tree.insert('', 'end', id=i, text=row['File-name'], value=tuple(row[1:-2]))

# set appearance for selected items
full_file_tree.tag_configure("selected", background="yellow")

# add scrollbar for file_preview
full_file_scrollbar = ttk.Scrollbar(file_preview_frame, orient=tk.VERTICAL,
    command=full_file_tree.yview)
full_file_tree.configure(yscrollcommand=full_file_scrollbar.set)
full_file_scrollbar.grid(row=0, column=1, sticky='nse')

### ADD BUTTONS ###
add_selection_button = ttk.Button(main_frame, text="Add Selected",
    command=add_selected)
add_selection_button.grid(row=2, column=1)

remove_selection_button = ttk.Button(main_frame, text="Remove Selected",
    command=remove_selected)
remove_selection_button.grid(row=2, column=3)

### FILTERING ###
# add dropdown menu for filtering
# filter options are from the columns of the df
filter_options = [''] + cols.to_list()
#filter_options.insert(0, ' ') # TODO: what is going on here?
print(filter_options)
filter_option_selected = tk.StringVar()
filter_optionmenu = ttk.OptionMenu(main_frame, filter_option_selected,
    filter_options[0], *filter_options) #TODO: set command , command=None)
filter_optionmenu.config(width=10)
filter_optionmenu.grid(row=3, column=1)

# Run the GUI
root.mainloop()
