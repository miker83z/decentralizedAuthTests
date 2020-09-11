import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import json
import sys

x_data = np.array([5, 10, 15, 20, 25])
check_permission_error = 3

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
tot = []
for item in data:
    enc.append(item['encryption'])
    dec.append(item['decryption'])
    tot.append(item['decryption'] + item['encryption'])
# means.sort()
# median.sort()
enc = np.array(enc)
dec = np.array(dec)
tot = np.array(tot)
a, b = np.polyfit(x_data, enc, deg=1)
enc_est = a * x_data + b
a, b = np.polyfit(x_data, dec, deg=1)
dec_est = a * x_data + b
a, b = np.polyfit(x_data, tot, deg=1)
tot_est = a * x_data + b

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
a, b = np.polyfit(x_data, enc2, deg=1)
enc_est2 = a * x_data + b
a, b = np.polyfit(x_data, dec2, deg=1)
dec_est2 = a * x_data + b
a, b = np.polyfit(x_data, tot2, deg=1)
tot_est2 = a * x_data + b


# plot the data
#fig = plt.figure()
#ax = fig.add_subplot(1, 1, 1)
#plt.plot(x_data, enc, color='tab:green', label='encryption')
#plt.plot(x_data, dec, color='tab:orange', label='decryption')
#plt.plot(x_data, tot, color='tab:blue', label='total')

plt.plot(x_data, enc_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data, dec_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data, tot_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data, enc, 'v', color='tab:blue', label='encryption', markersize=4)
plt.plot(x_data, dec, '*', color='tab:blue', label='decryption')
plt.plot(x_data, tot, 's', color='tab:blue', label='total')

plt.plot(x_data, enc_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data, dec_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data, tot_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data, enc2, 'v', color='tab:orange',
         label='encryption', markersize=4)
plt.plot(x_data, dec2, '*', color='tab:orange', label='decryption')
plt.plot(x_data, tot2, 's', color='tab:orange', label='total')

#plt.yticks(np.arange(0, 1200, 100))
plt.xticks(np.array([5, 10, 15, 20, 25]))
plt.ylabel('latency (ms)')
plt.xlabel('nodes number')

plt.grid(axis='x', color='0.95')

triangle = mlines.Line2D([], [], color='w', marker='v', linestyle='None', markeredgecolor='black',
                         markersize=5, label='encryption + keys distribution')
star = mlines.Line2D([], [], color='w', marker='*', linestyle='None', markeredgecolor='black',
                     markersize=5, label='decryption')
square = mlines.Line2D([], [], color='w', marker='s', linestyle='None', markeredgecolor='black',
                       markersize=5, label='total')
patch1 = mpatches.Patch(color='tab:blue', label='SS')
patch2 = mpatches.Patch(color='tab:orange', label='PRE')

plt.legend(handles=[patch1, patch2,
                    triangle, star, square])

# display the plot
plt.savefig('../dual-nodes-number.png', bbox_inches='tight', dpi=300)
