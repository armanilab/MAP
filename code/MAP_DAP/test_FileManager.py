# Test driver for FileManager class
#
# Written by: Lexie Scholtz
#
# Last updated: 2025.01.09

from FileManagerClass import FileManager

# --- TESTS FOR COLUMN NAMES ---
def test1_default_names():
    print('\n\n--- Test for default names ---')
    print('Expected: successful reading of all required columns\n')
    test_file = 'test_files/col_test1.xlsx'
    fm = FileManager(test_file)

def test2_alt_names():
    print('\n\n--- Test for alternate names ---')
    print('Expected: successful reading of all required columns\n')
    test_file = 'test_files/col_test2.xlsx'
    fm = FileManager(test_file)

def test3_missing_names():
    print('\n\n--- Test for missing columns ---')
    print('Expected: all 4 required columns missing\n')
    test_file = 'test_files/col_test3.xlsx'
    fm = FileManager(test_file)

test1_default_names()
test2_alt_names()
test3_missing_names()
