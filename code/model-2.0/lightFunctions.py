import numpy as np


'''The idea for this program is to create a series of functions
   that do the certain tasks of analyzing the light curve data
   from the experimentation. The tasks for these functions are
   as follows:
   1) Using gemetric inputs and initial strength of the magnet,
   	  determine the linear fit parameters of the magnetic field

   2) Adjust the data properly. Meaning, truncate the data set
      where the 15 second mark is at t = 0

   3) Take the log of the recip. of the data

   4) Create a funciton which, given some input values produces
   	  a light curve that matches the shape of log(1/T)

   5) use a fit to determine fit params of the fit function

   6) From the fit params, determine alpha, beta, and supsequently
      the magnetic suseptability

   '''

#Magnetic Field###########################################
def B_field(x, B_r, L, W, T):
   return (B_r/np.pi)*(np.arctan((L*W)/(2*x*np.sqrt(4*x**2+L**2+W**2)))-np.arctan((L*W)/(2*(x+T)*np.sqrt(4*(x+T)**2+L**2+W**2))))

def B_LinFit(x, A, b):
   return A*x+b


#Transmittance############################################
def transm(t, eps, S1, S2, omega):
   '''funtion that models log(1/T) and includes fit params
   that will give suseptability'''

   return eps*(-(S1/S2)*np.exp(S2*t)+np.exp(S1*t)) + omega

def transm2(t, S1, S2, omega):
   '''funtion that models log(1/T) and uses taylor expansion of exp'''

   return omega/(S1-S2)*(S2*np.exp(S1*t)-S1*np.exp(S2*t))

def der_transm(t, eps, S1, S2):
   '''Derivative of transm function'''

   return S1*(eps*np.exp(S1*t) + np.exp(S2*t))

def alpha(S1, S2):
   '''A ratio between drag constant and mass C_D/m
   can be found with the S1/S2 fit params'''

   return -S1-S2

def beta(S1, S2):
   '''Holds the value of magnetic suseptability. Comprised
   of fit params S1/S2'''

   return S1*S2

def mag_sus(p, mfs, S1, S2):
   '''p ------ material density
      mfs ---- slope from the linear fit to the magnetic field
      S1/S2 -- fit params found in exponentials'''
   mu_0 = np.pi*4e-7
   return S1*S2*(mu_0*p/mfs**2)


#Data adjustment##############################################
def matchEXP(T):
   # T_alt = T*1.44e-6
   #T_m = max(T)
   return T   #np.log10(max(T_alt)/T_alt)

def trunc(low, high, x, y):
   '''Takes high and low inputs and truncates an array
      between those values. Here it is used to truncate
      the independent variable array (in this case time)
      and adjust the dependent variable array accordingly
      (in this case the transmittanace data)'''

   if len(x)!=len(y):
      print("Array sizes do not match")

   indx = np.where((x>=low) & (x<=high))

   return x[indx], y[indx]

def dataAdj(x, y):
   '''takes the starting points and adusts it at point
      (0,0)'''

   if len(x)!=len(y):
      print("Array sizes do not match")

   x_trans = x[0]
   y_trans = y[0]

   x_new = x-x_trans
   y_new = y-y_trans

   return x_new, y_new

def column(matrix, i):
    return [row[i] for row in matrix]
#######
