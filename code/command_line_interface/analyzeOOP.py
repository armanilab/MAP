import numpy as np
from Classes import MagFieldFit, ParamGuesser
import sys # new


'''This code is to be run by students running the iron oxide
nanoparticle characterization lab. The structure of the code is as follows:
	1) Commandline prompt asking for sized magnet used in anaysis
	2) name of the folder containing the data
	3) name of the folder they would like to output the results to
This code is to replace multi_LA.py, which is less user friendly
'''

##########Determine fit params for magnetic field##############
magSize = input("Please select the size magnet used in the analysis:\n[a]\t3/8 inch\n[b]\t1/4 inch\n[c]\t3/16 inch\n")

if magSize == 'a':
	print("You selected the 3/8th inch magnet: The BIG KAHUNA.\n")
	B_r = 1.32 #Tesla
	t = 0.009525 # m
	magnet = "3/8"
elif magSize == 'b':
	print("You selected the 1/4th inch magnet: The KAHUNA.\n")
	B_r = 1.32 #Tesla
	t = 0.00635 # m
	magnet = "1/4"
elif magSize == 'c':
	print("You slected the 3/16th inch magnet: The Little Kahuna.\n")
	B_r = 1.32 #Tesla
	t = 0.0047625 # m
	magnet = "3/16"
else:
	print("ERROR: Invalid entry. Please enter either 'a', 'b', or 'c'.")
	print("Rerun the program and try again.\n")


B_fieldFit = MagFieldFit(B_r, t)
magFieldParams = B_fieldFit.get_magFitParams()
print("Mag. Field Params: {} \t {}\n".format(*magFieldParams))

# print("Magnetic Fit Parameters: A = {}\tb = {}".format(*magFieldParams))


###############Locating the Magnetometer Data#########################
file_input = input("Are you analzing...\n[a] a single file?\n[b] all files in a folder?\n")
if file_input == 'a':
	path = input("Please enter the path to the data file (not including the file name):\n")
	path = sys.argv[1]
	file = input("Please enter the file name:\n")
	file = sys.argv[2]
else:
	# TODO: change path input here
	path = input("Please enter the path to the data folder: ")
	file = None


trunctionNeed = input("Do you need to truncate the dataset?\n[a]\tYes\n[b]\tNo\n")

if trunctionNeed == "a":
	print("\nData Truncation:")
	truncation_min = float(input("Starting time (seconds): \n"))
	truncation_max = float(input("Ending time (seconds): \n"))
	minTrunc = truncation_min
	maxTrunc = truncation_max

else:
	print("Alrighty then... Mr. 'Perfect data'. No wonder why mother loved you more.\n")
	timeLenData = float(input("Atleast tell me how much time you ran your samples (seconds):\n"))
	minTrunc = 0
	maxTrunc = timeLenData


paramGuesses = ParamGuesser(path, file)

g = paramGuesses.get_paramGuesses(minTrunc, maxTrunc)
print(g)

# guessesTest = np.array([-1.3e-06, -4e+03, -0.0039])

results = paramGuesses.analyze(minTrunc, maxTrunc, g, magFieldParams)

# g = paramGuesses.get_paramGuesses(minTrunc, maxTrunc)
# print(g)

# # guessesTest = np.array([-1.3e-06, -4e+03, -0.0039])

# results = paramGuesses.analyze(minTrunc, maxTrunc, g, magFieldParams)
