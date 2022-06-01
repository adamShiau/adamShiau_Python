from test import test as ACT
import time
import numpy as np

# act = ACT()
# act.isRun = True
# print(act.isRun)
# act.start()
# time.sleep(5)
# act.isRun = False
# time.sleep(2)
# act.isRun = True
# print("act.isRun: ", act.isRun)
# act.start()
# time.sleep(5)

import sys

sys.path.append("../")
from pigImuReader import IMU_DATA_STRUCTURE

from myLib import common as cmn

A = {k: [np.empty(0) for i in range(len(IMU_DATA_STRUCTURE.get(k)))]
                for k in set(IMU_DATA_STRUCTURE)}

AA = {"A1": [[1, 2, 3],[1, 2, 3],[1, 2, 3],], "B1": [[4, 5, 6]]}
BB = {"A1": [[1],[1],[1],], "B1": [2]}
# print(cmn.dictOperation(AA, BB, "SUB"))
print(AA["B1"][0])
print(BB["B1"][0])




