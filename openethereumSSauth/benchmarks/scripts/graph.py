import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import numpy as np
import json
import sys

stats_file = sys.argv[1]
with open(stats_file) as json_file:
  data = json.load(json_file)

means = []
median = []

for item in data:
    print(item['mean'] / 10**9)
    means.append(item['mean'] / 10**9)

for item in data:
    print(item['median'] / 10**9)
    median.append(item['median'] / 10**9)

#means.sort()
#median.sort()
xdata = np.array(means)
xdata2 = np.array(median)

# plot the data
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(xdata, color='tab:orange')
ax.plot(xdata2, color='tab:blue')

# display the plot
plt.show()
