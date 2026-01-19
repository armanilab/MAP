# thesis formatting
from matplotlib import font_manager as fm
from numpy import average, log10, sum, mean, genfromtxt, min
from matplotlib import pyplot as plt
from matplotlib.legend_handler import HandlerLine2D, HandlerTuple

### DIMENSIONS ###
full_width = 6.25
dpi = 600
dpi_disp = 300
dpi_save = 1200


### COLORS ###
shades_purple = ["#6f4c9b", "#9b62a7", "#b58fc2"]
shades_blue = ["#1965b0", "#6195cf", "#7bafde"]
shades_green = ["#4eb265", "#90c987", "#cae0ab"]
shades_yellow = ["#f4a736", "#f7cb45", "#f7f056"]
shades_orange = ["#e65518", "#e67932", "#ee8026"]
shades_red = ["#95211b", "#b9221e", "#da2222"]
shades_grey = ["#333333", "#555555", "#777777"]
shades_brown = ["#95211b", "#721e17", "#521a13"]
all_colors = [shades_grey, shades_purple, shades_blue, shades_green, shades_yellow,
    shades_orange, shades_red]
rep_colors = [a[0] for a in all_colors]

# rainbow color scheme from: https://personal.sron.nl/~pault/#sec:sequential
rainbow_grey = '#777777'
rainbow = ['#d1bbd7', '#ae76a3', '#882e72', '#1965b0', '#5289c7', '#7bafde',
    '#4eb265', '#90c987', '#cae0ab', '#f7f056', '#f6c141', '#f1932d',
    '#e8601c', '#dc050c', rainbow_grey]

# vibrant color scheme from https://personal.sron.nl/~pault/#sec:sequential
purple = '#8645a3'
darker_blue = '#002e91'
dark_blue = '#0077bb'
cyan = '#33bbee'
teal = '#009988'
green = '#00dc79'
yellow = '#ffc800'
orange = '#ee7733'
red = '#cc3311'
maroon = '#a30011'
magenta = '#ee3377'
pink = '#ee85b7'
vib_grey = '#bbbbbb'
# rainbow_grey
black = '#000000'

vib_full = [darker_blue, dark_blue, cyan, teal, green, yellow,
    orange, red, pink, purple, vib_grey]
# blue, cyan, teal, orange, red, magenta , grey
vib_colors = [darker_blue, cyan, green, orange, red, purple, vib_grey]
vib_ordered = [orange, dark_blue, cyan, magenta, red, teal, vib_grey]
vib_3 = [cyan, teal, red]
trial_colors = [purple, cyan, orange]
trial_markers = ['o', 'D', 's']

### FONTS ###
fs = 10 # font-size
ticks_fs = 8
pfont = 'Avenir'
lfont = fm.FontProperties(family='Avenir', size=ticks_fs)
ax_label_fontdict = {'fontsize': fs, 'fontfamily': pfont}
ax_ticks_fontdict = {'fontsize': ticks_fs, 'fontfamily': pfont}
avenir_bold = fm.FontProperties(fname='avenir_bold.ttf', size=10)
garamond = fm.FontProperties(family='Garamond', weight='bold', size=12)

### PLOT PARAMETERS ###
markers = ['o', 's', 'D']
m_size = 5
m_width = 1.5
legend_colors = ["#000000", "#444444", "#777777"]
l_width = 1.5
h_length = 1.5 # for legend
h_length_short = 1 # for legend
h_length_dashed = 2.5
h_length_dotted = 1.75
borderpad_tight = 0.5
borderpad = 0.75
pad_tight = 0.5
pad_loose = 1.0

mkwargs = {'markersize': m_size, 'markeredgewidth': m_width,
    'markerfacecolor': 'none'}

plt.rcParams.update({'font.size': ticks_fs, 'font.family': 'Avenir',
    'axes.titlesize': fs, 'legend.fontsize': ticks_fs,
    'axes.labelsize': ticks_fs, 'lines.linewidth': l_width,
    'lines.markerfacecolor': 'none', 'lines.markersize': m_size,
    'lines.markeredgewidth': m_width, 'legend.borderpad': borderpad,
    'legend.edgecolor': black, 'legend.handlelength': h_length,
    'mathtext.default': 'regular',
})

# for tuples in legends, use this import statement:
# from matplotlib.legend_handler import HandlerLine2D, HandlerTuple
# and add this as an argument to the leg_ax.legend() call:
# handler_map={tuple: HandlerTuple(ndivide=None)}


def prep_legax(leg_axes):
    for leg_ax in leg_axes:
        leg_ax.spines['top'].set_visible(False)   # Hide top spine
        leg_ax.spines['right'].set_visible(False) # Hide right spine
        leg_ax.spines['left'].set_visible(False)
        leg_ax.spines['bottom'].set_visible(False)
        leg_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

# file processing stuff
df = ['1', '2', '3'] # default
alt = ['4', '5', '6']
c_ids = ['w', 'x', 'y', 'z']
cs = [100, 80, 60, 40]

n = 20
def calibrate(lux, c0):
    # convert to transmission
    e_0 = average(lux[-n:]) # "water" value
    transmission = lux / e_0
    # convert from transmission to attenuation
    att = -log10(transmission)

    # determine c vs. att linear relationship
    att0 = att[0]
    attf = average(att[-n:])

    # convert attenuation to concentration
    conc = c0 / (att0 - attf) * att + attf * c0 / (attf - att0)
    return conc

def lin_fit(x, a, b):
    return a * x + b

def calculate_rsq(slope, int, xs, ys):
    y_model = lin_fit(xs, slope, int)
    residuals = ys - y_model
    ss_res = sum(residuals ** 2)
    ss_total = sum((ys - mean(ys)) ** 2)
    r_sq = 1 - ss_res / ss_total
    return r_sq

def calculate_resp_time(file_path):
    data = genfromtxt(file_path)
    time = data[:, 0]
    lux = data[:, 1]

    rel_lux = lux - min(lux)
    end_mean = mean(rel_lux[-20:])
    #end_std_dev = np.std(re_lux[-20:])
    ninety_threshold = end_mean * 0.9
    above_times = time[rel_lux >= ninety_threshold]

    return above_times[0] # return first time above threshold
