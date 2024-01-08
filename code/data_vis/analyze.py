import numpy as np
import matplotlib.pyplot as plt
import lightFunctions as lf
from scipy.optimize import curve_fit
import scipy.stats as stats
import os
import sys
import codecs
from tqdm import tqdm

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
	B_r = 1.48 #Tesla
	magnet = "3/8"
elif magSize == 'b':
	print("You selected the 1/4th inch magnet: The KAHUNA.\n")
	B_r = 1.48 #Tesla
	magnet = "1/4"
elif magSize == 'c':
	print("You slected the 3/16th inch magnet: The Little Kahuna.\n")
	B_r = 1.32 #Tesla
	magnet = "3/16"
else:
	print("ERROR: Invalid entry. Please enter either 'a', 'b', or 'c'.")
	print("Rerun the program and try again.\n")

#Sensor position relative to magnet surface
sensor_pos = 0.015115 #position of sensor
sensor_w = 0.001 #Estimate sampling width at center distance
###

res = 1000 #data resolution
z = np.linspace(sensor_pos-sensor_w, sensor_pos+sensor_w, res)

#magnet dimensions in meters
L = 0.0254 #1 inch in m
W = 0.0254 #1 inch in m
T = 0.009525 #3/8th inch in m (thickness)
###

#Creating mag field based on K&J Magnets, Inc. specs.
B_s = lf.B_field(z, B_r, L, W, T)
###

#Linear curve fit of magnetic field in sampling region
(popt_B, pcov_B) = curve_fit(lf.B_LinFit, z, B_s, p0=None, sigma=None, bounds=(-np.inf,np.inf))

A, b = popt_B

print("Linear fit parameters:")
print("Slope: A = {}\nBias: b = {}\n".format(A, b))
######################################################################


###############Locating the Magnetometer Data#########################
path = input("Please enter the path to the data folder: ")

fileNames = os.listdir(path) #creates a list of names of files in data folder
######################################################################

#########Creating a file to store fit parameter values################
file = open("MagSusVals.txt", "w")
file.write("Data for {} inch magnets\n".format(magnet))
file.write("Name\tX\t\teps\t\tS1\t\tS2\t\tomega\n")


#######Creating arrays to be filled later with proper values#########
X_array = np.zeros(len(fileNames))
S1_array = np.zeros(len(X_array))
S2_array = np.zeros(len(X_array))
#####################################################################

#########Checking to see if "plots" directory exists################
plots_folder = "Fits"
datatxt_folder = "Fits_txt_data"
if os.path.exists(plots_folder) != True:
	os.mkdir(plots_folder)

if os.path.exists(datatxt_folder) != True:
	os.mkdir(datatxt_folder)
###################################################################

def column(matrix, i):
    return [row[i] for row in matrix]

s1_iter = np.linspace(-500, 0, 20)
s2_iter = np.linspace(-0.001, -1e-6, 50)

total_iters = len(s1_iter)*len(s2_iter)

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

density = 5240 #Intrinsic material density


###THE BEEF, BABY###
###############Fitting and data allocation############################
print("\nScanning parameter space...")
print("DON'T PANIC -- Overflow Errors are ok to see\n")
numFiles = len(fileNames)
fileCount=0
for i, name in enumerate(fileNames):
	fileCount+=1

	print("File {}/{}".format(fileCount, numFiles))

	#Determine fit params for light curves#########
	filecp = codecs.open(path+"/{}".format(name), encoding = 'cp1252')
	t_raw, T_raw = np.loadtxt(filecp, skiprows=3, delimiter=None,unpack=True)


	t_T, T_T = lf.trunc(minTrunc, maxTrunc, t_raw, T_raw)

	if np.any(T_T <= 0):
		print("Negative values detected in a dataset! Thats no good, mate.\nHere is the problem child: "+name)

	T_RAWlog = lf.matchEXP(T_T)
	t_F, T_logF = lf.dataAdj(t_T, T_RAWlog)


	def transmOmega(t, eps, S1, S2):
		Omega = T_logF[-1]
		return lf.transm(t, eps, S1, S2, Omega)


	# meanVarArray = np.zeros(total_iters)
	meanMatrix = np.zeros((total_iters, 3))


	omega = T_logF[-1]
	count = 0
	j=0
	for s1 in tqdm(s1_iter, desc=name):
		k=0
		for s2 in s2_iter:
			eps = s2*omega/(s1-s2)
			guesses = eps, s1, s2

			(poptG, pcovG) = curve_fit(transmOmega, t_F, T_logF, p0=guesses, maxfev=10000, method="dogbox", bounds=(-np.inf,np.inf))

			meanVar = np.mean(np.diag(pcovG))
			meanMatrix[count] = [j, k, abs(meanVar)]

			k+=1
			count+=1
		j+=1



	meanVarArray = column(meanMatrix, 2)
	indx_min = np.argmin(meanVarArray)
	S1_gIndx, S2_gIndx, m = meanMatrix[indx_min]

	S1g = s1_iter[int(S1_gIndx)]
	S2g = s2_iter[int(S2_gIndx)]
	epsg = S2g*omega/(S1g-S2g)
	guessArray = [epsg, S1g, S2g]

	print("\nGuesses Ready: {}\n".format(guessArray))

	(popt_T, pcov_T) = curve_fit(transmOmega, t_F, T_logF, p0=guessArray, maxfev=10000, bounds=(-np.inf,np.inf))

	#variables are redefined here. Ensure this doesnt cause issues later
	eps, S1, S2 = popt_T

	alpha = lf.alpha(S1, S2)
	beta = lf.beta(S1, S2)
	X = lf.mag_sus(density, A, S1, S2)

	X_array[i] = X
	S1_array[i] = S1
	S2_array[i] = S2

	file.write(name+"\t{:.2}\t\t{:.2}\t\t{:.2}\t\t{:.2}\t\t{:.2}\n".format(X, *popt_T, omega))

	time = np.linspace(0, maxTrunc-minTrunc, len(t_F))
	logT_fit = lf.transm(time, *popt_T, omega)

	plt.figure()
	plt.plot(t_F, T_logF, "b*", markevery=80)
	plt.plot(time, logT_fit, color="darkorange", label=name+"\nS1: {:.4}\nS2: {:.4}\nX: {:.3}".format(S1, S2, X))
	plt.legend()
	plt.xlabel("time (s)")
	plt.ylabel("log(1/T)")
	plt.savefig(plots_folder+"/{}.png".format(name), dpi=80)
	# plt.show()
	plt.close()

	datFile = open(datatxt_folder+"/fit_"+name, "w")
	datFile.write("###"+name+"\n 3/8th mag.\n")
	datFile.write("t\tlog(1/T)\tt-(fit)\tlog(1/T)-(fit)\n")

	for k in np.arange(len(t_F)):
		datFile.write("{}\t{}\t{}\t{}\n".format(t_F[k], T_logF[k], time[k], logT_fit[k]))

	datFile.close()

	#Here, since we have already scanned the large param space for one set, we can use the same findings
	#as guesses for the next set so we dont have to constantly scan the entire parameter space
	s1_iter = np.array([S1])
	s2_iter = np.array([S2])
##############################################################


###########Displaying values in command line###################
# print("Avg. S1*S2 Vals: ", np.mean(S1_array*S2_array))
# print("X Vals: ", X_array)

avgX = np.mean(X_array) #averaging magnetic suseptibility values
stdX = np.std(X_array)

print("Average Sus.: X = {:.3}\n".format(avgX))
###############################################################

file.write("AVERAGE Mag Sus:\n")
file.write("{}\n".format(avgX))
file.write("Standard Deviation:\n")
file.write("{}".format(stdX))

file.close() #closing MagSusVals.txt file

#Mag sus Gaussian Dist.
mu = avgX
sigma = stdX
x = np.linspace(mu - 3*sigma, mu + 3*sigma, 100)
normDist = stats.norm.pdf(x, mu, sigma)

tickVals = [mu - 2*sigma, mu - 1*sigma, mu, mu + 1*sigma, mu + 2*sigma]
tickLabels = ["-2σ", "-σ", "χ", "σ", "2σ"]

plt.figure()
plt.xticks(tickVals, tickLabels)
plt.vlines(mu, 0, 1, linestyle='dashed', color="black", alpha=0.25)
plt.vlines(mu - 1*sigma, 0, stats.norm.pdf(mu - 1*sigma, mu, sigma)/max(normDist), linestyle='dashed', color="black", alpha=0.25)
plt.vlines(mu + 1*sigma, 0, stats.norm.pdf(mu - 1*sigma, mu, sigma)/max(normDist), linestyle='dashed', color="black", alpha=0.25)
plt.vlines(mu - 2*sigma, 0, stats.norm.pdf(mu - 2*sigma, mu, sigma)/max(normDist), linestyle='dashed', color="black", alpha=0.25)
plt.vlines(mu + 2*sigma, 0, stats.norm.pdf(mu - 2*sigma, mu, sigma)/max(normDist), linestyle='dashed', color="black", alpha=0.25)
plt.plot(x, normDist/max(normDist), color="purple", label="χ = {:.3}\nσ = {:.3}".format(mu, sigma))
plt.legend()
plt.savefig('magSus.png', dpi=100)
plt.show()
################################################
