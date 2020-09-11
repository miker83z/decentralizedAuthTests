import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import numpy as np
import json
import sys

stats_file = sys.argv[1]
with open(stats_file) as json_file:
  data = json.load(json_file)

set_data = []
get_data = []
no_members_data = []

for item in data:
    set_data.append(item['set'])
    get_data.append(item['get'])
    no_members_data.append(item['no_members'])

#means.sort()
#median.sort()
set_data = np.array(set_data)
get_data = np.array(get_data)
no_members_data = np.array(no_members_data)

a, b = np.polyfit(no_members_data, set_data, deg=1)
set_est = a * no_members_data + b

a, b = np.polyfit(no_members_data, get_data, deg=1)
get_est = a * no_members_data + b


#plt.plot(x_data, tot_est, '--', color='tab:brown', alpha=0.5)
plt.plot(no_members_data, set_data, 'o', color='tab:green', label='allow users')
plt.plot(no_members_data, get_data, 'o', color='tab:orange', label='check permission')
plt.plot(no_members_data, set_est, '--', color='tab:brown', alpha=0.5)
plt.plot(no_members_data, get_est, '--', color='tab:brown', alpha=0.5)

plt.yticks(np.arange(0, 1200, 100))
plt.xticks(np.arange(0, 400, 50))
plt.ylabel('time [ms]')
plt.xlabel('number of room members')

plt.grid(axis='x', color='0.95')
plt.legend(title='Time[ms]')

# display the plot
plt.savefig('used-gas-graph.png', bbox_inches='tight', dpi=200)
