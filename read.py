import py3lib.FileToArray as file
import numpy as np
import matplotlib.pyplot as plt


data = np.empty(0)

data = file.TexTFileto1DList('srs200_1.txt', '123')
# data2 = float(data)
print(type(data[0]))
plt.figure(1)
plt.plot(data)
plt.show()
# print(type(data2[0]))
