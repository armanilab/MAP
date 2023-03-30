import numpy as np
import matplotlib.pyplot as plt
import lightFunctions as lf
from scipy.optimize import curve_fit
import os
import codecs

'''The goal of this program is to use the functions from
   lightFunctions.py and analyze the data from MULTIPLE experimentally
   produced light curve data. The comparisions and fits should
   be done using the log(1/T), where T is the raw data output
   from the experiemnt. The process of analyzing would be as 
   follows:
	1) import the data from n number of data sets located in a
	   file labeled "lightData"
	2) truncate the dataset to have t=0 at the 15 second mark
	   of the raw data
	3) Use functions to fit the fit function to the log(1/T) of
	   the truncated and translated experimental data
	4) Extract the fit params and determine mag. sus.
	5) plot the fit and the log(1/T) from the experimental data
	6) write a txt file with all the information regarding particle, 
	   fluid, and magnetit information (particle type, fluid type,
	   magnet geometry, mag. sus. value)'''


##########Determine fit params for magnetic field##############

sensor_pos = 0.015115 #position of sensor
sensor_w = 0.001 #Estimate sampling width at center distance
res = 1000 #data resolution

z = np.linspace(sensor_pos-sensor_w, sensor_pos+sensor_w, res)

B_r = 1.48 #Tesla

#magnet dimensions in meters
L = 0.0254 #1 inch in m
W = 0.0254 #1 inch in m
T = 0.009525 #3/8th inch in m (thickness)

B_s = lf.B_field(z, B_r, L, W, T)

(popt_B, pcov_B) = curve_fit(lf.B_LinFit, z, B_s, p0=None, sigma=None, bounds=(-np.inf,np.inf))

A, b = popt_B

print("A = {}\nb = {}".format(A, b))
######################################################################



## initial guess for fit function (this will be very important to get right)
eps = -0.0005 
S1 = -1000
S2 = -0.05#-0.001
omega = -1 #-1.12
guesses = np.array([eps,S1,S2,omega])

########################################################################

density = 5240 #Intrinsic material density

########Uploading the light curve data################################
path = "lightData/lexieData2/"
fileNames = os.listdir(path)
######################################################################


#########Creating a file to store fit parameter values################
file = open("MagSusVals.txt", "w")
file.write("Data for 3/8 inch magnets\n")
file.write("Name\tX\t\teps\t\tS1\t\tS2\t\tomega\n")


#######Creating arrays to be filled later with proper values#########
X_array = np.zeros(len(fileNames))
S1_array = np.zeros(len(X_array))
S2_array = np.zeros(len(X_array))
#####################################################################


#########Checking to see if "plots" directory exists################
plots_folder = "plotsTest"
datatxt_folder = "txt_data"
if os.path.exists(plots_folder) != True:
	os.mkdir(plots_folder) 

if os.path.exists(datatxt_folder) != True:
	os.mkdir(datatxt_folder) 
###################################################################


S1g = np.array([-1e3, -3.9e3, -400])
S2g = np.array([-0.02, -0.04, -0.02])

###############Fitting and data allocation############################
for i, name in enumerate(fileNames):
	#Determine fit params for light curves#########
	filecp = codecs.open(path+"/{}".format(name), encoding = 'cp1252')
	t_raw, T_raw = np.loadtxt(filecp, skiprows=3, delimiter=None,unpack=True)
	
	t_T, T_T = lf.trunc(17, 60, t_raw, T_raw)
	
	if np.any(T_T <= 0):
		print("your fucked\nHere is the problem child: "+name)
	
	T_RAWlog = lf.matchEXP(T_T)
	t_F, T_logF = lf.dataAdj(t_T, T_RAWlog)

	##################
	omega = T_logF[-1]
	S1 = S1g[i]
	S2 = S2g[i]
	eps = S2*omega/(S1-S2)
	##################

	###
	print("\n"+name+"\n")
	###Curve fitting trasm function with EXP data##
	(popt_T, pcov_T) = curve_fit(lf.transm, t_F, T_logF, p0=[eps, S1, S2, omega], maxfev=10000, bounds=(-np.inf,np.inf))
	
	#variables are redefined here. Ensure this doesnt cause issues later
	eps, S1, S2, omega = popt_T

	alpha = lf.alpha(S1, S2)
	beta = lf.beta(S1, S2)
	X = lf.mag_sus(density, A, S1, S2)

	X_array[i] = X
	S1_array[i] = S1
	S2_array[i] = S2

	file.write(name+"\t{:.2}\t\t{:.2}\t\t{:.2}\t\t{:.2}\t\t{:.2}\n".format(X, *popt_T))

	time = np.linspace(0, 43, len(t_F))
	logT_fit = lf.transm(time, *popt_T)

	plt.figure()
	plt.plot(t_F, T_logF)
	plt.plot(time, logT_fit, label=name+"\nS1: {:.4}\nS2: {:.4}\nX: {:.3}".format(S1, S2, X))
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


##############################################################


###########Displaying values in command line###################
print("Avg. S1*S2 Vals: ", np.mean(S1_array*S2_array))
print("X Vals: ", X_array)

avgX = np.mean(X_array) #averaging magnetic suseptibility values

print("Average Sus.: X = {:.3}\n".format(avgX))
###############################################################


file.write("AVERAGE Mag Sus:\n")
file.write("{}".format(avgX))

file.close() #closing MagSusVals.txt file
################################################
