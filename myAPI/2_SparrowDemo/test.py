import numpy as np
import common as cmn
import time

IMU_DATA_STRUCTURE = {
    "A": (0, 0, 0),
    "TIMES": [.0]
}

darray = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
          for k in set(IMU_DATA_STRUCTURE)}
d = {k: np.zeros(len(IMU_DATA_STRUCTURE.get(k))) for k in set(IMU_DATA_STRUCTURE)}

print(darray)
print(d)
print(type(time.perf_counter()))

for i in range(10):
    d["A"] = (i, i+1, i+2)
    d["TIMES"] = [time.perf_counter()]
    cmn.dictOperation(darray, d, "APPEND")
    print(d)
print(darray)

