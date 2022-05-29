from test import test as ACT
import time
import numpy as np

import sys

sys.path.append("../")
from myLib import common as cmn
A = [1, 2, 3, 4, 500]

B = (np.vstack(A)).T

C = (np.vstack([4, 5, 6, 7, 8])).T
# print(A)
# print(type(A))
# print(B)
# print(type(B))


isopen, fd = cmn.file_manager(True, "tt2.txt")
print("isopen: ", isopen)
print("fd: ", fd)

isopen2, fd2 = cmn.file_manager(True, "tt3.txt", 0)

print("isopen2: ", isopen2)
print("fd2: ", fd2)

np.savetxt(fd2, C, fmt="%d, %d, %d, %d, %.2f")

for i in range(5):
    if isopen:
        np.savetxt(fd, B, fmt="%d, %d, %d, %d, %.2f")

print("isopen2: ", isopen2)
print("fd2: ", fd2)


isopen2, fd2 = cmn.file_manager(False, "tt3.txt", 0)
isopen, fd = cmn.file_manager(False, "tt2.txt")
print("isopen: ", isopen)
print("fd: ", fd)



