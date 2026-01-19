# plot response data for testing over time
#
# Lexie Scholtz
# Created 2025.09.30

ver = 1.0
to_save = True

import sys
import numpy as np
from matplotlib import pyplot as plt
from qc_formats import *
from matplotlib import gridspec as gridspec

a_avgs = [27.580, 21.585, 32.430]
a_stds = [4.929, 1.953, 11.160]
b_avgs = [56.751, 116.725, 257.620]
b_stds = [4.191, 7.231, 17.943]
a_dates = [1, 11, 13]
b_dates = [2, 11, 13]
c_dates = [1, 13]
c_avgs = [116.981, 22.104]
c_stds = [19.805, 0.361]
e_dates = [3, 8, 13]
e_avgs = [24.744, 25.160, 27.883]
e_stds = [1.565, 0.485, 1.982]

fig, ax = plt.subplots(1, 1, figsize=(4, 3))

mkwargs = {'marker': 'o', 'capsize': m_size-1, 'elinewidth': l_width}
ax.errorbar(a_dates, a_avgs, a_stds, **mkwargs, label='A')
ax.errorbar(b_dates, b_avgs, b_stds, **mkwargs, label='B')
ax.errorbar(c_dates, c_avgs, c_stds, **mkwargs, label='C')
ax.errorbar(e_dates, e_avgs, e_stds, **mkwargs, label='E')

ax.set_xlabel('Month')
ax.set_xticks(range(1, 14), ['9/24', '10/24', '11/24', '12/24', '1/25', '2/25', '3/25', '4/25', '5/25', '6/25', '7/25', '8/25', '9/25'], rotation=60)
ax.set_ylabel('Response time (s)')
ax.legend(loc='upper left', ncol=2)
# --- SAVE FIG ---
plt.tight_layout(pad=pad_loose)

img_name = './' + sys.argv[0][:-3] + '_' + str(ver) + '.png'

if not to_save:
    # show fig - previews only
    print('displaying ' + img_name)
    plt.show()
else:
    # save fig
    plt.savefig(img_name, dpi=dpi_save)
    print('saved file as: ' + img_name)
