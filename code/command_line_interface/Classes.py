import numpy as np
import matplotlib.pyplot as plt
import lightFunctions as lf
from scipy.optimize import curve_fit
import scipy.stats as stats
import warnings
import os
import random
import codecs
from tqdm import tqdm

# modified to avg last 100 data points for omega


class MagFieldFit:

    def __init__(self, B_r, t=0.009525):
        self.B_r = B_r
        self.sensor_pos = 0.015115
        self.sensor_w = 0.001
        self.res = 1000 #data resolution
        self.z = np.linspace(self.sensor_pos-self.sensor_w, self.sensor_pos+self.sensor_w, self.res)
        #magnet dimensions in meters
        self.L = 0.0254 #1 inch in m
        self.W = 0.0254 #1 inch in m
        #self.T = 0.009525
        self.T = t #3/8th inch in m (thickness)
        #self.density = 5150 #Intrinsic material density
        print("magnet thickness: " + str(self.T))

    def get_sensor_pos(self):
        return self.sensor_pos

    def get_magnet_Dim(self):
        return "Length: {} Width: {} Thickness: {}".format(self.L, self.W, self.T)

    def get_magFitParams(self):
        #Creating mag field based on K&J Magnets, Inc. specs.
        B_s = lf.B_field(self.z, self.B_r, self.L, self.W, self.T)
        #Linear curve fit of magnetic field in sampling region
        (popt_B, pcov_B) = curve_fit(lf.B_LinFit, self.z, B_s, p0=None, sigma=None, bounds=(-np.inf,np.inf))

        A, b = popt_B

        return [A, b]


class ParamGuesser:

    def __init__ (self, path, file=None):
        self.path = path
        if file is None:
            self.fileNames = os.listdir(self.path)
        else:
            self.fileNames = [file]
        self.density = 5150 #5240 #Intrinsic material density

    def get_paramGuesses(self, minTrunc, maxTrunc):

        warnings.filterwarnings("ignore")

        # s1_iter = np.linspace(-500, 0, 20)
        # s2_iter = np.linspace(-0.001, -1e-6, 50)
        # s1_iter = np.linspace(-2000, -250, 20)
        s1_iter = np.linspace(-2000, -500, 40)
        # s2_iter = np.linspace(-0.01, -1e-6, 50)
        s2_iter = np.linspace(-0.01, -1e-6, 40)



        total_iters = len(s1_iter)*len(s2_iter)
        testFile = self.fileNames[random.randint(0, len(self.fileNames)-1)]

        #Determine fit params for light curves#########
        filecp = codecs.open(self.path+"/{}".format(testFile), encoding = 'cp1252')
        t_raw, T_raw = np.loadtxt(filecp, skiprows=3, delimiter=None,unpack=True)

        t_T, T_T = lf.trunc(minTrunc, maxTrunc, t_raw, T_raw)

        if np.any(T_T <= 0):
            print("Negative values detected in a dataset! Thats no good, mate.\nHere is the problem child: "+name)

        T_RAWlog = lf.matchEXP(T_T)
        t_F, T_logF = lf.dataAdj(t_T, T_RAWlog)

        def transmOmega(t, eps, S1, S2):
            Omega = np.mean(T_logF[-101:-1])
            return lf.transm(t, eps, S1, S2, Omega)

        # meanVarArray = np.zeros(total_iters)
        meanMatrix = np.zeros((total_iters, 3))
        omega = np.mean(T_logF[-101:-1])

        print("\n")
        j=0
        count=0
        for s1 in tqdm(s1_iter, desc="Scanning Parameters", ascii=" ▖▘▝▗▚▞█"):
            k=0
            for s2 in s2_iter:
                eps = s2*omega/(s1-s2)
                guesses = eps, s1, s2

                (poptG, pcovG) = curve_fit(transmOmega, t_F, T_logF, p0=guesses, maxfev=10000, bounds=(-np.inf,np.inf))

                meanVar = np.mean(np.diag(pcovG))
                meanMatrix[count] = [j, k, abs(meanVar)]

                k+=1
                count+=1
            j+=1

        meanVarArray = lf.column(meanMatrix, 2)
        indx_min = np.argmin(meanVarArray)
        S1_gIndx, S2_gIndx, m = meanMatrix[indx_min]
        S1g = s1_iter[int(S1_gIndx)]
        S2g = s2_iter[int(S2_gIndx)]
        epsg = S2g*omega/(S1g-S2g)
        guessArray = [epsg, S1g, S2g]

        return guessArray



    def analyze(self, minTrunc, maxTrunc, guesses, magFieldParams):

        A = magFieldParams[0]
        b = magFieldParams[1]

        #########Creating a file to store fit parameter values################
        file = open("MagSusVals.txt", "w")
        # file.write("Data for {} inch magnets\n".format(magnet))
        file.write("Name\tX\t\teps\t\tS1\t\tS2\t\tomega\n")

        #########Checking to see if "plots" directory exists################
        plots_folder = "Fits"
        datatxt_folder = "Fits_txt_data"
        if os.path.exists(plots_folder) != True:
            os.mkdir(plots_folder)

        if os.path.exists(datatxt_folder) != True:
            os.mkdir(datatxt_folder)
        ###################################################################

        #allocating arrays to store data later
        X_array = np.zeros(len(self.fileNames))
        S1_array = np.zeros(len(X_array))
        S2_array = np.zeros(len(X_array))


        # print("\nScanning parameter space...")
        print("\nDON'T PANIC -- Overflow Errors are ok to see\n")
        numFiles = len(self.fileNames)
        fileCount=0

        for i, name in enumerate(self.fileNames):
            fileCount+=1
            print("File {}/{}".format(fileCount, numFiles))
            print(name)

            #Determine fit params for light curves#########
            filecp = codecs.open(self.path+"/{}".format(name), encoding = 'cp1252')
            t_raw, T_raw = np.loadtxt(filecp, skiprows=3, delimiter=None,unpack=True)

            t_T, T_T = lf.trunc(minTrunc, maxTrunc, t_raw, T_raw)

            if np.any(T_T <= 0):
                print("Negative values detected in a dataset! Thats no good, mate.\nHere is the problem child: "+name)

            T_RAWlog = lf.matchEXP(T_T)
            t_F, T_logF = lf.dataAdj(t_T, T_RAWlog)

            def transmOmega(t, eps, S1, S2):
                Omega = np.mean(T_logF[-101:-1])
                return lf.transm(t, eps, S1, S2, Omega)

            omega = np.mean(T_logF[-101:-1])


            (popt, pcov) = curve_fit(transmOmega, t_F, T_logF, p0=guesses, maxfev=10000, bounds=(-np.inf,np.inf))


            eps, S1, S2 = popt


            alpha = lf.alpha(S1, S2)
            beta = lf.beta(S1, S2)
            X = lf.mag_sus(self.density, A, S1, S2)

            X_array[i] = X
            S1_array[i] = S1
            S2_array[i] = S2

            print(str(X) + "\t" + str(eps) + "\t" + str(S1) + "\t" + str(S2) + "\t" + str(omega))

            file.write(name+"\t{:.2}\t\t{:.2}\t\t{:.2}\t\t{:.2}\t\t{:.2}\n".format(X, *popt, omega))


            time = np.linspace(0, maxTrunc-minTrunc, len(t_F))
            logT_fit = lf.transm(time, *popt, omega)

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

            del(t_F, T_logF)


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
        #plt.show()
        ################################################

        return None
