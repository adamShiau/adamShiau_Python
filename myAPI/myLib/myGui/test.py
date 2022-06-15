import numpy as np

a = np.array([1, 2, 3, 4, 4, 5, 6])
b=np.array([8,9])

# print(np.unique(a))
a = np.append(a, b)
a =np.delete(a, [-1])
print(a[0:3])
# print(np.array(b).astype(int))