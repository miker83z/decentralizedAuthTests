import matplotlib.pyplot as plt
from matplotlib.collections import EventCollection
import numpy as np
import json
import sys

stats_file = sys.argv[1]
with open(stats_file) as json_file:
  data = json.load(json_file)

used_gas = []
no_members_data = []

for item in data:
    used_gas.append(item['used_gas'])
    no_members_data.append(item['no_members'])

#means.sort()
#median.sort()
used_gas = np.array(used_gas)
no_members_data = np.array(no_members_data)

a, b = np.polyfit(no_members_data, used_gas, deg=1)
used_gas_est = a * no_members_data + b


plt.plot(no_members_data, used_gas, 'o', color='tab:orange', label='used gas')
plt.plot(no_members_data, used_gas_est, '--', color='tab:brown', alpha=0.5)

#plt.yticks(np.arange(0, 1200, 100))
plt.xticks(np.arange(0, 400, 50))
plt.ylabel('used gas')
plt.xlabel('number of room members')

plt.grid(axis='x', color='0.95')
#plt.legend(title='Time[ms]')

# display the plot
plt.savefig('used-gas-graph.png', bbox_inches='tight', dpi=200)
