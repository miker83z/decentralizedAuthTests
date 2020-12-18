import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import json
import sys

x_data = np.arange(1, 26, 1)
check_permission_error = 3

if len(sys.argv) > 2:
    stats_file = sys.argv[1]
    stats_file2 = sys.argv[2]
else:
    stats_file = '../results/threshold-ss.json'
    stats_file2 = '../results/threshold-pre.json'

with open(stats_file) as json_file:
    data = json.load(json_file)
enc = []
key = []
dec = []
tot = []
for item in data:
    enc.append(item['encryption'])
    key.append(item['keys'])
    dec.append(item['decryption'])
    tot.append(item['encryption'] + item['keys'])
# means.sort()
# median.sort()
enc = np.array(enc)
key = np.array(key)
dec = np.array(dec)
tot = np.array(tot)

with open(stats_file2) as json_file:
    data2 = json.load(json_file)
enc2 = []
key2 = []
dec2 = []
tot2 = []
for item in data2:
    enc2.append(item['encryption'])
    key2.append(item['keys'])
    dec2.append(item['decryption'] + check_permission_error)
    tot2.append(item['encryption'] + item['keys'])
# means.sort()
# median.sort()
enc2 = np.array(enc2)
key2 = np.array(key2)
dec2 = np.array(dec2)
tot2 = np.array(tot2)

plt.bar(x_data - 0.175, enc, .35, color='lightcoral',
        edgecolor='black', align='center')
plt.bar(x_data - 0.175, key, .35, color='brown', edgecolor='black',
        bottom=enc, align='center')
plt.bar(x_data - 0.175, dec, .35, color='darkred', edgecolor='black',
        bottom=tot, align='center')

plt.bar(x_data + 0.175, enc2, .35, color='lightsteelblue',
        edgecolor='black', align='center')
plt.bar(x_data + 0.175, key2, .35, color='royalblue', edgecolor='black',
        bottom=enc2, align='center')
plt.bar(x_data + 0.175, dec2, .35, color='darkblue', edgecolor='black',
        bottom=tot2, align='center')

#plt.yticks(np.arange(0, 1200, 100))
plt.xticks(np.arange(1, 26, 1))
plt.ylabel('latency (ms)')
plt.xlabel('threshold value')

#plt.grid(axis='x', color='0.95')

patch01 = mpatches.Patch(color='brown', label='SS (left)')
patch02 = mpatches.Patch(color='royalblue', label='PRE (right)')
patch1 = mpatches.Patch(color='whitesmoke', label='encryption (light)')
patch2 = mpatches.Patch(color='silver', label='keys distr (medium)')
patch3 = mpatches.Patch(color='dimgray', label='decryption (dark)')

plt.legend(handles=[patch01, patch02, patch1, patch2, patch3])

# display the plot
figure = plt.gcf()
figure.set_size_inches(10, 5)
plt.savefig('../dual-threshold.png', bbox_inches='tight', dpi=300)
