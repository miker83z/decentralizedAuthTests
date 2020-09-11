import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import numpy as np
import json
import sys

stats_file = sys.argv[1]
with open(stats_file) as json_file:
  data = json.load(json_file)

#means.sort()
#median.sort()
xdata = np.array(data)

# plot the data
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(xdata, color='tab:orange')

# display the plot
plt.show()
