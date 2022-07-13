# -*- coding:UTF-8 -*-
""" ####### log stuff creation, always on the top ########  """
import builtins
import logging

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = __name__
logger = logging.getLogger(logger_name + '.' + __name__)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import sys
import os

sys.path.append("../../")
import numpy as np
import pandas as pd
import time
from myLib.myGui import graph
from myLib.myGui import myLabel
from myLib.myGui import myComboBox
from myLib.myGui import myProgressBar
import myLib.common as cmn
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import matplotlib.pyplot as plt

filename = '20220712_sp9_SF' + '.txt'
filename2 = '20220712_ix_sp9_SF' + '.txt'

data = pd.read_csv(filename, comment='#', skiprows=0, chunksize=None)
data2 = pd.read_csv(filename2, comment='#', skiprows=0, chunksize=None, sep='\t')
t = data['time']
fog = data['fog']
t2 = data2['Time']
wa = np.array(data2['wa'])
plt.plot(wa)
wt = np.array(data2['wt'])
size = len(wa)
print(len(wa))
wa2 = np.array(wa[1:size])
wa = wa[0:size - 1]
print(len(wa2))
# diff_wa = wa2 - wa
diff_wa = np.abs(wa2 - wa)
diff_wa2 = np.abs(wa2 - wa) > 5
idx1 = np.where(diff_wa2)[0]
for i in range(0, len(diff_wa2) - 1):

    if (diff_wa2[i]==False) and (diff_wa2[i + 1]==True):
        print(i, diff_wa2[i], diff_wa2[i + 1])
    #     print(idx1[i])
# idx2 = idx1[1:len(idx1)]
# idx1_1 = idx1[0:len(idx1)-1]
# is_idx = (idx2 - idx1_1) == 1
# print(idx1)
# idx3 = np.where(is_idx)[0]
# print(len(idx3))


# print(idx_pair)
# print('len(idx_pair): ', len(idx_pair))
# plt.plot(diff_wa2)
# idx = np.where(np.abs(diff_wa) > 50)[0]
# print(np.where(np.abs(diff_wa) > 50)[0])
# plt.plot(idx)
# plt.plot(np.abs(diff_wa))
plt.show()
