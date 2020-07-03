import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import numpy as np
import json
import sys

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

x_data_int = np.array([10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000,
                       1000000])
x_data = np.array(['10\nB', '50\nB', '100\nB', '500\nB', '1\nKB', '5\nKB', '10\nKB', '50\nKB', '100\nKB', '500\nKB',
                   '1\nMB'])
# plot the data
#fig = plt.figure()
#ax = fig.add_subplot(1, 1, 1)
#plt.plot(x_data, enc, color='tab:green', label='encryption')
#plt.plot(x_data, dec, color='tab:orange', label='decryption')
#plt.plot(x_data, tot, color='tab:blue', label='total')

a, b = np.polyfit(x_data_int, enc, deg=1)
enc_est = a * x_data_int + b

a, b = np.polyfit(x_data_int, dec, deg=1)
dec_est = a * x_data_int + b

a, b = np.polyfit(x_data_int, tot, deg=1)
tot_est = a * x_data_int + b

plt.plot(x_data_int, enc_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, dec_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, tot_est, '--', color='tab:brown', alpha=0.5)
plt.plot(x_data_int, enc, 'o', color='tab:green', label='encryption')
plt.plot(x_data_int, dec, 'o', color='tab:orange', label='decryption')
plt.plot(x_data_int, tot, 'o', color='tab:blue', label='total')
plt.xscale('log')
#plt.yticks(np.arange(0, 1200, 100))
plt.xticks(x_data_int, ['10\nB', '50\nB', '100\nB', '500\nB', '1\nKB', '5\nKB', '10\nKB', '50\nKB', '100\nKB', '500\nKB',
                        '1\nMB'])

plt.ylabel('time [ms]')
plt.xlabel('length of message')

#plt.grid(axis='x', color='0.95')
plt.legend(title='Time[ms]')

plt.savefig('../message-length-graph.png', bbox_inches='tight', dpi=200)
