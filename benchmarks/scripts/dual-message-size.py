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
check_permission_error = 3

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
a, b = np.polyfit(x_data_int, enc, deg=1)
enc_est = a * x_data_int + b
a, b = np.polyfit(x_data_int, dec, deg=1)
dec_est = a * x_data_int + b
a, b = np.polyfit(x_data_int, tot, deg=1)
tot_est = a * x_data_int + b

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
a, b = np.polyfit(x_data_int, enc2, deg=1)
enc_est2 = a * x_data_int + b
a, b = np.polyfit(x_data_int, dec2, deg=1)
dec_est2 = a * x_data_int + b
a, b = np.polyfit(x_data_int, tot2, deg=1)
tot_est2 = a * x_data_int + b


# plot the data
# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# plt.plot(x_data, enc, color='tab:green', label='encryption')
# plt.plot(x_data, dec, color='tab:orange', label='decryption')
# plt.plot(x_data, tot, color='tab:blue', label='total')

#plt.plot(x_data_int, enc_est2, '--', color='tab:brown', alpha=0.5)
#plt.plot(x_data_int, dec_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, tot_est2, '--', color='tab:brown', alpha=0.5)
# plt.plot(x_data_int, enc2, 'v', color='tab:orange', label = 'encryption', markersize = 4)
# plt.plot(x_data_int, dec2, '*', color='tab:orange', label='decryption')
plt.plot(x_data_int, tot2, 's', color='tab:orange', label='total')

#plt.plot(x_data_int, enc_est, '--', color='tab:brown', alpha=0.5)
#plt.plot(x_data_int, dec_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, tot_est, '--', color='tab:brown', alpha=0.5)
# plt.plot(x_data_int, enc, 'v', color='tab:blue', label = 'encryption', markersize = 4)
# plt.plot(x_data_int, dec, '*', color='tab:blue', label='decryption')
plt.plot(x_data_int, tot, 's', color='tab:blue', label='total')

plt.xscale('log')
# plt.yticks(np.arange(0, 1200, 100))
plt.xticks(x_data_int, x_data)

plt.ylabel('latency (ms)')
plt.xlabel('message size (log scale)')

'''
triangle = mlines.Line2D([], [], color='w', marker='v', linestyle='None', markeredgecolor='black',
                         markersize=5, label='encr + keys distr')
star = mlines.Line2D([], [], color='w', marker='*', linestyle='None', markeredgecolor='black',
                     markersize=5, label='decryption')
square = mlines.Line2D([], [], color='w', marker='s', linestyle='None', markeredgecolor='black',
                       markersize=5, label='total')
'''
patch1 = mpatches.Patch(color='tab:blue', label='SS')
patch2 = mpatches.Patch(color='tab:orange', label='PRE')

plt.legend(handles=[patch1, patch2])

plt.savefig('../dual-message-size.png', bbox_inches='tight', dpi=300)
