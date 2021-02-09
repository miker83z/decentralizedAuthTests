import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import json
import sys


def threshold():
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

    axes[0].grid(axis='y', color='0.8', zorder=0)

    axes[0].bar(x_data - 0.175, enc, .35, color='lightcoral',
                edgecolor='black', align='center', zorder=3)
    axes[0].bar(x_data - 0.175, key, .35, color='brown', edgecolor='black',
                bottom=enc, align='center', zorder=3)
    axes[0].bar(x_data - 0.175, dec, .35, color='darkred', edgecolor='black',
                bottom=tot, align='center', zorder=3)

    axes[0].bar(x_data + 0.175, enc2, .35, color='lightsteelblue',
                edgecolor='black', align='center', zorder=3)
    axes[0].bar(x_data + 0.175, key2, .35, color='royalblue', edgecolor='black',
                bottom=enc2, align='center', zorder=3)
    axes[0].bar(x_data + 0.175, dec2, .35, color='darkblue', edgecolor='black',
                bottom=tot2, align='center', zorder=3)

    #axes[0].yticks(np.arange(0, 1200, 100))
    axes[0].set_xticks(np.arange(1, 26, 2))
    axes[0].set_ylabel('latency (ms)')
    axes[0].set_xlabel('threshold value')

    axes[0].set_ylim(0, 1450)


def nodes():
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

    axes[1].grid(axis='y', color='0.8', zorder=0)

    axes[1].bar(x_data - 0.75, enc, 1.5, color='brown',
                edgecolor='black', align='center', zorder=3)
    axes[1].bar(x_data - 0.75, dec, 1.5, color='darkred', edgecolor='black',
                bottom=enc, align='center', zorder=3)

    axes[1].bar(x_data + 0.75, enc2, 1.5, color='royalblue',
                edgecolor='black', align='center', zorder=3)
    axes[1].bar(x_data + 0.75, dec2, 1.5, color='darkblue', edgecolor='black',
                bottom=enc2, align='center', zorder=3)

    #axes[1].yticks(np.arange(0, 1200, 100))
    axes[1].set_xticks(np.array([5, 10, 15, 20, 25]))
    #axes[1].set_ylabel('latency (ms)')
    axes[1].get_yaxis().set_ticklabels([])
    axes[1].set_xlabel('nodes number')

    axes[1].set_ylim(0, 1450)

    patch01 = mpatches.Patch(color='brown', label='SS')
    patch02 = mpatches.Patch(color='royalblue', label='TPRE')
    patch1 = mpatches.Patch(color='dimgray', label='decryption (dark)')
    patch2 = mpatches.Patch(color='silver', label='keys distr (medium)')
    patch3 = mpatches.Patch(color='whitesmoke', label='encryption (light)')

    axes[1].legend(handles=[patch01, patch02, patch1, patch2, patch3])


def messages():
    x_data_int = np.array([10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000,
                           1000000, 5000000, 10000000])
    x_data = np.array(['10\nB', ' ', '100\nB', ' ', '1\nKB', ' ', '10\nKB', ' ', '100\nKB', ' ',
                       '1\nMB', ' ', '10\nMB'])
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
    axes2.plot(x_data_int, enc, color='brown',
               linestyle="solid", linewidth=2)

    axes2.plot(x_data_int, enc2, color='royalblue',
               linestyle="solid", linewidth=2)

    axes2.plot(x_data_int, dec, color='brown',
               linestyle="dotted", linewidth=4)

    axes2.plot(x_data_int, dec2, color='royalblue',
               linestyle="dotted", linewidth=4)

    axes2.set_xscale('log')
    # axes2.set_yscale('log')
    axes2.set_xticks(x_data_int)
    axes2.set_xticklabels(x_data)

    axes2.set_ylabel('latency (ms)')
    axes2.set_xlabel('log scale message size (B)')

    patch01 = mpatches.Patch(color='brown', label='SS')
    patch02 = mpatches.Patch(color='royalblue', label='TPRE')
    soli = mlines.Line2D([], [], color='black',
                         linestyle='dotted', label='decryption')
    dott = mlines.Line2D([], [], color='black',
                         linestyle='solid', label='enc + keys distr')

    axes2.legend(handles=[patch01, patch02, dott, soli])


widths = [2.5, 1]
fig, axes = plt.subplots(
    nrows=1, ncols=2, constrained_layout=True, gridspec_kw=dict(width_ratios=widths))
fig.set_size_inches(10.5, 5)

threshold()
nodes()
# display the plot
plt.savefig('../complete.png', bbox_inches='tight', dpi=300)

plt.figure(2)
fig2, axes2 = plt.subplots(
    nrows=1, ncols=1, constrained_layout=True)
fig2.set_size_inches(4.5, 5)
messages()
plt.savefig('../complete2.png', bbox_inches='tight', dpi=300)
