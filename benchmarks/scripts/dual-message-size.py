import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import json
import sys

x_data_int = np.array([10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000,
                       1000000, 5000000, 10000000])
x_data = np.array(['10\nB', '50\nB', '100\nB', '500\nB', '1\nKB', '5\nKB', '10\nKB', '50\nKB', '100\nKB', '500\nKB',
                   '1\nMB', '5\nMB', '10\nMB'])
check_permission_error = 5

if len(sys.argv) > 2:
    stats_file = sys.argv[1]
    stats_file2 = sys.argv[2]
else:
    stats_file = '../results/message-size-ss.json'
    stats_file2 = '../results/message-size-pre.json'

with open(stats_file) as json_file:
    data = json.load(json_file)
enc = []
dec = []
tot = []
for item in data:
    enc.append(item['encryption'] + item['keys'])
    dec.append(item['decryption'])
    tot.append(item['decryption'] + item['encryption'] + item['keys'])
# means.sort()
# median.sort()
enc = np.array(enc)
dec = np.array(dec)
tot = np.array(tot)

with open(stats_file2) as json_file:
    data2 = json.load(json_file)
enc2 = []
dec2 = []
tot2 = []
for item in data2:
    enc2.append(item['encryption'] + item['keys'])
    dec2.append(item['decryption'] + check_permission_error)
    tot2.append(item['decryption'] + check_permission_error +
                item['encryption'] + item['keys'])
# means.sort()
# median.sort()
enc2 = np.array(enc2)
dec2 = np.array(dec2)
tot2 = np.array(tot2)


# plot the data
plt.plot(x_data_int, tot/x_data_int, color='brown')

plt.plot(x_data_int, tot2/x_data_int, color='royalblue')

plt.xscale('log')
plt.yscale('log')
plt.xticks(x_data_int, x_data)

plt.ylabel('relative latency ms/B (log)')
plt.xlabel('message size (log)')

patch1 = mpatches.Patch(color='brown', label='SS')
patch2 = mpatches.Patch(color='royalblue', label='PRE')

plt.legend(handles=[patch1, patch2])

plt.savefig('../dual-message-size.png', bbox_inches='tight', dpi=300)
