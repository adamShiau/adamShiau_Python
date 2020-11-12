# import allantools
import allantools # https://github.com/aewallin/allantools/
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append("../")
import py3lib.FileToArray as file


# Compute a deviation using the Dataset class
# data = np.random.rand(1000);
# plt.figure(1)
# plt.plot(data)

data = file.TexTFileto1DList('srs200_1.txt', '123')
data = [float(i) for i in data]
print(len(data))
print(type(data))
print(type(data[0]))


a = allantools.Dataset(data, rate=100.0)
a.compute("adev")


# New in 2019.7 : write results to file
a.write_results("output.dat")

# Plot it using the Plot class
b = allantools.Plot()
# New in 2019.7 : additional keyword arguments are passed to
# matplotlib.pyplot.plot()
b.plot(a, errorbars=True, grid=True, linestyle = '-', marker = '')
# You can override defaults before "show" if needed
b.ax.set_xlabel("Tau (s)")
b.show()
