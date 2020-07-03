import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import json
import sys

x_data_int = np.array([10, 50, 100, 500, 1000, 5000,
                       10000, 50000, 100000, 500000, 1000000])
x_data = np.array(['10\nB', '50\nB', '100\nB', '500\nB', '1\nKB',
                   '5\nKB', '10\nKB', '50\nKB', '100\nKB', '500\nKB', '1\nMB'])

stats_file = sys.argv[1]
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
a, b = np.polyfit(x_data_int, enc, deg=1)
enc_est = a * x_data_int + b
a, b = np.polyfit(x_data_int, dec, deg=1)
dec_est = a * x_data_int + b
a, b = np.polyfit(x_data_int, tot, deg=1)
tot_est = a * x_data_int + b

stats_file2 = sys.argv[2]
with open(stats_file2) as json_file:
    data2 = json.load(json_file)
enc2 = []
dec2 = []
tot2 = []
for item in data2:
    enc2.append(item['encryption'])
    dec2.append(item['decryption'])
    tot2.append(item['decryption'] + item['encryption'])
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
#fig = plt.figure()
#ax = fig.add_subplot(1, 1, 1)
#plt.plot(x_data, enc, color='tab:green', label='encryption')
#plt.plot(x_data, dec, color='tab:orange', label='decryption')
#plt.plot(x_data, tot, color='tab:blue', label='total')

plt.plot(x_data_int, enc_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, dec_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, tot_est2, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, enc2, 'o', color='tab:orange', label='encryption')
plt.plot(x_data_int, dec2, '*', color='tab:orange', label='decryption')
plt.plot(x_data_int, tot2, 's', color='tab:orange', label='total')

plt.plot(x_data_int, enc_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, dec_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, tot_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, enc, 'o', color='tab:blue', label='encryption')
plt.plot(x_data_int, dec, '*', color='tab:blue', label='decryption')
plt.plot(x_data_int, tot, 's', color='tab:blue', label='total')

plt.xscale('log')
#plt.yticks(np.arange(0, 1200, 100))
plt.xticks(x_data_int, ['10\nB', '50\nB', '100\nB', '500\nB', '1\nKB', '5\nKB', '10\nKB', '50\nKB', '100\nKB', '500\nKB',
                        '1\nMB'])

plt.ylabel('time [ms]')
plt.xlabel('length of message')

star = mlines.Line2D([], [], color='w', marker='*', linestyle='None', markeredgecolor='black',
                     markersize=7, label='decryption')
circle = mlines.Line2D([], [], color='w', marker='o', linestyle='None', markeredgecolor='black',
                       markersize=7, label='enctyption')
square = mlines.Line2D([], [], color='w', marker='s', linestyle='None', markeredgecolor='black',
                       markersize=7, label='total')
patch1 = mpatches.Patch(color='tab:blue', label='SecretStore')
patch2 = mpatches.Patch(color='tab:orange', label='UmbralPre')

plt.legend(handles=[patch1, patch2,
                    star, circle, square])

plt.savefig('../duel-message-length-graph.png', bbox_inches='tight', dpi=200)
