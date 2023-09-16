import matplotlib.pyplot as plt
from multiprocessing import shared_memory
import time as t
from typing import Union
import numpy as np


def EWMA(current, previous, beta=(2/11.0)):
    if previous is not None:
        return np.add(np.multiply(current, beta), np.multiply(previous, 1 - beta))
    else:
        return current

flabel = {"Fx": 0,
		  "Fy": 1,
		  "Fz": 2,
		  "Tx": 3,
		  "Ty": 4,
		  "Tz": 5}

funits = {"Fx": 'N',
		  "Fy": 'N',
		  "Fz": 'N',
		  "Tx": 'Nm',
		  "Ty": 'Nm',
		  "Tz": 'Nm'}


# n is the number of data points to display on the plot
# lb is the lower error margin, ub is the upper error margin
# arr is the shared memory array (shared with force recorder)
# arr is initialize to a huge value (999) since Array
# cannot accept None dtype
# nplt allows selection of subplots to show. Accepts list or str
# ie.: ["Fx", "Fy", "Fz"] shall plot Fx, Fy and Fz in subplots; "Fz" shall plot only Fz
def force_monitor(arr, n=100, eb:Union[list[tuple], None]=None, nplt:list[str]=["Fz"],
				  ylim:list[tuple]=[(-5,5)]):
	
	c_shm = shared_memory.SharedMemory('calib')
	q_shm = shared_memory.SharedMemory('quit')
	time = []  # in terms of data points
	count = 0
	
	series = {"Fx": [],
			  "Fy": [],
		      "Fz": [],
		      "Tx": [],
		      "Ty": [],
		      "Tz": []}
	
	filtered = {"Fx": [],
				"Fy": [],
				"Fz": [],
				"Tx": [],
				"Ty": [],
				"Tz": []}
		      
	beta = 2.0 / 11.0  # for filtering of the data series
	prev = None
	
	plt.ion()
	fig, axes = plt.subplots(len(nplt))
	
	while True:
		if c_shm.buf[:5] == b'ended':
			break
	
	if eb is not None:
		
		for i, ax in enumerate(axes):
			lower_margin = [eb[i][0]] * n
			upper_margin = [eb[i][1]] * n
			ax.plot(time, series[nplt[i]], color='blue')
			ax.plot(time, filtered[nplt[i]], color='green')
			ax.plot(range(n), lower_margin, color='red')
			ax.plot(range(n), upper_margin, color='red')
			ax.set_xlabel('Time')
			ax.set_ylabel(f'{nplt[i]} ({funits[nplt[i]]})')
			ax.set_ylim(ylim[i][0], ylim[i][1])
			ax.set_xlim([0, n - 1])
		
		plt.tight_layout(pad=0.5)
		
		fig.show()
		
		while q_shm.buf[:5] != b'quit!':
			prev = EWMA(arr, prev, beta)
			if 999 not in arr:
				if count == n:
					for key in nplt:
						del series[key][0]
						del filtered[key][0]
						series[key].append(arr[flabel[key]])
						filtered[key].append(prev[flabel[key]])
				else:
					for key in nplt:
						series[key].append(arr[flabel[key]])
						filtered[key].append(prev[flabel[key]])
					time.append(count)
					count = count + 1
				for i, ax in enumerate(axes):
					ax.lines[0].set_data(time, series[nplt[i]])
					ax.lines[1].set_data(time, filtered[nplt[i]])
				fig.canvas.flush_events()
				t.sleep(0.0001)
			
	else:
		
		for i, ax in enumerate(axes):
			ax.plot(time, series[nplt[i]], color='blue')
			ax.plot(time, filtered[nplt[i]], color='green')
			ax.plot(range(n), lower_margin, color='red')
			ax.plot(range(n), upper_margin, color='red')
			ax.set_xlabel('Time')
			ax.set_ylabel(f'{nplt[i]} ({funits[nplt[i]]})')
			ax.set_ylim(ylim[i][0], ylim[i][1])
			ax.set_xlim([0, n - 1])
		
		plt.tight_layout(pad=0.5)
		fig.show()
		
		while q_shm.buf[:5] != b'quit!':
			prev = EWMA(arr, prev, beta)
			if 999 not in arr:
				if count == n:
					for key in nplt:
						del series[key][0]
						del filtered[key][0]
						series[key].append(arr[flabel[key]])
						filtered[key].append(prev[flabel[key]])
				else:
					for key in nplt:
						series[key].append(arr[flabel[key]])
						filtered[key].append(prev[flabel[key]])
					time.append(count)
					count = count + 1
				for i, ax in enumerate(axes):
					ax.lines[0].set_data(time, series[nplt[i]])
					ax.lines[1].set_data(time, filtered[nplt[i]])
				fig.canvas.flush_events()
				t.sleep(0.0001)
	c_shm.close()
	q_shm.close()


if __name__ == '__main__':
	force_monitor()
