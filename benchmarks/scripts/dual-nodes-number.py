import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import json
import sys

x_data = np.array([5, 10, 15, 20, 25])
check_permission_error = 5

if len(sys.argv) > 2:
    stats_file = sys.argv[1]
    stats_file2 = sys.argv[2]
else:
    stats_file = '../results/nodes-number-ss.json'
    stats_file2 = '../results/nodes-number-pre.json'

with open(stats_file) as json_file:
    data = json.load(json_file)
enc = []
dec = []
for item in data:
    enc.append(item['encryption'])
    dec.append(item['decryption'])
# means.sort()
# median.sort()
enc = np.array(enc)
dec = np.array(dec)

with open(stats_file2) as json_file:
    data2 = json.load(json_file)
enc2 = []
dec2 = []
for item in data2:
    enc2.append(item['encryption'] + item['keys'])
    dec2.append(item['decryption'] + check_permission_error)
# means.sort()
# median.sort()
enc2 = np.array(enc2)
dec2 = np.array(dec2)

plt.grid(axis='y', color='0.95', zorder=0)

plt.bar(x_data - 0.75, enc, 1.5, color='brown',
        edgecolor='black', align='center', zorder=3)
plt.bar(x_data - 0.75, dec, 1.5, color='darkred', edgecolor='black',
        bottom=enc, align='center', zorder=3)

plt.bar(x_data + 0.75, enc2, 1.5, color='royalblue',
        edgecolor='black', align='center', zorder=3)
plt.bar(x_data + 0.75, dec2, 1.5, color='darkblue', edgecolor='black',
        bottom=enc2, align='center', zorder=3)

#plt.yticks(np.arange(0, 1200, 100))
plt.xticks(np.array([5, 10, 15, 20, 25]))
plt.ylabel('latency (ms)')
plt.xlabel('nodes number')


patch01 = mpatches.Patch(color='brown', label='SS (left)')
patch02 = mpatches.Patch(color='royalblue', label='PRE (right)')
patch1 = mpatches.Patch(color='silver', label='encr + keys distr (medium)')
patch2 = mpatches.Patch(color='dimgray', label='decryption (dark)')

plt.legend(handles=[patch01, patch02, patch1, patch2])

# display the plot
plt.savefig('../dual-nodes-number.png', bbox_inches='tight', dpi=300)
