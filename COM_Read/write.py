import os 
import sys 
sys.path.append("../") 
import py3lib.FileToArray as file
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt


data = np.empty(0)
cnt = 0
time_header = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
# while(1):
	# data = np.append(data, cnt)
	# cnt = cnt + 1
	# time.sleep(0.5)
	# m1 = time.time()*1e6
	# file.array1DtoTextFile('save.txt',data,'123', header = time_header)
	# print(time.time()*1e6-m1)


# x = [(0, 1, 2, 3, 4, 5),
# (0, 1, 2, 3, 4, 6),

# ]
y = [(0, 1, 2, 3),
	(3, 4, 5, 6)
]

for i in y :
	print(i)

# print(y)

# plt.plot(x,y)
# plt.show()


# def array1DtoTextFile(fname, array, loggername, header = ""):