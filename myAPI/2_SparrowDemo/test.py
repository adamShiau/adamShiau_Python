import numpy as np
import common as cmn

IMU_DATA_STRUCTURE = {
    "NANO33_W": (.0, .0, .0),
    "NANO33_A": (.0, .0, .0),
    "ADXL_A": (.0, .0, .0)
}

offset = {
    "NANO33_W": (1, 1, 1),
    "NANO33_A": (2, 2, 2),
    "ADXL_A": (.0, .0, .0)
}

# A = [np.zeros(3) for i in range(3)]
# print(A[0])

# print([IMU_DATA_STRUCTURE.get(k) for k in set(IMU_DATA_STRUCTURE)])
rt = {k: np.array(IMU_DATA_STRUCTURE.get(k)) for k in set(IMU_DATA_STRUCTURE)}
# print(rt)

A = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
     for k in set(IMU_DATA_STRUCTURE)}
B = {k: np.zeros(len(IMU_DATA_STRUCTURE.get(k))) for k in set(IMU_DATA_STRUCTURE)}
# print(A)

for i in range(10):
    B["NANO33_W"] = (i, i + 1, i + 2)
    B["NANO33_A"] = (2 * i, 2 * i + 1, 2 * i + 2)
    B["ADXL_A"] = (3 * i, 3 * i + 1, 3 * i + 2)
    print("B: ", B)
    cmn.dictOperation(A, B, "APPEND")

print("A: ", A)

# for k in set(B):
#     for j in range(len(B.get(k))):
#         rt.get(k)[j] = dictA.get(k)[j] - dictB.get(k)[j]

rt = {k: np.array(A.get(k)) for k in set(A)}
print(rt)

# A1 = A["NANO33_A"][0] - B["NANO33_A"][0]
# print(A["NANO33_A"][0])
# print(B["NANO33_A"][0])
# print(A1)
print(cmn.dictOperation(rt, offset, "SUB"))
