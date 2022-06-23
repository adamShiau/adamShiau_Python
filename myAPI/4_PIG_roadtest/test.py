import numpy as np

a = [i for i in range(0,1010)]
a = np.array(a)
ln = len(a)
print(len(a))
print(a)
b = a[ln-1000:ln+1]
print(len(b))
print(b)